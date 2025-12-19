"""Create block quotes."""

# Blockquotes are text where each line starts with a > symbol.

def create_blockquote(string: str) -> str:
    """Create a markdown blockquote of the provided string."""

    # Default text delimiter when reading files.
    delimiter = "\n"
    # Result string.
    res = ""
    # Split input into list of string to prefix it with "> ".
    splitres = string.split(delimiter)
    # Check if only one sentence was provided.
    if len(splitres) == 1:
        return "> " + string

    for l in splitres:
        # Check if current line has no content which equals "\n".
        if len(l) == 0:
            res += "> " + delimiter
        res += "> " + l + delimiter

    # Strip newline characters from end of string.
    return res.strip()