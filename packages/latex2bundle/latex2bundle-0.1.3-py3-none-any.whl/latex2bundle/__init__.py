"""latex2bundle package

Expose `run()` and `main()` at package level.
"""
__all__ = ["run", "main"]

from .cli import run, main

__version__ = "0.1.0"
