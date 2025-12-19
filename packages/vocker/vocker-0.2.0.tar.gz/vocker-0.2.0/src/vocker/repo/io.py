from __future__ import annotations

import abc
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import contextlib
import enum
import io
import itertools
from math import log2
from pathlib import Path, PurePosixPath
import shutil
import struct
import typing as ty

import attr
import cbor2
from sansio_tools import parser as sansio_parser
from sansio_tools.queue import BytesQueue, FileAdapterFromGeneratorBytes
import structlog

from ..integer_to_path import IntegerToPath
from ..util import assert_
from .. import image as im, multihash as mh, dedup as de, util as ut
from . import compression as cx

logger = structlog.get_logger(__name__)


CBOR_HEADER = b"\xd9\xd9\xf7"
STRUCT_ARCHIVE_SIZE = struct.Struct("!Q")
STRUCT_ESTIMATED_SIZE = struct.Struct("!H")


def cbor_dumps(obj) -> bytes:
    return cbor2.dumps(obj, datetime_as_timestamp=True, canonical=True)


def cbor_loads(data: bytes):
    return cbor2.loads(data)


def cbor_load(fp: ty.BinaryIO, max_size: int):
    left = max_size + 1
    q = BytesQueue()
    while buf := fp.read(left):
        left -= len(buf)
        q.append(buf)
        if not left:
            raise ValueError(f"input exceeded maximum size {max_size}")
    return cbor_loads(bytes(q))


def cbor_dump(obj, fp):
    fp.write(b"\xd9\xd9\xf7")
    cbor2.dump(obj, fp, datetime_as_timestamp=True, canonical=True)


@attr.s(eq=False, hash=False)
class ShardPathsWriter:
    file = attr.ib()

    def write_all(self, files: ty.Iterable[im.SingleFileImageMetadata]):
        cbor_dump([x.to_shard_entry() for x in files], self.file)


@attr.s(eq=False, hash=False)
class ArchiveDataWriter:
    file_archive: ty.BinaryIO = attr.ib()
    file_sizes: ty.BinaryIO = attr.ib()

    def begin_file(self, size: int, digest: mh.Digest):
        self.current_hasher = digest.function()
        self.current_size = 0
        self.expected_digest = digest
        self.expected_size = size

    def write_file_data(self, data: bytes):
        self.current_size += len(data)
        self.current_hasher.update(data)
        self.file_archive.write(data)

    def end_file(self):
        h = self.current_hasher.digest()
        h0 = self.expected_digest
        if (size := self.current_size) != (s0 := self.expected_size) or h != h0:
            raise AssertionError(
                f"written file did not match expected info ({size} != {s0}, {h} != {h0})"
            )
        self.file_sizes.write(STRUCT_ARCHIVE_SIZE.pack(size))


@attr.s(eq=False, hash=False)
class HashesWriter:
    file: ty.BinaryIO = attr.ib()

    def write_all(self, iterable: ty.Iterable[mh.Digest]):
        w = self.file.write
        for x in iterable:
            w(x.digest)


def estimated_archive_sizes_encode(sizes: ty.Iterable[int]):
    _s = STRUCT_ESTIMATED_SIZE
    result = []
    for size in sizes:
        if size <= 0:
            size = 1
        result.append(_s.pack(round(log2(size) * 1024)))
    return b"".join(result)


def estimated_archive_sizes_decode(data: bytes) -> list[int]:
    _s = STRUCT_ESTIMATED_SIZE
    data = memoryview(data)
    result = []
    for i in range(0, len(data), 2):
        [x] = _s.unpack(data[i : i + 2])
        result.append(round(2.0 ** (x / 1024)))
    return result


class MapXToYOperatorEnum(enum.Enum):
    OUT = 1
    AND = 2
    OR = 3


