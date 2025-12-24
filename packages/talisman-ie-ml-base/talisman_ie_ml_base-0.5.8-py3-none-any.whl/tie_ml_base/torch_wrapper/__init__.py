# flake8: noqa: E402 — we want to use deprecation warning before import due to possible import errors

__all__ = [
    'DEFAULT_PREFERRED_DEVICE', 'DirectorySerializableTorchModule', 'PicklableTorchModule', 'TorchModule'
]

import warnings

warnings.warn(
    f"`{__name__}` module was moved to `tie_ml_utils.torch_wrapper`",
    DeprecationWarning,
    stacklevel=2
)

from tie_ml_utils.torch_wrapper import DEFAULT_PREFERRED_DEVICE, DirectorySerializableTorchModule, PicklableTorchModule, TorchModule
