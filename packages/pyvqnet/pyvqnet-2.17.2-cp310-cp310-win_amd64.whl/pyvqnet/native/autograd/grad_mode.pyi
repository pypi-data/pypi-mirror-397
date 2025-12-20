from _typeshed import Incomplete
from pyvqnet.utils._contextlib import F, _DecoratorContextManager, _NoParamDecoratorContextManager
from typing import Any

__all__ = ['no_grad', 'enable_grad', 'set_grad_enabled']

class no_grad(_NoParamDecoratorContextManager):
    """Context-manager that disables gradient calculation.

    Disabling gradient calculation is useful for inference, when you are sure
    that you will not call :meth:`Tensor.backward()`. It will reduce memory
    consumption for computations that would otherwise have `requires_grad=True`.

    In this mode, the result of every computation will have
    `requires_grad=False`, even when the inputs have `requires_grad=True`.
    There is an exception! All factory functions, or functions that create
    a new Tensor and take a requires_grad kwarg, will NOT be affected by
    this mode.

    This context manager is thread local; it will not affect computation
    in other threads.

    Also functions as a decorator.

    .. note::
        No-grad is one of several mechanisms that can enable or
        disable gradients locally see :ref:`locally-disable-grad-doc` for
        more information on how they compare.


        If you want to disable forward AD for a computation, you can unpack
        your dual tensors.


    """
    prev: bool
    def __init__(self) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None: ...

class enable_grad(_NoParamDecoratorContextManager):
    """Context-manager that enables gradient calculation.

    Enables gradient calculation, if it has been disabled via :class:`~no_grad`
    or :class:`~set_grad_enabled`.

    This context manager is thread local; it will not affect computation
    in other threads.

    Also functions as a decorator.

    .. note::
        enable_grad is one of several mechanisms that can enable or
        disable gradients locally see :ref:`locally-disable-grad-doc` for
        more information on how they compare.





    """
    prev: Incomplete
    def __enter__(self) -> None: ...
    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None: ...

class set_grad_enabled(_DecoratorContextManager):
    """Context-manager that sets gradient calculation on or off.

    ``set_grad_enabled`` will enable or disable grads based on its argument :attr:`mode`.
    It can be used as a context-manager or as a function.

    This context manager is thread local; it will not affect computation
    in other threads.

    Args:
        mode (bool): Flag whether to enable grad (``True``), or disable
                     (``False``). This can be used to conditionally enable
                     gradients.

    .. note::
        set_grad_enabled is one of several mechanisms that can enable or
        disable gradients locally see :ref:`locally-disable-grad-doc` for
        more information on how they compare.





    """
    prev: Incomplete
    mode: Incomplete
    def __init__(self, mode: bool) -> None: ...
    def __call__(self, orig_func: F) -> F: ...
    def __enter__(self) -> None: ...
    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None: ...
    def clone(self) -> set_grad_enabled:
        """
        Create a copy of this class
        """
