def empty(line: str) -> bool:
    """
    Determines if the specified line is empty.
    """
    return line == ""


def whitespace(line: str) -> bool:
    """
    Determines if the specified line is empty or contains only whitespace
    characters.
    """
    return empty(line) or line.isspace()
