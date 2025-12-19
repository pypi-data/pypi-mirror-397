import attr


class InvalidPathError(ValueError):
    pass


@attr.s(eq=False, hash=False, kw_only=True)
class IntegerToPath:
    """
    Turn an integer into a structured file path.
    """

    entries_per_directory: int = attr.ib(default=256)
    format_code: str = attr.ib(default=None)
    file_suffix = attr.ib(default=".bin")

    def __attrs_post_init__(self):
        if self.format_code is None:
            self.format_code = self._make_default_format_code()

    def _make_default_format_code(self):
        bits = (self.entries_per_directory - 1).bit_length()
        hexdigits = (bits + 3) // 4
        return f"{{:0{hexdigits:d}x}}"

    def __call__(self, integer: int) -> str:
        assert integer >= 0
        fmt = self.format_code
        r = []
        div = integer
        ext = self.file_suffix
        n = self.entries_per_directory
        while True:
            div, rem = divmod(div, n)
            r.append(fmt.format(rem) + ext)
            ext = ""  # only add extension on the first loop
            if not div:
                break
        r.reverse()
        return "/".join(r)

    def invert(self, path: str) -> int:
        if not path.endswith(ext := self.file_suffix):
            raise InvalidPathError

        number_hex = path[: -len(ext)].replace("/", "")
        try:
            return int(number_hex, 16)
        except Exception as exc:
            raise InvalidPathError from exc
