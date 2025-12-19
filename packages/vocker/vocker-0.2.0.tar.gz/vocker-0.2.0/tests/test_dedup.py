import concurrent.futures as cf
from functools import partial
import io
import json
from pathlib import Path
import random
import shutil
from time import perf_counter, sleep

import attr
import pytest

from vocker.dedup import (
    BatchError,
    DedupBackendHardlink,
    DedupFileMetadata,
    DedupLinkRequest,
)
from vocker import multihash as mh, dedup as ded
from vocker.integer_to_path import IntegerToPath

from .conftest import RUN_SLOW_TESTS


def _run_batch(de, reqs):
    try:
        de.run_batch(reqs)
    except BatchError:
        for r in reqs:
            if (e := r.exc) is not None:
                raise e


@attr.s
class Waiter:
    wait_until: float | int | None = attr.ib(default=None)

    def __call__(self):
        if (t_start := self.wait_until) is not None:
            wait = t_start - perf_counter()
            if wait > 0 and False:
                sleep(wait)


@attr.s
class MockOpenFile:
    contents: bytes = attr.ib()
    waiter: Waiter | None = attr.ib(default=None)
    accessed: bool = attr.ib(init=False, default=False)

    def __call__(self):
        self.accessed = True
        if (w := self.waiter) is not None:
            w()
        return io.BytesIO(self.contents)


def _link_request(
    link_path: Path,
    contents: bytes,
    file_metadata: DedupFileMetadata,
    hash_function: mh.HashFunction,
    corrupt: bool = False,
):
    (h := hash_function()).update(contents)
    return DedupLinkRequest(
        hash_function=hash_function,
        link_path=link_path,
        file_metadata=file_metadata,
        file_contents_hash=h.digest(),
        open_file_once=MockOpenFile(contents + b"\0" if corrupt else contents),
    )


@pytest.mark.skipif(False, reason="manual test only")
@pytest.mark.parametrize("batch_size", [1, 10, 100, 1000])
def test_dedup_speed(tmp_path, batch_size):
    dedup_base = tmp_path / "dedup"
    (scratch := tmp_path / "scratch").mkdir()
    hf = mh.registry.name_to_hash["sha2-256"]

    m1 = DedupFileMetadata(executable=False)
    de = DedupBackendHardlink(base_path=dedup_base)
    f = partial(_link_request, hash_function=hf, file_metadata=m1)
    i2p = IntegerToPath()

    repeat = 3
    timings = []

    for k in range(repeat):
        requests = [f(scratch / str(k) / i2p(i), str(i).encode("ascii")) for i in range(batch_size)]
        for r in requests:
            r.link_path.parent.mkdir(exist_ok=True, parents=True)
        t0 = perf_counter()
        de.run_batch(requests)
        timings.append(t := perf_counter() - t0)
        print(t)

    print("@#@", json.dumps({"batch_size": batch_size, "timings": timings}))


def test_dedup_basic(tmp_path):
    dedup_base = tmp_path / "dedup"
    (scratch := tmp_path / "scratch").mkdir()
    hf = mh.registry.name_to_hash["sha2-512"]

    m1 = DedupFileMetadata(executable=False)
    de = DedupBackendHardlink(base_path=dedup_base)
    f = partial(_link_request, hash_function=hf, file_metadata=m1)

    reqs = [
        f(scratch / "a.bin", b"A"),
        f(scratch / "b.bin", b"B"),
        f(scratch / "c.bin", b"A"),
    ]
    _run_batch(de, reqs)

    (extra_path := de._path_dedup / "ff.bin").write_bytes(b"hello")

    assert reqs[0].open_file_once.accessed
    assert reqs[1].open_file_once.accessed
    assert not reqs[2].open_file_once.accessed, "should have reused the dedup file"

    assert reqs[0].link_path.read_bytes() == b"A"
    assert reqs[1].link_path.read_bytes() == b"B"
    assert reqs[2].link_path.read_bytes() == b"A"

    for req in reqs:
        assert de.get_file_hash(hf, req.link_path, check_link=False) == (1, req.file_contents_hash)
        # assert req.file_hash == de.hash_file_metadata(req.file_metadata, req.file_contents_hash)

    def _dedup_file_count():
        return sum(1 for x in de._path_dedup.glob("**/*.bin") if x != extra_path)

    # now let's try a corrupt file where the contents don't match the hash

    reqs2 = [f(scratch / "x.bin", b"XXX", corrupt=True)]
    with pytest.raises(BatchError):
        de.run_batch(reqs2)
    assert not reqs2[0].link_path.exists()

    stat = de.compute_stats()
    assert stat.dedup_count == 2
    print(stat)
    assert _dedup_file_count() == 2

    shutil.rmtree(str(scratch))
    assert _dedup_file_count() == 2
    assert de.compute_stats().orphaned_count == 0

    for req in reqs:
        assert de.get_file_hash(hf, req.link_path, check_link=False) == (1, req.file_contents_hash)
        assert de.get_file_hash(hf, req.link_path, check_link=True) == None

    # notice that the dedup files have become orphaned (no links)
    de.check_links()
    stats = de.compute_stats()
    assert stats.link_count == 0
    assert stats.dedup_count == 0
    assert stats.orphaned_count == 2
    assert _dedup_file_count() == 2

    # file have not been orphaned for one hour, so this should do nothing
    de.garbage_collect_dedup_files(min_age_seconds=3600)
    assert de.compute_stats().orphaned_count == 2
    assert _dedup_file_count() == 2

    # delete orphaned files for real
    de.garbage_collect_dedup_files(min_age_seconds=0)
    stats = de.compute_stats()
    assert stats.orphaned_count == 0
    assert stats.link_count == 0
    assert _dedup_file_count() == 0

    assert extra_path.exists()
    de.garbage_collect_extra_files()
    assert not extra_path.exists()


