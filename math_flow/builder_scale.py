from __future__ import annotations

import copy
import hashlib
import json
import math
from collections import deque
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Protocol

from .errors import MathFlowError
from .repository import sha256_json
from .research_builder_v7 import (
    _normalize_contribution,
    _normalize_program,
    _normalize_result,
    _with_state_digest,
    validate_research_program_state_v3,
)
from .research_builder_v9 import build_research_builder_v9_context


ADVERSARIAL_CHALLENGES = (
    "dependency-closure",
    "distant-duplicate",
    "cross-program-placement",
    "root-sibling",
    "misleading-capsule",
    "topology-revision",
)
PROVENANCE_FIELDS = {
    "sourceTransactionIds",
    "claimRefs",
    "judgmentIds",
}
DEFAULT_BUDGET_THRESHOLDS = (0.50, 0.70, 0.85, 0.95, 1.00)


@dataclass(frozen=True)
class SyntheticBuilderStateConfig:
    """Independent dimensions for a valid, provider-free builder state."""

    program_count: int
    result_count: int
    maximum_depth: int
    maximum_width: int
    provenance_per_result: int = 1
    dependency_depth: int = 1
    dependency_width: int = 1
    support_bytes: int = 96
    summary_bytes: int = 96
    evidence_bytes: int = 512
    challenges: tuple[str, ...] = ADVERSARIAL_CHALLENGES

    def validate(self) -> SyntheticBuilderStateConfig:
        integer_fields = {
            "program_count": self.program_count,
            "result_count": self.result_count,
            "maximum_depth": self.maximum_depth,
            "maximum_width": self.maximum_width,
            "provenance_per_result": self.provenance_per_result,
            "dependency_depth": self.dependency_depth,
            "dependency_width": self.dependency_width,
            "support_bytes": self.support_bytes,
            "summary_bytes": self.summary_bytes,
            "evidence_bytes": self.evidence_bytes,
        }
        if any(
            not isinstance(value, int) or isinstance(value, bool)
            for value in integer_fields.values()
        ):
            raise MathFlowError("synthetic builder scale settings must be integers")
        if (
            self.program_count < 1
            or self.result_count < 1
            or self.maximum_depth < 1
            or self.maximum_width < 1
            or self.provenance_per_result < 1
            or self.dependency_depth < 0
            or self.dependency_width < 1
            or self.support_bytes < 1
            or self.summary_bytes < 1
            or self.evidence_bytes < 1
        ):
            raise MathFlowError("synthetic builder scale settings are out of range")
        unknown = sorted(set(self.challenges) - set(ADVERSARIAL_CHALLENGES))
        if unknown:
            raise MathFlowError(
                "synthetic builder scale challenge is unsupported: " + unknown[0]
            )
        if len(self.challenges) != len(set(self.challenges)):
            raise MathFlowError("synthetic builder scale challenges must be unique")
        if "topology-revision" in self.challenges and self.program_count < 6:
            raise MathFlowError(
                "topology-revision fixture needs at least six programs"
            )
        if self.challenges and self.program_count < 3:
            raise MathFlowError("adversarial builder fixtures need at least three programs")
        required_dependency_results = (
            self.dependency_depth * self.dependency_width + 1
        )
        if self.result_count < required_dependency_results:
            raise MathFlowError(
                "synthetic builder state has too few results for its dependency closure"
            )
        regular_programs = self.program_count - (
            3 if "topology-revision" in self.challenges else 0
        )
        capacity = _tree_capacity(self.maximum_depth, self.maximum_width)
        if regular_programs > capacity:
            raise MathFlowError(
                "synthetic builder program count exceeds the requested depth/width capacity"
            )
        return self


class ContextStrategy(Protocol):
    """Adapter boundary for V10 or later route/author implementations."""

    def __call__(
        self,
        fixture: Mapping[str, object],
        challenge_name: str,
    ) -> Mapping[str, Mapping[str, object]]:
        """Return stage name -> named serialized prompt components."""


def make_v10_context_strategy(
    route_context_builder: Callable[[Mapping[str, object], object], dict[str, object]],
    authoring_packet_builder: Callable[..., dict[str, object]],
) -> ContextStrategy:
    """Bind the scale harness to V10's route/author API without importing it."""

    def strategy(
        fixture: Mapping[str, object], challenge_name: str
    ) -> Mapping[str, Mapping[str, object]]:
        state = fixture.get("state")
        claims = fixture.get("acceptedClaims")
        evidence = fixture.get("submissionEvidence")
        challenges = fixture.get("challenges")
        if (
            not isinstance(state, dict)
            or not isinstance(claims, list)
            or not isinstance(evidence, dict)
            or not isinstance(challenges, dict)
            or not isinstance(challenges.get(challenge_name), dict)
        ):
            raise MathFlowError("V10 scale strategy received an invalid fixture")
        challenge = challenges[challenge_name]
        route_context = route_context_builder(state, claims)
        context_digest = route_context.get("contextDigest")
        if not isinstance(context_digest, str):
            raise MathFlowError("V10 route context has no contextDigest")
        write_program_ids: list[str] = []
        write_result_ids: list[str] = []
        for raw_identifier in challenge.get("requiredWriteEntityIds", []):
            kind, separator, identifier = str(raw_identifier).partition(":")
            if not separator:
                raise MathFlowError("V10 scale challenge has an invalid write ID")
            if kind == "program":
                write_program_ids.append(identifier)
            elif kind == "intermediateResult":
                write_result_ids.append(identifier)
            else:
                raise MathFlowError("V10 scale challenge has an invalid entity kind")
        query = str(challenge.get("query", "")).strip()
        route_plan = {
            "schemaVersion": 1,
            "baseStateDigest": route_context["baseStateDigest"],
            "routeContextDigest": context_digest,
            "inspectProgramIds": sorted(
                {str(item) for item in challenge.get("requiredProgramIds", [])}
            ),
            "inspectResultIds": sorted(
                {str(item) for item in challenge.get("requiredResultIds", [])}
            ),
            "searchQueries": (
                [
                    {
                        "query": query,
                        "entityKinds": ["program", "intermediateResult"],
                        "limit": 8,
                    }
                ]
                if query
                else []
            ),
            "writeProgramIds": sorted(set(write_program_ids)),
            "writeResultIds": sorted(set(write_result_ids)),
            "createProgramIds": [],
            "createResultIds": [],
        }
        authoring_packet = authoring_packet_builder(
            state,
            claims,
            route_plan,
            route_context=route_context,
        )
        return {
            "route": {
                "routeContext": route_context,
                "acceptedClaimAssessments": copy.deepcopy(claims),
                "submissionEvidence": copy.deepcopy(evidence),
            },
            "author": {
                "authoringPacket": authoring_packet,
                "acceptedClaimAssessments": copy.deepcopy(claims),
                "submissionEvidence": copy.deepcopy(evidence),
            },
        }

    return strategy


