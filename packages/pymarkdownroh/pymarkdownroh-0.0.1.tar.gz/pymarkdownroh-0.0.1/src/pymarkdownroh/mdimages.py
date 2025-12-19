"""Create markdown image links."""

# from .mdlinks import MDLink
from .mdlinks import MDLink

class MDImage(MDLink):
    """Class for creating markdown images."""

    def __init__(self, linktext: str, url: str, title:str, linkname: str | int = 1):
        super().__init__(linktext, url, title, linkname)

    def create_inline_link(self) -> str:
        """Create inline image link."""

        return "!" + super().create_inline_link()
    
    def create_reference_link(self) -> str:
        """Create image reference link."""

        return "!" + super().create_reference_link()