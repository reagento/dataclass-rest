from warnings import warn

from .api.rest import *  # noqa: F403, compat

warn(
    "Use `import descanso.api.rest` instead",
    DeprecationWarning,
    stacklevel=2,
)
