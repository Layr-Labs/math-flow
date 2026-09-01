from __future__ import annotations

import unittest

from experiments.bssc_local_builder_v10 import BudgetedCapturingTransport
from math_flow.errors import MathFlowError


class BudgetedCapturingTransportTests(unittest.TestCase):
    def response(self, cost: object) -> dict[str, object]:
        return {
            "choices": [{"finish_reason": "stop", "message": {"content": "{}"}}],
            "usage": {
                "cost": cost,
                "prompt_tokens": 10,
                "completion_tokens": 10,
                "total_tokens": 20,
            },
        }

    def test_reserves_single_call_ceiling_before_spending(self) -> None:
        calls = []

        def inner(request: dict[str, object]) -> dict[str, object]:
            calls.append(request)
            return self.response(0.75)

        transport = BudgetedCapturingTransport(
            maximum_calls=5,
            maximum_cost_usd=1.0,
            maximum_single_call_cost_usd=0.75,
            maximum_request_bytes=1000,
            maximum_total_tokens=10000,
            transport=inner,
        )
        transport({"attempt": 1, "max_tokens": 100})
        with self.assertRaisesRegex(MathFlowError, "cost budget exhausted"):
            transport({"attempt": 2, "max_tokens": 100})
        self.assertEqual(len(calls), 1)
        self.assertEqual(transport.reported_cost_usd, 0.75)

    def test_missing_or_excessive_cost_blocks_all_followups(self) -> None:
        responses = iter([self.response(None), self.response(0.01)])
        transport = BudgetedCapturingTransport(
            maximum_calls=5,
            maximum_cost_usd=3.0,
            maximum_single_call_cost_usd=0.75,
            maximum_request_bytes=1000,
            maximum_total_tokens=10000,
            transport=lambda request: next(responses),
        )
        with self.assertRaisesRegex(MathFlowError, "omitted valid cost telemetry"):
            transport({"attempt": 1, "max_tokens": 100})
        with self.assertRaisesRegex(MathFlowError, "omitted valid cost telemetry"):
            transport({"attempt": 2, "max_tokens": 100})
        self.assertEqual(len(transport.requests), 1)

        expensive = BudgetedCapturingTransport(
            maximum_calls=5,
            maximum_cost_usd=3.0,
            maximum_single_call_cost_usd=0.75,
            maximum_request_bytes=1000,
            maximum_total_tokens=10000,
            transport=lambda request: self.response(0.80),
        )
        with self.assertRaisesRegex(MathFlowError, "single-call cost ceiling"):
            expensive({"attempt": 1, "max_tokens": 100})
        with self.assertRaisesRegex(MathFlowError, "single-call cost ceiling"):
            expensive({"attempt": 2, "max_tokens": 100})
        self.assertEqual(len(expensive.requests), 1)

    def test_oversized_request_fails_before_transport(self) -> None:
        calls = []
        transport = BudgetedCapturingTransport(
            maximum_calls=5,
            maximum_cost_usd=3.0,
            maximum_single_call_cost_usd=0.75,
            maximum_request_bytes=32,
            maximum_total_tokens=10000,
            transport=lambda request: calls.append(request) or self.response(0.01),
        )
        with self.assertRaisesRegex(MathFlowError, "request budget exhausted"):
            transport({"payload": "x" * 100})
        self.assertEqual(calls, [])
        self.assertEqual(transport.requests, [])


if __name__ == "__main__":
    unittest.main()
