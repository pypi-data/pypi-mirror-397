import filecmp
import os
import shutil
import subprocess as sbp
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

import pytest

from vocker import image as _vi


def _list_files_recursively(p: Path):
    return {
        (root / f).relative_to(p): root / f for root, dirs, files in _vi.pathwalk(p) for f in files
    }


def assert_compare_directories(a, b, should_be_equal: bool = True):
    cmps = [cmp_root := filecmp.dircmp(a, b, shallow=False)]

    # recursively traverse cmps
    is_equal = True
    while cmps:
        cmp = cmps.pop()
        cmps += cmp.subdirs.values()

        if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
            is_equal = False

    if is_equal != should_be_equal:
        cmp_root.report_full_closure()

    assert is_equal == should_be_equal


def _find_python_exe(p: Path) -> Path:
    for suffix in (".exe", ""):
        if (python_exe := p / f"python{suffix}").exists():
            return python_exe
    else:
        raise AssertionError("could not find python exe")


def _create_python_env(path: Path):
    if not (python_env := os.environ.get(env_var := "VOCKER_TESTS_PY_ENV")):
        pytest.skip(reason=f"{env_var} is not set")
    python_env = Path(python_env)

    def extract_to(dst: Path) -> Path:
        print("start extracting to", dst)
        if python_env.suffix != ".nupkg":
            raise AssertionError(f"don't know how to handle {python_env!r}")

        with zipfile.ZipFile(python_env) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                p = PurePosixPath(info.filename)
                if len(p.parts) > 1 and p.parts[0] == "tools":
                    (out := dst / Path(*p.parts[1:])).parent.mkdir(exist_ok=True, parents=True)
                    with zf.open(info) as f_r, out.open("wb") as f_w:
                        shutil.copyfileobj(f_r, f_w)  # type: ignore

        print("done extracting")
        return _find_python_exe(dst)

    # create a virtualenv for the sole purpose of stealing its activate scripts
    with tempfile.TemporaryDirectory() as tmp:
        tmp_python_exe = extract_to(tmp := Path(tmp))
        sbp.run(
            [str(tmp_python_exe), "-m", "venv", "--symlinks", "--without-pip", str(path)],
            check=True,
            stdin=sbp.DEVNULL,
        )

    # delete all files except for the activate scripts
    allowed_dirs = {path / "Scripts", path / "bin"}
    for root, dirs, files in _vi.pathwalk(path):
        for f in files:
            f = root / f
            if root in allowed_dirs and "activate" in f.stem.lower():
                pass
            else:
                f.unlink()

    # now extract the python installation onto the target path
    python_exe = extract_to(path)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copytree(
            str(Path(__file__).parent / "example_package_with_script"), str(tmp), dirs_exist_ok=True
        )
        sbp.run(
            [sys.executable, "-c", "import setuptools as s;s.setup()", "bdist_wheel"],
            check=True,
            cwd=str(tmp),
        )

        [wheel] = (tmp / "dist").glob("*.whl")

        env = os.environ.copy()
        # the current timestamp is embedded inside the Windows script executables
        env["SOURCE_DATE_EPOCH"] = "946702800"  # here's to another lousy millennium

        env["PIP_NO_CACHE_DIR"] = "1"

        cmd = [str(python_exe), "-m", "pip", "install", str(wheel)]
        sbp.run(cmd, check=True, stdin=sbp.DEVNULL, env=env)


def test_two_venvs_same_image(tmp_path):
    venv_names = "faddd72152675c9f7038b08e8e0c4605", "5149665a73d40dcf238a9901d240f1c8"
    venvs = [tmp_path / name for name in venv_names]
    images = [tmp_path / f"image-{i}" for i in (1, 2)]

    # create environments, and then turn them into images
    for v, image in zip(venvs, images):
        _create_python_env(v)

        # ensure the activate script exists and contains the venv name
        [activate_script] = v.glob("*/activate")
        assert v.name in activate_script.read_text(encoding="utf-8")

        # ensure that at least one example CLI script is there
        [example_cli] = v.glob("*/example-cli*")
        assert v.name.encode("utf-8") in example_cli.read_bytes()

        _vi.VenvImporter(input=v, output=image).run()

    # compare environments (they will be different)
    assert_compare_directories(*venvs, should_be_equal=False)

    # compare resulting images
    assert_compare_directories(*images)

    # now export the image under a different, longer name
    export_path = tmp_path / (venv_names[0][::-1] * 2)

    # export the image under a different Python environment
    files = _vi.VenvFileForTesting.generate_from_path(images[0])
    _vi.VenvExporter(output=export_path, files=files, threads=16).run()

    # check that we can run the Python executable inside
    python_exe = _find_python_exe(export_path)
    proc = sbp.run(
        [str(python_exe), "-c", "import bisect;print(bisect.__file__)"],
        capture_output=True,
        check=True,
    )
    assert export_path.name.encode("utf-8") in proc.stdout

    # check that we can run CLI scripts
    [example_cli] = export_path.glob("*/example-cli*")
    proc = sbp.run([str(example_cli)], capture_output=True, check=True)
    assert b"hello" in proc.stdout