@attr.s(eq=False, hash=False)
class MapShardToArchiveWriterTrivial:
    file: ty.BinaryIO = attr.ib()

    def write_all(self, *, shard_id: int, archive_id: int, archive_size: int):
        data = [
            [archive_id],
            [[MapXToYOperatorEnum.OUT.value, 0, shard_id]],
            estimated_archive_sizes_encode([archive_size]),
        ]
        cbor_dump(data, self.file)


@attr.s(eq=False, hash=False)
class MapImageToShardWriterTrivial:
    file: ty.BinaryIO = attr.ib()

    def write_all(self, *, image_id: int, shard_ids: ty.Iterable[int]):
        shard_ids = list(shard_ids)
        data = [
            shard_ids,
            [[MapXToYOperatorEnum.OUT.value, 0] + list(range(len(shard_ids)))],
        ]
        cbor_dump(data, self.file)


def image_file_entries_for_hashing_iter(
    image_user_data_hash: mh.Digest, entries: ty.Iterable[im.SingleFileImageMetadata]
):
    yield image_user_data_hash.to_multihash_bytes()

    d = {}
    keys = []
    for e in entries:
        keys.append(k := e.to_image_hash_sort_key())
        d[k] = e

    keys.sort()

    for k in keys:
        yield cbor_dumps(d[k].to_data_for_image_hash())


@attr.s(auto_exc=True, str=False)
class RepoFileNotFoundError(Exception):
    message = attr.ib(default="repository file not found")
    filename = attr.ib(default=None)
    remote_accessor = attr.ib(default=None)
    local_base_path = attr.ib(default=None)


@attr.s(auto_exc=True, str=False)
class ImageNotFoundError(Exception):
    message = attr.ib(default="image not found")
    image_id = attr.ib(default=None)


@attr.s(auto_exc=True, str=False)
class BadHashError(Exception):
    message = attr.ib(
        default="""Manifest hash does not match parent. Either the repository is corrupt or in \
the middle of an upload, in which case you should retry the operation."""
    )
    path = attr.ib(default=None)
    digest_expected = attr.ib(default=None)
    digest_observed = attr.ib(default=None)


