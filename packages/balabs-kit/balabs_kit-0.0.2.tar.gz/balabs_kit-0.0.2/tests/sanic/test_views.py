from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from bakit.sanic.views import serialize


@pytest.mark.parametrize(
    ("obj", "expected"),
    [
        # datetime / date
        (datetime(2025, 12, 16, 1, 2, 3), "2025-12-16T01:02:03"),  # noqa: DTZ001
        (datetime(2025, 12, 16, 1, 2, 3, tzinfo=UTC), "2025-12-16T01:02:03+00:00"),
        (date(2025, 12, 16), "2025-12-16"),
        # Decimal: zero variants
        (Decimal("0"), "0"),
        (Decimal("0.0"), "0"),
        (Decimal("0E-18"), "0"),
        (Decimal("-0E-18"), "0"),
        # Decimal: non-zero should preserve str() formatting (incl scientific)
        (Decimal("1"), "1"),
        (Decimal("10.00"), "10.00"),
        (Decimal("1E-18"), "1E-18"),
        (Decimal("-1E-18"), "-1E-18"),
        # passthrough primitives
        (None, None),
        (True, True),
        (False, False),
        (123, 123),
        (12.5, 12.5),
        ("hello", "hello"),
        # lists
        ([Decimal("0E-18"), Decimal("1E-3"), "x"], ["0", "0.001", "x"]),
        # dicts
        ({"a": Decimal("0E-18"), "b": Decimal("2E-2")}, {"a": "0", "b": "0.02"}),
        # nested
        (
            {
                "ts": datetime(2025, 12, 16, 1, 2, 3, tzinfo=UTC),
                "d": date(2025, 12, 16),
                "nums": [Decimal("0E-18"), {"n": Decimal("1E-18")}],
            },
            {
                "ts": "2025-12-16T01:02:03+00:00",
                "d": "2025-12-16",
                "nums": ["0", {"n": "1E-18"}],
            },
        ),
    ],
)
async def test_serialize(obj, expected):
    assert serialize(obj) == expected
