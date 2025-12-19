from __future__ import annotations

import io
from pathlib import Path, PureWindowsPath
import sys
from unittest import mock
import zipfile

import attr
import pytest

from vocker.repo import io as rio
from vocker.util import PurePathBase
from vocker import cli, image as im


@attr.s
class FakeImageInfo:
    path: Path = attr.ib()
    mock_path_str: str = attr.ib()


def create_fake_pyenv_windows(path: Path):
    def d(rel_path):
        (p := path / rel_path).parent.mkdir(exist_ok=True, parents=True)
        return p

    mock_path = PureWindowsPath("C:/vocker_example_xyzzy")

    d("Lib/dist-packages/library.py").write_bytes(b"# this is a library\n")
    d("Lib/dist-packages/library2/__init__.py").write_bytes(b"# another library\n")
    d("Lib/dist-packages/library2/util.py").write_bytes(b"# a submodule\n")
    d("Lib/dist-packages/library2/util_copy.py").write_bytes(b"# a submodule\n")
    d("Scripts/activate").write_bytes(
        f'# activate shell script\n\nVIRTUAL_ENV="{mock_path}"\n'.encode("utf-8")
    )

    example_exe_py = f'# example exe script\nprint("hello")\n'
    example_io = io.BytesIO()
    with zipfile.ZipFile(example_io, mode="w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr(zipfile.ZipInfo("__main__.py"), example_exe_py)
    example_exe = [b"MZ" * 100, b"\0" * 100]
    example_exe += f'#!"{mock_path!s}"\n'.encode("utf-8"), example_io.getvalue()

    d("Scripts/example.exe").write_bytes(b"".join(example_exe))
    d("python.exe").write_bytes(b"MZ_not_a_real_executable")
    return FakeImageInfo(path, mock_path_str=f"windows:{mock_path}")


def run_cli(path_base, argv):
    return cli.Main(argv, path_base=path_base).run_debug()


def test_repo_end_to_end(tmp_path):
    # tmp_path = Path("/tmp/repo")
    b = tmp_path / "b"
    run_cli(b, ["repo", "init", "first"])
    assert run_cli(b, ["repo", "ls"])["repos"]["first"] == "ok"

    # create mock image
    import_path = tmp_path / "i"
    res = create_fake_pyenv_windows(import_path)

    # import image into repo
    cmd = ["image", "import", "-R", "first", "--type", "pyenv1", "--mock-image-path"]
    cmd += str(res.mock_path_str), str(res.path)
    res = run_cli(b, cmd)
    print("create image result:", res)
    image_id = res["image_id"]

    # res = run_cli(b, cmd)
    # print("RESULT 2", res)

    # upload image
    (remote_path := tmp_path / "remote").mkdir()
    run_cli(b, ["repo", "remote", "add", "@foo", str(remote_path)])
    run_cli(b, ["repo", "upload", "first", "@foo"])

    # setup another system instance and add the same remote
    b2 = tmp_path / "b2"
    run_cli(b2, ["repo", "remote", "add", "@foo", remote_path.as_uri()])

    _export_image(b2, "@foo", image_id, import_path, tmp_path / "vex")

    # setup yet another system instance and clone the full thing, then export
    b3 = tmp_path / "b3"
    run_cli(b3, ["repo", "remote", "add", "@foo", remote_path.as_uri()])
    run_cli(b3, ["repo", "download", "@foo", "loc"])
    _export_image(b3, "loc", image_id, import_path, tmp_path / "vex2")


def _export_image(b, source_repo: str, image_id: str, import_path: Path, export_path: Path):
    # download and export image
    run_cli(
        b, ["image", "export", "--mock-use-system-python", source_repo, image_id, str(export_path)]
    )

    vname = export_path.name.encode("utf-8")
    assert vname not in (import_path / "Scripts/activate").read_bytes()
    assert vname in (export_path / "Scripts/activate").read_bytes()
    assert same_contents(import_path, export_path, "Lib/dist-packages/library.py")
    assert same_contents(import_path, export_path, "python.exe")
    assert list((export_path / "Lib/dist-packages/__pycache__").glob("*.pyc"))
    assert list((export_path / "Lib/dist-packages/library2/__pycache__").glob("*.pyc"))
    assert not list((export_path / "Lib").glob("*.pyc"))


def same_contents(a, b, suffix):
    return (a / suffix).read_bytes() == (b / suffix).read_bytes()


def test_estimated_archive_sizes():
    array = [0, 1, 2, 3, 4, 255, 256, 257, 1024, 65536, 2**32, 2**50]
    array2 = array.copy()
    array2[0] = 1

    data = rio.estimated_archive_sizes_encode(array)
    assert type(data) is bytes
    assert rio.estimated_archive_sizes_decode(data) == array2
