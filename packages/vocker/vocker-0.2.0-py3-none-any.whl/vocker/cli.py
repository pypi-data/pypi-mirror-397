from __future__ import annotations

import argparse
from pathlib import Path
import re
import functools
import json
import sys
import typing as ty

import structlog

from .util import parse_pure_path, pprofile

logger = structlog.get_logger(__name__)


rx_probably_uri = re.compile(r"^[a-z-]+://")


def syst():
    from . import system as syst

    return syst


def _remote_repo_name(s):
    if not s.startswith("@"):
        raise ValueError("remote repository name must be start with a @")

    return s[1:]


def _local_repo_name(s):
    if s.startswith("@"):
        raise ValueError("local repository name cannot start with @")

    return s


def _abspath(s):
    return Path(s).absolute()


class Main:
    def __init__(self, argv, *, path_base=None):
        self.argument_parser = self.init_argparser()
        self.a = self.argument_parser.parse_args(argv)
        self.path_base = path_base

    def cmd_missing(self):
        self.argument_parser.error("missing command")

    @functools.cached_property
    def system(self):
        return syst().System(path_base=self.path_base)

    def cmd_repo_remote_add(self):
        a = self.a
        name = _remote_repo_name(self.a.remote_name)
        if not rx_probably_uri.search(uri := a.uri):
            if (p := Path(uri)).exists():
                uri = p.as_uri()
            else:
                raise ValueError(f"not a valid URI or filesystem path: {uri!r}")
        self.system.remotes[name] = syst().RemoteRepository(uri=uri)

    def cmd_repo_remote_list(self):
        return dict(remotes={k: repr(v) for k, v in self.system.remotes.items()})

    def cmd_repo_remote_remove(self):
        name = _remote_repo_name(self.a.remote_name)
        del self.system.remotes[name]

    def cmd_repo_list(self):
        has_invalid = False
        d = {}
        for r in self.system.repo_list():
            if not (valid := r.check()):
                has_invalid = True
            d[r.name] = "ok" if valid else "damaged"
        comment = ""
        if has_invalid:
            comment = """There are damaged/invalid local repositories. This can happen if a local \
repository operation was interrupted (via a crash, an unexpected power loss, or Ctrl-C)."""
        return dict(repos=d, comment=comment)

    def cmd_repo_init(self):
        self.system.repo_init_new(self.a.local_name, self.a.hash_function)

    def _get_local_and_remote_names(self):
        local_name, remote_name = self.a.local_name, self.a.remote_name
        if local_name.startswith("@"):
            local_name, remote_name = remote_name, local_name
        local_name = _local_repo_name(local_name)
        remote_name = _remote_repo_name(remote_name)
        return local_name, remote_name

    def cmd_repo_upload(self):
        local_name, remote_name = self._get_local_and_remote_names()
        self.system.repo_upload(local_name, remote_name)

    def cmd_repo_download(self):
        local_name, remote_name = self._get_local_and_remote_names()
        self.system.repo_download(remote_name, local_name)

    def cmd_image_import(self):
        if (t := self.a.type) == "auto":
            t = None
        return self.system.repo_add_image(
            repo_name=self.a.repository,
            image_path=self.a.input,
            image_type=t,
            mock_image_path=self.a.mock_image_path,
        )

    def cmd_image_export(self):
        trusted = self.a.trusted
        use_sys_python = self.a.mock_use_system_python
        if (trusted + use_sys_python) != 1:
            raise ValueError("provide exactly one of --trusted or --mock-use-system-python")

        if (repo_name := self.a.repo_name).startswith("@"):
            kw = dict(remote_name=_remote_repo_name(repo_name))
        else:
            kw = dict(repo_name=_local_repo_name(repo_name))
        return self.system.export_image(
            image_id=self.a.image_id,
            target=self.a.target,
            mock_target=self.a.mock_target,
            mock_use_system_python=self.a.mock_use_system_python,
            **kw,
        )

    def cmd_gc(self):
        d = dict(main=self.system.dedup, repo=self.system.repo_dedup)
        dedups_keys = set()
        a = self.a
        max_age = a.max_age
        check_integrity = a.check_integrity
        check_links = a.check_links
        if a.main:
            dedups_keys.add("main")
        if a.repo:
            dedups_keys.add("repo")
        if a.full:
            dedups_keys.update(("main", "repo"))
            check_integrity = True
            check_links = True
            if max_age is None:
                max_age = 3600
        dedups = tuple(d[k] for k in dedups_keys)
        check_links_under: ty.Sequence[Path] = a.check_links_under or ()

        for k in dedups_keys:
            dedup = d[k]
            logger.info("Starting to gc.", data_dedup=k)
            if check_links:
                logger.info("Checking links.")
                dedup.check_links()
            elif check_links_under:
                for p in check_links_under:
                    logger.info(f"Checking links under user path.", data_path=str(p))
                    dedup.check_links(p)

            if check_integrity:
                logger.info("Checking integrity.")
                dedup.integrity_check(skip_same_mtime=True)
                dedup.garbage_collect_extra_files()

            if max_age is not None:
                logger.info("Deleting unused files.", data_max_age_seconds=max_age)
                dedup.update_all_orphaned()
                dedup.garbage_collect_dedup_files(max_age)

        def _info(dedup):
            return {
                "corrupted": [c.to_json() for c in dedup.corrupted_list()],
                "#comments": [f"Corrupted base path is at {dedup.path_corrupted!s}"],
            }

        result = {"dedup": {k: _info(v) for k, v in d.items()}, "comments": []}

        if not dedups:
            result["comments"].append(
                """No actions taken. You must use --main and/or --repo to specify which \
files to act on, or use --full to perform all cleanup actions against all of the files."""
            )

        return result

    def cmd_stats(self):
        def f(dedup):
            stats = dedup.compute_stats()
            if stats.dedup_total_bytes:
                ratio = stats.link_total_bytes / stats.dedup_total_bytes
            else:
                ratio = 1.0
            return stats.to_json() | {"#space_savings_ratio": ratio}

        d = dict(main=self.system.dedup, repo=self.system.repo_dedup)
        return {k: f(v) for k, v in d.items()}

    def init_argparser(self):
        parser = argparse.ArgumentParser()
        parser.set_defaults(callback=self.cmd_missing)
        subparsers = parser.add_subparsers()
        sub_repo = subparsers.add_parser("repo").add_subparsers()
        sub_remote = sub_repo.add_parser("remote").add_subparsers()
        sub_img = subparsers.add_parser("image").add_subparsers()

        p = {}

        def _add_parser(___parent, ___name):
            def f(*args, **kwargs):
                a = p[___name] = ___parent.add_parser(*args, **kwargs)
                a.set_defaults(callback=getattr(self, "cmd_" + ___name))
                return a

            return f

        def _Path(x):
            return Path(x).resolve()

        _add_parser(sub_repo, "repo_upload")(
            "upload",
            description="""\
Upload local repository copy to remote.""",
        )
        _add_parser(sub_repo, "repo_download")(
            "download",
            description="""\
Download remote repository to local.""",
        )

        def _arg_local(k):
            p[k].add_argument(
                "local_name", metavar="LOCAL-NAME", help="Name of the local repository."
            )

        def _arg_remote(k):
            p[k].add_argument(
                "remote_name",
                metavar="@REMOTE-NAME",
                help="Name of the remote repository, with a '@' character as a prefix.",
            )

        _arg_local("repo_upload")
        _arg_remote("repo_upload")

        _arg_remote("repo_download")
        _arg_local("repo_download")

        _add_parser(sub_remote, "repo_remote_add")(
            "add",
            description="Add a new remote repository location.",
        )
        _add_parser(sub_remote, "repo_remote_remove")(
            "remove",
            description="Remove remote repository.",
        )
        _add_parser(sub_remote, "repo_remote_list")(
            "list",
            aliases=["ls"],
            description="List remote repository locations.",
        )
        _arg_remote("repo_remote_add")
        _arg_remote("repo_remote_remove")
        p["repo_remote_add"].add_argument("uri", help="URI of repository location")

        _add_parser(sub_repo, "repo_list")(
            "list", aliases=["ls"], description="List local repositories."
        )
        _add_parser(sub_repo, "repo_init")("init", description="Create new empty local repository.")
        _arg_local("repo_init")
        p["repo_init"].add_argument("--hash-function", default="sha3-512")

        _add_parser(sub_img, "image_import")("import", description="Add image to local repository.")
        p["image_import"].add_argument(
            "--repository",
            "-R",
            metavar="LOCAL-REPO",
            help="Name of the local repository.",
            required=True,
        )
        p["image_import"].add_argument("--type", "-t", help="Image type. Autodetected by default.")
        p["image_import"].add_argument(
            "--mock-image-path",
            help="(For testing only) Pretend that this is the original location of the image.",
            type=parse_pure_path,
        )
        p["image_import"].add_argument(
            "input", metavar="INPUT-DIRECTORY", help="Input directory path.", type=_abspath
        )

        _add_parser(sub_img, "image_export")(
            "export",
            description="Download an image (if needed) and unpack its contents into a directory.",
        )
        p["image_export"].add_argument(
            "repo_name",
            metavar="LOCAL-REPO-NAME|@REMOTE-REPO-NAME",
            help="Name of the local or remote repository.",
        )
        p["image_export"].add_argument(
            "image_id",
            metavar="IMAGE-ID",
            help="Image ID. Must be a multihash in base64url format.",
        )
        p["image_export"].add_argument(
            "target", metavar="TARGET-DIR", help="Target directory to export to.", type=_abspath
        )
        p["image_export"].add_argument(
            "--trusted",
            help="Allow the execution of arbitrary code inside the image. This is necessary, for"
            "example, to generate the pyc files. The only other alternative is the "
            "--mock-use-system-python flag.",
            action="store_true",
        )
        p["image_export"].add_argument(
            "--mock-target",
            help="(For testing only) Pretend that this is the output path.",
            type=parse_pure_path,
        )
        p["image_export"].add_argument(
            "--mock-use-system-python",
            help="(For testing only) Do not attempt to use the Python.",
            action="store_true",
        )
        _add_parser(subparsers, "gc")("gc", description="Clean old and unused files.")
        p["gc"].add_argument(
            "--full",
            help="""Do everything. Equivalent to `--main --repo --check-links --check-integrity \
--max-age=3600`.""",
            action="store_true",
        )
        p["gc"].add_argument(
            "--main",
            help="Act on the files inside exported image directories.",
            action="store_true",
        )
        p["gc"].add_argument("--repo", help="Act on local repository files.", action="store_true")
        p["gc"].add_argument(
            "--check-links",
            help="Check the links created by the file deduplication system.",
            action="store_true",
        )
        p["gc"].add_argument(
            "--max-age", help="Delete unused files older than MAX-AGE seconds.", type=int
        )
        p["gc"].add_argument(
            "--check-links-under",
            "-L",
            help="Check the links under the following (potentially non-existing) path.",
            type=_abspath,
            action="append",
        )
        p["gc"].add_argument(
            "--check-integrity",
            help="Read every file contents and check the hash.",
            action="store_true",
        )
        _add_parser(subparsers, "stats")("stats", description="Show storage statistics.")

        return parser

    def setup_logging(self):
        structlog.configure(logger_factory=structlog.PrintLoggerFactory(sys.stderr))

    def run(self):
        with pprofile():
            value = self.a.callback()
        if isinstance(value, dict):
            print(json.dumps(value, indent=2))

    def run_debug(self):
        return self.a.callback()

    @classmethod
    def main(cls, argv=None, setup_logging=True):
        self = cls(argv=argv)
        if setup_logging:
            self.setup_logging()
        self.run()
