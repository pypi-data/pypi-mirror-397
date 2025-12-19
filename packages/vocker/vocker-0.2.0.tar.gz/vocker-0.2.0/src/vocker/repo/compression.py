from __future__ import annotations

import abc
import contextlib
import io
import typing as ty

import attr
from sansio_tools.queue import BytesQueue, FileAdapterFromGeneratorBytes


_bytes = bytes | bytearray | memoryview


class CompressorInterface(abc.ABC):
    @abc.abstractmethod
    def compress(self, data: _bytes | None) -> ty.Iterator[bytes]: ...


class DecompressorInterface(abc.ABC):
    eof: bool
    unused_data: bytes

    @abc.abstractmethod
    def feed(self, data: _bytes | None) -> None: ...

    @abc.abstractmethod
    def read(self, max_length: int) -> _bytes: ...


@attr.s(eq=False, hash=False)
class CompressorStdlibAdapter(CompressorInterface):
    object = attr.ib()

    def compress(self, data) -> ty.Iterator[_bytes]:
        if data is None:
            return iter((self.object.flush(),))
        else:
            return iter((self.object.compress(data),))


@attr.s(eq=False, hash=False)
class CompressorZstdAdapter(CompressorInterface):
    object = attr.ib()

    def compress(self, data) -> ty.Iterator[_bytes]:
        if data is None:
            return self.object.flush()
        else:
            return self.object.compress(data)


@attr.s(eq=False, hash=False)
class DecompressorStdlibAdapter(DecompressorInterface):
    object = attr.ib()
    _input: BytesQueue = attr.ib(factory=BytesQueue, init=False)
    _input_eof = False
    _flushed = False

    @property
    def eof(self):
        return self.object.eof

    @property
    def unused_data(self):
        return self.object.unused_data

    def feed(self, data):
        if data is None:
            self._input_eof = True
        elif self._input_eof:
            raise AssertionError("cannot feed data after eof")
        else:
            self._input.append(data)

    def read(self, max_length: int):
        obj = self.object

        if (b := self._input.popleft_any()) is None:
            # Input queue is empty. Perform flush if the input is finished.
            if self._input_eof and not self._flushed:
                self._flushed = True
                return obj.flush()

            # The input stream isn't done yet, so we must wait for more data.
            return b""
        else:
            result = obj.decompress(b, max_length)

            # Put back whatever input wasn't consumed. We will need to feed it back in.
            self._input.appendleft(obj.unconsumed_tail)

            return result


@attr.s(eq=False, hash=False)
class DecompressorStdlibNeedsInputAdapter(DecompressorStdlibAdapter):
    def read(self, max_length: int):
        obj = self.object

        if (b := self._input.popleft_any()) is None and obj.needs_input:
            # Input queue is empty. Perform flush if the input is finished.
            if self._input_eof and not self._flushed:
                self._flushed = True
                return obj.flush()

            # The input stream isn't done yet, so we must wait for more data.
            return b""
        else:
            try:
                return obj.decompress(b or b"", max_length)
            except EOFError:
                return b""


@attr.s(eq=False, hash=False)
class CompressIO(io.RawIOBase):
    file: ty.BinaryIO = attr.ib()
    compressor: CompressorInterface = attr.ib()
    _closed = False

    def readinto(self, buffer):
        raise NotImplementedError

    def write(self, buffer):
        for x in self.compressor.compress(buffer):
            self.file.write(x)
        return len(buffer)

    def close(self):
        if not self._closed:
            self._closed = True
            for x in self.compressor.compress(None):
                self.file.write(x)
        super().close()

    def readable(self):
        return False

    def writable(self):
        return True

    def seekable(self):
        return False


class DecompressIOError(ValueError):
    pass


@attr.s(eq=False, hash=False)
class DecompressIO(io.RawIOBase):
    file: ty.BinaryIO = attr.ib()
    _decompressor: DecompressorInterface = attr.ib()
    _buffer_size = attr.ib(default=65536)
    _strict: bool = attr.ib(default=True)
    _closed = False
    _input_eof = False
    _position = 0

    def tell(self):
        return self._position

    def readable(self):
        return True

    def writable(self):
        return False

    def seekable(self):
        return False

    def readinto(self, buffer):
        if not buffer:
            return 0

        dec = self._decompressor
        while True:
            b = dec.read(len(buffer))
            if b:
                buffer[: (n := len(b))] = b
                self._position += n
                return n

            if self._input_eof:
                if self._strict:
                    if not dec.eof:
                        raise DecompressIOError("truncated input")
                    if dec.unused_data:
                        raise DecompressIOError("unused data after end of compressed stream")
                return 0

            if c := self.file.read(self._buffer_size):
                dec.feed(c)
            else:
                dec.feed(None)
                self._input_eof = True


def make_xz_compressor(preset: int = 6):
    import lzma

    return CompressorStdlibAdapter(
        lzma.LZMACompressor(format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC32, preset=preset)
    )


def make_xz_decompressor() -> DecompressorInterface:
    import lzma

    return DecompressorStdlibNeedsInputAdapter(lzma.LZMADecompressor(format=lzma.FORMAT_XZ))


def make_zstd_compressor(level: int = 3) -> CompressorInterface:
    import pyzstd

    return CompressorStdlibAdapter(pyzstd.ZstdCompressor(level))


def make_zstd_decompressor():
    import pyzstd

    return DecompressorStdlibNeedsInputAdapter(pyzstd.ZstdDecompressor())


compressors = {"zst": make_zstd_compressor, "xz": make_xz_compressor}
decompressors = {"zst": make_zstd_decompressor, "xz": make_xz_decompressor}


def open_compressor(file, compressor: str | CompressorInterface) -> CompressIO:
    if not isinstance(compressor, CompressorInterface):
        compressor = compressors[compressor]()
    return contextlib.closing(CompressIO(file, compressor))


def open_decompressor(file, decompressor: str | DecompressorInterface) -> DecompressIO:
    if not isinstance(decompressor, DecompressorInterface):
        decompressor = decompressors[decompressor]()
    return contextlib.closing(DecompressIO(file, decompressor))
