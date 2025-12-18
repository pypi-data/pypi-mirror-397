"""Expected value test decorator implementation."""

from typing import Any, Callable, TypeVar

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

T = TypeVar("T")


class ExpectedValueParams(TestDecoratorParams):
    expected: Any


class ExpectedValueDecorator(SingleResultTestDecorator[ExpectedValueParams, Any]):

    def get_test_type(self) -> TestType:
        return TestType.PYTHON_VALUE

    def validate_result(self, result: Any, params: ExpectedValueParams) -> Any:
        return result

    def build_result(
        self,
        result: Any,
        params: ExpectedValueParams,
        common: CommonTestFields,
    ) -> TestDecoratorResult:
        matches = result == params.expected

        status = TestExecutionStatus.PASS if matches else TestExecutionStatus.FAIL
        failure_count = 0 if matches else 1

        description = (
            f"Value {result} matches expected value {params.expected}"
            if matches
            else f"Value {result} does not match expected value {params.expected}"
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
        return QualityDimension.ACCURACY

    def _params_from_config(self, config: dict) -> ExpectedValueParams:
        return ExpectedValueParams(expected=config.get("expected"))


def execute_expected_value_test(
    name: str,
    expected: Any,
    result: Any | Exception,
    argument_calculation_time: float = 0.0,
    code: str | None = None,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    metadata: dict | None = None,
    column_name: str | None = None,
    quality_dimension: QualityDimension | None = None,
) -> None:

    test_decorator = ExpectedValueDecorator()
    params = ExpectedValueParams(expected=expected)
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


def expected_value(
    name: str,
    expected: Any,
    severity: TestSeverity = TestSeverity.ERROR,
    description: str | None = None,
    metadata: dict | None = None,
    column_name: str | None = None,
    quality_dimension: QualityDimension | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def execute_test(
            decorated_function_execution: DecoratedFunctionExecution,
        ) -> None:
            execute_expected_value_test(
                name=name,
                expected=expected,
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
