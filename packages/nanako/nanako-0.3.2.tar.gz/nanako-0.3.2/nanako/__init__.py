"""
Yui (ゆい) - An educational programming language for the generative AI era.

A Turing-complete language using minimal operations to teach programming fundamentals
through constrained computation with Japanese syntax.
"""

from .nanako import (
    YuiRuntime,
    YuiParser,
    YuiArray,
    YuiError,
)

# Import yui_cli to register cell magic
try:
    from . import nanako_cli
except ImportError:
    pass

__version__ = "0.3.2"
__author__ = "Yui Project"
__description__ = "An educational programming language for the generative AI era"

__all__ = [
    'YuiRuntime',
    'YuiParser',
    'YuiError',
    'YuiArray',
]