@attr.s(eq=False, hash=False)
class RepoTransfer:
    path_local: Path = attr.ib()
    dedup: de.Dedup = attr.ib()
    accessor: RemoteRepoAccessor | None = attr.ib()
    _cached_manifests = attr.ib(factory=set, init=False)

    def _download_manifest(
        self, remote_path: PurePosixPath, destination: Path
    ) -> tuple[mh.Digest, ManifestNode]:
        with self.accessor.download_open(remote_path) as file:
            _feed = (reader := ManifestNodeReader()).parser.feed
            q = BytesQueue()

            def feed(b):
                if b:
                    q.append(b)
                _feed(b)

            def _download_remaining_data():
                yield from q.data
                while block := file.read(65536):
                    feed(block)
                    yield block
                feed(None)

            # first we download the header to check the digest and maybe avoid downloading the rest
            block = True
            while block:
                block = file.read(256)
                feed(block if block else None)
                if (digest := reader.out_claimed_digest) is not None:
                    # OK, we have our digest
                    break
            else:
                raise AssertionError("no digest available but no error from parser?")

            _open = lambda: FileAdapterFromGeneratorBytes(_download_remaining_data())
            destination.parent.mkdir(exist_ok=True, parents=True)
            req = self.make_manifest_link_request(digest, destination, dict(open_file_once=_open))
            self.dedup.run_batch([req])

        return digest, reader.out_verified_data

    @staticmethod
    def make_manifest_link_request(manifest_digest, destination, kwargs):
        return de.DedupLinkRequest(
            hash_function=manifest_digest.function,
            link_path=destination,
            file_metadata=de.DedupFileMetadata.make_plain(),
            file_contents_hash=None,
            tags={b"vmf:" + manifest_digest.to_multihash_bytes()},
            **kwargs,
        )

    @staticmethod
    def make_hash_32_path(digest: mh.Digest):
        return PurePosixPath(digest.digest[:4].hex("/")) / "i.cbor"

    def _upload_file(self, local_path, remote_path):
        self.accessor.upload(local_path, remote_path)

    def _local(self, p: PurePosixPath) -> Path:
        return self.path_local / p

    def upload_full(self):
        stack = [(False, PurePosixPath("."))]
        while stack:
            is_exit, path = stack.pop()
            local_path = self._local(path)
            if is_exit:
                self._upload_file(local_path / "manifest.bin", path / "manifest.bin")
            else:
                new_reader = ManifestNodeReader.from_bytes(
                    (local_path / "manifest.bin").read_bytes()
                )
                new_node = new_reader.out_verified_data
                new_digest = new_reader.out_claimed_digest
                with self.dedup.temporary_directory() as tmp:
                    old_digest = old_node = None
                    try:
                        old_digest, old_node = self._download_manifest(
                            path / "manifest.bin", (tmp_mf_path := tmp / "m.bin")
                        )
                    except FileNotFoundError:
                        pass
                    except Exception:
                        logger.warning(
                            "error downloading existing manifest",
                            exc_info=True,
                            data_path=str(path / "manifest.bin"),
                        )

                if old_digest == new_digest:
                    continue  # manifest is identical, carry on

                if old_digest is None:
                    # empty
                    old_node = None
                else:
                    # old manifest found
                    old_node = ManifestNodeReader.from_bytes(old_node).out_verified_data

                # we write the new manifest to /new/
                self._upload_file(local_path / "manifest.bin", "new" / path / "manifest.bin")

                # onto the stack we push a reminder to upload the final version to the right place,
                # but only AFTER all the children have been completed
                stack.append((True, path))

                # we now perform all the file operations for the current directory and recurse for
                # child directories
                for k, v in new_node.children.items():
                    if old_node is None or old_node.children.get(k) != v:
                        # this file or directory is different, so we will need to recurse into it
                        is_dir, digest = v
                        if is_dir:
                            # push it onto the stack
                            stack.append((False, path / k))
                        else:
                            # upload file now
                            self._upload_file(local_path / k, path / k)

    def download_full(self, archives: bool = True, manifest_only: bool = False):
        def _should_download(path: PurePosixPath) -> bool:
            if manifest_only:
                return False
            return not (not archives and path.name.startswith("a."))

        self._cached_manifests.clear()
        loc = self._local
        todo = [(PurePosixPath("."), None)]
        while todo:
            path, digest = todo.pop()

            with self.open(path / "manifest.bin") as mf:
                node = ManifestNodeReader.from_bytes(mf.read())

            if digest is not None:
                # avoid checking the top-level hash
                if node.out_claimed_digest != digest:
                    raise BadHashError(
                        path=path, digest_expected=digest, digest_observed=node.out_claimed_digest
                    )

            for item_name, (is_dir, item_digest) in node.out_verified_data.children.items():
                item_path = path / item_name
                if is_dir:
                    todo.append((item_path, item_digest))
                else:
                    if _should_download(item_path):
                        with self.open(item_path):
                            pass

    def _integer_to_path(self, i: int):
        return PurePosixPath(IntegerToPath(file_suffix="_d")(i))

    DEFAULT_CBOR_MAX_SIZE = 2**24

    def open(self, path: PurePosixPath):
        loc = self._local
        mf_path = path.parent / "manifest.bin"
        if (loc_path := loc(path)).exists():
            # don't even check the manifest for existing local files
            return loc_path.open("rb")

        def _not_found():
            raise RepoFileNotFoundError(
                filename=str(path), remote_accessor=self.accessor, local_base_path=self.path_local
            ) from None

        try:
            if (acc := self.accessor) is not None and mf_path not in self._cached_manifests:
                h, node = self._download_manifest(mf_path, loc(mf_path))
                self._cached_manifests.add(mf_path)
            else:
                x = loc(mf_path).read_bytes()
                reader = ManifestNodeReader.from_bytes(loc(mf_path).read_bytes())
                h, node = reader.out_claimed_digest, reader.out_verified_data
        except FileNotFoundError:
            _not_found()

        if mf_path == path:
            # goofy - caller is trying to open the manifest itself
            return loc(path).open("rb")

        try:
            is_dir, digest = node.children[path.name]
        except KeyError:
            _not_found()

        assert_(not is_dir)

        _open = None if acc is None else (lambda: acc.download_open(path))

        req = de.DedupLinkRequest(
            hash_function=digest.function,
            link_path=(loc_path := loc(path)),
            file_metadata=de.DedupFileMetadata.make_plain(),
            file_contents_hash=digest,
            open_file_once=_open,
        )
        # TODO: handle de.MissingContentError
        try:
            self.dedup.run_batch([req])
        except de.BatchError as exc:
            raise exc.requests[0].exc from None
        return loc_path.open("rb")

    @contextlib.contextmanager
    def open_compressed(self, path: PurePosixPath):
        # TODO: use gz if zstd not available
        p = path.parent / (path.name + ".xz")
        with self.open(p) as f1:
            with cx.open_decompressor(f1, "xz") as f:
                yield f

    def download_shard(self, shard_digest: mh.Digest) -> int | None:
        shard_hashes_path = "shard-by-hash-32" / self.make_hash_32_path(shard_digest)
        try:
            shard_hash_to_id = self._read_cbor(shard_hashes_path)
        except RepoFileNotFoundError:
            return None
        try:
            shard_id = shard_hash_to_id[shard_digest.digest]
        except KeyError:
            return None
        assert_(type(shard_id) is int)
        return shard_id

    def _read_cbor(self, path):
        max_size = self.DEFAULT_CBOR_MAX_SIZE
        with self.open(path) as f:
            return cbor_load(f, max_size=max_size)

    def download_image(self, image_id: str, download_archives: bool = True):
        # download image index to locate image ID by hash
        # download image metadata cbor and ID of latest image-to-shard mapping
        # download image-to-shard mapping
        # select shard set
        # for each shard, download metadata + ID of latest shard-to-archive mapping
        # download shard-to-archive mapping
        # select archive set
        digest = mh.registry.decode(image_id)
        hf = digest.function

        def _read_cbor_int(path) -> int:
            with self.open(path) as f:
                value: int = cbor_load(f, max_size=1024)
                assert_(type(value) is int)
            return value

        _read_cbor = self._read_cbor

        def _read_compressed_cbor(path, max_size=None):
            if max_size is None:
                max_size = self.DEFAULT_CBOR_MAX_SIZE
            with self.open_compressed(path) as f:
                return cbor_load(f, max_size=max_size)

        try:
            image_hashes_path = "image-by-hash-32" / self.make_hash_32_path(digest)
            image_hash_to_id = _read_cbor(image_hashes_path)
            img_id = image_hash_to_id[digest.digest]
        except Exception as exc:
            raise ImageNotFoundError(image_id=image_id) from exc
        assert_(type(img_id) is int)

        image_path = "image" / self._integer_to_path(img_id)

        with self.open_compressed(image_path / "u") as f:
            image_meta_hash = hf().update(f.read()).digest()

        i2s_path = "is" / self._integer_to_path(_read_cbor_int(image_path / "is.cbor"))

        with self.open_compressed(i2s_path / "m") as f:
            # HACK: gathering all shards instead of being smart
            shard_ids: list[int] = cbor_loads(f.read())[0]
            assert_(type(shard_ids) is list)
            assert_(all(type(x) is int for x in shard_ids))

        digest_size = hf.digest_size
        shard_entries: dict[str, im.SingleFileImageMetadata] = {}
        for shard_id in shard_ids:
            shard_path = "shard" / self._integer_to_path(shard_id)

            shard_entry_data = _read_compressed_cbor(shard_path / "p")

            with self.open(shard_path / "h.bin") as f:
                for data in shard_entry_data:
                    entry = im.SingleFileImageMetadata.from_shard_entry(
                        data, hf.digest_from_bytes(f.read(digest_size))
                    )
                    shard_entries[entry.path] = entry

        computed_image_hash = (
            hf()
            .update_iter(
                image_file_entries_for_hashing_iter(image_meta_hash, shard_entries.values())
            )
            .digest()
        )

        if (s := computed_image_hash.to_multihash_base64url()) != image_id:
            raise ValueError(f"image hash does not match, expected {image_id}, calculated {s}")

        digest_to_shard_entries = defaultdict(list)
        for entry in shard_entries.values():
            digest_to_shard_entries[entry.digest.digest].append(entry)

        logger.info("finished metadata")

        for shard_id in shard_ids:
            shard_path = "shard" / self._integer_to_path(shard_id)
            s2a_path = "sa" / self._integer_to_path(_read_cbor_int(shard_path / "sa.cbor"))
            archive_ids = _read_compressed_cbor(s2a_path / "m")[0]
            assert_(type(archive_ids) is list)
            assert_(all(type(x) is int for x in archive_ids))

            with self.open_compressed(s2a_path / "m") as f:
                # HACK: gathering all archives instead of being smart
                archive_ids: list[int] = cbor_loads(f.read())[0]

            _size_struct_size = STRUCT_ARCHIVE_SIZE.size
            for archive_id in archive_ids:
                export_inputs = []
                archive_path = "archive" / self._integer_to_path(archive_id)
                offset = 0
                with self.open(archive_path / "h.bin") as f_h, self.open_compressed(
                    archive_path / "s"
                ) as f_s:
                    while sz_bytes := f_s.read(_size_struct_size):
                        # archive file hashes and sizes
                        [size] = STRUCT_ARCHIVE_SIZE.unpack(sz_bytes)
                        digest = f_h.read(digest_size)
                        this_digest_shard_entries = digest_to_shard_entries.pop(digest, None)
                        if this_digest_shard_entries is not None:
                            export_inputs.append(
                                im.SolidArchiveFileInfo(
                                    files=this_digest_shard_entries, offset=offset, size=size
                                )
                            )
                        offset += size

                if download_archives:
                    with self.open_compressed(archive_path / "a") as f:
                        # ensure the contents are available
                        pass

                yield ArchiveFilesExportInfo(archive_path=archive_path / "a", files=export_inputs)

        if digest_to_shard_entries:
            raise ValueError(f"failed to find data for items: {digest_to_shard_entries}")

    def export(
        self,
        exporter: im.VenvExporter,
        iterable: ty.Iterator[ArchiveFilesExportInfo],
        max_workers: int = None,
    ):
        def _process(archive_infos):
            with contextlib.ExitStack() as ex:
                files = []
                for archive_info in archive_infos:
                    archive_io = ex.enter_context(self.open_compressed(archive_info.archive_path))
                    files += (A(archive_io, info) for info in archive_info.files)
                exporter.provide_files(files)

        def _group_archive_infos(iterable):
            n = 0
            lst = []
            for a in iterable:
                if ((n1 := len(a.files)) + n < 5000) and len(lst) < 50:
                    lst.append(a)
                    n += n1
                else:
                    yield lst
                    n = n1
                    lst = [a]
            if lst:
                yield lst

        exporter.begin_session()
        A = im.VenvExportInputFromSolidArchive
        with ThreadPoolExecutor(max_workers=max_workers) as exe, ut.cancel_futures_on_error(exe):
            ut.raise_as_completed(
                exe.submit(_process, a_info_group)
                for a_info_group in _group_archive_infos(iterable)
            )
        exporter.end_session()


