from __future__ import annotations

import abc
from collections import defaultdict
import contextlib
import enum
import functools
import io
import os
import re
import shutil
import subprocess as sbp
import tempfile
import typing as ty
import zipfile
from pathlib import Path, PurePosixPath
import struct
import sys
import itertools

import attr
from cached_property import cached_property
from sansio_tools.queue import BytesQueue

from . import dedup as de, multihash as mh
from .util import assert_, pathwalk


def get_start_of_zipfile(zfile) -> int | None:
    try:
        with zipfile.ZipFile(zfile) as z:
            # offset is the number of bytes from essentially the beginning of the file to a local file header. The smaller
            # the offset, the earlier in the file the local header is.

            local_offsets = (info.header_offset for info in z.infolist())
            return min(itertools.chain([z.start_dir], local_offsets))

            # start_dir is a pretty internal attribute of the ZipFile object. It initially starts at 0 (beginning of file)
            # but the first local file header may not be there, as is the case with exe files, where there's a zip file at
            # the end of the executable. It appears that start_dir can be arbitrarily somewhere in the file based on the
            # location of the outcome of file.seek(). The minimum of start_dir and the smallest local_offset would
            # inevitably result in the location of the start of the zip file.
    except zipfile.BadZipfile:
        return None


class Command(enum.Enum):
    LITERAL = b"\x80"
    VENV_BASE_PATH = b"\x81"
    VENV_NAME = b"\x82"


@attr.s(eq=False, hash=False)
class CommandSequenceWriter:
    """
    Command sequence encoding. There are currently three types of commands:

    - ``0x80 [8 byte "length"] [...length bytes...]``

      This means copy "length" bytes to the output stream.

    - ``0x81``

      This means copy the current Python executable path here.

    - ``0x82``

      This means copy the virtualenv name here.
    """

    max_literal_length: int = attr.ib(default=10 * 1024 * 1024)
    output: BytesQueue = attr.ib(init=False, factory=BytesQueue)
    _current_literal: BytesQueue = attr.ib(init=False, factory=BytesQueue, repr=False)

    def _end_literal(self):
        if n := len(lit := self._current_literal):
            out = self.output
            out.append(Command.LITERAL.value)
            out.append(struct.pack(">Q", n))
            lit.popleft_all_to(out)
            lit.clear()

    def feed(self, b: bytes | memoryview | Command):
        if isinstance(b, Command):
            self.feed_command(b)
        else:
            self.feed_data(b)

    def feed_data(self, b: bytes | memoryview):
        lit = self._current_literal
        n_max = self.max_literal_length
        while len(b):
            allowed = n_max - len(lit)
            current_b = b[:allowed]
            lit.append(current_b)
            if len(lit) == n_max:
                self._end_literal()
            b = b[allowed:]

    def feed_command(self, c):
        self._end_literal()
        self.output.append(c.value)

    def close(self):
        self._end_literal()

    def generator_pipe(
        self, gen: ty.Iterable[bytes | memoryview | Command]
    ) -> ty.Iterable[bytes, memoryview]:
        out = self.output
        for item in gen:
            self.feed(item)
            while out:
                yield out.popleft_any()
        self.close()
        while out:
            yield out.popleft_any()


@attr.s(eq=False, hash=False)
class CommandSequenceReader:
    f: ty.IO = attr.ib()
    literal_length_left = 0

    def _read_from_literal(self, n: int):
        if left := self.literal_length_left:
            output = self.f.read(min(n, left))
            self.literal_length_left -= len(output)
            return output
        return None

    def read(self, n: int) -> bytes | Command:
        """
        Read at most *n* literal bytes OR a command. EOF when an empty bytes is returned.
        """
        if r := self._read_from_literal(n):
            return r

        if not (c := self.f.read(1)):
            return b""  # EOF

        c = Command(c)
        if c == Command.LITERAL:
            [self.literal_length_left] = struct.unpack(">Q", self.f.read(8))
            return self._read_from_literal(n)
        else:
            return c


def _Path(p: Path | str) -> Path:
    if not hasattr(p, "is_absolute"):
        p = Path(p)
    return p if p.is_absolute() else Path.cwd() / p


