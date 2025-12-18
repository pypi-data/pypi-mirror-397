"""
Orangic Python SDK - Pre-release

This is a placeholder release to reserve the package name.
The full functionality will be available soon!

Visit https://orangic.tech for updates.
"""

from .client import (
    Orangic,
    OrangicError,
    completion,
    __version__,
)

__all__ = [
    "Orangic",
    "OrangicError",
    "completion",
    "__version__",
]

# Display notice on import
print(
    "⚠️  Orangic is currently in pre-release. "
    "Visit https://orangic.tech for updates."
)