@attr.s(frozen=True)
class ArchiveFilesExportInfo:
    archive_path: PurePosixPath = attr.ib()
    files: tuple[im.SolidArchiveFileInfo] = attr.ib(converter=tuple)


def read_multihash(p: sansio_parser.BinaryParser, maximum_digest_size: int):
    function_code = yield from mh.multihash_varint_decode(p)
    digest_size = yield from mh.multihash_varint_decode(p)
    if digest_size > maximum_digest_size:
        raise ValueError("digest size exceeds maximum")
    digest_bytes = yield from p.read_bytes(digest_size)
    return mh.registry.decode_from_code_and_digest(function_code, digest_bytes)


@attr.s(eq=False, hash=False)
class ManifestNode:
    hash_function: mh.HashFunction = attr.ib()
    children: dict[str, tuple[bool, mh.Digest]] = attr.ib()

    @classmethod
    def from_cbor_decoded(cls, hash_function: mh.HashFunction, data):
        is_dir_dict = {b"d": True, b"f": False}
        H = hash_function.digest_from_bytes
        return cls(
            hash_function,
            {k: (is_dir_dict[v[:1]], H(v[1:])) for k, v in data.items()},
        )

    def to_bytes(self) -> tuple[bytes, mh.Digest]:
        hf = self.hash_function
        for is_dir, digest in self.children.values():
            if digest.function != hf:
                raise AssertionError("child and parent must use the same hash function")
        d = {
            name: (b"d" if is_dir else b"f") + digest.digest
            for name, (is_dir, digest) in self.children.items()
        }
        b = cbor_dumps(d)
        h = hf().update(b).digest()
        return h.to_multihash_bytes() + b, h