def _tree_capacity(maximum_depth: int, maximum_width: int) -> int:
    if maximum_width == 1:
        return maximum_depth + 1
    return (maximum_width ** (maximum_depth + 1) - 1) // (maximum_width - 1)


def _stable_transaction(*parts: object) -> str:
    return hashlib.sha1(
        ":".join(str(part) for part in parts).encode("utf-8")
    ).hexdigest()


def _stable_digest(*parts: object) -> str:
    return "sha256:" + hashlib.sha256(
        ":".join(str(part) for part in parts).encode("utf-8")
    ).hexdigest()


def _padded_text(prefix: str, minimum_bytes: int) -> str:
    encoded = prefix.encode("utf-8")
    if len(encoded) >= minimum_bytes:
        return prefix
    return prefix + " " + "x" * (minimum_bytes - len(encoded) - 1)


def _regular_program_tree(
    count: int,
    *,
    maximum_depth: int,
    maximum_width: int,
) -> tuple[list[str], dict[str, str | None], dict[str, int]]:
    if count < 1:
        raise MathFlowError("synthetic program tree must contain root")
    ids = ["root"]
    parents: dict[str, str | None] = {"root": None}
    depths = {"root": 0}
    available: deque[str] = deque(["root"])
    child_counts = {"root": 0}
    while len(ids) < count:
        if not available:
            raise MathFlowError("synthetic program tree exhausted its configured capacity")
        parent = available[0]
        if (
            depths[parent] >= maximum_depth
            or child_counts[parent] >= maximum_width
        ):
            available.popleft()
            continue
        identifier = f"program/p{len(ids):06d}"
        ids.append(identifier)
        parents[identifier] = parent
        depths[identifier] = depths[parent] + 1
        child_counts[identifier] = 0
        child_counts[parent] += 1
        if depths[identifier] < maximum_depth:
            available.append(identifier)
    return ids, parents, depths


def _ancestors(
    program_id: str, parents: Mapping[str, str | None]
) -> list[str]:
    result: list[str] = []
    cursor: str | None = program_id
    while cursor is not None:
        result.append(cursor)
        cursor = parents[cursor]
    return result


def _incomparable_pair(
    program_ids: Sequence[str], parents: Mapping[str, str | None]
) -> tuple[str, str]:
    live = [program_id for program_id in program_ids if program_id != "root"]
    for index, left in enumerate(live):
        left_ancestors = set(_ancestors(left, parents))
        for right in live[index + 1 :]:
            right_ancestors = set(_ancestors(right, parents))
            if left not in right_ancestors and right not in left_ancestors:
                return left, right
    raise MathFlowError("synthetic fixture needs two incomparable active programs")


def _dependency_graph(
    result_ids: Sequence[str], *, depth: int, width: int
) -> tuple[dict[str, list[str]], str, list[str]]:
    required = depth * width + 1
    if len(result_ids) < required:
        raise MathFlowError("synthetic dependency graph has too few results")
    dependencies = {result_id: [] for result_id in result_ids}
    if depth == 0:
        return dependencies, result_ids[0], [result_ids[0]]
    layers = [
        list(result_ids[layer * width : (layer + 1) * width])
        for layer in range(depth)
    ]
    for layer_number in range(1, depth):
        prior = layers[layer_number - 1]
        for result_id in layers[layer_number]:
            dependencies[result_id] = list(prior)
    target = result_ids[depth * width]
    dependencies[target] = list(layers[-1])
    closure = [*result_ids[: depth * width], target]
    return dependencies, target, sorted(closure)


def _compact_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _without_digest(value: Mapping[str, object]) -> dict[str, object]:
    return {
        key: copy.deepcopy(item)
        for key, item in value.items()
        if key != "digest"
    }


