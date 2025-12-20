from ...tensor import empty_like as empty_like, split as split
from pyvqnet.distributed import get_rank as get_rank, get_world_size as get_world_size

def ensure_divisibility(numerator, denominator) -> None:
    """Ensure that numerator is divisible by the denominator."""
def divide(numerator, denominator):
    """Ensure that numerator is divisible by the denominator and return
    the division value."""
