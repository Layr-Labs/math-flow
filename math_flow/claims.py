from __future__ import annotations

import re

from .errors import MathFlowError


CLAIM_KEY = re.compile(r"^[a-z0-9][a-z0-9/_-]*$")
FULL_TRANSACTION_ID = re.compile(r"^[0-9a-f]{40}$")


def validate_claim_manifest(
    value: object,
    *,
    problem: str,
    subject_transaction_id: str | None = None,
    prior_transaction_ids: set[str] | None = None,
) -> list[dict[str, object]]:
    if not isinstance(value, dict) or set(value) != {"schemaVersion", "claims"}:
        raise MathFlowError("contribution claims manifest has an invalid envelope")
    claims = value.get("claims")
    if value.get("schemaVersion") != 1 or not isinstance(claims, list) or not claims:
        raise MathFlowError("contribution claims manifest must contain claims")
    validated: list[dict[str, object]] = []
    seen: set[str] = set()
    for claim in claims:
        if not isinstance(claim, dict) or set(claim) != {
            "claimKey",
            "statement",
            "dependencyTransactionIds",
        }:
            raise MathFlowError("contribution claims manifest contains an invalid claim")
        claim_key = claim.get("claimKey")
        statement = claim.get("statement")
        dependencies = claim.get("dependencyTransactionIds")
        if not isinstance(claim_key, str) or not CLAIM_KEY.fullmatch(claim_key):
            raise MathFlowError("contribution claimKey must be a stable lowercase path")
        if not claim_key.startswith(f"{problem}/"):
            raise MathFlowError("contribution claimKey must be scoped to its problem")
        if claim_key in seen:
            raise MathFlowError("contribution claimKeys must be unique")
        if not isinstance(statement, str) or not statement.strip():
            raise MathFlowError("contribution claim statement must be non-empty")
        if (
            not isinstance(dependencies, list)
            or any(
                not isinstance(item, str) or not FULL_TRANSACTION_ID.fullmatch(item)
                for item in dependencies
            )
            or len(dependencies) != len(set(dependencies))
        ):
            raise MathFlowError(
                "contribution claim dependencies must be unique full transaction IDs"
            )
        if subject_transaction_id is not None and subject_transaction_id in dependencies:
            raise MathFlowError("a contribution claim cannot depend on its own transaction")
        if prior_transaction_ids is not None:
            missing = set(dependencies) - prior_transaction_ids
            if missing:
                raise MathFlowError(
                    "contribution claim dependency is not a prior canonical transaction: "
                    f"{sorted(missing)[0]}"
                )
        seen.add(claim_key)
        validated.append(
            {
                "claimKey": claim_key,
                "statement": statement.strip(),
                "dependencyTransactionIds": list(dependencies),
            }
        )
    return validated
