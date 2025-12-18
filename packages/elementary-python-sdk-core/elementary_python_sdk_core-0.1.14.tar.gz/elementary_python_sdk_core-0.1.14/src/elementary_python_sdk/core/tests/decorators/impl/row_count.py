"""Row count test decorator implementation."""

from collections.abc import Sized
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


class RowCountParams(TestDecoratorParams):
    min: int | None = None
    max: int | None = None


class RowCountDecorator(SingleResultTestDecorator[RowCountParams, Sized]):

    def get_test_type(self) -> TestType:
        return TestType.PYTHON_ROW_COUNT

    def validate_result(self, result: Any, params: RowCountParams) -> Sized:
        if not isinstance(result, Sized):
            raise TypeError(
                f"Row count test must return a Sized object (with __len__), "
                f"got {type(result).__name__}"
            )
        return result

    def build_result(
        self,
        result: Sized,
        params: RowCountParams,
        common: CommonTestFields,
    ) -> TestDecoratorResult:
        count = len(result)
        in_range = (params.min is None or count >= params.min) and (
            params.max is None or count <= params.max
        )

        status = TestExecutionStatus.PASS if in_range else TestExecutionStatus.FAIL
        failure_count = 0 if in_range else 1

        range_str = f"[{params.min if params.min is not None else 0}, {params.max if params.max is not None else float('inf')}]"
        description = (
            f"Row count {count} is within expected range {range_str}"
            if in_range
            else f"Row count {count} is outside expected range {range_str}"
        )

        return TestDecoratorResult(
            status=status,
            description=description,
            failure_count=failure_count,
        )

    def get_default_quality_dimension(
        self,
        common: CommonTestFields,
    ) -> QualityDimension | None:
        return QualityDimension.COMPLETENESS

    def _params_from_config(self, config: dict) -> RowCountParams:
        return RowCountParams(
            min=config.get("min"),
            max=config.get("max"),
        )


def execute_row_count_test(
    name: str,
    result: Sized | Exception,
    min: int | None = None,
    max: int | None = None,
    argument_calculation_time: float = 0.0,
    code: str | None = None,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    metadata: dict | None = None,
) -> None:

    test_decorator = RowCountDecorator()
    params = RowCountParams(min=min, max=max)
    common = CommonTestFields(
        name=name,
        description=description,
        metadata=metadata,
        column_name=None,
        quality_dimension=QualityDimension.COMPLETENESS,
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


def row_count(
    name: str,
    min: int | None = None,
    max: int | None = None,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    metadata: dict | None = None,
) -> Callable[[Callable[..., Sized]], Callable[..., Sized]]:

    def decorator(func: Callable[..., Sized]) -> Callable[..., Sized]:
        def execute_test(
            decorated_function_execution: DecoratedFunctionExecution,
        ) -> None:
            execute_row_count_test(
                name=name,
                result=decorated_function_execution.function_result,
                min=min,
                max=max,
                argument_calculation_time=decorated_function_execution.function_run_time,
                code=decorated_function_execution.function_source_code,
                severity=severity,
                description=description,
                metadata=metadata,
            )

        return execute_test_decorator(execute_test, func, name)

    return decorator
