"""Boolean test decorator implementation."""

from typing import Any, Callable

from elementary_python_sdk.core.tests.decorators.base import (
    CommonTestFields,
    SingleResultTestDecorator,
    TestDecoratorParams,
    TestDecoratorResult,
)
from elementary_python_sdk.core.tests.decorators.executor import (
    DecoratedFunctionExecution,
    execute_test,
    execute_test_decorator,
)
from elementary_python_sdk.core.types.test import (
    QualityDimension,
    TestExecutionStatus,
    TestSeverity,
    TestType,
)

try:
    from numpy import bool_ as numpy_bool

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class BooleanTestParams(TestDecoratorParams):
    pass


class BooleanTestDecorator(SingleResultTestDecorator[BooleanTestParams, bool]):

    def get_test_type(self) -> TestType:
        return TestType.PYTHON_BOOLEAN

    def validate_result(self, result: Any, params: BooleanTestParams) -> bool:
        if isinstance(result, bool):
            return result

        if HAS_NUMPY and isinstance(result, numpy_bool):
            return bool(result)

        raise TypeError(f"Boolean test must return bool, got {type(result).__name__}")

    def build_result(
        self,
        result: bool,
        params: BooleanTestParams,
        common: CommonTestFields,
    ) -> TestDecoratorResult:
        status = TestExecutionStatus.PASS if result else TestExecutionStatus.FAIL
        failure_count = 0 if result else 1

        description = common.description or ""

        return TestDecoratorResult(
            status=status,
            description=description,
            failure_count=failure_count,
        )

    def get_default_quality_dimension(
        self,
        common: CommonTestFields,
    ) -> QualityDimension | None:
        return QualityDimension.VALIDITY if common.column_name else None

    def _params_from_config(self, config: dict) -> BooleanTestParams:
        return BooleanTestParams()


def execute_boolean_test(
    name: str,
    result: bool | Exception,
    argument_calculation_time: float = 0.0,
    code: str | None = None,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    metadata: dict | None = None,
    column_name: str | None = None,
    quality_dimension: QualityDimension | None = None,
) -> None:
    test_decorator = BooleanTestDecorator()
    params = BooleanTestParams()
    common = CommonTestFields(
        name=name,
        description=description,
        metadata=metadata,
        column_name=column_name,
        quality_dimension=quality_dimension,
        severity=severity,
    )

    execute_test(
        test_decorator=test_decorator,
        params=params,
        common=common,
        result=result,
        argument_calculation_time=argument_calculation_time,
        code=code,
    )


def boolean_test(
    name: str,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    metadata: dict | None = None,
    column_name: str | None = None,
    quality_dimension: QualityDimension | None = None,
) -> Callable[[Callable[..., bool]], Callable[..., bool]]:

    def decorator(func: Callable[..., bool]) -> Callable[..., bool]:
        def execute_test(
            decorated_function_execution: DecoratedFunctionExecution,
        ) -> None:
            execute_boolean_test(
                name=name,
                result=decorated_function_execution.function_result,
                argument_calculation_time=decorated_function_execution.function_run_time,
                code=decorated_function_execution.function_source_code,
                severity=severity,
                description=description,
                metadata=metadata,
                column_name=column_name,
                quality_dimension=quality_dimension,
            )

        return execute_test_decorator(execute_test, func, name)

    return decorator
