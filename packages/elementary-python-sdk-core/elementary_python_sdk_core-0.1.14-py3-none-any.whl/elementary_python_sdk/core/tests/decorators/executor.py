"""Common test execution logic for all test decorators."""

import functools
import inspect
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Generic, TypeVar

import pytz
from elementary_python_sdk.core.logger import get_logger
from elementary_python_sdk.core.tests.context import get_active_context
from elementary_python_sdk.core.tests.decorators.base import (
    CommonTestFields,
    TestDecorator,
    TestDecoratorParams,
)
from elementary_python_sdk.core.types.test import TestExecution

logger = get_logger()

T = TypeVar("T")
TParams = TypeVar("TParams", bound=TestDecoratorParams)
TResult = TypeVar("TResult")


@dataclass
class DecoratedFunctionExecution(Generic[TResult]):
    function_result: TResult | Exception
    function_run_time: float
    function_source_code: str | None


def execute_test(
    test_decorator: TestDecorator[TParams, TResult],
    params: TParams,
    common: CommonTestFields,
    result: TResult | Exception,
    argument_calculation_time: float,
    code: str | None = None,
) -> None:
    start_time = datetime.now(pytz.utc)
    context = get_active_context()
    if context is None:
        logger.warning(
            f"No active context for test {common.name}, skipping test recording"
        )
        return

    asset_id = context.asset.id if context.asset else None

    tests = test_decorator.resolve_tests(
        params=params,
        common=common,
        asset_id=asset_id,
    )

    for test in tests:
        context.register_test(test)

    if isinstance(result, Exception):
        for test in tests:
            error_resolver = context.create_error_resolver(
                test=test,
                exception=result,
                description="Test raised exception",
                start_time=start_time,
                code=code,
                quality_dimension=common.quality_dimension,
            )
            context.register_execution_resolver(error_resolver)
    else:

        def execution_resolver() -> list[TestExecution]:
            return test_decorator.resolve_test_results(
                tests=tests,
                params=params,
                result=result,
                start_time=start_time,
                duration_seconds=argument_calculation_time,
                code=code,
                common=common,
            )

        context.register_execution_resolver(execution_resolver)


def _get_function_source(func: Callable) -> str | None:
    """Try to get the source code of a function.

    Args:
        func: Function to get source from

    Returns:
        Source code string or None if not available
    """
    try:
        return inspect.getsource(func)
    except (OSError, TypeError):
        return None


def execute_test_decorator(
    execute_test: Callable[[DecoratedFunctionExecution], None],
    func: Callable[..., T],
    test_name: str,
) -> Callable[..., T]:

    start_time = datetime.now(pytz.utc)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        context = get_active_context()
        if context is None:
            logger.warning(
                f"No active context for test {test_name}, running without recording"
            )
            return func(*args, **kwargs)

        logger.info(f"Starting test: {test_name}")

        code = _get_function_source(func)

        try:
            result = func(*args, **kwargs)
            end_time = datetime.now(pytz.utc)
            argument_calculation_time = (end_time - start_time).total_seconds()

            execute_test(
                DecoratedFunctionExecution(result, argument_calculation_time, code)
            )

            return result

        except Exception as e:
            end_time = datetime.now(pytz.utc)
            argument_calculation_time = (end_time - start_time).total_seconds()

            execute_test(DecoratedFunctionExecution(e, argument_calculation_time, code))

            raise

    return wrapper
