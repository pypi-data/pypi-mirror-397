"""GenFlux Python SDK."""

from .client import GenFlux

__all__ = ["GenFlux"]
__version__ = "0.1.0"


def hello(name: str = "World") -> str:
    """Return a greeting message.

    Args:
        name: The name to greet.

    Returns:
        A greeting message.

    Example:
        >>> import genflux
        >>> genflux.hello()
        'Hello, World!'
        >>> genflux.hello("GenFlux")
        'Hello, GenFlux!'
    """
    return f"Hello, {name}!"


def version() -> str:
    """Return the SDK version.

    Returns:
        The version string of the SDK.

    Example:
        >>> import genflux
        >>> genflux.version()
        '0.1.0'
    """
    return __version__