def pyenv_split(root_path: Path):
    def _make_key(p: Path):
        return "/".join(p.relative_to(root_path).parts) or "."

    @functools.cache
    def _j(*args):
        return "".join(args)

    rx_exts = re.compile(r"(\.pyc$)|(\.(?:pkl|pickle|dll|pyd|lib|exe|lib|dylib|so(\.\d+)*)$)")
    out = defaultdict(list)
    joint_names = {"site-packages", "dist-packages"}

    def _f(p: Path, current_key: str):
        if not p.is_dir():
            if (m := rx_exts.search(p.name.lower())) is None:
                is_binary = False
            elif m.lastindex == 1:
                # it's a pyc file, ignore it
                return
            elif m.lastindex == 2:
                is_binary = True
            out[_j("bin:" if is_binary else "pure:", current_key)].append(p)
            return

        if len(p.relative_to(root_path).parts) <= 2:
            current_key = _make_key(p)

        for child in p.iterdir():
            if p.name in joint_names:
                _f(child, _make_key(child))
            else:
                _f(child, current_key)

    _f(root_path, "")
    return out


class VenvImporterReceiver:
    @abc.abstractmethod
    def call(
        self,
        input_path: Path,
        output_path: PurePosixPath,
        contents: Path | ty.Generator[bytes | memoryview],
        executable: bool,
        template_mode: bool,
    ): ...


def file_block_iter(path: Path, block_size: int = 65536):
    with path.open("rb") as f:
        while block := f.read(block_size):
            yield block


@attr.s(frozen=True)
class ImageFileMetadata:
    executable: bool = attr.ib()


@attr.s
class SingleFileImageMetadata:
    path: PurePosixPath = attr.ib()
    metadata: ImageFileMetadata = attr.ib()
    digest: mh.Digest = attr.ib()

    @classmethod
    def from_shard_entry(cls, data: type[str, str], digest: mh.Digest):
        p, m = data
        path = PurePosixPath(p)
        if m == "":
            metadata = ImageFileMetadata(executable=False)
        elif m == "x":
            metadata = ImageFileMetadata(executable=True)
        else:
            raise ValueError(f"value: {m!r}")
        return cls(path=path, metadata=metadata, digest=digest)

    def to_shard_entry(self):
        return [str(self.path), "x" if self.metadata.executable else ""]

    def to_data_for_image_hash(self):
        return [self.digest.to_multihash_bytes()] + self.to_shard_entry()

    def to_image_hash_sort_key(self):
        s = str(self.path).encode("utf-8")
        return len(s), s


@attr.s
class VenvImporterFileOutput:
    size: int = attr.ib()
    rest: SingleFileImageMetadata = attr.ib()


@attr.s(eq=False, hash=False)
class VenvImporterToImageMetadata:
    hash_function: mh.HashFunction = attr.ib()
    dedup: de.Dedup = attr.ib()

    def __call__(self, output: ImporterOutput) -> VenvImporterFileOutput:
        h = None
        if isinstance(c := output.contents, Path):
            if (r := self.dedup.get_file_hash(self.hash_function, c, check_link=False)) is not None:
                size, h = r

        if h is None:
            hasher = self.hash_function()
            size = 0
            for block in output.contents_iter():
                hasher.update(block)
                size += len(block)
            h = hasher.digest()

        return VenvImporterFileOutput(
            size=size,
            rest=SingleFileImageMetadata(
                path=output.path, digest=h, metadata=ImageFileMetadata(executable=False)
            ),
        )


_PurePathBase = object


