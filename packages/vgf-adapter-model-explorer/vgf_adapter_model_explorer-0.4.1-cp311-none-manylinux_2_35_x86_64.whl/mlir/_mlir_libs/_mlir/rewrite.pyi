from collections.abc import Callable
from typing import overload

import mlir

import _mlir.ir


class PatternRewriter:
    @property
    def ip(self) -> _mlir.ir.InsertionPoint:
        """The current insertion point of the PatternRewriter."""

    @overload
    def replace_op(self, op: mlir.ir.Operation, new_op: mlir.ir.Operation) -> None:
        """Replace an operation with a new operation."""

    @overload
    def replace_op(self, op: mlir.ir.Operation, values: list[mlir.ir.Value]) -> None:
        """Replace an operation with a list of values."""

    def erase_op(self, op: mlir.ir.Operation) -> None:
        """Erase an operation."""

class RewritePatternSet:
    def __init__(self, context: Context | None = None) -> None: ...

    def add(self, root: object, fn: Callable, benefit: int = 1) -> None:
        """
        Add a new rewrite pattern on the given root operation with the callable as the matching and rewriting function and the given benefit.
        """

    def freeze(self) -> FrozenRewritePatternSet:
        """Freeze the pattern set into a frozen one."""

class PDLResultList:
    @overload
    def append(self, value: mlir.ir.Value): ...

    @overload
    def append(self, op: mlir.ir.Operation): ...

    @overload
    def append(self, type: mlir.ir.Type): ...

    @overload
    def append(self, attr: mlir.ir.Attribute): ...

class PDLModule:
    @overload
    def __init__(self, module: mlir.ir.Module) -> None:
        """Create a PDL module from the given module."""

    @overload
    def __init__(self, module: mlir.ir.Module) -> None: ...

    def freeze(self) -> FrozenRewritePatternSet: ...

    def register_rewrite_function(self, arg0: str, arg1: Callable, /) -> None: ...

    def register_constraint_function(self, arg0: str, arg1: Callable, /) -> None: ...

class FrozenRewritePatternSet:
    @property
    def _CAPIPtr(self) -> object: ...

    def _CAPICreate(self) -> object: ...

@overload
def apply_patterns_and_fold_greedily(module: mlir.ir.Module, set: FrozenRewritePatternSet) -> None:
    """
    Applys the given patterns to the given module greedily while folding results.
    """

@overload
def apply_patterns_and_fold_greedily(module: mlir.ir.Module, set: FrozenRewritePatternSet) -> None:
    """
    Applys the given patterns to the given module greedily while folding results.
    """

@overload
def apply_patterns_and_fold_greedily(op: mlir.ir._OperationBase, set: FrozenRewritePatternSet) -> None:
    """
    Applys the given patterns to the given op greedily while folding results.
    """

@overload
def apply_patterns_and_fold_greedily(op: mlir.ir._OperationBase, set: FrozenRewritePatternSet) -> None:
    """
    Applys the given patterns to the given op greedily while folding results.
    """
