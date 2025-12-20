from .backends import global_backend as global_backend
from _typeshed import Incomplete
from functools import lru_cache as _lru_cache

if_show_bp_info: bool
is_dist_init: bool
DIST_DOT_THR: Incomplete

def set_dist_dot_thr(num) -> None:
    """
    this global var controls the way to run dot_product_real in DistQuantumLayerAdjoint.
    if batchsize * len(obs) * numel(statevectors) is larger than this threshold,
    we will use a method requires less memory, otherwise we will use a more quickly method.
    """
def get_dist_dot_thr():
    """
    this global var controls the way to run dot_product_real in DistQuantumLayerAdjoint.
    if batchsize * len(obs) * numel(statevectors) is larger than this threshold,
    we will use a method requires less memory, otherwise we will use a more quickly method.
    """
def get_is_dist_init():
    """
    global flag if vqnet distributed is initialed.

    """
def set_is_dist_init(flag) -> None:
    """
    set global flag if vqnet distributed is initialed.
    
    """
def get_if_grad_enabled():
    """
    get if_grad_enabled based on backend
    """
def set_if_grad_enabled(flag) -> None:
    """
    set value of if_grad_enabled
    """
def get_if_show_bp_info():
    """
    get flag of if_show_bp_info
    """
def set_if_show_bp_info(flag) -> None:
    """
    set flag of if_show_bp_info
    """
def init_if_show_bp() -> None:
    """
    init flag of if_show_bp_info to False
    """
@_lru_cache
def is_opt_einsum_available() -> bool:
    """Return a bool indicating if opt_einsum is currently available."""