@attr.s(eq=False, hash=False)
class VenvImporter:
    """
    Make sure the last component of :attr:`input` is a long random string.
    """

    input: _PurePathBase | Path = attr.ib(converter=_Path)
    input_real: Path = attr.ib(default=None)

    def __attrs_post_init__(self):
        self.forbidden_string = self.input.name.encode("utf-8")
        if self.input_real is None:
            self.input_real = self.input

    def _make_output_path(self, p: Path) -> PurePosixPath:
        return PurePosixPath(*p.relative_to(self.input_real).parts)

    def _handle_exe(self, p: Path):
        with p.open(mode="rb") as f:
            contents = f.read()
            f.seek(0)
            zip_position = get_start_of_zipfile(zfile=f)

        if zip_position is not None:
            if (i := contents.rfind(b"\0#!", zip_position - 1024, zip_position)) < 0:
                raise AssertionError("failed to find #!")
            i += 3  # actual start of path

            path_data = contents[i:zip_position].rstrip(b"\r\n")
            if path_data.startswith(b'"'):
                if not path_data.endswith(b'"'):
                    raise AssertionError("not matching doublequotes??")
                path_data = path_data[1:-1]

            current_path = type(self.input)(path_data.decode("utf-8"))
            if not current_path.is_relative_to(self.input):
                raise AssertionError(f"path {path_data!r} is not under venv base {self.input!r}")

            rel_path = current_path.relative_to(self.input)

            # now let's make it a suffix
            suffix_path = str("x" / rel_path)[1:]

            yield True  # template_mode
            yield contents[:i]
            yield b'"'
            yield Command.VENV_BASE_PATH
            yield suffix_path.encode("utf-8")
            yield b'"\n\r\n'
            yield contents[zip_position:]
        else:
            yield p  # template_mode

    def _handle_activate_script(self, p: Path):
        enc = "utf-8"
        with p.open(mode="rt", encoding=enc) as f:
            text = f.read()

        env_loc = re.escape(str(self.input))
        env_name = re.escape(self.input.name)

        rx = re.compile(f"({env_loc})|({env_name})")
        last_output_pos = 0
        first = True
        for m in rx.finditer(text):
            if first:
                yield True  # template_mode
                first = False
            yield text[last_output_pos : m.start()].encode(enc)

            if m.lastindex == 1:  # env_loc
                yield Command.VENV_BASE_PATH
            else:  # env_name
                yield Command.VENV_NAME

            last_output_pos = m.end()

        if first:
            # this means we found no matches
            yield False  # template_mode
        yield text[last_output_pos:].encode(enc)

    def _handle_dist_info_record(self, p: Path):
        yield False  # template_mode
        enc = "utf-8"
        with p.open(mode="rt", encoding=enc) as f:
            for line in f:
                if line.rstrip():
                    path, _hash, _length = line.rsplit(",", maxsplit=2)
                    yield path.encode(enc)
                    yield b",,\n"
                else:
                    yield line.encode(enc)

    def _handle_simple_copy(self, p: Path):
        yield p  # template_mode

    @cached_property
    def _scripts_dir(self):
        return self.input_real / "Scripts"

    @cached_property
    def _excluded(self):
        return {self.input_real / "pyvenv.cfg"}

    def run(self, file_path: Path) -> ty.Iterator[ty.ContextManager[ImporterOutput]]:
        p = file_path
        if p in self._excluded:
            return

        if p.suffix.lower() == ".pyc":
            return

        f = None
        if p.parent == self._scripts_dir:
            if p.suffix == ".exe":
                f = self._handle_exe
            elif p.stem.lower() == "activate":
                f = self._handle_activate_script

        if f is None:
            f = self._handle_simple_copy
            if p.parent.name.endswith(".dist-info"):
                if p.name == "RECORD":
                    f = self._handle_dist_info_record
                elif p.name == "direct_url.json":
                    return

        @contextlib.contextmanager
        def make():
            gen = f(p)
            template_mode = ty.cast("bool | Path", next(gen))

            if isinstance(template_mode, Path):
                sum(0 for _ in gen)  # exhaust generator
                gen = template_mode
                template_mode = False
            elif template_mode:
                gen = CommandSequenceWriter().generator_pipe(gen)

            path = ("template" if template_mode else "literal") / self._make_output_path(p)

            out = ImporterOutputVenv(
                path=path, template_mode=template_mode, is_executable=False, contents=gen
            )
            try:
                yield out
            finally:
                out.discard()

        yield make


class _Cancel(Exception):
    pass


class ImporterOutput:
    path: PurePosixPath
    is_executable: bool
    contents: Path | ty.Generator[bytes | memoryview]

    def contents_iter(self) -> ty.Generator[bytes | memoryview]:
        if isinstance((x := self.contents), Path):
            return file_block_iter(x)
        else:
            return x

    @abc.abstractmethod
    def discard(self):
        """
        Free up memory taken up by :attr:`contents`, if any.
        """
        if not isinstance(self.contents, Path):
            try:
                self.contents.throw(_Cancel())
            except _Cancel:
                pass


@attr.s(eq=False, hash=False)
class ImporterOutputVenv(ImporterOutput):
    """
    This object is NOT thread-safe.
    """

    path: PurePosixPath = attr.ib()
    template_mode: bool = attr.ib()
    is_executable: bool = attr.ib()
    contents: Path | ty.Generator[bytes | memoryview] = attr.ib()


class VenvFile:
    path: PurePosixPath

    @abc.abstractmethod
    def write_to(self, p: Path, will_never_modify: bool) -> None: ...

    @abc.abstractmethod
    def open_readonly(self) -> ty.IO: ...


