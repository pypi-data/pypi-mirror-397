from ...tensor.hooks import RemovableHandle as RemovableHandle
from _typeshed import Incomplete
from pyvqnet._core.vqnet.autograd import _Function as CFunction
from typing import Any

CTensor: Incomplete

class _HookMixin: ...

AUTOGRAD_FUNCTION_COUNTER: Incomplete

class FunctionCtx:
    to_save: Incomplete
    def save_for_backward(self, *tensors) -> None:
        """Save given tensors for a future call to :func:`~Function.backward`.

        ``save_for_backward`` should be called at most once, in either the
        :func:`setup_context` or :func:`forward` methods, and only with tensors.

        All tensors intended to be used in the backward pass should be saved
        with ``save_for_backward`` (as opposed to directly on ``ctx``) to prevent
        incorrect gradients and memory leaks, and enable the application of saved
        tensor hooks. See :class:`torch.autograd.graph.saved_tensors_hooks`.

        Note that if intermediary tensors, tensors that are neither inputs
        nor outputs of :func:`forward`, are saved for backward, your custom Function
        may not support double backward.
        Custom Functions that do not support double backward should decorate their
        :func:`backward` method with ``@once_differentiable`` so that performing
        double backward raises an error. If you'd like to support double backward,
        you can either recompute intermediaries based on the inputs during backward
        or return the intermediaries as the outputs of the custom Function. See the
        `double backward tutorial <https://pytorch.org/tutorials/intermediate/custom_function_double_backward_tutorial.html>`_
        for more details.

        In :func:`backward`, saved tensors can be accessed through the :attr:`saved_tensors`
        attribute. Before returning them to the user, a check is made to ensure
        they weren't used in any in-place operation that modified their content.

        Arguments can also be ``None``. This is a no-op.

        See :ref:`extending-autograd` for more details on how to use this method.

        Example::
            >>> # xdoctest: +REQUIRES(env:TORCH_DOCTEST_AUTOGRAD)
            >>> class Func(Function):
            >>>     @staticmethod
            >>>     def forward(ctx, x, y, z: int):
            >>>         w = x * z
            >>>         out = x * y + y * z + w * y
            >>>         ctx.save_for_backward(x, y, w, out)
            >>>         ctx.z = z  # z is not a tensor
            >>>         return out
            >>>
            >>>     @staticmethod
            >>>     @once_differentiable
            >>>     def backward(ctx, grad_out):
            >>>         x, y, w, out = ctx.saved_tensors
            >>>         z = ctx.z
            >>>         gx = grad_out * (y + y * z)
            >>>         gy = grad_out * (x + z + w)
            >>>         gz = None
            >>>         return gx, gy, gz
            >>>
            >>> a = torch.tensor(1., requires_grad=True, dtype=torch.double)
            >>> b = torch.tensor(2., requires_grad=True, dtype=torch.double)
            >>> c = 4
            >>> d = Func.apply(a, b, c)

        """
    non_differentiable: Incomplete
    def mark_non_differentiable(self, *args) -> None:
        """Mark outputs as non-differentiable.

        This should be called at most once, in either the :func:`setup_context`
        or :func:`forward` methods, and all arguments should be tensor outputs.

        This will mark outputs as not requiring gradients, increasing the
        efficiency of backward computation. You still need to accept a gradient
        for each output in :meth:`~Function.backward`, but it's always going to
        be a zero tensor with the same shape as the shape of a corresponding
        output.

        This is used e.g. for indices returned from a sort. See example::
            >>> class Func(Function):
            >>>     @staticmethod
            >>>     def forward(ctx, x):
            >>>         sorted, idx = x.sort()
            >>>         ctx.mark_non_differentiable(idx)
            >>>         ctx.save_for_backward(x, idx)
            >>>         return sorted, idx
            >>>
            >>>     @staticmethod
            >>>     @once_differentiable
            >>>     def backward(ctx, g1, g2):  # still need to accept g2
            >>>         x, idx = ctx.saved_tensors
            >>>         grad_input = torch.zeros_like(x)
            >>>         grad_input.index_add_(0, idx, g1)
            >>>         return grad_input

        """
    materialize_grads: Incomplete
    def set_materialize_grads(self, value: bool):
        """Set whether to materialize grad tensors. Default is ``True``.

        This should be called only from either the :func:`setup_context` or
        :func:`forward` methods.

        If ``True``, undefined grad tensors will be expanded to tensors full of zeros
        prior to calling the :func:`backward` and :func:`jvp` methods.

        Example::
            >>> # xdoctest: +REQUIRES(env:TORCH_DOCTEST_AUTOGRAD)
            >>> class SimpleFunc(Function):
            >>>     @staticmethod
            >>>     def forward(ctx, x):
            >>>         return x.clone(), x.clone()
            >>>
            >>>     @staticmethod
            >>>     @once_differentiable
            >>>     def backward(ctx, g1, g2):
            >>>         return g1 + g2  # No check for None necessary
            >>>
            >>> # We modify SimpleFunc to handle non-materialized grad outputs
            >>> class Func(Function):
            >>>     @staticmethod
            >>>     def forward(ctx, x):
            >>>         ctx.set_materialize_grads(False)
            >>>         ctx.save_for_backward(x)
            >>>         return x.clone(), x.clone()
            >>>
            >>>     @staticmethod
            >>>     @once_differentiable
            >>>     def backward(ctx, g1, g2):
            >>>         x, = ctx.saved_tensors
            >>>         grad_input = torch.zeros_like(x)
            >>>         if g1 is not None:  # We must check for None now
            >>>             grad_input += g1
            >>>         if g2 is not None:
            >>>             grad_input += g2
            >>>         return grad_input
            >>>
            >>> a = torch.tensor(1., requires_grad=True)
            >>> b, _ = Func.apply(a)  # induces g2 to be undefined

        """

