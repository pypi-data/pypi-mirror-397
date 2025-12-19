from contextlib import nullcontext
import io

import attr
import pytest

from vocker.repo import io as rio
from vocker import multihash as mh


@pytest.mark.parametrize("byte_at_a_time", [False, True])
@pytest.mark.parametrize("truncate", [0, 1])
@pytest.mark.parametrize("extra", [0, 1])
def test_manifest_roundtrip(byte_at_a_time, truncate, extra):
    hf = mh.registry.name_to_hash["sha2-256"]

    node = rio.ManifestNode(
        hf, {"file": (False, hf().digest()), "dir": (True, hf().update(b"foo").digest())}
    )

    reader = rio.ManifestNodeReader()

    data, digest = node.to_bytes()
    if truncate:
        data = memoryview(data)[:-truncate]
    if extra:
        data = bytes(data) + b"\x67" * extra

    expect_valid = not (truncate or extra)
    with pytest.raises(ValueError) if not expect_valid else nullcontext():
        if byte_at_a_time:
            for c in data:
                reader.parser.feed(bytes((c,)))
        else:
            reader.parser.feed(data)
        reader.parser.feed(None)

    assert (reader.out_verified_data is not None) == expect_valid
    if expect_valid:
        assert reader.out_claimed_digest == digest
        assert attr.asdict(reader.out_verified_data) == attr.asdict(node)
