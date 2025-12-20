from _typeshed import Incomplete
from pyvqnet.backends import global_backend as global_backend
from pyvqnet.device import DEV_CPU as DEV_CPU
from pyvqnet.native.autograd import Function as Function
from pyvqnet.native.backprop_utils import AutoGradNode as AutoGradNode
from pyvqnet.nn.module import Module as Module
from pyvqnet.nn.parameter import Parameter as Parameter
from pyvqnet.tensor.tensor import QTensor as QTensor, to_tensor as to_tensor

CoreTensor: Incomplete

class qdrlFun(Function):
    @staticmethod
    def forward(ctx, x, w, qlayer): ...
    @staticmethod
    def backward(ctx, cgrad_output): ...

class vmodel(Module):
    """
    vmodel
    """
    delta: Incomplete
    num_layers: Incomplete
    machine: Incomplete
    n_qubits: Incomplete
    params: Incomplete
    last: Incomplete
    def __init__(self, shape, num_layers: int = 3, q_delta: float = 0.0001) -> None: ...
    def forward(self, x):
        """
            forward function
        """

def qdrl_forward_v2(self, x): ...
def qdrl_forward_v1(self, x): ...
def get_grad(g: CoreTensor, x: CoreTensor, params: CoreTensor, forward_circult, delta, machine, nqubits, last):
    """
    get_grad
    """
def qdrl_circuit(input, weights, qlist, clist, machine):
    """
    qdrl_circuit
    """
def build_circult(param, x, n_qubits):
    """
    build_circult
    """
