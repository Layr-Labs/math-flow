"""Verified, provider-free consumption of published Builder V10 transitions."""

from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from .artifacts import read_verified_artifact
from .errors import MathFlowError
from .research_builder_v7 import (
    validate_research_builder_v7_handoff,
    validate_research_program_state_v3,
    validate_research_topology_alignment_v2,
)
from .research_projection import (
    load_research_build_bundle,
    validate_research_builder_v10_submission_input,
)
from .work_accounting_pipeline_v3 import validate_work_accounting_submission_input


DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class PublishedResearchV10Transition:
    """One fully verified adjacent transition from a published V10 bundle."""

    bundle_dir: Path
    bundle_digest: str
    manifest: dict[str, object]
    submission: dict[str, object]
    base_knowledge_state: dict[str, object]
    target_knowledge_state: dict[str, object]
    transition: dict[str, object]
    topology_alignment: dict[str, object]
    same_world_handoff: dict[str, object]


def _require_digest(value: object, label: str) -> str:
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
            f"published research-v10 artifact {role!r} is not valid JSON"
        ) from exc
    if not isinstance(value, dict):
        raise MathFlowError(
            f"published research-v10 artifact {role!r} must be an object"
        )
    return value


def load_published_research_v10_transition(
    bundle_dir: Path,
    *,
    expected_bundle_digest: str | None = None,
    expected_problem: str | None = None,
    expected_projection_spec_digest: str | None = None,
    expected_builder_spec_digest: str | None = None,
) -> PublishedResearchV10Transition:
    """Load one immutable V10 bundle after its full local-context replay."""

    bundle = bundle_dir.resolve()
    if not bundle.is_dir() or bundle.is_symlink():
        raise MathFlowError("published research-v10 bundle must be a regular directory")
    manifest, target_state, bundle_digest = load_research_build_bundle(bundle)
    if manifest.get("outputProfile") != "math-flow/hierarchical-research-v10":
        raise MathFlowError("published research transition is not a v10 bundle")
    if expected_bundle_digest is not None and bundle_digest != _require_digest(
        expected_bundle_digest, "expected research-v10 bundle digest"
    ):
        raise MathFlowError("published research-v10 bundle digest mismatch")
    problem = manifest.get("problemId")
    if not isinstance(problem, str) or (
        expected_problem is not None and problem != expected_problem
    ):
        raise MathFlowError("published research-v10 bundle belongs to another problem")
    inputs = manifest.get("inputs")
    judge = manifest.get("judgeSpec")
    if not isinstance(inputs, dict) or not isinstance(judge, dict):
        raise MathFlowError("published research-v10 bundle has invalid identities")
    projection_digest = _require_digest(
        inputs.get("projectionSpecDigest"), "research-v10 projection spec digest"
    )
    builder_digest = _require_digest(
        judge.get("digest"), "research-v10 builder spec digest"
    )
    if (
        expected_projection_spec_digest is not None
        and projection_digest != expected_projection_spec_digest
    ):
        raise MathFlowError("published research-v10 projection identity mismatch")
    if (
        expected_builder_spec_digest is not None
        and builder_digest != expected_builder_spec_digest
    ):
        raise MathFlowError("published research-v10 builder identity mismatch")

    base_state = validate_research_program_state_v3(
        _json_artifact(bundle, manifest, "research-program-base-state"), problem
    )
    target_state = validate_research_program_state_v3(target_state, problem)
    submission = validate_research_builder_v10_submission_input(
        _json_artifact(bundle, manifest, "research-builder-submission-input")
    )
    transition = _json_artifact(bundle, manifest, "research-program-transition")
    alignment = validate_research_topology_alignment_v2(
        _json_artifact(bundle, manifest, "research-topology-alignment"),
        base_state,
        target_state,
    )
    handoff = validate_research_builder_v7_handoff(
        _json_artifact(bundle, manifest, "research-builder-handoff"),
        base_state,
        target_state,
        alignment,
        str(submission["subjectTransactionId"]),
    )
    subject = str(submission["subjectTransactionId"])
    if (
        transition.get("subjectTransactionId") != subject
        or manifest.get("ledgerHead") != subject
        or target_state.get("ledgerHead") != subject
    ):
        raise MathFlowError("published research-v10 subject binding mismatch")
    return PublishedResearchV10Transition(
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


class PublishedResearchV10TransitionProvider:
    """Pipeline provider backed only by already-published V10 bundles."""

    def __init__(self, transitions: Sequence[PublishedResearchV10Transition]):
        loaded = list(transitions)
        if not loaded:
            raise MathFlowError("published research-v10 provider requires transitions")
        subjects = [str(item.submission["subjectTransactionId"]) for item in loaded]
        if len(subjects) != len(set(subjects)):
            raise MathFlowError("published research-v10 provider repeats a subject")
        self._transitions = dict(zip(subjects, loaded))

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
                f"published research-v10 transition is unavailable for subject {subject}"
            )
        base = validate_research_program_state_v3(
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
                "work-accounting submission does not match its published research-v10 transition"
            )
        return copy.deepcopy(loaded.transition)


__all__ = [
    "PublishedResearchV10Transition",
    "PublishedResearchV10TransitionProvider",
    "load_published_research_v10_transition",
]
