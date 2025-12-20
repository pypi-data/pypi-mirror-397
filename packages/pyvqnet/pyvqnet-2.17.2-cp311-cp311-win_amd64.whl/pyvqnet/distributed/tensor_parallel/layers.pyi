import pyvqnet
from ...tensor import QTensor as QTensor, to_tensor as to_tensor
from .utils import divide as divide
from _typeshed import Incomplete
from pyvqnet import tensor as tensor
from pyvqnet.backends import global_backend as global_backend
from pyvqnet.distributed import CommController as CommController, get_rank as get_rank, get_world_size as get_world_size
from pyvqnet.native.autograd import Function as Function
from pyvqnet.native.backprop_utils import AutoGradNode as AutoGradNode
from pyvqnet.nn.parameter import Parameter as Parameter
from pyvqnet.utils.initializer import zeros as zeros
from typing import Callable

CoreTensor: Incomplete

class RowParallelLinear(pyvqnet.nn.Module):
    '''Linear layer with row parallelism.

        Linear layer with row parallelism.

        The linear layer is defined as Y = XA + b. A is parallelized along its first dimension and X along its second dimension. 
        A = transpose([A_1 .. A_p]) X = [X_1, …, X_p]

        :param input_size: first dimension of matrix A.
        :param output_size: second dimension of matrix A.
        :param weight_initializer: `callable` - defaults to normal.
        :param bias_initializer: `callable` - defaults to zeros.
        :param use_bias: `bool` - defaults to True.
        :param dtype: default: None,use default data type.
        :param name: name of module,default:"".
        :param tp_comm: Comm Controller.
        
    Example::
    
        import pyvqnet

        from pyvqnet.distributed.tensor_parallel import ColumnParallelLinear, RowParallelLinear
        from pyvqnet.distributed import CommController
        from pyvqnet.device import DEV_GPU

        import pyvqnet

        pyvqnet.utils.set_random_seed(42)

        Comm_OP = CommController("nccl")

        fc1 = RowParallelLinear(8, 6, tp_comm = Comm_OP)

        z = pyvqnet.tensor.ones([2,8],device=Comm_OP.get_rank()+DEV_GPU)
        z.requires_grad = True

        fc1 = fc1.to(Comm_OP.get_rank()+DEV_GPU)

        y = fc1(z)

        y.backward()

        
    '''
    input_size: Incomplete
    output_size: Incomplete
    weight_initializer: Incomplete
    use_bias: Incomplete
    tp_comm: Incomplete
    gather_output: Incomplete
    output_size_per_partition: Incomplete
    weights: Incomplete
    bias: Incomplete
    def __init__(self, input_size, output_size, weight_initializer: Callable | None = None, bias_initializer: Callable | None = None, use_bias: bool = True, dtype: int | None = None, name: str = '', tp_comm: CommController = None) -> None: ...
    def forward(self, input: pyvqnet.tensor.QTensor): ...

class rplFun(Function):
    @staticmethod
    def forward(ctx, qlayer, *tensors): ...
    @staticmethod
    def backward(ctx, cgrad_output): ...

def rpl_fw_v2(self, x): ...
def rpl_linear_backward(self, weight, bias, data, g, dim): ...
def rpl_fw_v1(self, input: QTensor): ...

class ColumnParallelLinear(pyvqnet.nn.Module):
    '''Linear layer with column parallelism.

        The linear layer is defined as Y = XA + b. A is parallelized along its second dimension as A = [A_1, …, A_p].


        :param input_size: first dimension of matrix A.
        :param output_size: second dimension of matrix A.
        :param weight_initializer: `callable` - defaults to normal.
        :param bias_initializer: `callable` - defaults to zeros.
        :param use_bias: `bool` - defaults to True.
        :param dtype: default: None,use default data type.
        :param name: name of module,default:"".
        :param tp_comm: Comm Controller.

    Example::

        import pyvqnet

        from pyvqnet.distributed.tensor_parallel import ColumnParallelLinear, RowParallelLinear
        from pyvqnet.distributed import CommController
        from pyvqnet.device import DEV_GPU

        import pyvqnet

        pyvqnet.utils.set_random_seed(42)

        Comm_OP = CommController("nccl")

        fc1 = ColumnParallelLinear(8, 6, tp_comm = Comm_OP)

        z = pyvqnet.tensor.ones([2,8],device=Comm_OP.get_rank()+DEV_GPU)
        z.requires_grad = True

        fc1 = fc1.to(Comm_OP.get_rank()+DEV_GPU)

        y = fc1(z)

        y.backward()


    '''
    input_size: Incomplete
    output_size: Incomplete
    gather_output: Incomplete
    use_bias: Incomplete
    tp_comm: Incomplete
    input_size_per_partition: Incomplete
    weights: Incomplete
    bias: Incomplete
    def __init__(self, input_size, output_size, weight_initializer: Callable | None = None, bias_initializer: Callable | None = None, use_bias: bool = True, dtype: int | None = None, name: str = '', tp_comm: CommController = None) -> None: ...
    def forward(self, input: pyvqnet.tensor.QTensor): ...

class cplFun(Function):
    @staticmethod
    def forward(ctx, qlayer, *tensors): ...
    @staticmethod
    def backward(ctx, cgrad_output): ...

def cpl_fw_v2(self, x): ...
def cpl_linear_backward(self, weights, bias, input_parallel, g, dim): ...
def cpl_fw_v1(self, input_: QTensor): ...
