from ....dtype import kcomplex64 as kcomplex64
from ....nn.torch import TorchModule as TorchModule
from ....tensor import tensor as tensor
from ..qop import QMachine as NQMachine
from pyvqnet.backends_mock import TorchMock as TorchMock

def add_params_infos(self, params) -> None: ...

class QMachine(TorchModule, NQMachine):
    is_torch_qm: bool
    def __init__(self, num_wires: int, dtype: int = ..., grad_mode: str = '', save_ir: bool = False) -> None: ...
    def add_params_infos(self, params): ...
