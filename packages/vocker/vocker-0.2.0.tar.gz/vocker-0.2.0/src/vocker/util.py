import os
import pathlib
from pathlib import Path
import concurrent.futures as _cf
import contextlib
import platform
import urllib.parse as _up


PurePathBase = object


@contextlib.contextmanager
def pprofile(options=None):
    if options is None:
        options = os.environ.get("PPROFILE")

    if not options:
        yield None
        return

    d = dict(_up.parse_qsl(options.replace(",", "&"), keep_blank_values=True))
    use_threads = int(d.get("thread", "1"))
    prefix = d.get("prefix", "")
    if (stat := d.get("stat")) is not None:
        stat = float(stat)
    if (annotate := d.get("annotate")) is not None and not annotate:
        annotate = prefix + "annotate.txt"
    if (cg := d.get("cachegrind")) is not None and not cg:
        cg = prefix + "cachegrind.out.0"

    import pprofile

    if stat is None:
        prof = pprofile.Profile()
    else:
        prof = pprofile.StatisticalThread()

    if stat is not None:
        prof = pprofile.StatisticalProfile()
        runner = pprofile.StatisticalThread(profiler=prof, period=stat, single=not use_threads)
    else:
        klass = pprofile.ThreadProfile if use_threads else pprofile.Profile
        prof = runner = klass()

    try:
        with runner:
            yield runner
    finally:
        with open(cg, "wt", encoding="utf-8") as file:
            prof.callgrind(file)
        with open(annotate, "wt", encoding="utf-8") as file:
            prof.annotate(file)


def supports_executable() -> bool:
    return platform.system() != "Windows"


def assert_(x, message=None):
    if not x:
        if message:
            raise AssertionError(message)
        else:
            raise AssertionError


def pathwalk(p: Path, **kw):
    for root, dirs, files in os.walk(str(p), **kw):
        yield Path(root), dirs, files


def random_names(prefix: str, suffix: str):
    for n in (3, 4, 8, 16, 16):
        yield "".join((prefix, os.urandom(n).hex(), suffix))


def create_file_random(parent: Path, prefix: str, suffix: str):
    for name in random_names(prefix, suffix):
        try:
            return (path := parent / name).open("x+b")
        except OSError as exc:
            if not Path(path).parent.is_dir():
                raise
            exc_ = exc

    raise exc_


_path_prefix_to_pathlib_type = {
    "windows": "PureWindowsPath",
    "posix": "PurePosixPath",
    "": "PurePath",
}


def parse_pure_path(path: str) -> PurePathBase:
    before, sep, after = path.partition(":")
    if (clsname := _path_prefix_to_pathlib_type.get(before)) is None or not sep:
        raise ValueError(
            f'pure path must start with "windows:" or "posix:" or ":" prefix, got {path!r}'
        )
    return getattr(pathlib, clsname)(after)


def raise_as_completed(*args, **kwargs):
    """Go through each future as completed, re-raising any exception that occurs."""
    for future in _cf.as_completed(*args, **kwargs):
        future.result()  # this will re-raise an exception if one was raised by _process_file


@contextlib.contextmanager
def cancel_futures_on_error(exe: _cf.Executor):
    ok = False
    try:
        yield
        ok = True
    finally:
        if not ok:
            exe.shutdown(cancel_futures=True)
