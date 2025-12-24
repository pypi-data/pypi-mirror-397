# flake8: noqa: E402 — we want to use deprecation warning before import due to possible import errors

__all__ = [
    'memory_management', 'optimization'
]

import warnings

warnings.warn(
    f"`{__name__}` package was moved to `tie_ml_utils.tools`",
    DeprecationWarning,
    stacklevel=2
)

import tie_ml_utils.tools as tools

# Delegate submodule loading to the new package's location.
# This makes dotted imports like `tie_ml.modules.pooler.memory_management` work.
__path__ = getattr(tools, '__path__', __path__)

from tie_ml_utils.tools import memory_management, optimization  # noqa: I202
