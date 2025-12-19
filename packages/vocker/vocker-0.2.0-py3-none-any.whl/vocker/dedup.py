from __future__ import annotations

import abc
import contextlib
import filelock
import io
import json
import os
from pathlib import Path
import shutil
import stat
import threading
import time

import typing as ty
import attr
import structlog
import concurrent.futures as cf

import sqlalchemy as sa
from sqlalchemy import orm as sao
from sqlalchemy_boltons import sqlite as sq
from sqlalchemy_boltons.orm import RelationshipComparator as Rel, IdKey
from sqlalchemy_boltons.temporary import temporary_table
from sqlalchemy_boltons.core import bytes_startswith
from boltons.iterutils import chunked_iter
from cached_property import cached_property

from .integer_to_path import IntegerToPath, InvalidPathError
from .util import pathwalk, random_names, create_file_random, supports_executable
from . import dedup_models as mo
from . import multihash as mh


logger = structlog.get_logger(__name__)


@attr.s(eq=False, hash=False)
class Corrupted:
    path: Path | None = attr.ib()
    file_id: int = attr.ib()
    exception: str = attr.ib()
    link_paths: frozenset[str] = attr.ib()
    raw_link_paths: frozenset[str] = attr.ib()

    def to_json(self):
        d = attr.asdict(self)
        d["path"] = p if (p := d["path"]) is None else str(p)
        for k in ("link_paths", "raw_link_paths"):
            d[k] = sorted(d[k])
        return d


@attr.s(eq=False, hash=False, kw_only=True)
class DedupFileMetadata:
    executable: bool = attr.ib(default=False)

    @classmethod
    def make_plain(cls):
        return cls(executable=False)


@attr.s(eq=False, hash=False, auto_exc=True)
class InvalidContentsError(Exception):
    message = attr.ib(default="file contents do not match hash")
    link_request: DedupLinkRequest | None = attr.ib(default=None)
    hashes_expected: dict[mh.HashFunction, mh.Digest] | None = attr.ib(default=None)
    hashes_observed: dict[mh.HashFunction, mh.Digest] | None = attr.ib(default=None)


@attr.s(eq=False, hash=False, auto_exc=True)
class BatchError(Exception):
    message = attr.ib(default="at least one of the DedupLinkRequests failed")
    requests: list[DedupRequest] | None = attr.ib(default=None)


class NotADedupLinkError(Exception):
    pass


class MissingContentError(Exception):
    pass


@attr.s(eq=False, hash=False, kw_only=True)
class DedupRequest:
    success: bool = attr.ib(init=False, default=False)
    exc: Exception | None = attr.ib(init=False, default=None)

    def result(self):
        if self.exc is not None:
            raise self.exc
        return self.success


@attr.s(eq=False, hash=False, kw_only=True)
class DedupLinkRequest(DedupRequest):
    """
    Represents a single request to link a deduped file at a filesystem location :attr:`link_path`.
    If the file is already in the dedup folder, then link it. Otherwise add it to the dedup folder
    by first getting its contents from :attr:`open_file_once`. These requests are batched and
    executed together.

    If a file already exists at :attr:`link_path`, then it will be removed before linking. If it is
    a directory, then an exception will be raised.

    The :attr:`open_file_once` function will be called *at most* once. If a deduplicated file
    already exists in the dedup folder with the same :attr:`file_contents_hash` and equal or
    equivalent :attr:`file_metadata`, then it will be reused and the :attr:`open_file_once` function
    will not be called at all.

    The :attr:`open_file_once` function should an open file handle from which the file contents can
    be read. If :attr:`open_file_once` is None, then the link request will be silently
    discarded.

    Each :attr:`open_file_once` function will be called in the order it appears in a batch of
    requests. This guarantee supports the use case of directly decompressing a
    [solid archive](https://en.wikipedia.org/wiki/Solid_archive), in which case file contents
    become available in a sequential manner as the archive is decompressed and it is impossible
    to efficiently access files in a random order.

    The file contents hash will be (over)written to :attr:`file_contents_hash`.

    The :attr:`tags` argument is used as a sort of label that can be used to refer to a deduplicated
    file. If there exists another deduplicated file that shares at least one tag with :attr:`tags`,
    then that deduplicated file will be used. That existing deduplicated file will be used
    regardless of the :attr:`file_contents_hash`.

    If :attr:`file_contents_hash` is None and no matching :attr:`tags` was found,
    then :attr:`open_file_once` will always be called. Without the content hash, we have no way
    of checking whether a deduplicated file with the same hash exists.
    """

    hash_function: mh.HashFunction = attr.ib()
    link_path: Path = attr.ib()
    file_metadata: DedupFileMetadata = attr.ib()
    file_contents_hash: mh.Digest | None = attr.ib()
    open_file_once: ty.Callable[[], ty.BinaryIO] | None = attr.ib()
    file_not_needed: ty.Callable[[], None] | None = attr.ib(default=None)
    tags: ty.Set[bytes] = attr.ib(factory=frozenset)

    @classmethod
    def from_content(cls, content: bytes, **kwargs):
        kwargs.setdefault("open_file_once", None)
        kwargs.setdefault("file_contents_hash", None)
        return cls(**kwargs).set_content(content)

    def set_content(self, content: bytes):
        self.file_contents_hash = self.hash_function().update(content).digest()
        self.open_file_once = lambda: io.BytesIO(content)
        return self


@attr.s(eq=False, hash=False, kw_only=True)
class _ImplDedupRequestCommon:
    index: int = attr.ib()
    failed: bool = attr.ib(default=False)

    @abc.abstractmethod
    def set_failed(self, exc): ...


@attr.s(eq=False, hash=False, kw_only=True)
class _ImplDedupLinkRequest(_ImplDedupRequestCommon):
    req: DedupLinkRequest = attr.ib(default=None)
    lookup_key = attr.ib(default=None)
    dedup_file_path: Path = attr.ib(default=None)
    link_path_str: bytes | None = attr.ib(default=None)
    file: IdKey[mo.DedupFile] | None = attr.ib(default=None)
    metadata_bytes: bytes | None = attr.ib(default=None)
    file_size: int = attr.ib(default=None)
    file_mtime: int = attr.ib(default=None)
    fast_path: bool = attr.ib(default=False)  # can we use the fast-path without db transaction?
    is_new: bool = attr.ib(default=False)  # is it a brand new FileDedup?
    hashes_promised: dict[mh.HashFunction, mh.Digest] = attr.ib(default=None)
    hashes_computed: dict[mh.HashFunction, mh.Digest] | None = attr.ib(default=None)
    called_file: bool = attr.ib(default=False)

    def set_failed(self, exc):
        self.req.exc = exc
        self.failed = True
        self.call_file_not_needed()

    def call_file_not_needed(self) -> None:
        if not self.called_file:
            if (f := self.req.file_not_needed) is not None:
                try:
                    f()
                except Exception:
                    logger.warning("uncaught exception", exc_info=True)
            self.called_file = True

    def call_open_file_once(self):
        if self.called_file:
            raise AssertionError
        try:
            return self.req.open_file_once()
        finally:
            self.called_file = True