def build_synthetic_builder_fixture(
    configuration: SyntheticBuilderStateConfig,
) -> dict[str, object]:
    """Construct one valid v3 state plus reusable teacher/student challenges."""

    config = configuration.validate()
    has_revision = "topology-revision" in config.challenges
    regular_count = config.program_count - (3 if has_revision else 0)
    program_ids, parents, depths = _regular_program_tree(
        regular_count,
        maximum_depth=config.maximum_depth,
        maximum_width=config.maximum_width,
    )
    lineage: dict[str, list[dict[str, str]]] = {
        program_id: [] for program_id in program_ids
    }
    statuses = {program_id: "active" for program_id in program_ids}
    revision_ids: tuple[str, str, str] | None = None
    if has_revision:
        old_id = "program/revision-old"
        left_id = "program/revision-left"
        right_id = "program/revision-right"
        revision_ids = (old_id, left_id, right_id)
        for program_id in revision_ids:
            program_ids.append(program_id)
            parents[program_id] = "root"
            depths[program_id] = 1
        statuses[old_id] = "retired"
        statuses[left_id] = "active"
        statuses[right_id] = "active"
        lineage.update(
            {
                old_id: [
                    {"relation": "split-into", "programId": left_id},
                    {"relation": "split-into", "programId": right_id},
                ],
                left_id: [{"relation": "split-from", "programId": old_id}],
                right_id: [{"relation": "split-from", "programId": old_id}],
            }
        )

    active_program_ids = [
        program_id
        for program_id in program_ids
        if program_id != "root" and statuses[program_id] == "active"
    ]
    left_program, right_program = _incomparable_pair(active_program_ids, parents)
    result_ids = [f"result/r{number:06d}" for number in range(config.result_count)]
    dependency_graph, dependency_target, dependency_closure = _dependency_graph(
        result_ids,
        depth=config.dependency_depth,
        width=config.dependency_width,
    )
    result_programs = {
        result_id: active_program_ids[index % len(active_program_ids)]
        for index, result_id in enumerate(result_ids)
    }
    related_programs = {result_id: [] for result_id in result_ids}

    cross_result = result_ids[min(1, len(result_ids) - 1)]
    if "cross-program-placement" in config.challenges:
        result_programs[cross_result] = left_program
        related_programs[cross_result] = [right_program]

    duplicate_results = result_ids[-2:] if len(result_ids) >= 2 else result_ids
    if "distant-duplicate" in config.challenges:
        if len(duplicate_results) != 2:
            raise MathFlowError("distant duplicate challenge needs two results")
        result_programs[duplicate_results[0]] = left_program
        result_programs[duplicate_results[1]] = right_program

    revision_result: str | None = None
    if revision_ids is not None:
        revision_result = result_ids[max(0, len(result_ids) - 3)]
        result_programs[revision_result] = revision_ids[1]
        related_programs[revision_result] = []

    contribution_records: dict[str, dict[str, object]] = {}
    result_transactions: dict[str, list[str]] = {}
    result_judgments: dict[str, list[str]] = {}
    result_historical_programs: dict[str, list[str]] = {}
    ordered_transactions: list[str] = []
    for result_number, result_id in enumerate(result_ids):
        linked_programs = sorted(
            {result_programs[result_id], *related_programs[result_id]}
        )
        direct_programs = linked_programs
        if revision_ids is not None and result_id == revision_result:
            direct_programs = [revision_ids[0]]
            result_historical_programs[result_id] = direct_programs
        else:
            result_historical_programs[result_id] = []
        transactions: list[str] = []
        judgments: list[str] = []
        dependency_transactions = sorted(
            {
                result_transactions[dependency_id][0]
                for dependency_id in dependency_graph[result_id]
            }
        )
        for provenance_number in range(config.provenance_per_result):
            transaction_id = _stable_transaction(
                "builder-scale", result_number, provenance_number
            )
            claim_key = f"claim/r{result_number:06d}/c{provenance_number:04d}"
            judgment_id = _stable_digest(
                "builder-scale-judgment", result_number, provenance_number
            )
            transactions.append(transaction_id)
            judgments.append(judgment_id)
            ordered_transactions.append(transaction_id)
            contribution_records[transaction_id] = _normalize_contribution(
                transaction_id,
                {
                    "id": transaction_id,
                    "transactionId": transaction_id,
                    "claimKeys": [claim_key],
                    "directProgramIds": direct_programs,
                    "intermediateResultIds": [result_id],
                    "dependencyTransactionIds": dependency_transactions,
                    "judgmentId": judgment_id,
                },
            )
        result_transactions[result_id] = sorted(transactions)
        result_judgments[result_id] = sorted(judgments)

    result_records: dict[str, dict[str, object]] = {}
    program_result_ids = {program_id: set() for program_id in program_ids}
    program_source_ids = {program_id: set() for program_id in program_ids}
    for result_number, result_id in enumerate(result_ids):
        primary_program_id = result_programs[result_id]
        linked_programs = [primary_program_id, *related_programs[result_id]]
        for program_id in linked_programs:
            program_result_ids[program_id].add(result_id)
            for ancestor_id in _ancestors(program_id, parents):
                program_source_ids[ancestor_id].update(result_transactions[result_id])
        for historical_program_id in result_historical_programs[result_id]:
            program_source_ids[historical_program_id].update(
                result_transactions[result_id]
            )
        statement = f"Synthetic intermediate result {result_number}."
        if result_id in duplicate_results and "distant-duplicate" in config.challenges:
            statement += (
                " The rare-distant-duplicate-marker establishes the same reusable lemma."
            )
        if result_id == cross_result and "cross-program-placement" in config.challenges:
            statement += " The conclusion jointly changes two incomparable programs."
        support_text = _padded_text(
            f"Proof support for {result_id}.", config.support_bytes
        )
        claim_refs = [
            {
                "transactionId": transaction_id,
                "claimKey": str(
                    contribution_records[transaction_id]["claimKeys"][0]
                ),
            }
            for transaction_id in result_transactions[result_id]
        ]
        artifact_transaction = result_transactions[result_id][0]
        artifact_path = (
            "problems/synthetic-builder-scale/contributions/"
            f"{artifact_transaction}/README.md"
        )
        result_records[result_id] = _normalize_result(
            result_id,
            {
                "id": result_id,
                "primaryProgramId": primary_program_id,
                "relatedProgramIds": related_programs[result_id],
                "title": f"Synthetic result {result_number}",
                "statement": statement,
                "scopeQualifications": ["Synthetic benchmark scope only."],
                "support": {
                    "proofs": [support_text],
                    "methods": [f"Method for {result_id}."],
                    "computations": [],
                    "tools": [],
                    "artifactRefs": [
                        {
                            "path": artifact_path,
                            "digest": _stable_digest(
                                "builder-scale-artifact", result_number
                            ),
                        }
                    ],
                    "attestationRefs": [],
                },
                "dependencyResultIds": dependency_graph[result_id],
                "claimRefs": claim_refs,
                "sourceTransactionIds": result_transactions[result_id],
                "judgmentIds": result_judgments[result_id],
                "status": "active",
                "supersededByResultIds": [],
            },
        )

    misleading_program = right_program
    program_records: dict[str, dict[str, object]] = {}
    for program_number, program_id in enumerate(program_ids):
        if program_id == "root":
            title = "Synthetic canonical problem"
            objective = "Resolve the synthetic canonical problem."
        elif revision_ids is not None and program_id == revision_ids[0]:
            title = "Retired broad revision predecessor"
            objective = "The historical broad objective before a split."
        elif revision_ids is not None and program_id in revision_ids[1:]:
            title = "Revision successor " + program_id.rsplit("-", 1)[-1]
            objective = "Track one independently variable successor package."
        else:
            title = f"Synthetic program {program_number}"
            objective = f"Resolve synthetic package {program_number}."
        summary_prefix = f"Current state for {program_id}."
        if (
            program_id == misleading_program
            and "misleading-capsule" in config.challenges
        ):
            summary_prefix += (
                " Misleading-capsule text emphasizes an unrelated decoy direction."
            )
        program_records[program_id] = _normalize_program(
            program_id,
            {
                "id": program_id,
                "parentId": parents[program_id],
                "title": title,
                "objective": objective,
                "currentStateSummary": _padded_text(
                    summary_prefix, config.summary_bytes
                ),
                "localResidualSummary": _padded_text(
                    f"Residual work for {program_id} remains.",
                    config.summary_bytes,
                ),
                "status": statuses[program_id],
                "intermediateResultIds": sorted(program_result_ids[program_id]),
                "sourceTransactionIds": sorted(program_source_ids[program_id]),
                "lineage": lineage[program_id],
            },
        )

    state = _with_state_digest(
        {
            "schemaVersion": 3,
            "problemId": "synthetic-builder-scale",
            "ledgerHead": ordered_transactions[-1],
            "baseStateDigest": None,
            "rootProgramId": "root",
            "programs": program_records,
            "intermediateResults": result_records,
            "contributions": contribution_records,
        }
    )
    validate_research_program_state_v3(state)

    dependency_transaction = result_transactions[dependency_target][0]
    accepted_claims = [
        {
            "claimKey": "claim/current",
            "declaredStatement": "A synthetic current contribution advances a local package.",
            "validitySummary": "The benchmark's restricted current statement is accepted.",
            "scopeQualifications": ["Synthetic benchmark scope only."],
            "evidenceTransactionIds": [],
            "dependencyTransactionIds": [dependency_transaction],
        }
    ]
    submission_evidence = {
        "files": [
            {
                "path": "problems/synthetic-builder-scale/contributions/current/README.md",
                "content": _padded_text(
                    "Current synthetic submission evidence.", config.evidence_bytes
                ),
            }
        ]
    }

    dependency_program_ids = sorted(
        {
            str(program_id)
            for result_id in dependency_closure
            for program_id in [
                result_records[result_id]["primaryProgramId"],
                *result_records[result_id]["relatedProgramIds"],
            ]
        }
    )
    challenges: dict[str, dict[str, object]] = {}
    if "dependency-closure" in config.challenges:
        challenges["dependency-closure"] = {
            "query": "load the declared dependency and its transitive result closure",
            "requiredProgramIds": dependency_program_ids,
            "requiredResultIds": dependency_closure,
            "requiredWriteEntityIds": [],
            "dependencyTransactionIds": [dependency_transaction],
        }
    if "distant-duplicate" in config.challenges:
        challenges["distant-duplicate"] = {
            "query": "rare-distant-duplicate-marker reusable lemma",
            "requiredProgramIds": sorted(
                {result_programs[result_id] for result_id in duplicate_results}
            ),
            "requiredResultIds": sorted(duplicate_results),
            "requiredWriteEntityIds": [],
        }
    if "cross-program-placement" in config.challenges:
        challenges["cross-program-placement"] = {
            "query": "one conclusion jointly changes two incomparable programs",
            "requiredProgramIds": [left_program, right_program],
            "requiredResultIds": [cross_result],
            "requiredWriteEntityIds": [],
        }
    if "root-sibling" in config.challenges:
        challenges["root-sibling"] = {
            "query": "an independent route whose inclusion can vary separately",
            "requiredProgramIds": ["root"],
            "requiredResultIds": [],
            "requiredWriteEntityIds": [],
            "requiredParentProgramId": "root",
            "forbiddenParentProgramId": left_program,
        }
    if "misleading-capsule" in config.challenges:
        exact_result = duplicate_results[-1]
        challenges["misleading-capsule"] = {
            "query": "rare-distant-duplicate-marker despite an unrelated program summary",
            "requiredProgramIds": [result_programs[exact_result]],
            "requiredResultIds": [exact_result],
            "requiredWriteEntityIds": [],
            "misleadingProgramId": misleading_program,
        }
    if revision_ids is not None:
        challenges["topology-revision"] = {
            "query": "revise both successors of the retired broad predecessor atomically",
            "requiredProgramIds": list(revision_ids),
            "requiredResultIds": [revision_result],
            "requiredWriteEntityIds": [
                f"program:{program_id}" for program_id in revision_ids
            ],
            "retiredProgramId": revision_ids[0],
            "successorProgramIds": list(revision_ids[1:]),
        }

    return {
        "schemaVersion": 1,
        "configuration": asdict(config),
        "state": state,
        "acceptedClaims": accepted_claims,
        "submissionEvidence": submission_evidence,
        "challenges": challenges,
        "fixtureDigest": "sha256:"
        + sha256_json(
            {
                "configuration": asdict(config),
                "stateDigest": state["stateDigest"],
                "acceptedClaims": accepted_claims,
                "challenges": challenges,
            }
        ),
    }


