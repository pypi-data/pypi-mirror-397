from __future__ import annotations

import cbor2
from collections import defaultdict
from collections.abc import MutableMapping
import contextlib
import enum
from functools import cached_property
import io
import json
import os
from pathlib import Path, PurePath, PurePosixPath
import re
import shutil
import typing as ty

import atomicwrites
import attr
import marshmallow as ma
import marshmallow.fields as maf
import platformdirs
import structlog

from . import dedup as de, multihash as mh, image as im
from .repo import io as rio, compression as cx
from .util import PurePathBase
from .integer_to_path import IntegerToPath


logger = structlog.get_logger(__name__)


def tqdm():
    import tqdm

    return tqdm


def validate_local_repo_name(name: str) -> None:
    if not re.search(r"^(\w|-)*$", name):
        raise ValueError(f"invalid repo name: {name!r}")


@attr.s(eq=False, hash=False)
class RemoteRepository:
    uri: str = attr.ib()

    def as_dict(self):
        return attr.asdict(self, recurse=False)


@attr.s(auto_exc=True, hash=False, str=True)
class LocalRepositoryExistsError(ValueError):
    message: str = attr.ib(default="local repository already exists")
    repo_path: Path = attr.ib(default=None)


@attr.s(auto_exc=True, hash=False, str=True)
class LocalRepositoryInvalidError(ValueError):
    message: str = attr.ib(default="local repository does not exist or is corrupted")
    repo_path: Path = attr.ib(default=None)


@attr.s(eq=False, hash=False)
class _Remotes(MutableMapping[str, RemoteRepository]):
    system: System = attr.ib()

    @property
    def _data(self):
        return self.system._config["remote_repositories"]

    def __getitem__(self, k):
        d = self._data[k]
        d.pop("comment", None)
        return RemoteRepository(**d)

    def __setitem__(self, k, v: RemoteRepository | None):
        if v is None:
            try:
                del self._data[k]
            except KeyError:
                pass
        else:
            self._data[k] = v.as_dict()
        self.system._config_write()

    def __delitem__(self, k):
        self[k] = None

    def __iter__(self):
        return iter(x for x in self._data)

    def __len__(self, k, v):
        return len(self._data)


