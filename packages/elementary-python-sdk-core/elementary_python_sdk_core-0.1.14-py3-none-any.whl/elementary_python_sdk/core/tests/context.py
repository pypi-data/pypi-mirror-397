import traceback
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Callable, Generator, TypeVar

import pytz
from elementary_python_sdk.core.cloud.request import ElementaryObject
from elementary_python_sdk.core.logger import get_logger
from elementary_python_sdk.core.test_context import TestContext
from elementary_python_sdk.core.types.asset import TableAsset
from elementary_python_sdk.core.types.test import (
    QualityDimension,
    Test,
    TestExecution,
    TestExecutionStatus,
    TestSeverity,
)

logger = get_logger()


class ElementaryTestContext(TestContext):

    def __init__(self, asset: TableAsset | None = None):
        self.asset = asset
        self.tests: dict[str, Test] = {}
        self._execution_resolvers: list[Callable[[], list[TestExecution]]] = []
        self.context_start_time = datetime.now(pytz.utc)

    def register_test(self, test: Test) -> None:
        self.tests[test.name] = test
        logger.debug(f"Registered test: {test.name}")

    def register_execution_resolver(
        self, resolver: Callable[[], list[TestExecution]]
    ) -> None:
        self._execution_resolvers.append(resolver)
        logger.debug(
            f"Registered execution resolver (total: {len(self._execution_resolvers)})"
        )

    def create_error_resolver(
        self,
        test: Test,
        exception: Exception,
        description: str,
        start_time: datetime | None = None,
        code: str | None = None,
        quality_dimension: QualityDimension | None = None,
    ) -> Callable[[], list[TestExecution]]:
        if start_time is None:
            start_time = self.context_start_time

        traceback_str = traceback.format_exc()

        def error_resolver() -> list[TestExecution]:
            return [
                TestExecution(
                    test_id=test.id,
                    test_sub_unique_id=test.id,
                    sub_type=test.test_type.value,
                    failure_count=0,
                    status=TestExecutionStatus.ERROR,
                    code=code,
                    start_time=start_time,
                    duration_seconds=(
                        datetime.now(pytz.utc) - start_time
                    ).total_seconds(),
                    exception=str(exception),
                    traceback=traceback_str,
                    description=description,
                    column_name=test.column_name,
                    quality_dimension=quality_dimension,
                )
            ]

        return error_resolver

    def log_test_completion(
        self,
        test_name: str,
        execution: TestExecution,
    ) -> None:
        log_msg = f"Test '{test_name}' completed: {execution.status.value} (duration: {execution.duration_seconds:.3f}s)"
        if execution.status == TestExecutionStatus.PASS:
            logger.info(log_msg)
        elif execution.status == TestExecutionStatus.WARN:
            logger.warning(log_msg)
        elif execution.status == TestExecutionStatus.FAIL:
            logger.error(f"{log_msg} - {execution.description}")
        elif execution.status == TestExecutionStatus.ERROR:
            logger.error(f"{log_msg} - {execution.description}")
            if execution.exception:
                logger.error(f"Exception: {execution.exception}")
        else:
            logger.info(log_msg)

    def record_exception_results(self, exception: Exception) -> None:
        for test in self.tests.values():
            error_resolver = self.create_error_resolver(
                test=test,
                exception=exception,
                description="Test context failed with exception",
            )
            self.register_execution_resolver(error_resolver)

    def get_elementary_objects(self) -> list[ElementaryObject]:
        objects: list[ElementaryObject] = []

        if self.asset:
            objects.append(self.asset)

        objects.extend(list(self.tests.values()))

        all_executions: list[TestExecution] = []

        for resolver in self._execution_resolvers:
            try:
                executions = resolver()
                objects.extend(executions)
                all_executions.extend(executions)

                for execution in executions:
                    test_name = next(
                        (
                            name
                            for name, test in self.tests.items()
                            if test.id == execution.test_id
                        ),
                        "unknown",
                    )
                    self.log_test_completion(test_name, execution)

            except Exception as e:
                logger.error(f"Error resolving test executions: {e}")

                for test in self.tests.values():
                    error_executions = self.create_error_resolver(
                        test=test,
                        exception=e,
                        description="Failed to resolve test execution",
                    )()
                    objects.extend(error_executions)
                    all_executions.extend(error_executions)

                    for error_execution in error_executions:
                        self.log_test_completion(test.name, error_execution)

        self._log_context_summary(all_executions)

        return objects

    def _inner_test_context(
        self,
        test_execution_callback: Callable[[Any], None],
        raise_on_error: bool = False,
    ) -> Generator["InnerTestContext", None, None]:
        inner_context = InnerTestContext(test_execution_callback, asset=self.asset)

        try:
            yield from _elementary_test_context(
                inner_context, raise_on_error=raise_on_error
            )
        finally:
            for test_name, test in inner_context.tests.items():
                self.tests[test_name] = test

            for resolver in inner_context._execution_resolvers:
                self._execution_resolvers.append(resolver)

    @contextmanager
    def boolean_test(
        self,
        name: str,
        severity: TestSeverity = TestSeverity.ERROR,
        description: str | None = None,
        metadata: dict | None = None,
        column_name: str | None = None,
        quality_dimension: QualityDimension | None = None,
    ) -> Generator["InnerTestContext", None, None]:
        from elementary_python_sdk.core.tests.decorators.impl import (
            execute_boolean_test,
        )

        def execute_test(value: Any) -> None:
            execute_boolean_test(
                name=name,
                result=value,
                severity=severity,
                description=description,
                metadata=metadata,
                column_name=column_name,
                quality_dimension=quality_dimension,
            )

        yield from self._inner_test_context(execute_test)

    @contextmanager
    def expected_range_test(
        self,
        name: str,
        min: float | None = None,
        max: float | None = None,
        severity: TestSeverity = TestSeverity.ERROR,
        description: str | None = None,
        metadata: dict | None = None,
        column_name: str | None = None,
        quality_dimension: QualityDimension | None = None,
    ) -> Generator["InnerTestContext", None, None]:
        from elementary_python_sdk.core.tests.decorators.impl import (
            execute_expected_range_test,
        )

        def execute_test(value: Any) -> None:
            execute_expected_range_test(
                name=name,
                min=min,
                max=max,
                result=value,
                severity=severity,
                description=description,
                metadata=metadata,
                column_name=column_name,
                quality_dimension=quality_dimension,
            )

        yield from self._inner_test_context(execute_test)

    @contextmanager
    def expected_value_test(
        self,
        name: str,
        expected: Any,
        code: str | None = None,
        severity: TestSeverity = TestSeverity.ERROR,
        description: str | None = None,
        metadata: dict | None = None,
        column_name: str | None = None,
        quality_dimension: QualityDimension | None = None,
    ) -> Generator["InnerTestContext", None, None]:
        from elementary_python_sdk.core.tests.decorators.impl import (
            execute_expected_value_test,
        )

        def execute_test(value: Any) -> None:
            execute_expected_value_test(
                name=name,
                expected=expected,
                result=value,
                code=code,
                severity=severity,
                description=description,
                metadata=metadata,
                column_name=column_name,
                quality_dimension=quality_dimension,
            )

        yield from self._inner_test_context(execute_test)

    @contextmanager
    def row_count_test(
        self,
        name: str,
        min: int | None = None,
        max: int | None = None,
        severity: TestSeverity = TestSeverity.ERROR,
        description: str | None = None,
        metadata: dict | None = None,
    ) -> Generator["InnerTestContext", None, None]:
        from elementary_python_sdk.core.tests.decorators.impl import (
            execute_row_count_test,
        )

        def execute_test(value: Any) -> None:
            execute_row_count_test(
                name=name,
                min=min,
                max=max,
                result=value,
                severity=severity,
                description=description,
                metadata=metadata,
            )

        yield from self._inner_test_context(execute_test)

    def _log_context_summary(self, executions: list[TestExecution]) -> None:
        total_tests = len(executions)

        if total_tests == 0:
            logger.info("Test context completed with no tests executed")
            return

        status_counts: dict[TestExecutionStatus, int] = {}
        failed_tests = []
        warned_tests = []
        errored_tests = []

        for execution in executions:
            test_name = next(
                (
                    name
                    for name, test in self.tests.items()
                    if test.id == execution.test_id
                ),
                "unknown",
            )
            status_counts[execution.status] = status_counts.get(execution.status, 0) + 1

            if execution.status == TestExecutionStatus.FAIL:
                failed_tests.append(test_name)
            elif execution.status == TestExecutionStatus.WARN:
                warned_tests.append(test_name)
            elif execution.status == TestExecutionStatus.ERROR:
                errored_tests.append(test_name)

        logger.info("=" * 60)
        logger.info("Test Context Summary")
        logger.info("=" * 60)

        if self.asset:
            if isinstance(self.asset, TableAsset):
                logger.info(f"Asset: {self.asset.fqn}")
            else:
                logger.info(f"Asset: {self.asset.name}")

        logger.info(f"Total tests executed: {total_tests}")
        for status, count in sorted(status_counts.items()):
            logger.info(f"  {status}: {count}")

        if errored_tests:
            logger.error(f"Tests with errors ({len(errored_tests)}):")
            for test_name in errored_tests:
                logger.error(f"  - {test_name}")

        if failed_tests:
            logger.error(f"Failed tests ({len(failed_tests)}):")
            for test_name in failed_tests:
                logger.error(f"  - {test_name}")

        if warned_tests:
            logger.warning(f"Tests with warnings ({len(warned_tests)}):")
            for test_name in warned_tests:
                logger.warning(f"  - {test_name}")

        logger.info("=" * 60)


