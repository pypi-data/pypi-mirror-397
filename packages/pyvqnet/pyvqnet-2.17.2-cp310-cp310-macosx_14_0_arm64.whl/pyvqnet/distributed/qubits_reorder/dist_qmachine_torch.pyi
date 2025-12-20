from ...qnn.vqc.torch.qmachine import add_params_infos as add_params_infos
from .dist_qmachine import DistributeQMachine as NDistributeQMachine, QubitReorderLocalQmachine as NQubitReorderLocalQmachine
from pyvqnet import kcomplex64 as kcomplex64, tensor as tensor
from pyvqnet.qnn.vqc.torch.qmachine import QMachine as TorchQMachine, TorchModule as TorchModule

class TorchQubitReorderLocalQmachine(TorchQMachine, NQubitReorderLocalQmachine):
    def __init__(self, q_machine) -> None: ...

class TorchDistributeQMachine(TorchModule, NDistributeQMachine):
    def __init__(self, num_wires, dtype=..., grad_mode: str = '') -> None: ...
    def add_params_infos(self, params): ...