def test_dedup_corrupt(tmp_path):
    dedup_base = tmp_path / "dedup"
    (scratch := tmp_path / "scratch").mkdir()
    hf = mh.registry.name_to_hash["sha2-512"]

    m1 = DedupFileMetadata(executable=False)
    de = DedupBackendHardlink(base_path=dedup_base)
    f = partial(_link_request, hash_function=hf, file_metadata=m1)

    reqs = [
        f(scratch / "a1.txt", b"A" * 137),
        f(scratch / "a2.txt", b"A" * 137),
        f(scratch / "b.txt", b"B" * 1027),
    ]
    _run_batch(de, reqs)

    de.integrity_check(skip_same_mtime=False, keep_corrupted=True)
    assert not list(de.corrupted_list())

    (scratch / "a2.txt").write_bytes(b"X")
    de.integrity_check(skip_same_mtime=False, keep_corrupted=True)

    assert not (scratch / "a1.txt").exists()
    assert not (scratch / "a2.txt").exists()
    assert (scratch / "b.txt").exists()

    corrupted = list(de.corrupted_list())
    print(corrupted)
    assert len(corrupted) == 1
    assert len(corrupted[0].link_paths) == 2

    de.corrupted_clear()
    assert not list(de.corrupted_list())


def test_dedup_removed(tmp_path):
    dedup_base = tmp_path / "dedup"
    (scratch := tmp_path / "scratch").mkdir()
    hf = mh.registry.name_to_hash["sha2-512"]

    m1 = DedupFileMetadata(executable=False)
    de = DedupBackendHardlink(base_path=dedup_base)
    f = partial(_link_request, hash_function=hf, file_metadata=m1)

    reqs = [
        f(scratch / "a1.txt", b"A" * 137),
        f(scratch / "a2.txt", b"A" * 137),
        f(scratch / "b.txt", b"B" * 1027),
    ]
    _run_batch(de, reqs)


@attr.s(eq=False, hash=False)
class TortureEntry:
    t: float = attr.ib()
    hash_function: mh.HashFunction = attr.ib()
    corrupt: bool | None = attr.ib()  # None means no hash provided
    link_path: str = attr.ib()
    contents: bytes = attr.ib()
    request = attr.ib(init=False)

    def set_request(self, **kw):
        self.request = r = self.to_request(**kw)
        return r

    def to_request(self, *, start_time):
        hf = self.hash_function
        waiter = Waiter(start_time + self.t)
        return DedupLinkRequest(
            hash_function=hf,
            link_path=self.link_path,
            file_metadata=DedupFileMetadata(executable=False),
            file_contents_hash=(
                None if self.corrupt is None else hf().update(self.contents).digest()
            ),
            open_file_once=MockOpenFile(
                self.contents + b"\0" if self.corrupt else self.contents, waiter=waiter
            ),
            file_not_needed=waiter,
        )