def _result_dependency_closure(
    state: Mapping[str, object], initial_result_ids: Sequence[str]
) -> set[str]:
    results = state.get("intermediateResults")
    if not isinstance(results, dict):
        raise MathFlowError("builder scale fixture has no intermediate results")
    loaded: set[str] = set()
    pending = list(initial_result_ids)
    while pending:
        result_id = pending.pop()
        if result_id in loaded:
            continue
        result = results.get(result_id)
        if not isinstance(result, dict):
            raise MathFlowError("builder scale fixture names a missing result")
        loaded.add(result_id)
        dependency_ids = result.get("dependencyResultIds")
        if not isinstance(dependency_ids, list):
            raise MathFlowError("builder scale fixture has invalid result dependencies")
        pending.extend(str(item) for item in dependency_ids)
    return loaded


def _program_card(program: Mapping[str, object]) -> dict[str, object]:
    return {
        "id": program["id"],
        "parentId": program["parentId"],
        "title": program["title"],
        "objective": program["objective"],
        "currentStateSummary": program["currentStateSummary"],
        "localResidualSummary": program["localResidualSummary"],
        "status": program["status"],
        "resultCount": len(program["intermediateResultIds"]),
        "sourceCount": len(program["sourceTransactionIds"]),
        "recordDigest": program["digest"],
    }


def _result_card(result: Mapping[str, object]) -> dict[str, object]:
    return {
        "id": result["id"],
        "primaryProgramId": result["primaryProgramId"],
        "relatedProgramIds": copy.deepcopy(result["relatedProgramIds"]),
        "title": result["title"],
        "statement": result["statement"],
        "scopeQualifications": copy.deepcopy(result["scopeQualifications"]),
        "dependencyResultIds": copy.deepcopy(result["dependencyResultIds"]),
        "status": result["status"],
        "sourceCount": len(result["sourceTransactionIds"]),
        "claimCount": len(result["claimRefs"]),
        "recordDigest": result["digest"],
    }


def build_trusted_search_catalog(
    state: Mapping[str, object],
) -> dict[str, object]:
    """Build a host-side catalog; the complete catalog is not a prompt component."""

    programs = state.get("programs")
    results = state.get("intermediateResults")
    if not isinstance(programs, dict) or not isinstance(results, dict):
        raise MathFlowError("builder scale catalog requires a two-entity state")
    core = {
        "schemaVersion": 1,
        "baseStateDigest": state.get("stateDigest"),
        "programCards": {
            str(program_id): _program_card(program)
            for program_id, program in sorted(programs.items())
            if isinstance(program, dict)
        },
        "resultCards": {
            str(result_id): _result_card(result)
            for result_id, result in sorted(results.items())
            if isinstance(result, dict)
        },
    }
    return {**core, "catalogDigest": "sha256:" + sha256_json(core)}


def _semantic_record(
    value: Mapping[str, object], *, include_provenance: bool
) -> dict[str, object]:
    if include_provenance:
        return copy.deepcopy(dict(value))
    result = {
        key: copy.deepcopy(item)
        for key, item in value.items()
        if key not in PROVENANCE_FIELDS and key != "digest"
    }
    result["provenanceCounts"] = {
        field: len(value[field])
        for field in sorted(PROVENANCE_FIELDS)
        if isinstance(value.get(field), list)
    }
    result["recordDigest"] = value.get("digest")
    return result


