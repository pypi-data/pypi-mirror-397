"""
Access Control CLI

Command line interface for managing the access control system.
Gracefully handles cases where CLI dependencies are not installed.
"""

from ..core.compatibility import has_cli_support, require_optional_dependency

if has_cli_support():
    try:
        from .main import app
        __all__ = ["app"]
    except ImportError as e:
        def app(*args, **kwargs):
            raise ImportError(f"CLI failed to load: {e}")
        __all__ = ["app"]
else:
    def app(*args, **kwargs):
        require_optional_dependency('typer', 'CLI functionality')
    __all__ = ["app"]
