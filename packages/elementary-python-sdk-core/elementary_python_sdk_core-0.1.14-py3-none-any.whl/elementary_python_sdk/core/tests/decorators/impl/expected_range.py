"""Expected range test decorator implementation."""

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


class ExpectedRangeParams(TestDecoratorParams):
    min: float | None = None
    max: float | None = None


class ExpectedRangeDecorator(SingleResultTestDecorator[ExpectedRangeParams, float]):

    def get_test_type(self) -> TestType:
        return TestType.PYTHON_RANGE

    def validate_result(self, result: Any, params: ExpectedRangeParams) -> float:
        try:
            return float(result)
        except (TypeError, ValueError):
            raise TypeError(
                f"Range test must return numeric value, got {type(result).__name__}"
            )

    def build_result(
        self,
        result: float,
        params: ExpectedRangeParams,
        common: CommonTestFields,
    ) -> TestDecoratorResult:

        in_range = (params.min is None or result >= params.min) and (
            params.max is None or result <= params.max
        )

        status = TestExecutionStatus.PASS if in_range else TestExecutionStatus.FAIL
        failure_count = 0 if in_range else 1

        range_str = f"[{params.min if params.min is not None else '-∞'}, {params.max if params.max is not None else '∞'}]"
        description = (
            f"Value {result} is within expected range {range_str}"
            if in_range
            else f"Value {result} is outside expected range {range_str}"
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
        return QualityDimension.VALIDITY

    def _params_from_config(self, config: dict) -> ExpectedRangeParams:
        return ExpectedRangeParams(
            min=config.get("min"),
            max=config.get("max"),
        )


def execute_expected_range_test(
    name: str,
    result: float | Exception,
    min: float | None = None,
    max: float | None = None,
    argument_calculation_time: float = 0.0,
    code: str | None = None,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    metadata: dict | None = None,
    column_name: str | None = None,
    quality_dimension: QualityDimension | None = None,
) -> None:

    test_decorator = ExpectedRangeDecorator()
    params = ExpectedRangeParams(min=min, max=max)
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


def expected_range(
    name: str,
    min: float | None = None,
    max: float | None = None,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    metadata: dict | None = None,
    column_name: str | None = None,
    quality_dimension: QualityDimension | None = None,
) -> Callable[[Callable[..., float]], Callable[..., float]]:

    def decorator(func: Callable[..., float]) -> Callable[..., float]:
        def execute_test(
            decorated_function_execution: DecoratedFunctionExecution,
        ) -> None:
            execute_expected_range_test(
                name=name,
                result=decorated_function_execution.function_result,
                min=min,
                max=max,
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