class InnerTestContext(ElementaryTestContext):
    def __init__(
        self,
        test_execution_callback: Callable[[Any], None],
        asset: TableAsset | None = None,
    ):
        self.test_execution_callback = test_execution_callback
        super().__init__(asset=asset)

    def register_test(self, test: Test) -> None:
        if len(self.tests) > 0:
            raise ValueError("InnerTestContext can only register one test")
        super().register_test(test)

    def register_execution_resolver(
        self, resolver: Callable[[], list[TestExecution]]
    ) -> None:
        if len(self._execution_resolvers) > 0:
            raise ValueError(
                "InnerTestContext can only register one execution resolver"
            )
        super().register_execution_resolver(resolver)

    def assert_value(self, value: Any) -> None:
        self.test_execution_callback(value)


def log_context_initialization(test_context: ElementaryTestContext) -> None:
    if test_context.asset:
        if isinstance(test_context.asset, TableAsset):
            logger.info(f"Starting test context for asset: {test_context.asset.fqn}")
        else:
            logger.info(f"Starting test context for asset: {test_context.asset.name}")
    else:
        logger.info("Starting test context without asset")


TestContextType = TypeVar("TestContextType", bound=ElementaryTestContext)


def _elementary_test_context(
    test_context: TestContextType,
    raise_on_error: bool = False,
) -> Generator[TestContextType, None, None]:
    previous_context = get_active_context()
    set_active_context(test_context)
    try:
        yield test_context
    except Exception as e:
        logger.exception(f"Error in elementary test context: {e}")
        test_context.record_exception_results(e)
        if raise_on_error:
            raise
    finally:
        set_active_context(previous_context)


