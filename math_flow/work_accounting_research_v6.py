"""Verified, provider-free consumption of published research-v6 transitions."""

from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from .artifacts import read_verified_artifact
from .errors import MathFlowError
from .research_builder_v6 import (
    apply_research_builder_v6_transition,
    validate_research_builder_v6_handoff,
)
from .research_projection import (
    load_research_build_bundle,
    validate_research_builder_v6_submission_input,
)
from .research_topology import (
    validate_research_program_state_v2,
    validate_research_topology_alignment,
)
from .work_accounting_pipeline import validate_work_accounting_submission_input


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class PublishedResearchV6Transition:
    """One fully verified adjacent transition from a published v6 run bundle."""

    bundle_dir: Path
    bundle_digest: str
    manifest: dict[str, object]
    submission: dict[str, object]
    base_knowledge_state: dict[str, object]
    target_knowledge_state: dict[str, object]
    transition: dict[str, object]
    topology_alignment: dict[str, object]
    same_world_handoff: dict[str, object]


def _require_digest(value: object, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not DIGEST.fullmatch(value):
        raise MathFlowError(f"{label} must be a sha256 digest")
    return value


def _json_artifact(
    bundle_dir: Path, manifest: dict[str, object], role: str
) -> dict[str, object]:
    try:
        value = json.loads(read_verified_artifact(bundle_dir, manifest, role))
    except json.JSONDecodeError as exc:
        raise MathFlowError(
            f"published research-v6 artifact {role!r} is not valid JSON"
        ) from exc
    if not isinstance(value, dict):
        raise MathFlowError(
            f"published research-v6 artifact {role!r} must be an object"
        )
    return value


def load_published_research_v6_transition(
    bundle_dir: Path,
    *,
    expected_bundle_digest: str | None = None,
    expected_problem: str | None = None,
    expected_projection_spec_digest: str | None = None,
    expected_builder_spec_digest: str | None = None,
) -> PublishedResearchV6Transition:
    """Load one immutable v6 bundle and independently replay every derived value."""

    bundle = bundle_dir.resolve()
    if not bundle.is_dir() or bundle.is_symlink():
        raise MathFlowError("published research-v6 bundle must be a regular directory")
    manifest, target_state, bundle_digest = load_research_build_bundle(bundle)
    if manifest.get("outputProfile") != "math-flow/hierarchical-research-v6":
        raise MathFlowError("published research transition is not a v6 bundle")
    if expected_bundle_digest is not None:
        _require_digest(expected_bundle_digest, "expected research-v6 bundle digest")
        if bundle_digest != expected_bundle_digest:
            raise MathFlowError("published research-v6 bundle digest mismatch")
    problem = manifest.get("problemId")
    if not isinstance(problem, str) or (
        expected_problem is not None and problem != expected_problem
    ):
        raise MathFlowError("published research-v6 bundle belongs to another problem")
    inputs = manifest.get("inputs")
    judge = manifest.get("judgeSpec")
    if not isinstance(inputs, dict) or not isinstance(judge, dict):
        raise MathFlowError("published research-v6 bundle has invalid identities")
    projection_digest = _require_digest(
        inputs.get("projectionSpecDigest"), "research-v6 projection spec digest"
    )
    builder_digest = _require_digest(
        judge.get("digest"), "research-v6 builder spec digest"
    )
    if (
        expected_projection_spec_digest is not None
        and projection_digest != expected_projection_spec_digest
    ):
        raise MathFlowError("published research-v6 projection identity mismatch")
    if (
        expected_builder_spec_digest is not None
        and builder_digest != expected_builder_spec_digest
    ):
        raise MathFlowError("published research-v6 builder identity mismatch")

    base_state = validate_research_program_state_v2(
        _json_artifact(bundle, manifest, "research-program-base-state"), problem
    )
    target_state = validate_research_program_state_v2(target_state, problem)
    submission = validate_research_builder_v6_submission_input(
        _json_artifact(bundle, manifest, "research-builder-submission-input")
    )
    transition = _json_artifact(bundle, manifest, "research-program-transition")
    alignment = validate_research_topology_alignment(
        _json_artifact(bundle, manifest, "research-topology-alignment"),
        base_state,
        target_state,
    )
    handoff = validate_research_builder_v6_handoff(
        _json_artifact(bundle, manifest, "research-builder-handoff"),
        base_state,
        target_state,
        alignment,
        str(submission["subjectTransactionId"]),
    )
    reduced = apply_research_builder_v6_transition(
        base_state,
        transition,
        accepted_claims=submission["acceptedClaims"],
        judgment_id=str(submission["judgmentId"]),
    )
    if (
        reduced["postState"] != target_state
        or reduced["topologyAlignment"] != alignment
        or reduced["sameWorldHandoff"] != handoff
    ):
        raise MathFlowError(
            "published research-v6 derived artifacts differ from reducer replay"
        )
    subject = str(submission["subjectTransactionId"])
    if (
        transition.get("subjectTransactionId") != subject
        or manifest.get("ledgerHead") != subject
        or target_state.get("ledgerHead") != subject
    ):
        raise MathFlowError("published research-v6 subject binding mismatch")

    return PublishedResearchV6Transition(
        bundle_dir=bundle,
        bundle_digest=bundle_digest,
        manifest=copy.deepcopy(manifest),
        submission=copy.deepcopy(submission),
        base_knowledge_state=copy.deepcopy(base_state),
        target_knowledge_state=copy.deepcopy(target_state),
        transition=copy.deepcopy(transition),
        topology_alignment=copy.deepcopy(alignment),
        same_world_handoff=copy.deepcopy(handoff),
    )


def _published_bundle_path(projection_root: Path, digest: str) -> Path:
    _require_digest(digest, "published research-v6 run digest")
    digest_hex = digest.removeprefix("sha256:")
    root = projection_root.resolve()
    target = root / "objects" / "knowledge-build" / digest_hex[:2] / digest_hex
    if not target.is_dir() or target.is_symlink():
        raise MathFlowError(f"published research-v6 run is missing: {digest}")
    try:
        target.resolve().relative_to(root)
    except ValueError as exc:  # pragma: no cover - constructed beneath root
        raise MathFlowError("published research-v6 bundle escapes projection root") from exc
    return target


def load_published_research_v6_chain(
    projection_root: Path,
    terminal_bundle_digest: str,
    *,
    expected_problem: str | None = None,
    expected_projection_spec_digest: str | None = None,
    expected_builder_spec_digest: str | None = None,
    maximum_transitions: int = 10_000,
) -> list[PublishedResearchV6Transition]:
    """Load a complete terminal-to-origin v6 predecessor chain in forward order."""

    if (
        not isinstance(maximum_transitions, int)
        or isinstance(maximum_transitions, bool)
        or maximum_transitions < 1
    ):
        raise MathFlowError("published research-v6 chain limit must be positive")
    current: str | None = str(
        _require_digest(terminal_bundle_digest, "terminal research-v6 run digest")
    )
    reverse_chain: list[PublishedResearchV6Transition] = []
    seen: set[str] = set()
    while current is not None:
        if current in seen:
            raise MathFlowError("published research-v6 predecessor chain contains a cycle")
        if len(reverse_chain) >= maximum_transitions:
            raise MathFlowError("published research-v6 predecessor chain exceeds its limit")
        seen.add(current)
        loaded = load_published_research_v6_transition(
            _published_bundle_path(projection_root, current),
            expected_bundle_digest=current,
            expected_problem=expected_problem,
            expected_projection_spec_digest=expected_projection_spec_digest,
            expected_builder_spec_digest=expected_builder_spec_digest,
        )
        reverse_chain.append(loaded)
        current = _require_digest(
            loaded.manifest.get("baseRun"),
            "research-v6 predecessor run",
            nullable=True,
        )

    chain = list(reversed(reverse_chain))
    previous: PublishedResearchV6Transition | None = None
    for loaded in chain:
        if previous is None:
            if loaded.manifest.get("baseRun") is not None:
                raise MathFlowError("published research-v6 chain does not reach its origin")
        elif (
            loaded.manifest.get("baseRun") != previous.bundle_digest
            or loaded.base_knowledge_state != previous.target_knowledge_state
            or int(loaded.submission["ledgerOrdinal"])
            <= int(previous.submission["ledgerOrdinal"])
        ):
            raise MathFlowError("published research-v6 predecessor states do not compose")
        previous = loaded
    return chain


class PublishedResearchV6TransitionProvider:
    """Callable pipeline provider backed only by already-published v6 bundles."""

    def __init__(self, transitions: Sequence[PublishedResearchV6Transition]):
        loaded = list(transitions)
        if not loaded:
            raise MathFlowError("published research-v6 provider requires transitions")
        subjects = [
            str(item.submission["subjectTransactionId"]) for item in loaded
        ]
        if len(subjects) != len(set(subjects)):
            raise MathFlowError("published research-v6 provider repeats a subject")
        for previous, current in zip(loaded, loaded[1:]):
            if (
                current.manifest.get("baseRun") != previous.bundle_digest
                or current.base_knowledge_state != previous.target_knowledge_state
            ):
                raise MathFlowError("published research-v6 provider chain is not adjacent")
        self._transitions = {
            subject: item for subject, item in zip(subjects, loaded)
        }

    @classmethod
    def from_published_chain(
        cls,
        projection_root: Path,
        terminal_bundle_digest: str,
        **kwargs: object,
    ) -> "PublishedResearchV6TransitionProvider":
        return cls(
            load_published_research_v6_chain(
                projection_root, terminal_bundle_digest, **kwargs
            )
        )

    def __call__(
        self,
        *,
        base_knowledge_state: Mapping[str, object],
        submission: Mapping[str, object],
    ) -> object:
        pipeline_submission = validate_work_accounting_submission_input(
            copy.deepcopy(dict(submission))
        )
        subject = str(pipeline_submission["transactionId"])
        loaded = self._transitions.get(subject)
        if loaded is None:
            raise MathFlowError(
                f"published research-v6 transition is unavailable for subject {subject}"
            )
        base = validate_research_program_state_v2(
            copy.deepcopy(dict(base_knowledge_state)),
            str(pipeline_submission["problemId"]),
        )
        published_submission = loaded.submission
        evidence = pipeline_submission["evidenceManifest"]
        if (
            base != loaded.base_knowledge_state
            or pipeline_submission["problemId"] != loaded.manifest["problemId"]
            or subject != published_submission["subjectTransactionId"]
            or pipeline_submission["ordinal"] != published_submission["ledgerOrdinal"]
            or pipeline_submission["judgmentId"] != published_submission["judgmentId"]
            or pipeline_submission["acceptedClaims"]
            != published_submission["acceptedClaims"]
            or not isinstance(evidence, dict)
            or evidence.get("manifestDigest")
            != published_submission["evidenceManifestDigest"]
        ):
            raise MathFlowError(
                "work-accounting submission does not match its published research-v6 transition"
            )
        return copy.deepcopy(loaded.transition)
