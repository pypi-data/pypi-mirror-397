"""Formatting operations emphasizing strings."""

# Default character used when converting emphasizing string.
_EMPHASIZEPREF = "*"

_EMPHASIZEKIND = {
    "bold": f"{_EMPHASIZEPREF + _EMPHASIZEPREF}",
    "italic": f"{_EMPHASIZEPREF}",
    "boldItalic": f"{_EMPHASIZEPREF + _EMPHASIZEPREF+ _EMPHASIZEPREF}"
}

class MDFormat:
    """Class to write strings emphasized. You can write strings in bold, latin or both."""

    def __init__(self, string: str = "", start: int = 0, end: int = 1000):
        self.string = string
        self.start = start
        self.end = end

    def write_bold(self) -> str:
        """Convert provided string to bold string."""

        _verify_range(self.start, self.end)
        return self.string[:self.start] + _EMPHASIZEKIND["bold"] + self.string[self.start:self.end] + _EMPHASIZEKIND["bold"] + self.string[self.end:]

    def write_italic(self) -> str:
        """Convert provided self.string to italic self.string."""

        _verify_range(self.start, self.end)
        return self.string[:self.start] + _EMPHASIZEKIND["italic"] + self.string[self.start:self.end] + _EMPHASIZEKIND["italic"] + self.string[self.end:]


    def write_bold_italic(self) -> str:
        """Convert provided self.string to italic and bold."""

        _verify_range(self.start, self.end)
        return self.string[:self.start] + _EMPHASIZEKIND["boldItalic"] + self.string[self.start:self.end] + _EMPHASIZEKIND["boldItalic"] + self.string[self.end:]

    @staticmethod
    def create_horizontal_rule():
        return str(_EMPHASIZEPREF + " " + _EMPHASIZEPREF + " " +_EMPHASIZEPREF)

def _verify_range(start: int, end: int) -> Exception:
    if end < start:
        raise ValueError(f"End {end} smaller than Start {start}.")