class BackwardCFunction(CFunction, FunctionCtx, _HookMixin):
    """
    This class is used for internal autograd work. Do not use.
    """
    def apply(self, *args):
        """
        Apply method used when executing this Node during the backward
        """
    def apply_jvp(self, *args):
        """
        Apply method used when executing forward mode AD during the forward
        """

class FunctionMeta(type):
    """Function metaclass.

    This metaclass sets up the following properties:
        _backward_cls: The Function class corresponding to the differentiated
            version of this function (which is generated on the fly by this
            metaclass).
    """
    def __init__(cls, name, bases, attrs) -> None: ...

class _SingleLevelFunction(CFunction, FunctionCtx, _HookMixin, metaclass=FunctionMeta):
    @staticmethod
    def forward(*args: Any, **kwargs: Any) -> Any:
        """Define the forward of the custom autograd Function.

        This function is to be overridden by all subclasses.
        There are two ways to define forward:

        Usage 1 (Combined forward and ctx)::

            @staticmethod
            def forward(ctx: Any, *args: Any, **kwargs: Any) -> Any:
                pass

        - It must accept a context ctx as the first argument, followed by any
          number of arguments (tensors or other types).
        - See :ref:`combining-forward-context` for more details

        Usage 2 (Separate forward and ctx)::

            @staticmethod
            def forward(*args: Any, **kwargs: Any) -> Any:
                pass

            @staticmethod
            def setup_context(ctx: Any, inputs: Tuple[Any, ...], output: Any) -> None:
                pass

        - The forward no longer accepts a ctx argument.
        - Instead, you must also override the :meth:`torch.autograd.Function.setup_context`
          staticmethod to handle setting up the ``ctx`` object.
          ``output`` is the output of the forward, ``inputs`` are a Tuple of inputs
          to the forward.
        - See :ref:`extending-autograd` for more details

        The context can be used to store arbitrary data that can be then
        retrieved during the backward pass. Tensors should not be stored
        directly on `ctx` (though this is not currently enforced for
        backward compatibility). Instead, tensors should be saved either with
        :func:`ctx.save_for_backward` if they are intended to be used in
        ``backward`` (equivalently, ``vjp``) or :func:`ctx.save_for_forward`
        if they are intended to be used for in ``jvp``.
        """
    @staticmethod
    def backward(ctx: Any, *grad_outputs: Any) -> Any:
        """Define a formula for differentiating the operation with backward mode automatic differentiation.

        This function is to be overridden by all subclasses.
        

        It must accept a context :attr:`ctx` as the first argument, followed by
        as many outputs as the :func:`forward` returned (None will be passed in
        for non tensor outputs of the forward function),
        and it should return as many tensors, as there were inputs to
        :func:`forward`. Each argument is the gradient w.r.t the given output,
        and each returned value should be the gradient w.r.t. the
        corresponding input. If an input is not a Tensor or is a Tensor not
        requiring grads, you can just pass None as a gradient for that input.

        The context can be used to retrieve tensors saved during the forward
        pass. It also has an attribute :attr:`ctx.needs_input_grad` as a tuple
        of booleans representing whether each input needs gradient. E.g.,
        :func:`backward` will have ``ctx.needs_input_grad[0] = True`` if the
        first input to :func:`forward` needs gradient computed w.r.t. the
        output.
        """
    vjp = backward

class Function(_SingleLevelFunction):
    def preprocess(*args): ...
    def __init__(self, *args, **kwargs) -> None: ...
    def __call__(self, *args, **kwargs) -> None: ...
    @classmethod
    def apply(cls, *args, **kwargs): ...