@attr.s(eq=False, hash=False)
class ManifestNodeReader:
    maximum_digest_size: int = attr.ib(default=1024)
    parser = attr.ib(default=None, init=False)

    out_claimed_digest: mh.Digest = attr.ib(init=False, default=None)
    out_verified_data: ManifestNode = attr.ib(init=False, default=None)

    def __attrs_post_init__(self):
        self.parser = sansio_parser.BinaryParser(self._parse)

    def _parse(self, p: sansio_parser.BinaryParser):
        digest_top = yield from read_multihash(p, self.maximum_digest_size)
        self.out_claimed_digest = digest_top
        hf = digest_top.function
        hasher_top = hf()

        q2 = BytesQueue()
        while not p.eof:
            while p.queue:
                hasher_top.update(p.queue.popleft_any_to(q2))
            yield

        if digest_top != hasher_top.digest():
            raise ValueError("content does not match top-level hash")

        self.out_verified_data = ManifestNode.from_cbor_decoded(hf, cbor2.loads(bytes(q2)))

    @classmethod
    def from_bytes(cls, data):
        (self := cls()).parser.feed(data).feed(None)
        return self

    @classmethod
    def parse_bytes(cls, data: bytes | memoryview):
        return cls.from_data(data).out_verified_data


class RemoteRepoAccessor(abc.ABC):
    def download(self, path: Path, remote_path: PurePosixPath):
        raise NotImplementedError
        if path.is_file():
            offset = path.stat().st_size
        with self.download_open_iter(remote_path=remote_path, offset=offset) as xs, path.open(
            "w+b"
        ) as fw:
            fw.seek(offset)
            for block in xs:
                fw.write(block)

    @abc.abstractmethod
    def download_open(
        self, remote_path: PurePosixPath, offset: int = 0
    ) -> ty.ContextManager[ty.BinaryIO]: ...

    @abc.abstractmethod
    def upload(self, path: Path, remote_path: PurePosixPath): ...


@attr.s(eq=False, hash=False)
class RemoteRepoAccessorFilesystem(RemoteRepoAccessor):
    base_path: Path = attr.ib()

    @contextlib.contextmanager
    def download_open(self, remote_path: PurePosixPath, offset: int = 0):
        with (self.base_path / remote_path).open("rb") as f:
            if offset:
                f.seek(offset)
            yield f

    def upload(self, path, remote_path):
        dst = self.base_path / remote_path
        if dst.exists():
            try:
                dst.unlink()
            except OSError:
                shutil.rmtree(dst)

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(path), str(dst), follow_symlinks=False)
