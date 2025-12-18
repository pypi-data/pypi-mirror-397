"""Elementary tests module for Python SDK.

This module provides decorators and context managers for defining and executing
generic Python data tests that integrate with Elementary's observability platform.
"""

# Context (includes registry functions)
from elementary_python_sdk.core.tests.context import (
    elementary_test_context,
)

# Decorators
from elementary_python_sdk.core.tests.decorators.impl.boolean_test import (
    boolean_test,
)
from elementary_python_sdk.core.tests.decorators.impl.expected_range import (
    expected_range,
)
from elementary_python_sdk.core.tests.decorators.impl.expected_value import (
    expected_value,
)
from elementary_python_sdk.core.tests.decorators.impl.row_count import (
    row_count,
)

__all__ = [
    # Context
    "elementary_test_context",
    # "ElementaryTestContext",
    # "get_active_context",
    # "set_active_context",
    # Decorators
    "boolean_test",
    "expected_range",
    "expected_value",
    "row_count",
    "custom_test",
    # Base classes (for creating custom test types)
    # "TestDecorator",
    # "TestDecoratorParams",
    # "TestDecoratorResult",
    # "CommonTestFields",
]
