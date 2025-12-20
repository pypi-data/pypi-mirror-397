from ... import nn as nn, tensor as tensor
from ...backends import global_backend as global_backend
from ...config import get_if_grad_enabled as get_if_grad_enabled
from ...dtype import complex_dtype_to_float_dtype as complex_dtype_to_float_dtype
from ...qnn.vqc import QModule as QModule, op_history_to_list as op_history_to_list, operation_derivative as operation_derivative
from ...qnn.vqc.adjoint_grad import AdjointRunningScope as AdjointRunningScope, adjoint_grad_node_gen as adjoint_grad_node_gen, apply_operation as apply_operation, get_multi_output_obs_num as get_multi_output_obs_num, qadjointFunction as qadjointFunction, reduce_sum_real_jac as reduce_sum_real_jac
from ...qnn.vqc.qmeasure.utils import maybe_parse_obs as maybe_parse_obs, ob_class_parse as ob_class_parse
from ...qnn.vqc.qop import Observable as Observable
from ...qnn.vqc.utils.utils import apply_gate_operation_impl as apply_gate_operation_impl
from ...tensor import QTensor as QTensor, no_grad as no_grad, to_tensor as to_tensor
from ..ControlComm import get_world_size as get_world_size
from .dist_qmachine import DistributeQMachine as DistributeQMachine
from .dist_qmachine_torch import TorchModule as TorchModule
from .dist_vqc import DistQuantumLayerAdjoint as DistQuantumLayerAdjoint, adjoint_grad_calc as adjoint_grad_calc, check_if_need_qr as check_if_need_qr, dist_single_paulisum_exp as dist_single_paulisum_exp, find_dist_qmachine as find_dist_qmachine, measure_all_for_qr as measure_all_for_qr, update_all_qubit_obs_bras as update_all_qubit_obs_bras
from .swap_qubits import compute_qubit_mapping as compute_qubit_mapping, compute_qubit_remapping as compute_qubit_remapping, get_global_CommController_for_qr as get_global_CommController_for_qr
from .utils import construct_measure_obs_for_qr as construct_measure_obs_for_qr, exec_states_qr as exec_states_qr
from pyvqnet.device import DEV_GPU as DEV_GPU

class TorchDistQuantumLayerAdjoint(TorchModule, DistQuantumLayerAdjoint):
    def __init__(self, vqc_module: nn.Module, name: str = '') -> None: ...
    def get_q_machine(self, vqc_module): ...
    def forward(self, x, *args, **kwargs): ...
