"""GenFlux Client module."""

import os
from dataclasses import dataclass, field


@dataclass
class GenFlux:
    """GenFlux API Client.

    Args:
        api_key: API key for authentication. If not provided, uses GENFLUX_API_KEY env var.
        base_url: Base URL for the GenFlux API.

    Example:
        >>> from genflux import GenFlux
        >>> client = GenFlux()
        >>> client.ping()
        {'status': 'ok', 'message': 'GenFlux SDK is working!'}
    """

    api_key: str | None = field(default=None, repr=False)
    base_url: str = "https://api.genflux.example.com"

    def __post_init__(self) -> None:
        """Initialize the client with API key from environment if not provided."""
        if self.api_key is None:
            self.api_key = os.getenv("GENFLUX_API_KEY")

    def ping(self) -> dict[str, str]:
        """Test if the SDK is working.

        Returns:
            A dictionary with status and message.
        """
        return {"status": "ok", "message": "GenFlux SDK is working!"}

    def echo(self, message: str) -> str:
        """Echo back the given message.

        Args:
            message: The message to echo.

        Returns:
            The same message.
        """
        return message

    def add(self, a: int | float, b: int | float) -> int | float:
        """Add two numbers.

        Args:
            a: First number.
            b: Second number.

        Returns:
            Sum of a and b.
        """
        return a + b