def build_bounded_local_packet_model(
    fixture: Mapping[str, object],
    challenge_name: str = "dependency-closure",
    *,
    include_exact_provenance: bool = False,
    maximum_sibling_cards: int = 4,
    maximum_search_results: int = 8,
    maximum_exact_results: int = 128,
) -> dict[str, Mapping[str, object]]:
    """Model a two-call fractal route/author flow without guessing V10's schema."""

    state = fixture.get("state")
    claims = fixture.get("acceptedClaims")
    evidence = fixture.get("submissionEvidence")
    challenges = fixture.get("challenges")
    if (
        not isinstance(state, dict)
        or not isinstance(claims, list)
        or not isinstance(evidence, dict)
        or not isinstance(challenges, dict)
        or not isinstance(challenges.get(challenge_name), dict)
    ):
        raise MathFlowError("builder scale packet received an invalid fixture")
    if any(
        not isinstance(value, int) or isinstance(value, bool) or value < 1
        for value in (
            maximum_sibling_cards,
            maximum_search_results,
            maximum_exact_results,
        )
    ):
        raise MathFlowError("builder scale packet limits must be positive integers")
    programs = state["programs"]
    results = state["intermediateResults"]
    assert isinstance(programs, dict)
    assert isinstance(results, dict)
    challenge = challenges[challenge_name]
    required_program_ids = {
        str(item) for item in challenge.get("requiredProgramIds", [])
    }
    initial_result_ids = {
        str(item) for item in challenge.get("requiredResultIds", [])
    }
    exact_result_ids = _result_dependency_closure(state, sorted(initial_result_ids))
    if len(exact_result_ids) > maximum_exact_results:
        raise MathFlowError(
            "builder scale local packet dependency closure exceeds maximumExactResults"
        )
    for result_id in exact_result_ids:
        result = results[result_id]
        assert isinstance(result, dict)
        required_program_ids.add(str(result["primaryProgramId"]))
        required_program_ids.update(str(item) for item in result["relatedProgramIds"])
    parents = {
        str(program_id): (
            str(program["parentId"])
            if isinstance(program, dict) and isinstance(program.get("parentId"), str)
            else None
        )
        for program_id, program in programs.items()
    }
    exact_program_ids: set[str] = set()
    for program_id in required_program_ids:
        if program_id not in programs:
            raise MathFlowError("builder scale challenge names a missing program")
        exact_program_ids.update(_ancestors(program_id, parents))
    exact_program_ids.add("root")

    children: dict[str, list[str]] = {str(program_id): [] for program_id in programs}
    for program_id, parent_id in parents.items():
        if parent_id is not None:
            children[parent_id].append(program_id)
    for child_ids in children.values():
        child_ids.sort()
    route_child_ids = children["root"][:maximum_sibling_cards]
    route_context = {
        "schemaVersion": 1,
        "baseStateDigest": state["stateDigest"],
        "rootCapsule": _program_card(programs["root"]),
        "childCapsules": [
            _program_card(programs[program_id]) for program_id in route_child_ids
        ],
        "collapsedRootChildCount": max(0, len(children["root"]) - len(route_child_ids)),
        "acceptedClaimAssessments": copy.deepcopy(claims),
        "submissionEvidence": copy.deepcopy(evidence),
    }

    catalog = build_trusted_search_catalog(state)
    query_terms = {
        term.lower()
        for term in str(challenge.get("query", "")).replace("-", " ").split()
        if term
    }
    scored_cards: list[tuple[int, str, str, dict[str, object]]] = []
    for entity_kind, collection_name in (
        ("program", "programCards"),
        ("intermediateResult", "resultCards"),
    ):
        cards = catalog[collection_name]
        assert isinstance(cards, dict)
        for entity_id, card in cards.items():
            serialized = _compact_json(card).lower().replace("-", " ")
            score = sum(term in serialized for term in query_terms)
            scored_cards.append((score, entity_kind, str(entity_id), card))
    search_cards = [
        {"entityKind": kind, **copy.deepcopy(card)}
        for score, kind, _, card in sorted(
            scored_cards,
            key=lambda item: (-item[0], item[1], item[2]),
        )[:maximum_search_results]
        if score > 0
    ]

    boundary_ids: set[str] = set()
    for program_id in exact_program_ids:
        boundary_ids.update(children[program_id])
    boundary_ids -= exact_program_ids
    boundary_cards = [
        _program_card(programs[program_id])
        for program_id in sorted(boundary_ids)[:maximum_sibling_cards]
    ]
    author_context = {
        "schemaVersion": 1,
        "baseStateDigest": state["stateDigest"],
        "challenge": copy.deepcopy(challenge),
        "programs": {
            program_id: _semantic_record(
                programs[program_id],
                include_provenance=include_exact_provenance,
            )
            for program_id in sorted(exact_program_ids)
        },
        "intermediateResults": {
            result_id: _semantic_record(
                results[result_id],
                include_provenance=include_exact_provenance,
            )
            for result_id in sorted(exact_result_ids)
        },
        "boundaryProgramCards": boundary_cards,
        "searchResultCards": search_cards,
        "omitted": {
            "programCount": len(programs) - len(exact_program_ids),
            "resultCount": len(results) - len(exact_result_ids),
            "catalogDigest": catalog["catalogDigest"],
        },
        "acceptedClaimAssessments": copy.deepcopy(claims),
        "submissionEvidence": copy.deepcopy(evidence),
    }
    return {
        "route": {"routeContext": route_context},
        "author": {"authoringPacket": author_context},
    }


def build_v9_context_view(
    fixture: Mapping[str, object], challenge_name: str
) -> dict[str, Mapping[str, object]]:
    del challenge_name
    state = fixture.get("state")
    claims = fixture.get("acceptedClaims")
    evidence = fixture.get("submissionEvidence")
    if not isinstance(state, dict) or not isinstance(claims, list):
        raise MathFlowError("builder scale V9 view received an invalid fixture")
    return {
        "organize": {
            "baseStateContext": build_research_builder_v9_context(state, claims),
            "acceptedClaimAssessments": copy.deepcopy(claims),
            "submissionEvidence": copy.deepcopy(evidence),
        }
    }


def build_bounded_semantic_context_view(
    fixture: Mapping[str, object], challenge_name: str
) -> Mapping[str, Mapping[str, object]]:
    return build_bounded_local_packet_model(
        fixture, challenge_name, include_exact_provenance=False
    )


def build_bounded_exact_context_view(
    fixture: Mapping[str, object], challenge_name: str
) -> Mapping[str, Mapping[str, object]]:
    return build_bounded_local_packet_model(
        fixture, challenge_name, include_exact_provenance=True
    )


def measure_serialized_value(value: object) -> dict[str, object]:
    serialized = _compact_json(value)
    utf8_bytes = len(serialized.encode("utf-8"))
    return {
        "characters": len(serialized),
        "utf8Bytes": utf8_bytes,
        "estimatedTokens": math.ceil(utf8_bytes / 4),
        "tokenEstimateMethod": "ceil(compact-utf8-bytes/4)",
        "tokenUpperBound": utf8_bytes,
    }


