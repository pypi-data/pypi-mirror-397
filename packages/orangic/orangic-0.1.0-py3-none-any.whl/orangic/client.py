"""
Orangic Python SDK - Pre-release Version
A Python client library for the Orangic API
"""

__version__ = "0.1.0"


class OrangicError(Exception):
    """Base exception for Orangic API errors"""
    pass


class Orangic:
    """
    Main Orangic API client
    
    Note: This is a pre-release version. The API is not yet functional.
    This package reserves the 'orangic' name on PyPI.
    """
    
    def __init__(self, api_key=None, base_url="https://api.orangic.tech", **kwargs):
        """
        Initialize the Orangic client
        
        Args:
            api_key: Your Orangic API key (coming soon)
            base_url: Base URL for the API
            **kwargs: Additional configuration options
        """
        raise NotImplementedError(
            "Orangic is currently in development. "
            "This package reserves the name for the upcoming release. "
            "Visit https://orangic.tech for updates."
        )


# Placeholder for future functionality
def completion(*args, **kwargs):
    """Quick completion function - Coming soon!"""
    raise NotImplementedError(
        "Orangic is currently in development. "
        "Visit https://orangic.tech for updates."
    )