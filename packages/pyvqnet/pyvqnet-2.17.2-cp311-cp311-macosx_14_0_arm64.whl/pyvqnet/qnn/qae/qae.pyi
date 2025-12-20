from _typeshed import Incomplete
from pyvqnet.backends import global_backend as global_backend
from pyvqnet.device import DEV_CPU as DEV_CPU
from pyvqnet.native.autograd import Function as Function
from pyvqnet.native.backprop_utils import AutoGradNode as AutoGradNode
from pyvqnet.nn.module import Module as Module, Parameter as Parameter
from pyvqnet.tensor.tensor import QTensor as QTensor, to_tensor as to_tensor

CoreTensor: Incomplete

class qaeFun(Function):
    @staticmethod
    def forward(ctx, x, w, qlayer): ...
    @staticmethod
    def backward(ctx, cgrad_output): ...

class QAElayer(Module):
    '''
    parameterized quantum circuit Layer.It contains paramters can be trained.

    Example::
        from pyvqnet.qnn.qae import QAElayer
        import pyvqnet.tensor as tensor
        import numpy as np

        qaelayer = QAElayer(trash_qubits_number=2, total_qubits_number=7, machine=\'cpu\')
        x = tensor.QTensor(np.random.rand(1, 8))
        output = qaelayer(x)
        print("Output:", output)

    '''
    machine: Incomplete
    qlist: Incomplete
    clist: Incomplete
    history_prob: Incomplete
    n_qubits: Incomplete
    n_aux_qubits: Incomplete
    n_trash_qubits: Incomplete
    weights: Incomplete
    def __init__(self, trash_qubits_number: int = 2, total_qubits_number: int = 7, machine: str = 'cpu') -> None:
        """
        trash_qubits_number: 'int' - should tensor's gradient be tracked, defaults to False
        total_qubits_number: 'int' - Ansatz circuits repeat block times
        machine: 'str' - compute machine
        """
    def forward(self, x):
        """
            forward function
        """

def forward_v2(self, x): ...
def forward_v1(self, x):
    """
        forward function
    """
def SWAP_CIRCUITS(input, param, qubits, n_qubits: int = 7, n_aux_qubits: int = 1, n_trash_qubits: int = 2):
    """
    SWAP_CIRCUITS
    """
def paramterized_quautum_circuits(input: CoreTensor, param: CoreTensor, qubits, clist, n_qubits: int = 7, n_aux_qubits: int = 1, n_trash_qubits: int = 2):
    """
    use qpanda to define circuit

    """