@contextmanager
def elementary_test_context(
    asset: TableAsset | None = None, raise_on_error: bool = False
) -> Generator[ElementaryTestContext, None, None]:
    """Context manager for elementary tests.

    Args:
        asset: Optional asset that tests are running against

    Yields:
        ElementaryTestContext instance

    Example:
        ```python
        with elementary_test_context(asset=my_asset) as ctx:
            result = check_data(df)
        ```
        this will work when check_data is using one of elementary test decorators, for example:
        ```python
        @boolean_test(name="has_data", severity="ERROR")
        def check_data(df: pd.DataFrame) -> bool:
            return df.shape[0] > 0
        ```

        if you wish to execute the test directly without wrapping your function with a decorator, you can use inner context like this
        ```python
        with elementary_test_context(asset=my_asset) as ctx:
            with ctx.boolean_test(name="has_data", severity="ERROR") as inner_ctx:
                inner_ctx.assert_value(df.shape[0] > 0)
        ```
    """
    test_context = ElementaryTestContext(asset=asset)
    yield from _elementary_test_context(test_context, raise_on_error=raise_on_error)


# Thread-local storage for the active test context
_active_context: ContextVar[ElementaryTestContext | None] = ContextVar(
    "_active_context", default=None
)


def get_active_context() -> ElementaryTestContext | None:
    return _active_context.get()


def set_active_context(context: ElementaryTestContext | None) -> None:
    _active_context.set(context)
