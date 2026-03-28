from warnings import warn

from .transformers.response import *  # noqa: F403, compat

warn(
    "Use `import descanso.transformers.response` instead",
    DeprecationWarning,
    stacklevel=2,
)
