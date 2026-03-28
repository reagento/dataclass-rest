from warnings import warn

from .transformers.request import *  # noqa: F403, compat

warn(
    "Use `import descanso.transformers.request` instead",
    DeprecationWarning,
    stacklevel=2,
)