@pytest.mark.parametrize("thread_count", [5])
@pytest.mark.parametrize("runtime_seconds", [3, 10] if RUN_SLOW_TESTS else [5])
@pytest.mark.parametrize("contents_count", [5, 20, 100] if RUN_SLOW_TESTS else [20])
@pytest.mark.parametrize(
    "corrupt_count,no_hash_count", [(3, 3), (10, 10), (47, 47)] if RUN_SLOW_TESTS else [(47, 47)]
)
@pytest.mark.parametrize("random_seed", list(range(30)) if RUN_SLOW_TESTS else [1])
def test_dedup_torture_test(
    random_seed,
    tmp_path,
    thread_count,
    contents_count,
    corrupt_count,
    no_hash_count,
    runtime_seconds,
):
    rng = random.Random(random_seed + 100)

    dedup_base = tmp_path / "dedup"
    (scratch := tmp_path / "scratch").mkdir()
    hf = mh.registry.name_to_hash["sha2-256"]

    contents = [
        bytes(rng.randrange(0, 256) for _ in range(257)) * 23 for _ in range(contents_count)
    ]
    total_entries = 100 * thread_count

    corrupt_indices = random.sample(range(total_entries), corrupt_count + no_hash_count)
    corrupt = {i: True for i in corrupt_indices[:corrupt_count]}
    corrupt.update((i, None) for i in corrupt_indices[corrupt_count:])

    thread_entries = [[] for _ in range(thread_count)]
    for i in range(total_entries):
        thread_entries[rng.randrange(0, thread_count)].append(
            TortureEntry(
                t=rng.uniform(0, runtime_seconds),
                hash_function=hf,
                corrupt=corrupt.get(i, False),
                link_path=scratch / f"{i}.bin",
                contents=rng.choice(contents),
            )
        )

    start_time = perf_counter() + 0.05

    for t in thread_entries:
        t.sort(key=lambda x: x.t)
        for e in t:
            e.set_request(start_time=start_time)

    def _thread_entrypoint(thread_index: int):
        de.run_batch([e.request for e in thread_entries[thread_index]])

    # expected_contents_count_min = len(
    #     {e.contents for t in thread_entries for e in t if not e.corrupt}
    # )
    # expected_contents_count_max = len(
    #     {
    #         e.contents if e.corrupt is False else e.link_path
    #         for t in thread_entries
    #         for e in t
    #         if not e.corrupt
    #     }
    # )
    expected_link_count = sum(1 for t in thread_entries for e in t if not e.corrupt)

    de = DedupBackendHardlink(base_path=dedup_base, sqlite_synchronous="OFF")

    with cf.ThreadPoolExecutor() as exe:
        [exe.submit(_thread_entrypoint, i) for i in range(1, thread_count)]
        try:
            _thread_entrypoint(0)
        except BatchError:
            pass

    for t in thread_entries:
        for e in t:
            if not e.corrupt:
                if exc := e.request.exc:
                    raise exc
                assert e.link_path.exists()

    stats = de.compute_stats()
    # assert stats.dedup_count >= expected_contents_count_min
    # assert stats.dedup_count <= expected_contents_count_max
    assert stats.link_count >= expected_link_count


def _dedup_file_count(de):
    return len(list(de._path_dedup.glob("*.bin")))


def test_adopt(tmp_path):
    dedup_base = tmp_path / "dedup"
    (scratch := tmp_path / "scratch").mkdir()
    hf = mh.registry.name_to_hash["sha2-256"]

    de = DedupBackendHardlink(base_path=dedup_base, sqlite_synchronous="OFF")
    assert de.compute_stats().link_count == 0

    (scratch / "A1.txt").write_bytes(b"A")
    (scratch / "A2.txt").write_bytes(b"A")
    (scratch / "B1.txt").write_bytes(b"B")
    de.adopt_files(
        hf,
        [
            ded.AdoptRequest(path=scratch / "A1.txt"),
            ded.AdoptRequest(path=scratch / "B1.txt"),
            ded.AdoptRequest(path=scratch / "A2.txt"),
        ],
    )
    de.check_links()
    de.integrity_check(skip_same_mtime=False)
    assert de.compute_stats().dedup_count == 2
    assert de.compute_stats().link_count == 3
    assert _dedup_file_count(de) == 2

    with de.temporary_directory() as tmp:
        (tmp / "B2.txt").write_bytes(b"B")
        (tmp / "C1.txt").write_bytes(b"C")
        de.adopt_files(
            hf,
            [
                ded.AdoptRequest(path=tmp / "B2.txt"),
                ded.AdoptRequest(path=tmp / "C1.txt"),
            ],
        )
        assert de.compute_stats().orphaned_count == 0
        assert de.compute_stats().dedup_count == 3
        assert de.compute_stats().link_count == 5
        assert _dedup_file_count(de) == 3

    assert not tmp.exists()
    assert de.compute_stats().orphaned_count == 1
    assert de.compute_stats().dedup_count == 2
    assert de.compute_stats().link_count == 3
    assert _dedup_file_count(de) == 3

    de.garbage_collect_dedup_files(0)
    assert de.compute_stats().orphaned_count == 0
    assert de.compute_stats().dedup_count == 2
    assert de.compute_stats().link_count == 3
    assert _dedup_file_count(de) == 2


@pytest.mark.skipif(not RUN_SLOW_TESTS, reason="skipping slow test")
@pytest.mark.xfail(reason="not fixed yet, see tktview/1c0485c208")
def test_hardlink_limit(tmp_path):
    dedup_base = tmp_path / "dedup"
    (scratch := tmp_path / "scratch").mkdir()
    hf = mh.registry.name_to_hash["sha2-256"]

    m1 = DedupFileMetadata(executable=False)
    de = DedupBackendHardlink(base_path=dedup_base)
    f = partial(_link_request, hash_function=hf, file_metadata=m1)

    count = 1023 + 10
    data = b"B" * 1027
    i2p = IntegerToPath()

    def _make_path(i: int):
        (p := scratch / i2p(i)).parent.mkdir(parents=True, exist_ok=True)
        return p

    reqs = [f(_make_path(i), data) for i in range(count)]
    _run_batch(de, reqs)
