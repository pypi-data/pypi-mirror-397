from typing import Any

import mlir._mlir_libs._mlir.ir
import mlir.ir


def register_python_test_dialect(context: mlir.ir.Context, load: bool = True) -> None: ...

def register_dialect(registry: mlir.ir.DialectRegistry) -> None: ...

def test_diagnostics_with_errors_and_notes(arg: mlir.ir.Context, /) -> None: ...

class TestAttr(mlir._mlir_libs._mlir.ir.Attribute):
    @staticmethod
    def isinstance(other_attribute: mlir.ir.Attribute) -> bool: ...

    def __repr__(self) -> object: ...

    @staticmethod
    def get_static_typeid() -> mlir.ir.TypeID: ...

    @classmethod
    def get(*args, **kwargs) -> Any:
        """get(cls: object, context: mlir.ir.Context | None = None) -> object"""

class TestType(mlir._mlir_libs._mlir.ir.Type):
    @staticmethod
    def isinstance(other_type: mlir.ir.Type) -> bool: ...

    def __repr__(self) -> str: ...

    @staticmethod
    def get_static_typeid() -> mlir.ir.TypeID: ...

    @classmethod
    def get(*args, **kwargs) -> Any:
        """get(cls: object, context: mlir.ir.Context | None = None) -> object"""

class TestIntegerRankedTensorType(mlir._mlir_libs._mlir.ir.RankedTensorType):
    @staticmethod
    def isinstance(other_type: mlir.ir.Type) -> bool: ...

    def __repr__(self) -> str: ...

    @classmethod
    def get(*args, **kwargs) -> Any:
        """
        get(cls: object, shape: collections.abc.Sequence[int], width: int, context: mlir.ir.Context | None = None) -> object
        """

class TestTensorValue(mlir._mlir_libs._mlir.ir.Value):
    @staticmethod
    def isinstance(other_value: mlir.ir.Value) -> bool: ...

    def is_null(self) -> bool: ...
