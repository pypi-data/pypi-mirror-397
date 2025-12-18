"""FileEx type-hint definitions.

This module defines type-hints used throughout the package.
"""

from pathlib import Path
from typing import TypeAlias


PathLike: TypeAlias = Path | str
"""A file path, either as a string or a `pathlib.Path` object."""


FileLike: TypeAlias = PathLike | str | bytes
"""A file-like input.

- If a `pathlib.Path` is provided, it is interpreted as the path to a file.
- If `bytes` are provided, they are interpreted as the content of the file.
- If a `str` is provided, it is interpreted as the content of the file
  unless it is a valid existing file path, in which case it is treated as the path to a file.
"""
