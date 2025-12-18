from __future__ import annotations

from functools import wraps
from pathlib import Path
from typing import Callable

def wtl(
    x: str,
    *,
    keyword: str,
    file_path: Path | str,
    verbose: bool = False,
    encoding: str = "utf-8",
) -> None:
    """
    Insert `x` on the line immediately AFTER the line containing `keyword`.
    If there is already an inserted line there from a previous run, overwrite it.

    Assumption (same as your old code): the "value line" is exactly ONE line
    immediately below the keyword line.
    """
    path = Path(file_path)

    lines = path.read_text(encoding=encoding).splitlines(keepends=True)

    out: list[str] = []
    i = 0
    inserted = False

    while i < len(lines):
        line = lines[i]
        out.append(line)

        if (not inserted) and (keyword in line):
            # overwrite the next line (if any) by skipping it
            if i + 1 < len(lines):
                i += 1  # skip one line after keyword
            out.append(x.rstrip("\n") + "\n")
            inserted = True

        i += 1

    if not inserted:
        raise ValueError(f"Keyword '{keyword}' not found in {path}")

    path.write_text("".join(out), encoding=encoding)
    if verbose:
        print(f"Output written to '{path}'")


def write_to_latex(func: Callable[..., str]) -> Callable[..., str]:
    """
    Decorator: run the function, then write its string return value to LaTeX.

    Usage:
        @write_to_latex
        def compute_square(x): ...
        compute_square(4, file_path="doc.tex", keyword="RESULT_PLACEHOLDER")
    """

    @wraps(func)
    def wrapper(*args: object, **kwargs: object) -> str:
        file_path_obj = kwargs.pop("file_path", None)
        keyword_obj = kwargs.pop("keyword", None)
        verbose_obj = kwargs.pop("verbose", False)
    
        file_path: Path | str | None
        if file_path_obj is None or isinstance(file_path_obj, (Path, str)):
            file_path = file_path_obj
        else:
            raise TypeError("file_path must be Path or str")
    
        keyword: str | None
        if keyword_obj is None or isinstance(keyword_obj, str):
            keyword = keyword_obj
        else:
            raise TypeError("keyword must be str")
    
        verbose: bool
        if isinstance(verbose_obj, bool):
            verbose = verbose_obj
        else:
            raise TypeError("verbose must be bool")

        result = func(*args, **kwargs)
        if not isinstance(result, str):
            raise TypeError(f"{func.__name__} must return a str, got {type(result).__name__}")

        if file_path is None or keyword is None:
            raise TypeError("Missing required keyword arguments: file_path=..., keyword=...")

        wtl(result, keyword=keyword, file_path=file_path, verbose=verbose)
        return result

    return wrapper
