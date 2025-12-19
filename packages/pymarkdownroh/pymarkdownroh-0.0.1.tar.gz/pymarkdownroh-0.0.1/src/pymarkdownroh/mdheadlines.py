"""Create markdown headline or title."""

# Different headline levels. 
# A headlinelevel is definded as a <hx></hx> in html.
_HEADLINELEVEL = {
    1: "#",
    2: "##",
    3: "###",
    4: "####",
    5: "#####",
    6: "######"
}

def create_headline(hlvl: int, string: str) -> str:
    """Create a title or headline with the specified text."""

    if not _verify_headline_lvl(hlvl):
        return _HEADLINELEVEL[hlvl] + " " + string


def _verify_headline_lvl(hlvl: int):
    """Check if headline level is between 1 and 6."""

    if hlvl not in _HEADLINELEVEL:
        raise ValueError("Value must be between 1 and 6.")