@attr.s(eq=False, hash=False)
class DedupCopyLinkRequest(DedupRequest):
    src: Path = attr.ib()
    dst: Path = attr.ib()


@attr.s(eq=False, hash=False, kw_only=True)
class _ImplDedupCopyLinkRequest(_ImplDedupRequestCommon):
    req: DedupCopyLinkRequest = attr.ib()
    src_str: str = attr.ib(default=None)
    dst_str: str = attr.ib(default=None)
    dedup_file_path: Path = attr.ib(default=None)

    def set_failed(self, exc):
        self.req.exc = exc
        self.failed = True


@attr.s(eq=False, hash=False)
class AdoptRequest:
    path: Path = attr.ib()
    tags: ty.Set[bytes] = attr.ib(factory=frozenset)

    out_size: int | None = attr.ib(init=False, default=None)
    out_digest: mh.Digest | None = attr.ib(init=False, default=None)


@attr.s(eq=False, hash=False)
class _ImplAdoptRequest:
    req: AdoptRequest = attr.ib()
    link_path: bytes = attr.ib(default=None)
    file_metadata: DedupFileMetadata = attr.ib(default=None)
    file_metadata_bytes: bytes = attr.ib(default=None)
    done: bool = attr.ib(default=False)
    dedup_file_path: Path = attr.ib(default=None)
    delete: bool = attr.ib(default=False)


"""
@attr.s(eq=False, hash=False)
class DedupUnlinkRequest(DedupRequest):
    link_path: Path = attr.ib()
"""


class DedupError:
    pass


@attr.s(frozen=True)
class DedupStats:
    dedup_count: int = attr.ib()
    orphaned_count: int = attr.ib()
    link_count: int = attr.ib()
    dedup_total_bytes: int = attr.ib()
    orphaned_total_bytes: int = attr.ib()
    link_total_bytes: int = attr.ib()

    def to_json(self):
        return attr.asdict(self)


@attr.s(frozen=True)
class DedupFile:
    pass


@attr.s(eq=False, hash=False)
class _PendingUpdater:
    sessionmaker_r: sao.sessionmaker = attr.ib()
    sessionmaker_w: sao.sessionmaker = attr.ib()
    pending: IdKey[mo.Pending] = attr.ib()
    seconds_in_the_future: int = attr.ib()
    update_interval: float = attr.ib(default=None)
    _should_exit = False
    update_on_exit: bool = attr.ib(default=False)

    def __attrs_post_init__(self):
        if self.update_interval is None:
            self.update_interval = (self.seconds_in_the_future - 3) / 2

        if (u := self.update_interval) < 1:
            raise ValueError(f"invalid update_interval={u!r}")

    def _update(self):
        with self.sessionmaker_w() as s:
            pending: mo.Pending = self.pending.get_one(s)
            pending.expire_at = mo.now() + self.seconds_in_the_future

    def _thread_target(self):
        while not self._should_exit:
            t = self.update_interval
            try:
                self._update()
            except Exception:
                logger.warning("failed to update pending", exc_info=True)
                t = 1  # try again soon
            self._event.wait(t)
            self._event.clear()
        if self.update_on_exit:
            self._update()

    def start(self):
        self._should_exit = False
        self._event = threading.Event()
        self._thread = t = threading.Thread(target=self._thread_target)
        t.start()

    def stop(self):
        self._should_exit = True
        self._event.set()
        self._thread.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()


class SkippedReqException(Exception):
    pass


def make_sqlite_options(synchronous):
    return sq.Options.new(
        timeout=60.0,
        begin="DEFERRED",
        foreign_keys="DEFERRED",
        recursive_triggers=True,
        trusted_schema=True,
        schemas={"main": sq.SchemaOptions.new(journal="WAL", synchronous=synchronous)},
    )