@attr.s(eq=False, hash=False)
class VenvFileForTesting(VenvFile):
    path: PurePosixPath = attr.ib()
    local_fs_path: Path = attr.ib()

    def write_to(self, p: Path, will_never_modify: bool) -> None:
        shutil.copyfile(str(self.local_fs_path), str(p))

    def open_readonly(self):
        return self.local_fs_path.open("rb")

    @classmethod
    def generate_from_path(cls, base: Path):
        d = {}
        for root, dirs, files in pathwalk(base):
            for p in files:
                p = root / p
                rel = PurePosixPath(*p.relative_to(base).parts)
                d[rel] = cls(path=rel, local_fs_path=p)
        return d


@attr.s(eq=False, hash=False)
class _PycEntry:
    path_py = attr.ib()
    path_pyc = attr.ib()


def check_process(process: sbp.Popen):
    if retcode := process.poll():
        raise sbp.CalledProcessError(retcode, process.args)


@attr.s(eq=False, hash=False)
class PycGenerator:
    python_exe: Path = attr.ib()
    optimization_level: int = attr.ib()
    max_threads: int = attr.ib(default=0)
    magic: bytes = attr.ib(init=False, default=None)
    suffix: str = attr.ib(init=False, default=None)

    def get_data_to_hash(self):
        self._ensure_analyze()
        yield str(self.optimization_level).encode("ascii")
        yield b","
        yield self.magic

    def _compileall(self, base: Path, files: ty.Iterable[Path]) -> None:
        cmd = [str(self.python_exe.absolute())]
        cmd += "-B", "-m", "compileall", "-l", "-s", str(base)
        cmd += "--invalidation-mode", "unchecked-hash"  # disable timestamp and hash checking
        cmd += "-o", str(self.optimization_level)
        cmd += "-j", str(self.max_threads)
        cmd += "-i", "-"  # input from stdin
        cmd_input = b"".join(x for f in files for x in (str(f).encode("utf-8"), b"\n"))

        proc = sbp.Popen(cmd, stdin=sbp.PIPE, stdout=sbp.PIPE, env={"PYTHONUTF8": "1"} | os.environ)

        # This is not a race condition because compileall does not start until it has received
        # all of its input.
        proc.stdin.write(cmd_input)
        proc.stdin.close()

        i = 0
        for line in proc.stdout:
            # TODO: progress bar
            if line.startswith(b"Compiling "):
                i += 1
            if i % 100 == 0:
                print(f"{i:>5d}/{len(files):<5d}")

        proc.wait()
        # We do not check the return code as some of the source files may have failed to compile.
        # This happens surprisingly often with test cases for syntax errors.

    def _ensure_analyze(self):
        if self.magic is None:
            self._analyze()

    def _analyze(self):
        """
        Figure out the pyc file naming scheme and magic.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            basename = "xyzzy"
            (py_path := tmp / f"{basename}.py").write_bytes(b"")
            self._compileall(tmp, (py_path,))
            py_path.unlink()
            [pyc_path] = (p for p in tmp.rglob("*") if p.is_file())
            pyc_path: Path
            assert_(pyc_path.name.startswith(basename))
            assert_(pyc_path.name.endswith(".pyc"))
            self.suffix = pyc_path.name[len(basename) :]
            with pyc_path.open("rb") as f:
                self.magic = f.read(4)

    def map_path(self, p: Path):
        """
        Map a source file path to the corresponding pyc file path.
        """
        assert_(p.name.endswith(".py"))
        return p.parent / "__pycache__" / (p.name[:-3] + self.suffix)

    def __call__(self, base: Path, paths: ty.Iterable[Path]):
        self._ensure_analyze()
        self._compileall(base, paths)


class PycGeneratorMockUseSystemPython(PycGenerator):
    @property
    def python_exe(self):
        return Path(sys.executable)

    @python_exe.setter
    def python_exe(self, value):
        pass


@attr.s(eq=False, hash=False)
class _VenvExporterPycFile:
    path_py: Path = attr.ib()
    path_pyc: Path = attr.ib()
    pyc_tags: frozenset[bytes] = attr.ib(default=None)
    link_request: de.DedupLinkRequest = attr.ib(default=None)


@attr.s(eq=False, hash=False)
class VenvExporter:
    hash_function: mh.HashFunction = attr.ib()
    dedup: de.Dedup = attr.ib()
    output: _PurePathBase | None = attr.ib()
    output_real: Path = attr.ib(converter=_Path)
    venv_name: str = attr.ib(default=None)
    mock_use_system_python: bool = attr.ib(default=False)

    def __attrs_post_init__(self):
        if self.output is None:
            self.output = self.output_real
        if self.venv_name is None:
            self.venv_name = re.compile("[^0-9a-zA-Z_-]").sub("_", self.output.name)

    def _handle_command(self, c: Command) -> bytes:
        if c == Command.VENV_BASE_PATH:
            return str(self.output).encode("utf-8")
        else:  # Can only be Command.VENV_NAME
            return self.venv_name.encode("utf-8")

    def _process_file(self, file: VenvFile):
        # get rid of the "literal"/"template" at the start, then join the path with the output path
        output = self._map_path(file.path)
        output.parent.mkdir(exist_ok=True, parents=True)
        if (first_component := file.path.parts[0]) == "literal":
            file.write_to(output, will_never_modify=True)
        else:
            with file.open_readonly() as f, output.open("wb") as f_w:
                reader = CommandSequenceReader(f)
                while item := reader.read(65536):
                    if isinstance(item, bytes):
                        f_w.write(item)
                    else:
                        f_w.write(self._handle_command(item))

    def begin_session(self):
        pass

    def end_session(self):
        self._generate_pyc(0)

    def _generate_pyc(self, optimization_level: int):
        """
        1. Find source python files that don't have a pyc file.
        2. Query hashes from dedup.
        3. Attempt to link dedup'd pyc files.
        4. Generate pyc files using compileall.
        5. Adopt newly-generated pyc files into the dedup system.
        """
        exe = self._find_python()
        hf = self.hash_function

        if self.mock_use_system_python:
            PycGenerator_ = PycGeneratorMockUseSystemPython
        else:
            PycGenerator_ = PycGenerator

        pg = PycGenerator_(python_exe=exe, optimization_level=optimization_level)
        h_exe: mh.Digest = self.dedup.get_or_compute_file_hash(hf, exe, check_link=False)[1]
        h_key = hf().update(h_exe.to_multihash_bytes()).update_iter(pg.get_data_to_hash()).digest()
        h_key_bytes = h_key.to_multihash_bytes()

        def _pyc_tag(py_path: Path) -> bytes:
            h_py: mh.Digest = self.dedup.get_or_compute_file_hash(hf, py_path, check_link=False)[1]
            h_pyc = hf().update(h_key_bytes).update(h_py.to_multihash_bytes()).digest()
            return b"pyc:" + h_pyc.to_multihash_bytes()

        py_paths = self.output_real.rglob("*.py")

        todo = [
            _VenvExporterPycFile(
                path_py=path_py,
                path_pyc=pg.map_path(path_py),
                pyc_tags=frozenset((_pyc_tag(path_py),)),
            )
            for path_py in py_paths
        ]

        for x in todo:
            x.link_request = de.DedupLinkRequest(
                hash_function=hf,
                link_path=x.path_pyc,
                file_metadata=de.DedupFileMetadata.make_plain(),
                file_contents_hash=None,
                open_file_once=None,
                tags=x.pyc_tags,
            )
            x.path_pyc.parent.mkdir(parents=True, exist_ok=True)

        try:
            self.dedup.run_batch([x.link_request for x in todo])
        except de.BatchError as exc:
            for r in exc.requests:
                if not isinstance(r.exc, de.MissingContentError):
                    raise r.exc

        todo = [x for x in todo if not x.link_request.success]

        if not todo:
            # early exit if there are no files to compile
            return

        # Now we compile the pyc files.
        pg(self.output_real, [x.path_py for x in todo])

        # Some pyc files may fail to appear (syntax errors for example) so we must skip them.
        self.dedup.adopt_files(
            hf,
            (
                de.AdoptRequest(x.path_pyc, tags=x.pyc_tags)
                for x in todo
                if x.path_pyc.exists() and x.path_pyc.stat().st_size >= 256
            ),
        )

    def _find_python(self):
        files = {p.name.lower(): p for p in self.output_real.iterdir()}
        for name in ("python.exe", "python"):
            if path := files.get(name):
                return path
        raise ValueError("could not find python executable")

    def _map_path(self, path: PurePosixPath):
        return self.output_real / Path(*path.parts[1:])

    def _dedup_file_metadata(self, x: ImageFileMetadata):
        return de.DedupFileMetadata(executable=x.executable)

    def _process_template_file(self, f: ty.BinaryIO, f_w: ty.BinaryIO):
        reader = CommandSequenceReader(f)
        while item := reader.read(65536):
            if isinstance(item, bytes):
                f_w.write(item)
            else:
                f_w.write(self._handle_command(item))

    def provide_files(self, inputs: ty.Iterable[VenvExportInput]):
        """
        Provide the files and their contents.
        """

        counter = 0
        later: list[tuple[Path, VenvExportInput]] = []
        with self.dedup.temporary_directory() as tmp:
            batch = []

            for x in inputs:
                digest = x.info.files[0].digest
                d = {f.metadata for f in x.info.files}
                kw = dict(
                    hash_function=digest.function,
                    file_contents_hash=digest,
                    open_file_once=x.contents_open,
                    file_not_needed=x.contents_reject,
                )

                # HACK: We simply copy files smaller than 256 bytes. This is to avoid bumping into
                # the limit on the number of hardlinks for a single file, which is 1023 on Windows.
                # This limit would be exceeded by the numerous zero-length "__init__.py" files.
                if (
                    len(d) > 1
                    or any(f.path.parts[0] != "literal" for f in x.info.files)
                    or x.info.size < 256
                ):
                    # slow path - we need to write the file to a temporary location first
                    batch.append(
                        de.DedupLinkRequest(
                            link_path=(tmp_file := tmp / f"c{counter}.bin"),
                            file_metadata=de.DedupFileMetadata.make_plain(),
                            **kw,
                        )
                    )
                    counter += 1
                    later.append((tmp_file, x))
                else:
                    # all files are literal
                    for f in x.info.files:
                        (dst := self._map_path(f.path)).parent.mkdir(exist_ok=True, parents=True)
                        batch.append(
                            de.DedupLinkRequest(
                                link_path=dst,
                                file_metadata=self._dedup_file_metadata(f.metadata),
                                **kw,
                            )
                        )
                        kw["open_file_once"] = None

            self.dedup.run_batch(batch)

            for tmp_file, x in later:
                for f in x.info.files:
                    (dst := self._map_path(f.path)).parent.mkdir(exist_ok=True, parents=True)
                    with tmp_file.open("rb") as f_r, dst.open("wb") as f_w:
                        if f.path.parts[0] == "literal":
                            shutil.copyfileobj(f_r, f_w)
                        else:
                            self._process_template_file(f_r, f_w)
                    self.dedup.apply_metadata_to_file(dst, self._dedup_file_metadata(f.metadata))


class VenvExportInput(abc.ABC):
    info: SolidArchiveFileInfo

    @abc.abstractmethod
    def contents_open(self) -> ty.BinaryIO: ...

    @abc.abstractmethod
    def contents_reject(self) -> None: ...


@attr.s(eq=False, hash=False)
class SolidArchiveFileInfo:
    files: list[SingleFileImageMetadata] = attr.ib()
    offset: int = attr.ib()
    size: int = attr.ib()


@attr.s(eq=False, hash=False)
class VenvExportInputFromSolidArchive(VenvExportInput):
    archive_io: ty.BinaryIO = attr.ib()
    info: SolidArchiveFileInfo = attr.ib()

    def _skip_to(self, offset: int):
        bs = 2**17
        to_skip = offset - (f := self.archive_io).tell()
        assert_(to_skip >= 0, "solid archive members must be read in the order they appear in")
        while to_skip:
            to_skip -= (n := len(f.read(min(to_skip, bs))))
            assert_(n, "attempted to skip past the end of the solid archive")

    def contents_open(self):
        self._skip_to(self.info.offset)
        # NOTE: we don't check the hash here because the dedup code does it
        return LimitIO(self.archive_io, self.info.size)

    def contents_reject(self):
        # With some luck, we might not need to decompress this archive at all if we don't
        # need any of the contents.
        pass


@attr.s(eq=False, hash=False)
class LimitIO(io.RawIOBase):
    _raw: ty.BinaryIO = attr.ib()
    _bytes_left: int = attr.ib()

    def writable(self):
        return False

    def seekable(self):
        return False

    def readinto(self, b):
        if len(b) > (n := self._bytes_left):
            if n == 0:
                return 0
            b = memoryview(b)[:n]
        read_count = self._raw.readinto(b)
        self._bytes_left -= read_count
        return read_count
