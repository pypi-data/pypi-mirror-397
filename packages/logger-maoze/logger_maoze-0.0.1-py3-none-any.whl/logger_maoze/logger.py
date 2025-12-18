import time
import os
from functools import wraps
from typing import Optional

try:
    term_cols = os.get_terminal_size().columns
except OSError:
    term_cols = 80  # Default value if terminal size cannot be determined


def update_terminal_size(f):
    """
        Decorator to update the terminal size before calling the function.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        global term_cols
        try:
            term_cols = os.get_terminal_size().columns
        except OSError:
            term_cols = 80  # Default value if terminal size cannot be determined
        return f(*args, **kwargs)
    return wrapper


def log(msg: Optional[str] = None, newline: bool = False):
    """
        Simple log function to print messages in one line.
    """
    if not msg:
        msg = ""
    if newline:
        print(msg.ljust(term_cols - 1) + "\r", end="\n")
    else:
        print(msg.ljust(term_cols - 1) + "\r", end="")


def casclog(msg, sep: str = " | ", newline: bool = False):
    """
        Cascading log function to print messages in one line separated by sep.
    """
    if newline:
        print(msg, sep)
    else:
        print(msg, sep, end="")


@update_terminal_size
def casciterlog(iterable, sep: str = " | ", column_width: int = 10):
    """
        Cascading iterable log function to print messages from an iterable in one line separated by sep.
    """
    for i, item in enumerate(iterable):
        print(str(item).ljust(column_width), end=sep if (i + 1) % (term_cols // (column_width + len(sep))) != 0 else "\n")
    print()


def anilog(msg: str | list[str], delay: float = 0.01, newline: bool = True,
           color: Optional[str] = None):
    """
        Animated log function to print messages character by character.
    """
    match msg:
        case list():
            for line in msg:
                if newline:
                    anilog("\n" + line, delay, True)
                anilog(line, delay, False)
        case str():
            for char in msg:
                if color:
                    msg = colorize(msg, color)
                print(char, end="", flush=True)
                time.sleep(delay)
    if newline:
        print()


@update_terminal_size
def centerlog(msg: str):
    """
        Centered log function to print messages in the center of the terminal.
    """
    print(msg.center(term_cols))


@update_terminal_size
def gridlog(msg: str, sep: str = " | ", columns: int = 4):
    """
        Grid log function to print messages in a grid format.
    """
    width = term_cols // columns
    for i, line in enumerate(msg.split("\n")):
        print(line.ljust(width), end=sep if i < len(msg.split("\n")) - 1 else "\n")


@update_terminal_size
def generator_gridlog(iterable, sep: str = " | ", columns: int = 4):
    """
        Generator grid log function to print messages in a grid format.
    """
    width = term_cols // columns
    for i, item in enumerate(iterable):
        print(str(item).ljust(width), end=sep if (i + 1) % columns != 0 else "\n")
    print()


@update_terminal_size
def centerize(text: str) -> str:
    return text.center(term_cols)


def colorize(text: str, color: str) -> str:
    """
        Colorize text for terminal output.
        Supported colors: red, green, yellow, blue, magenta, cyan, white, peach, orange, purple, pink, lime
    """
    match color:
        case "red":
            return f"\033[91m{text}\033[0m"
        case "green":
            return f"\033[92m{text}\033[0m"
        case "yellow":
            return f"\033[93m{text}\033[0m"
        case "blue":
            return f"\033[94m{text}\033[0m"
        case "magenta":
            return f"\033[95m{text}\033[0m"
        case "cyan":
            return f"\033[96m{text}\033[0m"
        case "white":
            return f"\033[97m{text}\033[0m"
        case "peach":
            return f"\033[38;2;255;229;180m{text}\033[0m"
        case "orange":
            return f"\033[38;2;255;165;0m{text}\033[0m"
        case "purple":
            return f"\033[38;2;128;0;128m{text}\033[0m"
        case "pink":
            return f"\033[38;2;255;192;203m{text}\033[0m"
        case "lime":
            return f"\033[38;2;0;255;0m{text}\033[0m"
        case _:
            return text


@update_terminal_size
def loadingbar(char: str, k: int, n: int, percentage=False):
    count = int((k / n) * (term_cols - 2 - (percentage * 6)))
    log("[" + count * char + (term_cols - (percentage * 6) - 2 - count) * " " + "]" + percentage * f"[{int((k / n) * 100)}%]", False)


@update_terminal_size
def iterable_loadingbar(iterable, char: str = "#", percentage: bool = False, msg: Optional[str | list[str]] = None):
    n = len(iterable)
    if msg:
        anilog(msg=msg, newline=True, delay=0.005)
    for k, item in enumerate(iterable, start=1):
        loadingbar(char, k, n, percentage)
        yield item
    print()


@update_terminal_size
def generator_loadingbar(generator, char: str = "#", percentage: bool = False, msg: Optional[str | list[str]] = None):
    items = list(generator)
    n = len(items)
    if msg:
        anilog(msg=msg, newline=True, delay=0.005)
    for k, item in enumerate(items, start=1):
        loadingbar(char, k, n, percentage)
        yield item
    print()
