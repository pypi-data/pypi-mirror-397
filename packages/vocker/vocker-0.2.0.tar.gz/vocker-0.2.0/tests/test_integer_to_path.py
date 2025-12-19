import pytest

from vocker.integer_to_path import IntegerToPath


@pytest.mark.parametrize("power_of_two", range(1, 66))
@pytest.mark.parametrize("offset", [-1, 0, 1])
def test_roundtrip(power_of_two, offset):
    x = 2**power_of_two + offset

    i2p = IntegerToPath()

    path = i2p(x)
    assert i2p.invert(path) == x
