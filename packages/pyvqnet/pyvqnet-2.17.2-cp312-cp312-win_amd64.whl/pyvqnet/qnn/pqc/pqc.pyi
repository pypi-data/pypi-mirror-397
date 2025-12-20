from _typeshed import Incomplete
from pyvqnet.backends import global_backend as global_backend
from pyvqnet.device import DEV_CPU as DEV_CPU
from pyvqnet.native.autograd import Function as Function
from pyvqnet.native.backprop_utils import AutoGradNode as AutoGradNode
from pyvqnet.nn.module import Module as Module, Parameter as Parameter
from pyvqnet.tensor.tensor import QTensor as QTensor, to_tensor as to_tensor
from pyvqnet.utils.initializer import zeros as zeros

CoreTensor: Incomplete

class pqcFun(Function):
    @staticmethod
    def forward(ctx, x, w, qlayer): ...
    @staticmethod
    def backward(ctx, cgrad_output): ...

class PQCLayer(Module):
    '''
    parameterized quantum circuit Layer.It contains paramters can be trained.

    Example::
        from pyvqnet.qnn.pqc import PQCLayer
        import pyvqnet.tensor as tensor
        import numpy as np
        pqlayer = PQCLayer(machine="cpu", quantum_number=4, rep=3, measure_qubits="Z0 Z1")

        x = tensor.QTensor(np.random.rand(1, 8))

        output = pqlayer(x)

        print("Output:", output)

    '''
    machine: Incomplete
    qlist: Incomplete
    history_expectation: Incomplete
    weights: Incomplete
    measure_qubits: Incomplete
    def __init__(self, machine: str = 'cpu', quantum_number: int = 4, rep: int = 3, measure_qubits: str = 'Z0 Z1') -> None:
        """
        machine: 'str' - compute machine
        quantum_number: 'int' - should tensor's gradient be tracked, defaults to False
        rep: 'int' - Ansatz circuits repeat block times
        measure_qubits: 'str' - measure qubits
        """
    def forward(self, x):
        """
            forward function
        """

def pqc_forward_v2(self, x): ...
def pqc_forward_v1(self, x): ...
def cnot_rz_rep_cir(qubits, param, rep: int = 3):
    """
    cnot_rz_rep_cir
    """
def paramterized_quautum_circuits(input: CoreTensor, param: CoreTensor, qubits, rep: int):
    """
    use qpanda to define circuit

    """
def Hamiltonian(input: str):
    '''
        Interchange two axes of an array.

        :param input: expect measure qubits.
        :return: hamiltion operator

        Examples::
        Hamiltonian("Z0 Z1" )
    '''