def _budget_assessment(
    estimated_tokens: int,
    input_budget_tokens: int,
    thresholds: Sequence[float],
) -> dict[str, object]:
    utilization = estimated_tokens / input_budget_tokens
    reached = [threshold for threshold in thresholds if utilization >= threshold]
    return {
        "inputBudgetTokens": input_budget_tokens,
        "estimatedUtilization": utilization,
        "thresholdTokens": {
            str(int(threshold * 100)): math.ceil(input_budget_tokens * threshold)
            for threshold in thresholds
        },
        "thresholdsReachedPercent": [int(threshold * 100) for threshold in reached],
        "estimatedHardInputCrossing": estimated_tokens > input_budget_tokens,
    }


def measure_context_view(
    stages: Mapping[str, Mapping[str, object]],
    *,
    input_budget_tokens: int,
    thresholds: Sequence[float] = DEFAULT_BUDGET_THRESHOLDS,
) -> dict[str, object]:
    if (
        not isinstance(input_budget_tokens, int)
        or isinstance(input_budget_tokens, bool)
        or input_budget_tokens < 1
    ):
        raise MathFlowError("builder scale input budget must be a positive integer")
    if (
        not thresholds
        or any(threshold <= 0 or threshold > 1 for threshold in thresholds)
        or list(thresholds) != sorted(set(thresholds))
    ):
        raise MathFlowError("builder scale budget thresholds are invalid")
    stage_reports: dict[str, dict[str, object]] = {}
    cumulative_tokens = 0
    for stage_name, components in stages.items():
        if not isinstance(stage_name, str) or not isinstance(components, Mapping):
            raise MathFlowError("builder scale context strategy returned invalid stages")
        total = measure_serialized_value(components)
        component_reports = {
            str(name): measure_serialized_value(value)
            for name, value in sorted(components.items())
        }
        estimated_tokens = int(total["estimatedTokens"])
        cumulative_tokens += estimated_tokens
        stage_reports[stage_name] = {
            "total": total,
            "components": component_reports,
            "budget": _budget_assessment(
                estimated_tokens, input_budget_tokens, thresholds
            ),
        }
    maximum_stage_tokens = max(
        int(report["total"]["estimatedTokens"])
        for report in stage_reports.values()
    )
    return {
        "stages": stage_reports,
        "maximumStageEstimatedTokens": maximum_stage_tokens,
        "cumulativeEstimatedTokens": cumulative_tokens,
        "maximumStageBudget": _budget_assessment(
            maximum_stage_tokens, input_budget_tokens, thresholds
        ),
    }


def measure_provenance_growth(state: Mapping[str, object]) -> dict[str, object]:
    programs = state.get("programs")
    results = state.get("intermediateResults")
    if not isinstance(programs, dict) or not isinstance(results, dict):
        raise MathFlowError("builder scale provenance needs a two-entity state")
    components = {
        "rootSourceTransactionIds": programs["root"]["sourceTransactionIds"],
        "nonRootProgramSourceTransactionIds": {
            program_id: program["sourceTransactionIds"]
            for program_id, program in programs.items()
            if program_id != "root" and isinstance(program, dict)
        },
        "resultSourceTransactionIds": {
            result_id: result["sourceTransactionIds"]
            for result_id, result in results.items()
            if isinstance(result, dict)
        },
        "resultClaimRefs": {
            result_id: result["claimRefs"]
            for result_id, result in results.items()
            if isinstance(result, dict)
        },
        "resultJudgmentIds": {
            result_id: result["judgmentIds"]
            for result_id, result in results.items()
            if isinstance(result, dict)
        },
    }
    occurrences = {
        "rootSourceTransactions": len(programs["root"]["sourceTransactionIds"]),
        "nonRootProgramSourceTransactions": sum(
            len(program["sourceTransactionIds"])
            for program_id, program in programs.items()
            if program_id != "root" and isinstance(program, dict)
        ),
        "resultSourceTransactions": sum(
            len(result["sourceTransactionIds"])
            for result in results.values()
            if isinstance(result, dict)
        ),
        "resultClaimReferences": sum(
            len(result["claimRefs"])
            for result in results.values()
            if isinstance(result, dict)
        ),
        "resultJudgments": sum(
            len(result["judgmentIds"])
            for result in results.values()
            if isinstance(result, dict)
        ),
    }
    return {
        "occurrences": occurrences,
        "serialized": {
            name: measure_serialized_value(value)
            for name, value in components.items()
        },
        "allProvenance": measure_serialized_value(components),
    }


def measure_program_topology(state: Mapping[str, object]) -> dict[str, int]:
    programs = state.get("programs")
    if not isinstance(programs, dict):
        raise MathFlowError("builder scale topology needs programs")
    parents: dict[str, str | None] = {}
    child_counts = {str(program_id): 0 for program_id in programs}
    for program_id, program in programs.items():
        if not isinstance(program, dict):
            raise MathFlowError("builder scale topology has an invalid program")
        parent = program.get("parentId")
        parents[str(program_id)] = str(parent) if isinstance(parent, str) else None
        if isinstance(parent, str):
            child_counts[parent] += 1
    maximum_depth = max(
        len(_ancestors(program_id, parents)) - 1 for program_id in parents
    )
    return {
        "maximumDepth": maximum_depth,
        "maximumWidth": max(child_counts.values()),
    }


def _strip_provenance(value: object) -> object:
    if isinstance(value, dict):
        return {
            str(key): _strip_provenance(item)
            for key, item in value.items()
            if key not in PROVENANCE_FIELDS
        }
    if isinstance(value, list):
        return [_strip_provenance(item) for item in value]
    return copy.deepcopy(value)


