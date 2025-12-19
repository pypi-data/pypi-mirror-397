"""
Dynamic factory that composes a Provider from three modules.

Required modules
----------------
- chain        → <root>.chains.<chain>
- rpc          → <root>.rpcs.<rpc>
- aggregator   → <root>.aggregators.<aggregator>
"""

from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import Any, Dict, Optional, Type

def _imp(relpath: str) -> ModuleType:
    """
    Import *relative to* this package
    """
    return import_module(relpath, __package__)

def _import_provider_module() -> ModuleType:               return _imp("..provider.provider")

def _import_chain_module(chain: str) -> ModuleType:        return _imp(f"..chains.{chain}")
def _import_rpc_module(rpc: str) -> ModuleType:            return _imp(f"..rpcs.{rpc}")
def _import_aggregator_module(agg: str) -> ModuleType:     return _imp(f"..aggregators.{agg}")

def _require_named_class(mod: ModuleType, name: str) -> Type[Any]:
    cls = getattr(mod, name, None)

    if not isinstance(cls, type):
        raise ImportError(f"{mod.__name__} must define class '{name}'")

    return cls

def get_provider(
    chain: str,
    rpc: str,
    aggregator: str,
    *,
    chain_params: Optional[Dict[str, Any]] = None,
    rpc_params: Optional[Dict[str, Any]] = None,
    aggregator_params: Optional[Dict[str, Any]] = None,
):
    """
    Composes provider instance.

    Required modules:
      • <root>.chains.<chain>
      • <root>.rpcs.<rpc>
      • <root>.aggregators.<aggregator>
    """
    if not chain:
        raise ValueError("chain module name is required")
    if not rpc:
        raise ValueError("rpc module name is required")
    if not aggregator:
        raise ValueError("aggregator module name is required")

    # Resolve configuration dictionaries, avoiding shared mutable defaults
    chain_params = chain_params or {}
    rpc_params = rpc_params or {}
    aggregator_params = aggregator_params or {}

    # Load classes
    provider_mod  = _import_provider_module()
    ProviderCls   = _require_named_class(provider_mod, "Provider")

    chain_mod     = _import_chain_module(chain)
    ChainCls      = _require_named_class(chain_mod, "Chain")
    chain_obj     = ChainCls(**chain_params)

    rpc_mod       = _import_rpc_module(rpc)
    RPCCls        = _require_named_class(rpc_mod, "RPC")
    rpc_obj       = RPCCls(**rpc_params)

    agg_mod       = _import_aggregator_module(aggregator)
    AggregatorCls = _require_named_class(agg_mod, "Aggregator")
    agg_obj       = AggregatorCls(**aggregator_params)

    # Compose
    return ProviderCls(chain=chain_obj, rpc=rpc_obj, aggregator=agg_obj)
