from __future__ import annotations

import base64
import dataclasses
from functools import cached_property
import hashlib
import re
import typing as ty

from sansio_tools.parser import BinaryParser

__all__ = [
    "HashFunction",
    "Hasher",
    "Digest",
    "HashFunctionRegistry",
    "registry",
    "multihash_varint_encode",
    "multihash_varint_decode",
    "multibase_encode_base64url",
    "multibase_decode_base64url",
    "BadHashSpecError",
    "InvalidHashError",
]


def multihash_varint_encode(n: int) -> bytes:
    assert n >= 0, "n must be nonnegative"
    output = []
    while n or not output:
        byte = n & 127
        n >>= 7
        if n:
            byte |= 128
        output.append(byte)
    return bytes(output)


def multihash_varint_decode(s: bytes, startpos: int = 0) -> tuple[int, int]:
    """
    Raises ValueError in case of invalid encoding. Raises IndexError in case of truncated data.
    """

    output = 0
    bit_position = 0
    for i in range(startpos, startpos + 9):
        byte = s[i]
        output |= (byte & 127) << bit_position
        bit_position += 7
        if byte < 128:
            if byte == 0 and i > startpos:
                raise ValueError("non-canonical encoding (unnecessary bytes)")
            return (i + 1, output)

    raise ValueError("varint too long")


def multihash_varint_decode(p: BinaryParser):
    return p.read_variable_length_int_7bit(
        9, byteorder="big", continuation_bit_value=True, require_canonical=True
    )


_base64url_re = re.compile(b"[a-zA-Z0-9_-]*")


def multibase_decode_base64url(data: str | bytes) -> bytes:
    """
    Decode base64url data.

    https://github.com/multiformats/multibase
    """
    if type(data) is str:
        data = data.encode("ascii")

    if data[:1] != b"u":
        raise AssertionError("only support base64url")

    b64data = data[1:]

    # Python's base64.b64decode implementation simply ignores trailing data
    # after the padding. We check that the data is 100% made up of valid
    # characters.
    if not _base64url_re.fullmatch(b64data):
        raise ValueError("base64url-encoded data contains invalid characters")

    return base64.urlsafe_b64decode(b64data + b"==")


def multibase_encode_base64url(data: bytes) -> str:
    return "u" + base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


class BadHashSpecError(Exception):
    pass


class InvalidHashError(KeyError, BadHashSpecError):
    pass


@dataclasses.dataclass(eq=False)
class HashFunction:
    """
    Describes a hash function.

    Parameters
    ----------
    name: str
        User-friendly name.
    function_code: int
        [Multihash](https://github.com/multiformats/multihash) function code
        used as a prefix to the multihash.
    digest_size: int
        Multihash output digest size in bytes, used as the second prefix.
    hashlib_name: str
        Name used to instantiate a hash function using :func:`hashlib.new()`.
    hashlib_needs_digest_size: bool
        Is the function a variable digest size function (like SHAKE-256)?
    """

    def __str__(self):
        return "registry.name_to_hash[{self.name!r}]"

    name: str
    function_code: int
    digest_size: int
    hashlib_name: str
    hashlib_needs_digest_size: bool

    @cached_property
    def multihash_prefix(self) -> bytes:
        e = multihash_varint_encode
        return e(self.function_code) + e(self.digest_size)

    def digest_from_bytes(self, data: bytes | bytearray | memoryview):
        data = bytes(data)
        if len(data) != self.digest_size:
            raise ValueError("incorrect digest length")
        return Digest(self, data)

    def __call__(self):
        wrapped = hashlib.new(self.hashlib_name)
        if self.hashlib_needs_digest_size:
            cls = ExplicitLengthHasher
        else:
            cls = ImplicitLengthHasher
        return cls(function=self, wrapped=wrapped)


@dataclasses.dataclass
class Hasher:
    """
    An instantiated hash function. Can be used to hash data via :meth:`update`
    or to produce a digest using :meth:`digest`.
    """

    function: HashFunction
    wrapped: object

    @property
    def digest_size(self):
        return self.function.digest_size

    def update(self, data):
        self.wrapped.update(data)
        return self

    def update_iter(self, data):
        for x in data:
            self.update(x)
        return self

    def digest(self) -> Digest:
        return Digest(self.function, self.digest_bytes())

    def digest_bytes(self) -> bytes:
        raise NotImplementedError

    def copy(self):
        return dataclasses.replace(self, wrapped=self.wrapped.copy())


