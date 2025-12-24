"""Public exports for the AIE intermediate representation."""

from .context import (
    AIEBackendContext,
    BackendPolicies,
    DeviceSpec,
    TraitDefinition,
    TraitRegistry,
    ensure_backend_context,
    get_backend_context,
)
from .graph import LogicalIR, OpNode, ResolvedAttributes, TensorVar, TraitInstance

__all__ = [
    'AIEBackendContext',
    'LogicalIR',
    'OpNode',
    'TensorVar',
    'BackendPolicies',
    'DeviceSpec',
    'ResolvedAttributes',
    'TraitDefinition',
    'TraitInstance',
    'TraitRegistry',
    'ensure_backend_context',
    'get_backend_context',
]