class _SchemaWithComment(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    comment = maf.Field(allow_none=True, data_key="#", required=False)


class SchemaRemoteRepository(_SchemaWithComment):
    uri = maf.String(required=True)


class SchemaConfig(_SchemaWithComment):
    remote_repositories = maf.Dict(maf.String(), maf.Nested(SchemaRemoteRepository, required=False))


class ImageType(enum.Enum):
    PYENV_V1 = "pyenv1"


@attr.s(eq=False, hash=False)
class JSONFileWithCaching:
    path: Path = attr.ib()
    schema: ma.Schema = attr.ib(default=None)
    _mtime = None
    _document = None

    @property
    def document(self):
        if (mtime := (p := self.path).stat().st_mtime_ns) != self._mtime:
            self._document = doc = self.schema.load(json.loads(p.read_bytes()))
            self._mtime = mtime
        else:
            doc = self._document
        return doc

    @document.setter
    def document(self, new_value):
        with atomicwrites.atomic_write(
            str(self.path), mode="wt", overwrite=True, encoding="utf-8", newline="\n"
        ) as fp:
            json.dump(self.schema.dump(new_value), fp, indent=2)
        self._document = new_value


@attr.s(eq=False, hash=False)
class UpdatingLocalRepository:
    parent: LocalRepository = attr.ib()
    workspace_path: Path = attr.ib()
    hash_function = attr.ib()
    updated_paths: set[PurePath] = attr.ib(init=False, factory=set)

    def get_path_for_open(self, path: PurePath | str, mode: str):
        path = PurePath(path)
        if mode == "rb":
            if path in self.updated_paths:
                return self.workspace_path / path
            else:
                return self.parent._path_base / path
        elif mode == "wb":
            self.updated_paths.add(path)
            (p := self.workspace_path / path).parent.mkdir(exist_ok=True, parents=True)
            return p
        else:
            raise ValueError(f"mode={mode!r}")

    def open(self, path: PurePath | str, mode: str):
        return self.get_path_for_open(path, mode).open(mode)

    @contextlib.contextmanager
    def open_for_write_multi_compressed(self, path: PurePath | str):
        path = PurePath(path)

        def p(suffix):
            return path.with_name(path.name + suffix)

        # compress contents directly to zstandard
        with self.open(p(".zst"), "wb") as f1, cx.open_compressor(f1, "zst") as f:
            yield f

        # compress to xz as well
        with self.open(p(".zst"), "rb") as fr1, cx.open_decompressor(fr1, "zst") as fr, self.open(
            p(".xz"), "wb"
        ) as fw1, cx.open_compressor(fw1, "xz") as fw:
            shutil.copyfileobj(fr, fw)

    def iterdir(self, path: PurePath):
        raise NotImplementedError("not needed yet")

    def unlink(self, path: PurePath):
        self.updated_paths.add(path)
        (self.workspace_path / path).unlink(missing_ok=True)

    def id_to_path(self, name: str, value: int):
        return PurePath(name) / self.parent.integer_to_path(value)

    def allocate_id(self, name: str) -> tuple[int, PurePath]:
        with self.open("counters.json", "rb") as f:
            counters: dict[str, int] = json.loads(f.read())
        counters[name] = counter = counters.get(name, 0) + 1
        with self.open("counters.json", "wb") as f:
            f.write(json.dumps(counters, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        return counter

    def add_image_to_index(self, digest: mh.Digest, image_id: int | None):
        self._add_id_to_hash32_index("image-by-hash-32", digest, image_id)

    def add_shard_to_index(self, digest: mh.Digest, shard_id: int | None):
        self._add_id_to_hash32_index("shard-by-hash-32", digest, shard_id)

    def _add_id_to_hash32_index(self, dir_name: str, digest: mh.Digest, object_id: int | None):
        path = dir_name / rio.RepoTransfer.make_hash_32_path(digest)

        try:
            with self.open(path, "rb") as f:
                d = rio.cbor_load(f, 1024 * 1024)
        except FileNotFoundError:
            d = {}

        if object_id is None:
            d.pop(digest.digest, None)
        else:
            d[digest.digest] = object_id

        with self.open(path, "wb") as f:
            rio.cbor_dump(d, f)


@attr.s
class LocalRepository:
    system: System = attr.ib()
    path: Path = attr.ib()
    integer_to_path: IntegerToPath = attr.ib(factory=lambda: IntegerToPath(file_suffix="_d"))

    @property
    def name(self):
        return self.path.name

    @property
    def _path_ok(self):
        return self.path / "ok"

    @property
    def _path_base(self):
        return self.path / "b"

    def init_new(self, hash_function: mh.HashFunction):
        self.delete()
        with self.updating(init_hash_function=hash_function) as u:
            with u.open("version.txt", "wb") as f:
                f.write(b"1")
            with u.open("counters.json", "wb") as f:
                f.write(b"{}")

    def get_hash_function(self):
        return self.manifest_read_toplevel_hash_only(self._path_base / "manifest.bin").function

    @contextlib.contextmanager
    def updating(self, *, init_hash_function=None):
        with self.system.repo_dedup.temporary_directory() as tmp_path:
            if init_hash_function is None:
                hf = self.get_hash_function()
            else:
                hf = init_hash_function
            u = UpdatingLocalRepository(parent=self, workspace_path=tmp_path, hash_function=hf)
            yield u

            # Adopt the files.
            base = self._path_base
            reqs_adopt = []
            reqs_copy = []
            for p_rel in u.updated_paths:
                p = u.workspace_path / p_rel
                p_rel_str = "/".join(p_rel.parts)
                if p.exists():
                    if not p.is_file():
                        raise ValueError("only regular files are supported")
                    reqs_adopt.append(adopt_req := de.AdoptRequest(p))
                    reqs_copy.append(de.DedupCopyLinkRequest(src=p, dst=(dst := base / p_rel)))
                    dst.parent.mkdir(exist_ok=True, parents=True)

            dedup = self.system.repo_dedup
            dedup.adopt_files(hf, reqs_adopt)

            # Now we gather the hashes for all the files so we can update the manifest nodes. We
            # need to do this after the `adopt_files` above because that operation computes the
            # hashes and stores them in the dedup db.
            dirs: dict[int, dict[PurePosixPath, dict[str, tuple[bool, mh.Digest] | None]]] = (
                defaultdict(lambda: defaultdict(dict))
            )
            for p_rel in u.updated_paths:
                if (p := u.workspace_path / p_rel).exists():
                    r = dedup.get_file_hash(hf, u.workspace_path / p_rel, check_link=True)
                    assert r is not None
                    value = False, r[1]
                else:
                    value = None
                dirs[len(p_rel.parts) - 1][p_rel.parent][p_rel.name] = value

            # Here begins the critical section. If this part fails, the local repository will be broken.
            self._path_ok.unlink(missing_ok=True)

            for p_rel in u.updated_paths:
                dedup.delete_tree(base / p_rel)

            # Copy the links from `u.workspace` to `base`.
            dedup.run_batch(reqs_copy)

            # Recursively update the manifest nodes.
            max_depth = max(dirs)
            for i in range(max_depth, -1, -1):
                for dir_path, children in dirs[i].items():
                    mf_path = dir_path / "manifest.bin"
                    if (dst := base / mf_path).exists():
                        node = rio.ManifestNodeReader.from_bytes(dst.read_bytes()).out_verified_data
                    else:
                        node = rio.ManifestNode(hash_function=hf, children={})

                    for child_name, child in children.items():
                        if child is None:
                            node.children.pop(child_name, None)
                        else:
                            node.children[child_name] = child

                    if node.children or i == 0:
                        node_bytes, node_hash = node.to_bytes()
                        kw = dict(open_file_once=lambda: io.BytesIO(node_bytes))
                        req = rio.RepoTransfer.make_manifest_link_request(node_hash, dst, kw)
                        dedup.run_batch([req])
                        del node_bytes, kw, req
                    else:
                        # delete empty manifest
                        dedup.delete_file(dst)
                        node_hash = None

                    if i > 0:
                        parent_value = None if node_hash is None else (True, node_hash)
                        dirs[i - 1][dir_path.parent][dir_path.name] = parent_value

            self._path_ok.write_bytes(b"")
            # Here ends the critical section.

    def delete(self):
        if self.path.exists():
            self._path_ok.unlink(missing_ok=True)
            self.system.repo_dedup.delete_tree(self.path)

    def check(self) -> bool:
        return self._path_ok.exists()

    def raise_if_not_valid(self) -> None:
        if not self.check():
            raise LocalRepositoryInvalidError(repo_path=self.path)

    def ensure_deleted_and_raise_if_exists(self) -> None:
        if self.path.exists():
            if self.check():
                self._raise_exists_error()
            else:
                logger.warning(
                    "deleting corrupted or incomplete repository", data_path=str(self.path)
                )
                self.delete()

    def _raise_exists_error(self):
        raise LocalRepositoryExistsError(repo_path=self.path)

    @staticmethod
    def manifest_read_toplevel_hash_only(p: Path):
        reader = rio.ManifestNodeReader()
        feed = reader.parser.feed
        with p.open("rb") as f:
            while b := f.read(4096):
                feed(b)
                if (h := reader.out_claimed_digest) is not None:
                    return h
        feed(None)
        raise AssertionError


@attr.s(eq=False, hash=False, kw_only=True)
class System:
    path_base: Path = attr.ib(default=None)
    path_dedup: Path = attr.ib(default=None)
    path_repo_base: Path = attr.ib(default=None)
    path_repo_dedup: Path = attr.ib(default=None)
    path_repo_local: Path = attr.ib(default=None)
    dedup: de.Dedup = attr.ib(default=None)
    repo_dedup: de.Dedup = attr.ib(default=None)

    def __attrs_post_init__(self):
        self._init()

    def _get_default_dedup_path(self):
        if (p := os.environ.get("VOCKER_BASE", None)) is not None:
            return Path(p)
        return platformdirs.user_data_path("vocker", False)

    def _init(self):
        if self.path_base is None:
            self.path_base = self._get_default_dedup_path()

        if self.path_dedup is None:
            self.path_dedup = self.path_base / "dup"

        if self.path_repo_base is None:
            self.path_repo_base = self.path_base / "repo"

        if self.path_repo_dedup is None:
            self.path_repo_dedup = self.path_repo_base / "dup"

        if self.path_repo_local is None:
            self.path_repo_local = self.path_repo_base / "local"

        # FIXME: support other backends
        if self.dedup is None:
            self.dedup = de.DedupBackendHardlink(self.path_dedup)
            self.dedup.garbage_collect_deleted()

        if self.repo_dedup is None:
            self.repo_dedup = de.DedupBackendHardlink(self.path_repo_dedup)
            self.repo_dedup.garbage_collect_deleted()

        self.path_repo_local.mkdir(exist_ok=True, parents=True)

        config_path = self.path_base / "vocker.json"
        cfg = JSONFileWithCaching(config_path, schema=SchemaConfig())
        try:
            cfg.document
        except FileNotFoundError:
            config_path.parent.mkdir(exist_ok=True, parents=True)
            config_path.write_bytes(b"{}")
            cfg.document
        self._config_file = cfg
        self._init_config()

    def _init_config(self):
        c = self._config
        modified = False

        if c.get(k := "remote_repositories") is None:
            c[k] = {}
            modified = True

        if c.get(k := "comment") is None:
            c[k] = [
                "Since JSON doesn't allow comments, you can place them inside the '#' key inside",
                "most of the dictionaries.",
            ]
            modified = True

        if modified:
            self._config_write(c)

    @property
    def _config(self):
        return self._config_file.document

    def _config_write(self, value=None) -> None:
        if value is None:
            value = self._config_file.document
        self._config_file.document = value

    def repo_init_new(self, repo_name: str, hash_function_name: str):
        self.repo_get(repo_name).init_new(mh.registry.name_to_hash[hash_function_name])

    def repo_get(self, repo_name: str):
        validate_local_repo_name(repo_name)
        return LocalRepository(self, self.path_repo_local / repo_name)

    def repo_list(self):
        return [LocalRepository(self, p) for p in self.path_repo_local.iterdir() if p.is_dir()]

    def repo_add_image(
        self,
        repo_name: str,
        image_path: Path,
        image_type: str | None,
        mock_image_path: PurePathBase = None,
    ) -> int:
        """
        Return new image ID.
        """
        # 1. split image into shards based off the paths
        # 2. send each shard into VenvImporter - if it gets too big, then split it into multiple
        #    shards of a more manageable size
        # 3. check whether there already exists a shard with the exact same contents inside the
        #    repo, in which case just re-use it
        (repo := self.repo_get(repo_name)).raise_if_not_valid()

        if image_type is None:
            # TODO: proper autodetection
            image_type = "pyenv1"

        image_type = ImageType(image_type)

        if mock_image_path is None:
            kw = dict(input=image_path)
        else:
            kw = dict(input=mock_image_path, input_real=image_path)

        hf = repo.get_hash_function()
        importer = im.VenvImporter(**kw)
        d = im.pyenv_split(image_path)

        transfer = self.get_repo_transfer(repo, None)

        shard_ids = []

        with repo.updating() as u:
            all_shard_entries = []

            for key, paths in tqdm().tqdm(d.items()):
                outs = [x for p in paths for x in importer.run(p)]
                make_file_meta = im.VenvImporterToImageMetadata(
                    hash_function=hf, dedup=self.repo_dedup
                )
                archive_digests_and_sizes = {}
                archive_digest_to_output = {}
                shard_entries = []
                for out in outs:
                    with out() as o:
                        entry = make_file_meta(o)
                    shard_entries.append(entry)
                    all_shard_entries.append(entry.rest)
                    archive_digests_and_sizes[entry.rest.digest] = entry.size
                    archive_digest_to_output[entry.rest.digest] = out
                archive_digests = list(archive_digests_and_sizes)
                archive_digests.sort(key=lambda x: x.digest)
                archive_digest_to_index = {k: i for i, k in enumerate(archive_digests)}
                archive_sizes = tuple(archive_digests_and_sizes[k] for k in archive_digests)

                shard_digest = (
                    hf()
                    .update_iter(
                        rio.image_file_entries_for_hashing_iter(
                            hf().digest(), (x.rest for x in shard_entries)
                        )
                    )
                    .digest()
                )

                shard_id = transfer.download_shard(shard_digest)
                if shard_id is not None:
                    shard_ids.append(shard_id)
                    continue

                archive_path = u.id_to_path("archive", (archive_id := u.allocate_id("archive")))

                with u.open_for_write_multi_compressed(
                    archive_path / "s"
                ) as f_s, u.open_for_write_multi_compressed(archive_path / "a") as f_a:
                    writer = rio.ArchiveDataWriter(file_archive=f_a, file_sizes=f_s)
                    for entry_size, entry_digest in zip(archive_sizes, archive_digests):
                        out = archive_digest_to_output[entry_digest]
                        writer.begin_file(size=entry_size, digest=entry_digest)
                        with out() as o:
                            for block in o.contents_iter():
                                writer.write_file_data(block)
                        writer.end_file()
                with u.open(archive_path / "h.bin", "wb") as f:
                    rio.HashesWriter(f).write_all(h for h in archive_digests)

                archive_size = u.get_path_for_open(archive_path / "a.zst", "wb").stat().st_size

                shard_path = u.id_to_path("shard", (shard_id := u.allocate_id("shard")))
                with u.open_for_write_multi_compressed(shard_path / "p") as f:
                    rio.ShardPathsWriter(f).write_all(e.rest for e in shard_entries)

                with u.open(shard_path / "h.bin", "wb") as f:
                    rio.HashesWriter(f).write_all(e.rest.digest for e in shard_entries)

                # allocate shard-to-archive mapping
                s2a_path = u.id_to_path("sa", (s2a_id := u.allocate_id("sa")))

                with u.open(shard_path / "sa.cbor", "wb") as f:
                    rio.cbor_dump(s2a_id, f)

                with u.open_for_write_multi_compressed(s2a_path / "m") as f:
                    rio.MapShardToArchiveWriterTrivial(f).write_all(
                        shard_id=shard_id, archive_id=archive_id, archive_size=archive_size
                    )

                u.add_shard_to_index(shard_digest, shard_id)
                shard_ids.append(shard_id)

            img_path = u.id_to_path("image", (img_id := u.allocate_id("image")))

            # image user data
            with u.open_for_write_multi_compressed(img_path / "u") as f:
                rio.cbor_dump({"image_type": image_type.value}, f)

            with u.open(img_path / "u.zst", "rb") as f1, cx.open_decompressor(f1, "zst") as f:
                hasher = hf()
                while b := f.read(65536):
                    hasher.update(b)
            image_meta_hash = hasher.digest()

            # allocate image-to-shard mapping
            i2s_path = u.id_to_path("is", (i2s_id := u.allocate_id("is")))

            with u.open(img_path / "is.cbor", "wb") as f:
                rio.cbor_dump(i2s_id, f)

            with u.open_for_write_multi_compressed(i2s_path / "m") as f:
                rio.MapImageToShardWriterTrivial(f).write_all(shard_ids=shard_ids, image_id=img_id)

            computed_image_hash = (
                hf()
                .update_iter(
                    rio.image_file_entries_for_hashing_iter(image_meta_hash, all_shard_entries)
                )
                .digest()
            )

            u.add_image_to_index(computed_image_hash, img_id)

            return {"image_id": computed_image_hash.to_multihash_base64url()}

    def export_image(
        self,
        *,
        repo_name: str = None,
        remote_name: str = None,
        image_id: str,
        target: Path,
        mock_use_system_python: bool,
        mock_target: PurePathBase | None = None,
    ):
        """
        Write image contents to *target*.
        """
        assert (repo_name is not None) + (remote_name is not None) == 1

        with contextlib.ExitStack() as ex:
            if repo_name is None:
                tmp_repo_path = ex.enter_context(self.repo_dedup.temporary_directory())
                repo = LocalRepository(self, tmp_repo_path)
            else:
                repo = self.repo_get(repo_name)

            # TODO: support partial local clones

            transfer = self.get_repo_transfer(local_repo=repo, remote_name=remote_name)
            with transfer.open(PurePosixPath("manifest.bin")):
                pass  # ensure the top-level manifest is available
            hf = repo.get_hash_function()
            exporter = im.VenvExporter(
                hash_function=hf,
                dedup=self.dedup,
                output=mock_target,
                output_real=target,
                mock_use_system_python=mock_use_system_python,
            )
            transfer.export(exporter, transfer.download_image(image_id), max_workers=3)

    def repo_upload(self, repo_name: str, remote_name: str, force: str | None = None) -> None:
        """
        Upload local ``repo_name`` to ``remote_name``. If the remote manifest hash changed, then
        raise an Exception unless ``force`` is not None. In that case, then ``force`` must contain
        the current remote manifest hash.
        """
        (src := self.repo_get(repo_name)).raise_if_not_valid()
        self.get_repo_transfer(src, remote_name).upload_full()
        # FIXME: implement 'force' argument

    def get_remote_repo_accessor(self, remote_name: str) -> rio.RemoteRepoAccessor:
        base = Path.from_uri(self.remotes[remote_name].uri)
        return rio.RemoteRepoAccessorFilesystem(base)

    def get_repo_transfer(self, local_repo: LocalRepository, remote_name: str | None):
        return rio.RepoTransfer(
            path_local=local_repo._path_base,
            dedup=self.repo_dedup,
            accessor=None if remote_name is None else self.get_remote_repo_accessor(remote_name),
        )

    def repo_download(self, remote_name: str, repo_name: str) -> None:
        """
        Download ``remote_name`` to ``repo_name``.
        """
        (dst := self.repo_get(repo_name)).ensure_deleted_and_raise_if_exists()
        transfer = self.get_repo_transfer(dst, remote_name)
        transfer.download_full()

    def repo_copy(self, src: str, dst: str) -> None:
        (src := self.repo_get(src)).raise_if_not_valid()
        (dst := self.repo_get(dst)).ensure_deleted_and_raise_if_exists()
        self.dedup.copy_tree(src, dst)

    @cached_property
    def remotes(self):
        return _Remotes(self)
