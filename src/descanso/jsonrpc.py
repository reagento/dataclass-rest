from warnings import warn

from .api.jsonrpc import *  # noqa: F403, compat

warn(
    "Use `import descanso.api.jsonrpc` instead",
    DeprecationWarning,
    stacklevel=2,
)