@dataclasses.dataclass
class MultiHasher:
    hashers: dict[ty.Any, Hasher]
    size: int = 0

    def update(self, data):
        for h in self.hashers.values():
            h.update(data)
        self.size += len(data)
        return self

    def digest(self):
        return {k: v.digest() for k, v in self.hashers.items()}

    def copy(self):
        return dataclasses.replace(self, hashers={k: v.copy() for k, v in self.hashers.items()})


@dataclasses.dataclass
class ImplicitLengthHasher(Hasher):
    def digest_bytes(self):
        return self.wrapped.digest()


@dataclasses.dataclass
class ExplicitLengthHasher(Hasher):
    def digest_bytes(self):
        return self.wrapped.digest(self.function.digest_size)


@dataclasses.dataclass(frozen=True, repr=False)
class Digest:
    function: HashFunction
    digest: bytes

    def __repr__(self):
        return f"<Digest {self.function.name} {self.digest.hex()}>"

    def to_multihash_bytes(self) -> bytes:
        """Output a multihash digest as a bytestring."""
        return self.function.multihash_prefix + self.digest

    def to_multihash_base64url(self) -> str:
        """Output a multihash digest using multibase base64url encoding."""
        return multibase_encode_base64url(self.to_multihash_bytes())


@dataclasses.dataclass(eq=False)
class HashFunctionRegistry:
    HASHES = (
        HashFunction("sha2-256", 0x12, 32, "sha256", False),
        HashFunction("sha2-512", 0x13, 64, "sha512", False),
        HashFunction("sha3-512", 0x14, 64, "sha3_512", False),
        HashFunction("shake256-512", 0x19, 64, "shake_256", True),
        HashFunction("blake2s", 0xB260, 32, "blake2s", False),
        HashFunction("blake2b", 0xB240, 64, "blake2b", False),
    )
    hashes: list = dataclasses.field(default=None)
    name_to_hash: dict[str, HashFunction] = dataclasses.field(init=False, default_factory=dict)
    code_and_size_to_hash: dict[tuple[int, int], HashFunction] = dataclasses.field(
        init=False, default_factory=dict
    )

    def __post_init__(self):
        if self.hashes is None:
            self.hashes = self.HASHES

        for h in self.hashes:
            self._register(h)

    def _register(self, desc: HashFunction):
        self.name_to_hash[desc.name] = desc
        self.code_and_size_to_hash[desc.function_code, desc.digest_size] = desc

    def register(self, desc: HashFunction):
        self.hashes.append(desc)
        self._register(desc)

    def decode(self, multihash: str | bytes | bytearray | memoryview) -> Digest:
        if isinstance(multihash, str):
            multihash = multibase_decode_base64url(multihash)
        code, size, out = self.static_decode(multihash)
        return Digest(self.code_and_size_to_hash[code, size], out)

    def decode_from_code_and_digest(self, function_code: int, digest: bytes) -> Digest:
        return Digest(self.code_and_size_to_hash[function_code, len(digest)], digest)

    @staticmethod
    def static_decode(data: bytes | bytearray | memoryview, check=True) -> tuple[int, int, bytes]:
        """
        Decode a multihash (https://github.com/multiformats/multihash) into a
        tuple ``(function_code, digest_size, hash_function_output)``.

        If ``check`` is True, then check that
        ``len(hash_function_output) == digest_size`` or else raise a
        ValueError.
        """
        result = None

        def _gen(p):
            nonlocal result
            function_code = yield from multihash_varint_decode(p)
            digest_size = yield from multihash_varint_decode(p)
            result = function_code, digest_size

        p = BinaryParser(trailing_data_raises=False)
        p.generator = _gen(p)
        p.feed(data)
        p.feed(b"")
        function_code, digest_size = result
        hash_function_output = bytes(p.queue)

        if check and len(hash_function_output) != digest_size:
            raise ValueError("multihash output does not match digest length")

        return (function_code, digest_size, hash_function_output)


registry = HashFunctionRegistry()