@attr.s(eq=False, hash=False)
class Dedup(abc.ABC):
    base_path: Path = attr.ib()
    extra_hashes: ty.Set[mh.HashFunction] = attr.ib(
        factory=lambda: {mh.registry.name_to_hash["sha2-256"]}
    )
    _path_dedup: Path | None = attr.ib(default=None, kw_only=True)
    _path_db: Path | None = attr.ib(default=None, kw_only=True)
    path_temporary: Path | None = attr.ib(default=None, kw_only=True)
    path_deleted: Path | None = attr.ib(default=None, kw_only=True)
    path_corrupted: Path | None = attr.ib(default=None, kw_only=True)
    _integer_to_path = attr.ib(factory=IntegerToPath, kw_only=True)
    _sqlite_synchronous = attr.ib(default="NORMAL", kw_only=True)
    _batch_size = 1000

    def __attrs_post_init__(self):
        if self._path_dedup is None:
            self._path_dedup = self.base_path / "f"

        if self._path_db is None:
            self._path_db = self.base_path / "dedup.db"

        if self.path_deleted is None:
            self.path_deleted = self.base_path / "deleted"

        if self.path_temporary is None:
            self.path_temporary = self.base_path / "tmp"

        if self.path_corrupted is None:
            self.path_corrupted = self.base_path / "corrupted"

        self._path_dedup.mkdir(exist_ok=True, parents=True)
        self._path_db.parent.mkdir(exist_ok=True, parents=True)
        self.path_corrupted.mkdir(exist_ok=True, parents=True)
        self.path_deleted.mkdir(exist_ok=True, parents=True)
        self._path_temporary_dirs.mkdir(exist_ok=True, parents=True)
        self._path_temporary_lock.mkdir(exist_ok=True, parents=True)
        engine = sq.create_engine_sqlite(self._path_db, create_engine_args=dict(echo=False))
        engine = make_sqlite_options(synchronous=self._sqlite_synchronous).apply(engine)
        self._engine_r = engine
        self._engine_w = sq.Options.apply_lambda(engine, lambda x: x.evolve(begin="IMMEDIATE"))

        self._SessionR = sao.sessionmaker(self._engine_r)
        self._SessionW = sao.sessionmaker(self._engine_w)

        # FIXME: use proper session management
        # self.session = Session(self.engine_rw)  # HACK
        # self.engine = self.engine_rw  # HACK

        self._initialize_db()

    def _initialize_db(self):
        """Initialize the database schema."""
        with self._engine_w.connect() as conn:
            mo.BaseDedup.metadata.create_all(conn)
            conn.commit()

    @contextlib.contextmanager
    def _beginw(self):
        with self._SessionW.begin() as s:
            s.connection()  # ensure the transaction is started
            yield s

    def apply_metadata_to_file(self, path: Path, metadata: DedupFileMetadata) -> None:
        if supports_executable():
            mode = path.lstat().st_mode
            if not stat.S_ISDIR(mode) and bool(stat.S_IXUSR & mode) != metadata.executable:
                mask = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                new_mode = mode & ~mask
                if metadata.executable:
                    new_mode |= mask
                os.chmod(str(path), new_mode, follow_symlinks=False)

    def get_metadata_from_file(self, path: Path) -> DedupFileMetadata:
        if supports_executable():
            mode = path.stat().st_mode
            if not stat.S_ISREG(mode):
                raise AssertionError
            return DedupFileMetadata(executable=bool(stat.S_IXUSR & mode))
        else:
            return DedupFileMetadata(executable=False)

    def convert_file_metadata_to_bytes(self, metadata: DedupFileMetadata) -> bytes:
        # TODO: make it platform-dependent whether we care about the executable bit
        return b"x=" + str(int(metadata.executable)).encode("ascii")

    def _link_path_to_string(self, p: Path) -> bytes:
        return str(p).encode("utf-8")

    def _link_path_from_string(self, data: bytes) -> Path:
        return Path(data.decode("utf-8"))

    @contextlib.contextmanager
    def _ignore_skip(self):
        try:
            yield
        except SkippedReqException:
            pass

    @contextlib.contextmanager
    def _catch_req_exc(self, r: _ImplDedupLinkRequest | _ImplDedupCopyLinkRequest):
        if r.failed:
            raise SkippedReqException from None
        try:
            yield
        except Exception as exc:
            r.set_failed(exc)
            raise SkippedReqException from None

    def _cfg_hash_functions_get(self, s: sao.Session):
        # TODO: not used yet
        if (cfg := s.get(mo.DedupConfig, "hashes")) is None:
            h = self._DEFAULT_HASHES
        else:
            h = json.loads(cfg.value)

        return [mh.registry.name_to_hash[name] for name in h]

    def _cfg_hash_functions_set(self, s: sao.Session, hashes: list[mh.HashFunction]):
        # TODO: not used yet
        if (cfg := s.get(mo.DedupConfig, "hashes")) is None:
            cfg = mo.DedupConfig(key="hashes", value="")
        cfg.value = json.dumps([h.name for h in hashes])

    def _make_dedup_file(self, link: _ImplDedupLinkRequest, pending=None):
        f = mo.Hash.from_digest
        return mo.DedupFile(
            file_metadata=link.metadata_bytes,
            size=0,
            mtime=0,
            orphaned_at=None,
            pending=pending,
            hashes=[f(h) for h in link.hashes_promised.values()],
        )

    def _add_tags_to_file(self, session: sao.Session, file: mo.DedupFile, tags: ty.Set[bytes]):
        if not tags:
            return

        Tag = sao.aliased(mo.Tag)
        current_tags = frozenset(
            session.execute(sa.select(Tag.name).where(Tag.file == file)).scalars().all()
        )
        for name in tags - current_tags:
            session.add(mo.Tag(name=name, file=file))

    def _prepare_dedup_file_for_linking(
        self, session: sao.Session, file: mo.DedupFile, link: _ImplDedupLinkRequest
    ):
        if link.is_new:
            # We need to flush so that the DedupFile gets assigned an ID. The merge below needs it.
            session.flush()

        # We add our tags.
        self._add_tags_to_file(session, file, link.req.tags)

        # Delete any existing link.
        session.connection().execute(
            sa.delete(mo.Link)
            .where(mo.Link.link_path == link.link_path_str)
            .execution_options(synchronize_session=False)
        )

        # Create link object.
        session.add(mo.Link(link_path=link.link_path_str, file=file))

        # Since we created a link, the file is definitely not orphaned.
        file.orphaned_at = None

        # This also relies on the flush above.
        link.dedup_file_path = self._make_dedup_file_path(file.id)

    def run_batch(self, requests: ty.Iterable[DedupRequest]) -> None:
        """
        Link and/or delete many files using batching for efficiency. If the
        :attr:`DedupLinkRequest.file_hash` attribute is ``None``, then write the file hash to it.

        The requests will be addressed in the order that they appear in the iterable.

        Notes
        -----

        The implementation tries to spend as little time as possible inside database transactions.

        1. Search database for existing deduplicated files that can be reused. These are files
           that match either the hash or one of the tags.
        2. Create a record for each new deduplicated file. Create a Pending
        3.

        NEW IDEA FIXME
        --------------

        Split into fast path and slow path. If it's a brand new file OR it's an existing file that
        is done being written (not pending), then that's the fast path. Otherwise it's the slow
        path.

        On the *fast path* we don't need to check for what other threads are doing.

        """

        links = []
        copies = []
        # unlinks = []
        for i, req in enumerate(requests):
            if isinstance(req, DedupLinkRequest):
                links.append(_ImplDedupLinkRequest(req=req, index=i))
            elif isinstance(req, DedupCopyLinkRequest):
                copies.append(_ImplDedupCopyLinkRequest(req=req, index=i))
            else:
                raise TypeError(f"{type(req)!r}")

        if links and copies:
            # We don't do this yet because a copy request could be interfering with a link request
            # by having the same source or destination link.
            raise AssertionError(
                "doing both links and copies in the same batch is not supported for now"
            )

        # Preliminaries to do before we start writing to the database.
        all_tags: set[bytes] = set()
        hashes_to_search: list[dict] = []
        with self._SessionR() as s:
            for link in links:
                with self._ignore_skip(), self._catch_req_exc(link):
                    req = link.req
                    link.link_path_str = self._link_path_to_string(req.link_path)
                    # Remove existing file if present. This may raise if the path is actually a
                    # directory.
                    req.link_path.unlink(missing_ok=True)

                    all_tags |= req.tags

                    link.metadata_bytes = self.convert_file_metadata_to_bytes(req.file_metadata)

                    if (h := req.file_contents_hash) is not None:
                        link.lookup_key = h, link.metadata_bytes
                        d = {
                            "id": link.index,
                            "hash_function": h.function.function_code,
                            "digest": h.digest,
                            "metadata_bytes": link.metadata_bytes,
                        }
                        hashes_to_search.append(d)
                        link.hashes_promised = {h.function: h}
                    else:
                        link.hashes_promised = {}

        for copy in copies:
            with self._ignore_skip(), self._catch_req_exc(copy):
                req = copy.req
                copy.src_str = self._link_path_to_string(req.src)
                copy.dst_str = self._link_path_to_string(req.dst)

        def _q_gather_file_related(s, cls, attribute, values_set):
            """
            Query DedupFile-related information.
            """
            if not values_set:
                return ()  # short-cut to avoid doing the query at all
            Related = sao.aliased(cls)
            q = sa.select(Related).where(getattr(Related, attribute).in_(values_set))
            q = q.options(sao.joinedload(Related.file))
            return s.execute(q).scalars()

        # Now we check the database and add file hash records where we can.
        with self._beginw() as s:
            s.add(pending := mo.Pending(expire_at=mo.now() + 30.0))
            s.flush()
            pending_key = IdKey.from_instance(pending)

            # Load relevant tags.
            q = _q_gather_file_related(s, mo.Tag, "name", all_tags)
            tag_to_file: dict[bytes, mo.DedupFile] = {x.name: x.file for x in q}

            # Load relevant hashes.
            if hashes_to_search:
                with temporary_table(s, mo.tmp_hash_lookup) as tmp:
                    s.connection().execute(sa.insert(tmp), hashes_to_search).close()
                    H = sao.aliased(mo.Hash)
                    F = sao.aliased(mo.DedupFile)
                    q = (
                        sa.select(H, F)
                        .join(F, H.file)
                        .join(
                            tmp,
                            (tmp.c.digest == H.hash)
                            & (tmp.c.hash_function == H.hash_function)
                            & (tmp.c.metadata_bytes == F.file_metadata),
                        )
                    )
                    hash_to_file = {
                        (h.to_digest(), f.file_metadata): f for h, f in s.execute(q).all()
                    }
            else:
                hash_to_file = {}

            # Construct a set so that we can check for intersection quickly.
            tag_to_file_set = set(tag_to_file)

            for link in links:
                if link.failed:
                    continue

                req = link.req

                if overlap := req.tags & tag_to_file_set:
                    # We found a deduped file with a common alternate key! We use it!
                    file = tag_to_file[next(iter(overlap))]
                elif (key := link.lookup_key) is not None:
                    # Check for a deduped file with the same hash.
                    file = hash_to_file.get(key, None)
                else:
                    file = None

                if file is None:
                    # We did not find a matching file. We create a new one if we can.
                    link.is_new = True
                    link.fast_path = True

                    if req.open_file_once is None:
                        # The user does not actually have the contents of the file. We skip over
                        # it.
                        link.set_failed(MissingContentError())
                        continue

                    # We must create a file.
                    s.add(file := self._make_dedup_file(link, pending))
                elif file.pending_id is None:
                    # We found a matching file and it is not pending. We can use it directly.
                    link.fast_path = True
                else:
                    # If the file is still in a pending state, the hashes and tags are unreliable.
                    # The file might fail to be written, the hashes might be invalid, etc. We must
                    # use the slow path and wait for the file to become ready.
                    link.fast_path = False
                    file = None

                if link.fast_path:
                    self._prepare_dedup_file_for_linking(s, file, link)
                    if link.is_new:
                        # If the same file shows up later in the batch, ensure that it is used.
                        for v in link.hashes_promised.values():
                            hash_to_file[v, file.file_metadata] = file

                # the _prepare_dedup_file_for_linking caused a flush, so our primary key is ready
                if file is not None:
                    link.file = IdKey.from_instance(file)

            L = sao.aliased(mo.Link)
            q = sa.select(L).where(
                (L.link_path == sa.bindparam("x_src")) | (L.link_path == sa.bindparam("x_dst"))
            )
            for copy in copies:
                with self._ignore_skip(), self._catch_req_exc(copy):
                    link_objs = {
                        x.link_path: x
                        for x in s.execute(q, {"x_src": copy.src_str, "x_dst": copy.dst_str})
                        .scalars()
                        .all()
                    }

                    if (src_link := link_objs.get(copy.src_str)) is None:
                        raise NotADedupLinkError

                    if (dst_link := link_objs.get(copy.dst_str)) is not None:
                        s.delete(dst_link)

                    copy.dedup_file_path = self._make_dedup_file_path(src_link.file_id)
                    s.add(mo.Link(file_id=src_link.file_id, link_path=copy.dst_str))
                    s.flush()
            del q, L

            pending.expire_at = mo.now() + 30.0

        del hash_to_file, tag_to_file, tag_to_file_set, pending

        to_be_flushed = []
        failed_requests = []

        def _flush_now(s: sao.Session):
            for link in to_be_flushed:
                file: mo.DedupFile | None = None if (f := link.file) is None else f.get(s)

                if link.failed or file is None:
                    failed_requests.append(link.req)
                    if file is not None:
                        s.delete(file)
                    continue

                if (size := link.file_size) is not None:
                    file.size = size
                if (mtime := link.file_mtime) is not None:
                    file.mtime = mtime

                # We need to add whatever extra hashes were computed.
                if d := link.hashes_computed:
                    already_in_db = link.hashes_promised
                    for k, v in d.items():
                        if k not in already_in_db:
                            s.add(mo.Hash.from_digest(v, file=file))

                # We checked the hashes (if any), the file contents are written, and the link
                # (if any) has been created. We are therefore ready to set the "file.pending"
                # column to NULL, thus marking the dedup file as finalized.
                file.pending = None

            to_be_flushed.clear()

        for copy in copies:
            with self._ignore_skip(), self._catch_req_exc(copy):
                self._delete_file(copy.req.dst)
                self._create_actual_link(copy.dedup_file_path, copy.req.dst)

        if links:
            # Now we write the file data without holding the database transaction open. The
            # "_PendingUpdater" ensures that other threads know that we're working.
            with self._PendingUpdater(
                pending=pending_key,
                sessionmaker_r=self._SessionR,
                sessionmaker_w=self._SessionW,
                seconds_in_the_future=20,
            ) as pu:
                for link in links:
                    with self._ignore_skip(), self._catch_req_exc(link):
                        if not link.fast_path:
                            with self._beginw() as s:
                                _flush_now(s)
                            self._slow_path_wait_for_dedup_file(link=link, pending=pending_key)

                        self._write_dedup_file_contents(link=link)
                    to_be_flushed.append(link)
                pu.update_on_exit = True

            with self._beginw() as s:
                _flush_now(s)

                # Delete Pending object along with any DedupFile objects that had errors in them
                # using the "ON DELETE CASCADE".
                s.delete(pending_key.get_one(s))

            for link in links:
                link.req.success = not link.failed

        if copies:
            for copy in copies:
                copy.req.success = not copy.failed
                if not copy.req.success:
                    failed_requests.append(copy.req)

        if failed_requests:
            first_exc = failed_requests[0].exc
            raise BatchError(requests=failed_requests) from first_exc

    def _make_dedup_file_path(self, file_id: int) -> Path:
        return self._path_dedup / self._integer_to_path(file_id)

    def _write_file_computing_hashes(
        self, target: Path, open1, hashes: ty.Iterable[mh.HashFunction]
    ) -> tuple[int, dict[mh.HashFunction, mh.Digest]]:
        target.parent.mkdir(exist_ok=True, parents=True)
        m = mh.MultiHasher({f: f() for f in hashes})
        with target.open("wb") as f_w, open1() as f_r:
            while block := f_r.read(65536):
                m.update(block)
                f_w.write(block)
        return m.size, m.digest()

    def _write_dedup_file_contents(self, link: _ImplDedupLinkRequest) -> None:
        if link.is_new:
            if link.req.open_file_once is None:
                link.call_file_not_needed()
                return

            p = link.dedup_file_path
            (fs := set(link.hashes_promised)).update(self.extra_hashes)
            link.file_size, d = self._write_file_computing_hashes(p, link.call_open_file_once, fs)
            self.apply_metadata_to_file(p, link.req.file_metadata)
            link.file_mtime = int(p.stat().st_mtime)
            link.hashes_computed = d

            # Check that the hashes match what was claimed inside the link request.
            computed = {k: d[k] for k in link.hashes_promised}
            if link.hashes_promised != computed:
                p.unlink(missing_ok=True)
                raise InvalidContentsError(
                    link_request=link.req,
                    hashes_expected=link.hashes_promised,
                    hashes_observed=computed,
                )
        else:
            # existing file - we don't need to do anything
            link.call_file_not_needed()

            # TODO: quickly check whether the file mtime matches and check the content hash if not

        self._create_actual_link(link.dedup_file_path, link.req.link_path)

    def _slow_path_wait_for_dedup_file(
        self, link: _ImplDedupLinkRequest, pending: IdKey[mo.Pending]
    ) -> None:
        """
        The file we are interested in is actively being written to by another thread. We need to
        wait for it to be finished or for the other thread to fail.

        Either way, we add the required data to the database such that we can continue with the
        fast path procedure after this method returns.
        """

        # Construct query which looks for a DedupFile matching hashes or overlapping tags.
        F = sao.aliased(mo.DedupFile)
        H = sao.aliased(mo.Hash)
        T = sao.aliased(mo.Tag)

        def _exists(Alias):
            return sa.exists().select_from(Alias).where(Rel(Alias.file) == F)

        q = sa.select(F)
        for v in link.hashes_promised.values():
            q = q.where(_exists(H).where(H.compare_digest() == v))
        if link.req.tags:
            q = q.where(_exists(T).where(T.name.in_(link.req.tags)))
        q = q.options(sao.joinedload(F.pending))

        def _check(s: sao.Session) -> mo.DedupFile | bool:
            for x in s.execute(q).scalars():
                x: mo.DedupFile
                if x.pending is None:
                    # We found a finished DedupFile we can use directly.
                    return x
                elif x.pending_id == pending.key[0]:
                    # It's already our dedupfile!!!
                    raise AssertionError("deadlock")
                elif x.pending.expire_at >= mo.now():
                    # We found an in-progress DedupFile, so we stand down and continue polling.
                    return False

            # There are no matching DedupFile objects, so we can create a new one ourselves.
            return True

        def _wait_first_time():
            nonlocal _wait
            _wait = _wait_normal

        def _wait_normal():
            time.sleep(2)

        _wait = _wait_first_time
        while True:
            _wait()

            with self._SessionR() as s:  # check using a read-only transaction
                result = _check(s)
                if result is False:
                    continue

            with self._beginw() as s:  # use a write transaction
                result = _check(s)
                if result is False:
                    continue

                if result is True:
                    # We need to create a new DedupFile
                    s.add(file := self._make_dedup_file(link, pending.get_one(s)))
                    link.is_new = True
                else:
                    file = result
                    link.is_new = False

                link.fast_path = True
                self._prepare_dedup_file_for_linking(s, file, link)

                # we can only do this after the flush
                link.file = IdKey.from_instance(file)

            break

    @property
    def _PendingUpdater(self):
        return _PendingUpdater

    @abc.abstractmethod
    def _create_actual_link(self, existing: Path, new: Path): ...

    @abc.abstractmethod
    def _adopt_file_and_link(self, existing_path: Path, dedup_file_path: Path): ...

    @abc.abstractmethod
    def _verify_link(self, link: mo.Link) -> bool: ...

    def _pre_delete_links(self, path: Path):
        """
        Delete link records for all paths under *path*. Note that you must still delete the actual
        files, for example using rmtree.
        """
        self._check_links(path, True)

    def check_links(self, path: Path | None = None) -> None:
        """
        Detect links that were removed from the filesystem.

        If *path* is provided, then only traverse files under *path*. If the *path* does not exist,
        that means that everything under that *path* is gone.
        """
        self._check_links(path, False)

    def _check_links(self, path: Path | None, pre_delete: bool) -> None:
        F = sao.aliased(mo.DedupFile)
        L = sao.aliased(mo.Link)

        _verify_link = self._verify_link

        prefix = None
        if path is not None:
            exact_path = self._link_path_to_string(path)
            prefix = self._link_path_to_string(path / "x")[:-1]

            if pre_delete or not path.exists():
                # FAST PATH: Entire directory is gone, so all of its contents are gone. No need to
                # do any checking.
                _verify_link = lambda link: False

        q = sa.select(L).order_by(L.link_path).options(sao.joinedload(L.file))
        q = q.limit(self._batch_size)
        if prefix is not None:
            q = q.where((L.link_path == exact_path) | bytes_startswith(L.link_path, prefix))

        with self._SessionR() as s:
            last_link_path: str | None = None
            while True:
                if last_link_path is None:
                    q2 = q
                else:
                    q2 = q.where(L.link_path > last_link_path)

                results: list[mo.Link] = s.execute(q2).scalars().all()
                if not results:
                    break

                to_delete = []
                for link in results:
                    if not _verify_link(link):
                        to_delete.append(link.link_path)

                if to_delete:
                    with self._beginw() as s2, temporary_table(
                        s2, mo.tmp_bytes
                    ) as t_links, temporary_table(s2, mo.tmp_ints) as t_files:
                        s2.connection().execute(
                            sa.insert(t_links), [{"id": x} for x in to_delete]
                        ).close()

                        # There are the DedupFile entries that may end up orphaned.
                        s2.connection().execute(
                            sa.insert(t_files).from_select(
                                [t_files.c.id],
                                sa.select(F.id)
                                .distinct()
                                .select_from(L)
                                .join(F, L.file)
                                .join(t_links, t_links.c.id == L.link_path),
                            )
                        ).close()

                        # Remove the links that have been deleted.
                        s2.connection().execute(
                            sa.delete(L).where(L.link_path.in_(sa.select(t_links.c.id))),
                        ).close()

                        # Detect newly-orphaned files.
                        s2.connection().execute(
                            F.make_update_orphaned().where(F.id.in_(sa.select(t_files.c.id)))
                        ).close()

                last_link_path = results[-1].link_path

    def update_all_orphaned(self):
        with self._beginw() as s:
            F = sao.aliased(mo.DedupFile)
            s.connection().execute(F.make_update_orphaned()).close()

    def garbage_collect_dedup_files(self, min_age_seconds: int) -> None:
        """
        Remove dedup files that have no links to them as well as dedup files that were left behind
        by a failed batch of content insertion.
        """
        cutoff = mo.now() - min_age_seconds
        pending_cutoff = 7200
        F = sao.aliased(mo.DedupFile)
        P = sao.aliased(mo.Pending)
        q = sa.select(F).options(sao.selectinload(F.links)).limit(self._batch_size).order_by(F.id)
        q1 = q.where(F.orphaned_at != None, F.orphaned_at <= cutoff)
        q2 = q.join(P, F.pending).where(P.expire_at <= pending_cutoff)
        self._garbage_collect_using_query(q1, F)
        self._garbage_collect_using_query(q2, F)

    def _garbage_collect_using_query(self, q, F):
        F1 = sao.aliased(mo.DedupFile)
        while True:
            with self._beginw() as s:
                files: list[mo.DedupFile] = s.scalars(q).all()
                if not files:
                    break
                s.expunge_all()  # remove DedupFile objects from session
                s.connection().execute(sa.delete(F1).where(F1.id.in_(q.with_only_columns(F.id))))

            for file in files:
                for link in file.links:
                    self._delete_file(link._link_path_from_string(link.link_path))
                self._delete_file(self._make_dedup_file_path(file.id))

    def garbage_collect_deleted(self):
        """
        Delete unused temporary directories created with :meth:`.temporary_directory` as well as
        files that could not be deleted previously (due to locking on Windows, for example).
        """

        # We must ALWAYS lock self._path_temporary_master_lock before attempting to create or delete
        # an child lock file inside self._path_temporary_lock.
        for q in self._path_temporary_lock.iterdir():
            with contextlib.ExitStack() as ex:
                # Holding the master lock, we check the timestamp of the child lock and, if it's old
                # enough, we lock it.
                with self._filelock(self._path_temporary_master_lock, blocking=True):
                    if q.lstat().st_mtime >= mo.now() - 3600:
                        continue

                    try:
                        ex.enter_context(self._filelock(q, blocking=False))
                    except filelock.Timeout:
                        continue  # it's still locked, leave it alone

                    # We release the master lock as we don't need it anymore.

                # Still holding the child lock, delete the corresponding temporary dir.
                self.delete_tree(self._path_temporary_dirs / q.name)

            # Holding the master lock, finally delete the child lock.
            with self._filelock(self._path_temporary_master_lock, blocking=True):
                try:
                    with self._filelock(q, blocking=False):
                        pass
                except filelock.Timeout as exc_:
                    pass  # another thread chose the same name and locked it, leave it alone
                else:
                    self._remove_file_or_dir(q, ignore_errors=True)

        for p in self.path_deleted.iterdir():
            self._remove_file_or_dir(p, ignore_errors=True)

    def _remove_file_or_dir(self, p: Path, ignore_errors: bool):
        try:
            p.unlink()
        except Exception:
            if not p.exists():
                pass  # mission (already) accomplished
            elif stat.S_ISDIR(p.lstat().st_mode):
                shutil.rmtree(str(p), ignore_errors=ignore_errors)
            elif not ignore_errors:
                raise

    def garbage_collect_extra_files(self):
        """
        Look for files in the dedup directory that were left behind due to errors or unexpected
        shutdown. Delete such files.

        This recursively lists every file in the dedup store, so it takes a long time.
        """
        F = sao.aliased(mo.DedupFile)
        i2p = self._integer_to_path
        cutoff = mo.now() - 3600

        base = self._path_dedup
        for chunk in chunked_iter(base.rglob("*"), self._batch_size):
            to_be_unlinked = []
            file_ids = {}
            for p in chunk:
                if not p.is_file():
                    continue

                try:
                    file_id = i2p.invert("/".join(p.relative_to(base).parts))
                except InvalidPathError:
                    if p.stat().st_mtime < cutoff:
                        to_be_unlinked.append(p)
                    continue

                file_ids[file_id] = p

            if file_ids:
                # We use a write transaction to avoid a race condition between checking that a path
                # does not contain a valid file ID and then later deleting that file outside the
                # transaction.
                with self._SessionW() as s, temporary_table(s, mo.tmp_ints) as tmp:
                    s.execute(sa.insert(tmp), [{"id": x} for x in file_ids]).close()
                    tmp_ = sa.alias(tmp)
                    bad_file_ids = (
                        s.execute(
                            sa.select(tmp_.c.id).where(
                                ~sa.exists().select_from(F).where(F.id == tmp_.c.id)
                            )
                        )
                        .scalars()
                        .all()
                    )
                    for file_id in bad_file_ids:
                        self._delete_file(file_ids[file_id])

            for p in to_be_unlinked:
                self._delete_file(p)

    def corrupted_list(self) -> ty.Generator[Corrupted]:
        """
        Get the list of corrupted files found using :meth:`integrity_check`.
        """
        for p in self.path_corrupted.glob("*.json"):
            d = json.loads(p.read_bytes())
            yield Corrupted(
                path=bin_path if (bin_path := p.with_suffix(".bin")).exists() else None,
                file_id=d["file_id"],
                exception=d["exception"],
                link_paths=frozenset(d["link_paths"]),
                raw_link_paths=frozenset(d["raw_link_paths"]),
            )

    def corrupted_clear(self):
        """
        Delete all corrupted files.
        """
        for glob in ["*.bin", "*.json"]:
            for p in self.path_corrupted.glob(glob):
                self._delete_file(p)

    @staticmethod
    def _copy_tree_default_fallback(src: Path, dst: Path):
        shutil.copy2(str(src), str(dst), follow_symlinks=False)

    def copy_tree(self, src: Path, dst: Path, fallback_copy=None) -> None:
        if fallback_copy is None:
            fallback_copy = self._copy_tree_default_fallback
        if dst.exists():
            raise AssertionError("dst must not exist")
        self.check_links(dst)

        def _run():
            self.run_batch(to_copy)
            for req in to_copy:
                try:
                    req.result()
                except NotADedupLinkError:
                    fallback_copy(req.src, req.dst)
            to_copy.clear()

        if src.is_dir():
            to_copy = []
            for root, dirs, files in pathwalk(src):
                root_dst = dst / root.relative_to(src)
                root_dst.mkdir(exist_ok=True, parents=True)
                for f in files:
                    to_copy.append(DedupCopyLinkRequest(src=root / f, dst=root_dst / f))
                    if len(to_copy) > 1000:
                        _run()
        else:
            # must be a file
            to_copy = [DedupCopyLinkRequest(src=src, dst=dst)]

        if to_copy:
            _run()

    def delete_tree(self, p: Path) -> None:
        def f(func, path, exc_info):
            if (p := Path(path)).exists():
                self._move_to_deleted(p)

        shutil.rmtree(str(p.absolute()), onerror=f)
        if p.exists():
            self._move_to_deleted(p)
        self.check_links(p)

    def delete_file(self, p: Path) -> None:
        self._delete_file(p)
        self.check_links(p)

    def _delete_file(self, p: Path) -> None:
        """
        On Windows, a locked file cannot be deleted. So instead we move it out of the way to a
        different directory in the hopes of deleting it later when it's not locked.
        """
        try:
            p.unlink(missing_ok=True)
        except OSError:
            if not p.exists() or p.is_dir():
                raise
        else:
            return

        self._move_to_deleted(p)

    def _move_to_deleted(self, p: Path) -> None:
        base = self.path_deleted
        for name in random_names("", ".bin"):
            try:
                p.rename(base / name)
            except OSError as exc:
                exc_ = exc
            else:
                return

        raise exc_

    def _filelock(self, path: Path, blocking: bool):
        return filelock.FileLock(path, blocking=blocking)

    @property
    def _path_temporary_dirs(self):
        return self.path_temporary / "dirs"

    @property
    def _path_temporary_lock(self):
        return self.path_temporary / "lock"

    @property
    def _path_temporary_master_lock(self):
        return self.path_temporary / "master.lock"

    @contextlib.contextmanager
    def temporary_directory(self, prefix="tmp_", suffix=""):
        exc = None
        for name in random_names(prefix=prefix, suffix=suffix):
            p = self._path_temporary_dirs / name
            q = self._path_temporary_lock / name

            # We must always acquire the master lock before acquiring a child lock. The order must
            # be consistent in order to prevent deadlocks.
            with contextlib.ExitStack() as ex:
                with self._filelock(self._path_temporary_master_lock, blocking=True):
                    try:
                        ex.enter_context(self._filelock(q, blocking=False))
                    except filelock.Timeout as exc_:
                        continue  # try a different name

                    # We now release the master lock because we don't need it any more.

                try:
                    p.mkdir(parents=True)
                except OSError as exc_:
                    exc = exc_
                    continue

                try:
                    yield p
                    break
                finally:
                    self.delete_tree(p)

                    # Release the lock file. We will attempt to delete it next.
                    ex.close()

                    # Attempt to delete the lock file.
                    with self._filelock(self._path_temporary_master_lock, blocking=True):
                        try:
                            with self._filelock(q, blocking=False):
                                pass
                        except filelock.Timeout as exc_:
                            pass  # another thread chose the same name and locked it, leave it alone
                        else:
                            self._remove_file_or_dir(q, ignore_errors=True)
        else:
            raise AssertionError("retry count exceeded, unknown cause") if exc is None else exc

    @cached_property
    def _q_get_hash(self):
        L = sao.aliased(mo.Link)
        F = sao.aliased(mo.DedupFile)
        H = sao.aliased(mo.Hash)
        return (
            sa.select(L, H, F.size)
            .select_from(L)
            .join(F, L.file)
            .outerjoin(H, (Rel(H.file) == F) & (H.hash_function == sa.bindparam("x_hf")))
            .options(sao.contains_eager(L.file.of_type(F)))
            .where(L.link_path == sa.bindparam("x_link_path"), F.pending == None)
        )

    def _query_by_link_path(
        self, s: sao.Session, link_path: bytes, hash_function: mh.HashFunction
    ) -> list[tuple[mo.Link, mo.Hash, int]]:
        return s.execute(
            self._q_get_hash,
            {"x_link_path": link_path, "x_hf": hash_function.function_code},
        ).all()

    def get_file_hash(
        self, hash_function: mh.HashFunction, path: Path, check_link: bool
    ) -> tuple[int, mh.Digest] | None:
        """
        Query the database to obtain the file contents hash of file at *path*. Return None if the
        file is not in the dedup database. If *check_link* is True, then check that the link is
        intact before returning the hash. If the link is damaged or removed, then call
        :meth:`check_links` to unregister the link then return None.
        """
        with self._SessionR() as s:
            link_path: bytes = self._link_path_to_string(path)
            links = self._query_by_link_path(s, link_path, hash_function)

            if not links:
                return None

            link, h, size = links[0]
            if h is None:
                return None

            if not (check_link and not self._verify_link(link)):
                return size, h.to_digest()

        self.check_links(path)
        return None

    def get_or_compute_file_hash(
        self, hash_function: mh.HashFunction, path: Path, **kw
    ) -> tuple[int, mh.Digest] | None:
        r = self.get_file_hash(hash_function, path, **kw)
        if r is None:
            hasher = hash_function()
            size = 0
            with path.open("rb") as f:
                while block := f.read(65536):
                    size += len(block)
                    hasher.update(block)
            r = size, hasher.digest()
        return r

    def adopt_files(
        self, hash_function: mh.HashFunction, requests: ty.Iterable[AdoptRequest]
    ) -> None:
        """
        Adopt each file given in *paths*. If the path is already a dedup link, then leave it
        alone. If the path is not a dedup link, then compute its hash and move the file to the
        dedup store and create a link to it. If the path is already a dedup link but does not
        have the right kind of hash digest, then compute the hash digest and store it in the
        database.

        This method is implemented in a somewhat inefficient way.
        """
        reqs = [_ImplAdoptRequest(req) for req in requests]

        # first use a read-only session while we compute file hashes
        with self._SessionR() as s:
            for x in reqs:
                x.link_path = self._link_path_to_string(x.req.path)
                existing = self._query_by_link_path(s, x.link_path, hash_function)
                if existing:
                    l, h, sz = existing[0]
                    if h is not None:
                        x.req.out_digest = h.to_digest()
                        x.req.out_size = sz
                        x.done = True

                if not x.done:
                    with open(x.req.path, "rb") as f:
                        h = hash_function()
                        size = 0
                        while block := f.read(65536):
                            h.update(block)
                            size += len(block)
                        x.req.out_digest = h.digest()
                    x.file_metadata = DedupFileMetadata(executable=False)  # TODO
                    x.req.out_size = size
                    x.file_metadata_bytes = self.convert_file_metadata_to_bytes(x.file_metadata)

        F = sao.aliased(mo.DedupFile)
        H = sao.aliased(mo.Hash)
        q = (
            sa.select(F)
            .join(H, F.hashes)
            .where(
                H.hash_function == sa.bindparam("x_hf"),
                H.hash == sa.bindparam("x_h"),
                F.pending == None,
                F.file_metadata == sa.bindparam("x_f_meta"),
            )
        )

        # then we use a RW session to update the database
        with self._beginw() as s:
            for x in reqs:
                if x.done:
                    continue

                # re-check for an existing link
                existing = self._query_by_link_path(s, x.link_path, hash_function)
                if existing:
                    l, h, sz = existing[0]
                    file = l.file
                    if h is None:
                        s.add(mo.Hash.from_digest(x.req.out_digest, file=file))
                    else:
                        # never mind, nothing to do here
                        x.req.out_size = sz
                        x.req.out_digest = h.to_digest()
                        x.done = True
                        continue
                else:
                    # try to lookup by digest first
                    # TODO: also look up by tag
                    files = (
                        s.execute(
                            q,
                            dict(
                                x_hf=hash_function.function_code,
                                x_h=x.req.out_digest.digest,
                                x_f_meta=x.file_metadata_bytes,
                            ),
                        )
                        .scalars()
                        .all()
                    )
                    if files:
                        file = files[0]
                    else:
                        file = None
                    if file is not None:
                        file.orphaned_at = None
                        x.delete = True
                    else:
                        # no existing file found, need to create one
                        file = mo.DedupFile(
                            file_metadata=x.file_metadata_bytes,
                            size=x.req.out_size,
                            mtime=int(x.req.path.stat().st_mtime),
                            orphaned_at=None,
                            pending=None,
                            hashes=[mo.Hash.from_digest(x.req.out_digest)],
                        )
                        s.add(file)
                        s.flush()  # we need to make sure the file has an ID

                    s.add(mo.Link(link_path=x.link_path, file=file))

                x.dedup_file_path = self._make_dedup_file_path(file.id)

                # We add our tags.
                self._add_tags_to_file(s, file, x.req.tags)

                s.flush()

        # and finally we make filesystem changes
        for x in reqs:
            if (dst := x.dedup_file_path) is not None:
                if x.delete:
                    # We already have a DedupFile with the required contents, so we replace the
                    # link_path file with a link to that existing DedupFile.
                    self._delete_file(x.req.path)
                    self._create_actual_link(dst, x.req.path)
                else:
                    dst.parent.mkdir(exist_ok=True, parents=True)
                    self._adopt_file_and_link(x.req.path, dst)

    def integrity_check(
        self,
        skip_same_mtime: bool,
        threads: int | None = None,
        keep_corrupted: bool = True,
    ):
        """
        Verify all deduplicated files match their stored hashes. Use modification time to skip
        unchanged files if *skip_same_mtime* is True. Move the corrupted files to
        :attr:`path_corrupted`.
        """

        F = sao.aliased(mo.DedupFile)
        batch_size = 1000
        q = sa.select(F).options(sao.selectinload(F.hashes)).order_by(F.id).limit(batch_size)

        def _hash_check(file: mo.DedupFile) -> None:
            p = self._make_dedup_file_path(file.id)
            st_mtime = int(p.stat().st_mtime)
            if skip_same_mtime and file.mtime == st_mtime:
                return

            d = file.hashes_dict
            m = mh.MultiHasher({hf: hf() for hf in d})
            with p.open("rb") as fh:
                while block := fh.read(65536):
                    m.update(block)
            if d != (observed := m.digest()):
                raise InvalidContentsError(hashes_expected=d, hashes_observed=observed)

            # TODO: also check file metadata matches, such as the executable bit

            # The digest was the same, so update the mtime in the DB.
            with self._SessionW() as s:
                IdKey.from_instance(file).get_one(s).mtime = st_mtime

        id_min = -1
        with cf.ThreadPoolExecutor(max_workers=threads) as exe:
            while True:
                invalid_file_ids = []

                with self._SessionR() as s:
                    q2 = q.where(F.id > id_min, F.pending == None)
                    dedup_files: list[mo.DedupFile] = s.execute(q2).scalars().all()

                    if not dedup_files:
                        break

                    id_min = dedup_files[-1].id
                    futures = {exe.submit(_hash_check, f): f for f in dedup_files}
                    for future in cf.as_completed(futures):
                        if (exc := future.exception()) is not None:
                            if not isinstance(exc, Exception):
                                # Some other type of exception
                                raise exc

                            file = futures[future]
                            self._integrity_check_process_corrupt_one(s, file, exc, keep_corrupted)
                            invalid_file_ids.append(file.id)

                if invalid_file_ids:
                    with self._SessionW() as s:
                        s.connection().execute(
                            sa.delete(F).where(F.id == sa.bindparam("_id")),
                            [{"_id": x} for x in invalid_file_ids],
                        )

    def _integrity_check_process_corrupt_one(
        self, s: sao.Session, file: mo.DedupFile, exc: Exception, keep_corrupted: bool
    ):
        """
        Process one file that has been found to be corrupted.
        """

        path_file = self._make_dedup_file_path(file.id)

        # Load the links as we will need them
        s.refresh(file, ["links"])

        link_paths = [self._link_path_from_string(link.link_path) for link in file.links]
        json_data = {
            "file_id": file.id,
            "link_paths": [str(x) for x in link_paths],
            "raw_link_paths": [
                link.link_path.decode("utf-8", errors="replace") for link in file.links
            ],
            "exception": repr(exc),
        }

        with create_file_random(self.path_corrupted, "f_", ".json") as f:
            path_json = Path(f.name)
            f.write(json.dumps(json_data, indent=2, sort_keys=True).encode("utf-8"))

        if keep_corrupted:
            try:
                path_file.rename(path_json.with_suffix(".bin"))
            except Exception:
                if path_file.exists():
                    logger.warning(
                        "failed to rename corrupt file", exc_info=True, data=str(path_file)
                    )

        for x in link_paths:
            self._delete_file(x)

    class _compute_stats_ZeroRow:
        orphaned = None
        count = 0
        size = 0

    def compute_stats(self) -> DedupStats:
        with self._SessionR() as s:
            F = sao.aliased(mo.DedupFile)
            L = sao.aliased(mo.Link)
            orph = F.orphaned_at != None

            q = (
                sa.select(
                    orph.label("orphaned"),
                    sa.func.count().label("count"),
                    sa.func.sum(F.size).label("size"),
                )
                .select_from(F)
                .where(F.pending == None)
                .group_by(orph)
            )
            file_stats = {k: self._compute_stats_ZeroRow() for k in (False, True)}
            file_stats |= {row.orphaned: row for row in s.execute(q).all()}

            q = (
                sa.select(sa.func.count().label("count"), sa.func.sum(F.size).label("size"))
                .select_from(L)
                .join(F, L.file)
            ).where(F.pending == None)
            link_stats = s.execute(q).one()

        return DedupStats(
            dedup_count=file_stats[False].count,
            dedup_total_bytes=file_stats[False].size,
            orphaned_count=file_stats[True].count,
            orphaned_total_bytes=file_stats[True].size,
            link_count=link_stats.count,
            link_total_bytes=link_stats.size or 0,
        )


class DedupBackendHardlink(Dedup):
    def _create_actual_link(self, existing: Path, new: Path):
        # Path.link_to was removed and replaced by Path.hardlink_to, but I want this to work across
        # Python 3.9 to 3.13
        os.link(str(existing), str(new))

    def _adopt_file_and_link(self, existing_path: Path, dedup_file_path: Path):
        # hard links are indistinguishable from each other
        self._create_actual_link(existing_path, dedup_file_path)

    def _verify_link(self, link: mo.Link) -> bool:
        p = Path(link.link_path.decode("utf-8"))

        try:
            a = p.lstat()
        except Exception:
            return False

        if link.file.mtime != int(a.st_mtime):
            return False

        # st_ino is 0 on unsupported filesystems on Windows.

        # TODO: should we even allow st_ino=0?
        if a.st_ino != 0:
            if (file_stat := getattr(link.file, "_cached_file_stat", None)) is None:
                try:
                    file_stat = self._make_dedup_file_path(link.file.id).stat()
                except Exception:
                    return False
                link.file._cached_file_stat = file_stat

            if a.st_ino != file_stat.st_ino:
                return False

        return True