def classify_capacity_outcome(
    *,
    prompt: object,
    input_budget_tokens: int,
    completion_limit_tokens: int,
    output_text: str = "",
    finish_reason: str | None = None,
    provider_prompt_tokens: int | None = None,
    provider_completion_tokens: int | None = None,
    semantic_checks: Mapping[str, bool] | None = None,
) -> dict[str, object]:
    """Keep input, output, and soft semantic failure classes disjoint."""

    if input_budget_tokens < 1 or completion_limit_tokens < 1:
        raise MathFlowError("builder scale capacity limits must be positive")
    prompt_measurement = measure_serialized_value(prompt)
    prompt_tokens = (
        provider_prompt_tokens
        if provider_prompt_tokens is not None
        else int(prompt_measurement["estimatedTokens"])
    )
    completion_tokens = provider_completion_tokens
    if completion_tokens is None:
        completion_tokens = math.ceil(len(output_text.encode("utf-8")) / 4)
    trailing_whitespace = len(output_text) - len(output_text.rstrip())
    repeated_run = 0
    prior = None
    current_run = 0
    for character in output_text:
        if character == prior:
            current_run += 1
        else:
            prior = character
            current_run = 1
        repeated_run = max(repeated_run, current_run)
    semantic = dict(semantic_checks or {})
    if prompt_tokens > input_budget_tokens:
        classification = "hard-input-exhaustion"
    elif finish_reason == "length" or completion_tokens >= completion_limit_tokens:
        classification = "hard-output-exhaustion"
    elif semantic and not all(semantic.values()):
        classification = "soft-semantic-degradation"
    else:
        classification = "passed"
    return {
        "classification": classification,
        "promptTokens": prompt_tokens,
        "promptTokenSource": (
            "provider-reported"
            if provider_prompt_tokens is not None
            else str(prompt_measurement["tokenEstimateMethod"])
        ),
        "inputBudgetTokens": input_budget_tokens,
        "completionTokens": completion_tokens,
        "completionTokenSource": (
            "provider-reported"
            if provider_completion_tokens is not None
            else "ceil(output-utf8-bytes/4)"
        ),
        "completionLimitTokens": completion_limit_tokens,
        "finishReason": finish_reason,
        "outputCharacters": len(output_text),
        "trailingWhitespaceCharacters": trailing_whitespace,
        "maximumRepeatedCharacterRun": repeated_run,
        "outputPathologyObserved": (
            trailing_whitespace > max(256, len(output_text) // 2)
            or repeated_run > 1024
        ),
        "semanticChecks": semantic,
    }


def score_adversarial_route_plan(
    fixture: Mapping[str, object],
    challenge_name: str,
    route_plan: Mapping[str, object],
) -> dict[str, object]:
    challenges = fixture.get("challenges")
    if not isinstance(challenges, dict) or not isinstance(
        challenges.get(challenge_name), dict
    ):
        raise MathFlowError("builder scale route scorer received an unknown challenge")
    challenge = challenges[challenge_name]
    selected_program_ids = {
        str(item) for item in route_plan.get("selectedProgramIds", [])
    }
    selected_result_ids = {
        str(item) for item in route_plan.get("selectedResultIds", [])
    }
    requested_write_ids = {
        str(item) for item in route_plan.get("requestedWriteIds", [])
    }
    checks = {
        "requiredProgramsLoaded": set(challenge.get("requiredProgramIds", []))
        <= selected_program_ids,
        "requiredResultsLoaded": set(challenge.get("requiredResultIds", []))
        <= selected_result_ids,
        "requiredWriteScopeLoaded": set(
            challenge.get("requiredWriteEntityIds", [])
        )
        <= requested_write_ids,
    }
    required_parent = challenge.get("requiredParentProgramId")
    if isinstance(required_parent, str):
        checks["requiredParentSelected"] = (
            route_plan.get("proposedParentProgramId") == required_parent
        )
    forbidden_parent = challenge.get("forbiddenParentProgramId")
    if isinstance(forbidden_parent, str):
        checks["forbiddenParentAvoided"] = (
            route_plan.get("proposedParentProgramId") != forbidden_parent
        )
    return {
        "challenge": challenge_name,
        "passed": all(checks.values()),
        "checks": checks,
        "missingProgramIds": sorted(
            set(challenge.get("requiredProgramIds", [])) - selected_program_ids
        ),
        "missingResultIds": sorted(
            set(challenge.get("requiredResultIds", [])) - selected_result_ids
        ),
        "missingWriteIds": sorted(
            set(challenge.get("requiredWriteEntityIds", [])) - requested_write_ids
        ),
    }


def build_positioned_semantic_probe(
    fixture: Mapping[str, object],
    challenge_name: str,
    position: str,
    *,
    distractor_limit: int = 63,
) -> dict[str, object]:
    """Place gold cards at the beginning, middle, or end of a soft-context probe."""

    if position not in {"beginning", "middle", "end"}:
        raise MathFlowError("builder scale semantic probe position is invalid")
    if distractor_limit < 3:
        raise MathFlowError("builder scale semantic probe needs at least three cards")
    state = fixture.get("state")
    challenges = fixture.get("challenges")
    if not isinstance(state, dict) or not isinstance(challenges, dict):
        raise MathFlowError("builder scale semantic probe received an invalid fixture")
    challenge = challenges.get(challenge_name)
    if not isinstance(challenge, dict):
        raise MathFlowError("builder scale semantic probe received an unknown challenge")
    catalog = build_trusted_search_catalog(state)
    gold_ids = {
        *map(str, challenge.get("requiredProgramIds", [])),
        *map(str, challenge.get("requiredResultIds", [])),
    }
    cards: list[dict[str, object]] = []
    for entity_kind, collection_name in (
        ("program", "programCards"),
        ("intermediateResult", "resultCards"),
    ):
        collection = catalog[collection_name]
        assert isinstance(collection, dict)
        cards.extend(
            {"entityKind": entity_kind, **copy.deepcopy(card)}
            for card in collection.values()
        )
    gold = [card for card in cards if str(card["id"]) in gold_ids]
    distractors = [card for card in cards if str(card["id"]) not in gold_ids][
        :distractor_limit
    ]
    insertion = {
        "beginning": 0,
        "middle": len(distractors) // 2,
        "end": len(distractors),
    }[position]
    ordered = [*distractors[:insertion], *gold, *distractors[insertion:]]
    core = {
        "schemaVersion": 1,
        "challenge": challenge_name,
        "position": position,
        "query": challenge.get("query"),
        "cards": ordered,
        "expectedEntityIds": sorted(gold_ids),
    }
    return {**core, "probeDigest": "sha256:" + sha256_json(core)}


def score_positioned_semantic_probe(
    probe: Mapping[str, object], selected_entity_ids: Sequence[str]
) -> dict[str, object]:
    expected = {str(item) for item in probe.get("expectedEntityIds", [])}
    selected = {str(item) for item in selected_entity_ids}
    missing = sorted(expected - selected)
    return {
        "passed": not missing,
        "expectedEntityIds": sorted(expected),
        "selectedEntityIds": sorted(selected),
        "missingEntityIds": missing,
    }


def default_scale_configurations() -> tuple[SyntheticBuilderStateConfig, ...]:
    return (
        SyntheticBuilderStateConfig(16, 24, 3, 3, 1, 2, 2),
        SyntheticBuilderStateConfig(64, 128, 4, 3, 4, 3, 3),
        SyntheticBuilderStateConfig(256, 512, 5, 4, 8, 4, 4),
        SyntheticBuilderStateConfig(1024, 2048, 6, 4, 16, 5, 5),
    )


def run_provider_free_builder_context_scale_probe(
    configurations: Sequence[SyntheticBuilderStateConfig] | None = None,
    *,
    input_budget_tokens: int = 128_000,
    challenge_name: str = "dependency-closure",
    strategies: Mapping[str, ContextStrategy] | None = None,
) -> dict[str, object]:
    """Measure scale/locality and deterministic adversarial gold with zero calls."""

    selected_configurations = tuple(configurations or default_scale_configurations())
    if not selected_configurations:
        raise MathFlowError("builder scale probe needs at least one configuration")
    strategy_map: Mapping[str, ContextStrategy] = strategies or {
        "v9-all-core": build_v9_context_view,
        "bounded-semantic": build_bounded_semantic_context_view,
        "bounded-exact-provenance": build_bounded_exact_context_view,
    }
    if not strategy_map:
        raise MathFlowError("builder scale probe needs at least one context strategy")
    cases: list[dict[str, object]] = []
    for configuration in selected_configurations:
        fixture = build_synthetic_builder_fixture(configuration)
        state = fixture["state"]
        assert isinstance(state, dict)
        strategy_reports = {
            name: measure_context_view(
                strategy(fixture, challenge_name),
                input_budget_tokens=input_budget_tokens,
            )
            for name, strategy in strategy_map.items()
        }
        v9_report = strategy_reports.get("v9-all-core")
        comparisons: dict[str, object] = {}
        if isinstance(v9_report, dict):
            v9_maximum = int(v9_report["maximumStageEstimatedTokens"])
            for name, report in strategy_reports.items():
                maximum = int(report["maximumStageEstimatedTokens"])
                comparisons[name] = {
                    "maximumStageRatioToV9": maximum / v9_maximum,
                    "maximumStageTokenReductionPercent": 100
                    * (1 - maximum / v9_maximum),
                    "cumulativeRatioToV9SingleCall": int(
                        report["cumulativeEstimatedTokens"]
                    )
                    / int(v9_report["cumulativeEstimatedTokens"]),
                }
            v9_context = build_research_builder_v9_context(
                state, fixture["acceptedClaims"]
            )
            v9_full = measure_serialized_value(v9_context)
            v9_stripped = measure_serialized_value(_strip_provenance(v9_context))
            comparisons["v9ProvenanceOverhead"] = {
                "fullEstimatedTokens": v9_full["estimatedTokens"],
                "withoutCumulativeProvenanceEstimatedTokens": v9_stripped[
                    "estimatedTokens"
                ],
                "estimatedProvenanceOverheadTokens": int(
                    v9_full["estimatedTokens"]
                )
                - int(v9_stripped["estimatedTokens"]),
                "estimatedProvenanceOverheadPercent": 100
                * (
                    1
                    - int(v9_stripped["estimatedTokens"])
                    / int(v9_full["estimatedTokens"])
                ),
            }

        challenges = fixture["challenges"]
        assert isinstance(challenges, dict)
        scorer_checks: dict[str, object] = {}
        for name, challenge in challenges.items():
            assert isinstance(challenge, dict)
            complete_plan = {
                "selectedProgramIds": challenge.get("requiredProgramIds", []),
                "selectedResultIds": challenge.get("requiredResultIds", []),
                "requestedWriteIds": challenge.get("requiredWriteEntityIds", []),
                "proposedParentProgramId": challenge.get(
                    "requiredParentProgramId"
                ),
            }
            scorer_checks[name] = {
                "goldPlan": score_adversarial_route_plan(
                    fixture, name, complete_plan
                ),
                "emptyPlan": score_adversarial_route_plan(fixture, name, {}),
            }
        position_probes = {
            position: measure_serialized_value(
                build_positioned_semantic_probe(
                    fixture,
                    "distant-duplicate",
                    position,
                )
            )
            for position in ("beginning", "middle", "end")
            if "distant-duplicate" in challenges
        }
        cases.append(
            {
                "configuration": fixture["configuration"],
                "fixtureDigest": fixture["fixtureDigest"],
                "state": {
                    "stateDigest": state["stateDigest"],
                    "programCount": len(state["programs"]),
                    "resultCount": len(state["intermediateResults"]),
                    "contributionCount": len(state["contributions"]),
                    "topology": measure_program_topology(state),
                    "dependencyClosureResultCount": len(
                        fixture["challenges"][challenge_name]["requiredResultIds"]
                    ),
                    "serialized": measure_serialized_value(state),
                },
                "provenance": measure_provenance_growth(state),
                "strategies": strategy_reports,
                "comparisons": comparisons,
                "adversarialScorers": scorer_checks,
                "softSemanticProbeSizes": position_probes,
            }
        )

    all_gold_pass = all(
        bool(checks["goldPlan"]["passed"])
        for case in cases
        for checks in case["adversarialScorers"].values()
    )
    all_nontrivial_empty_plans_fail = all(
        not bool(checks["emptyPlan"]["passed"])
        for case in cases
        for checks in case["adversarialScorers"].values()
        if any(
            checks["emptyPlan"]["missingProgramIds"]
            or checks["emptyPlan"]["missingResultIds"]
            or checks["emptyPlan"]["missingWriteIds"]
        )
    )
    return {
        "schemaVersion": 1,
        "status": "passed" if all_gold_pass else "failed",
        "providerCalls": 0,
        "inputBudgetTokens": input_budget_tokens,
        "challenge": challenge_name,
        "tokenTelemetry": {
            "source": "provider-free-estimate",
            "method": "ceil(compact-utf8-bytes/4)",
            "warning": (
                "Use provider-reported token counts for live attempts; this estimate "
                "identifies scale trends and candidate budget crossings only."
            ),
        },
        "cases": cases,
        "verifiedInvariants": {
            "allSyntheticStatesValidate": True,
            "providerCallsRemainZero": True,
            "cumulativeProvenanceMeasuredSeparately": True,
            "fullV9AndBoundedPacketsCompared": "v9-all-core" in strategy_map,
            "goldAdversarialPlansPass": all_gold_pass,
            "incompleteAdversarialPlansFail": all_nontrivial_empty_plans_fail,
            "inputOutputAndSoftFailureClassesAreDistinct": True,
        },
    }


__all__ = [
    "ADVERSARIAL_CHALLENGES",
    "ContextStrategy",
    "SyntheticBuilderStateConfig",
    "build_bounded_local_packet_model",
    "build_positioned_semantic_probe",
    "build_synthetic_builder_fixture",
    "build_trusted_search_catalog",
    "classify_capacity_outcome",
    "default_scale_configurations",
    "measure_context_view",
    "measure_program_topology",
    "measure_provenance_growth",
    "measure_serialized_value",
    "make_v10_context_strategy",
    "run_provider_free_builder_context_scale_probe",
    "score_adversarial_route_plan",
    "score_positioned_semantic_probe",
]
