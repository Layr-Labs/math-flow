from __future__ import annotations

import json
from pathlib import Path

from .directions import research_direction_ledger, validate_direction_event
from .errors import MathFlowError
from .governance import list_active_projections
from .repository import read_at, resolve_commit, sha256_json, validate_slug


CREDIT_INPUT_CAPABILITIES = {
    "locked-knowledge-ledger-v1": [
        "canonical-contribution-ledger",
        "knowledge-state",
    ],
    "locked-knowledge-ledger-directions-v2": [
        "canonical-contribution-ledger",
        "knowledge-state",
        "research-direction-events",
    ],
    "locked-research-history-v2": [
        "research-program-state",
        "accepted-submission-content",
        "validity-records",
        "serialized-research-state-history",
    ],
}


def _json_object(text: str, label: str) -> dict[str, object]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise MathFlowError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise MathFlowError(f"{label} must be a JSON object")
    return value


def credit_status(
    root: Path, problem: str, head: str = "HEAD"
) -> dict[str, object]:
    """Describe active credit policies without requiring or running an overlay."""

    root = root.resolve()
    validate_slug(problem, "problem id")
    canonical_head = resolve_commit(root, head)
    active = list_active_projections(
        root, problem, canonical_head, engine="overlay-repository-v1"
    )
    directions = research_direction_ledger(root, problem, canonical_head)
    overlays: list[dict[str, object]] = []
    registration_aware: list[str] = []
    for projection in active["projections"]:
        runner = projection.get("runner")
        if (
            not isinstance(runner, dict)
            or not isinstance(runner.get("spec"), str)
            or not isinstance(runner.get("implementation"), str)
        ):
            raise MathFlowError("active credit projection has no governed runner")
        spec_path = str(runner["spec"])
        spec = _json_object(
            read_at(root, canonical_head, spec_path),
            f"credit policy specification {spec_path}",
        )
        if spec.get("implementation") != runner["implementation"]:
            raise MathFlowError("credit projection runner does not match its policy spec")
        input_builder = spec.get("inputBuilder")
        if not isinstance(input_builder, str):
            raise MathFlowError("credit policy has no input builder")
        capabilities = CREDIT_INPUT_CAPABILITIES.get(input_builder)
        if capabilities is None:
            raise MathFlowError(
                f"credit policy uses an unsupported input builder: {input_builder}"
            )
        consumes_registrations = "research-direction-events" in capabilities
        projection_id = str(projection["projectionId"])
        if consumes_registrations:
            registration_aware.append(projection_id)
        rubric = spec.get("rubric")
        overlays.append(
            {
                "projectionId": projection_id,
                "projectionSpecDigest": projection["projectionSpecDigest"],
                "description": spec.get("description", ""),
                "runner": {
                    "implementation": runner["implementation"],
                    "specPath": spec_path,
                    "specDigest": f"sha256:{sha256_json(spec)}",
                    "inputBuilder": input_builder,
                    "outputProfile": spec.get("outputProfile"),
                },
                "inputCapabilities": list(capabilities),
                "consumesResearchDirectionEvents": consumes_registrations,
                "dependencies": projection["dependencies"],
                "scheduling": projection["scheduling"],
                "rubric": rubric if isinstance(rubric, dict) else {},
            }
        )
    overlays.sort(key=lambda item: str(item["projectionId"]))
    registration_aware.sort()
    if registration_aware:
        message = (
            "Registration events are inputs to the listed active credit overlays, "
            "but remain non-exclusive evidence rather than ownership or guaranteed credit."
        )
    elif overlays:
        message = (
            "Active credit overlays do not consume research-direction events; "
            "registration remains useful only for coordination and provenance."
        )
    else:
        message = (
            "No active credit overlay applies to this problem; registration remains "
            "useful only for coordination and provenance unless policy changes later."
        )
    return {
        "schemaVersion": 1,
        "problemId": problem,
        "canonicalHead": canonical_head,
        "directionState": {
            "eventCount": len(directions["events"]),
            "activeDirectionIds": sorted(
                str(item["directionId"])
                for item in directions["directions"]
                if item["status"] == "active"
            ),
        },
        "activeCreditOverlays": overlays,
        "registrationAwareOverlayIds": registration_aware,
        "registrationAffectsActiveCreditPolicy": bool(registration_aware),
        "message": message,
    }


def register_direction(
    root: Path,
    problem: str,
    direction: str,
    event: str,
    title: str,
    summary: str,
    plan_file: Path,
    node_ids: list[str],
    head: str = "HEAD",
) -> dict[str, object]:
    """Scaffold one policy-neutral register event at its canonical repository path."""

    root = root.resolve()
    validate_slug(problem, "problem id")
    validate_slug(direction, "research direction id")
    validate_slug(event, "research direction event id")
    canonical_head = resolve_commit(root, head)
    existing = research_direction_ledger(root, problem, canonical_head)
    if any(item["directionId"] == direction for item in existing["directions"]):
        raise MathFlowError(f"research direction already exists: {direction}")
    if not plan_file.is_file():
        raise MathFlowError(f"research direction plan file does not exist: {plan_file}")
    plan = plan_file.read_text(encoding="utf-8")
    if not plan.strip():
        raise MathFlowError("research direction plan file must contain Markdown")
    normalized_nodes = sorted(set(node_ids))
    if normalized_nodes != node_ids:
        raise MathFlowError(
            "related knowledge node IDs must be unique and sorted"
        )
    value = validate_direction_event(
        {
            "schemaVersion": 1,
            "eventType": "register",
            "eventId": event,
            "directionId": direction,
            "title": title,
            "summary": summary,
            "relatedKnowledgeNodeIds": normalized_nodes,
        },
        expected_direction_id=direction,
        expected_event_id=event,
    )
    relative = Path("problems") / problem / "directions" / direction / "events" / event
    target = root / relative
    if target.exists():
        raise MathFlowError(f"research direction event path already exists: {relative}")
    direction_root = root / "problems" / problem / "directions" / direction
    if direction_root.exists():
        raise MathFlowError(f"research direction path already exists: {direction}")
    target.mkdir(parents=True)
    readme = target / "README.md"
    event_json = target / "event.json"
    readme.write_text(plan.rstrip() + "\n", encoding="utf-8")
    event_json.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {
        "schemaVersion": 1,
        "problemId": problem,
        "directionId": direction,
        "eventId": event,
        "eventType": "register",
        "canonicalHead": canonical_head,
        "path": relative.as_posix(),
        "files": [
            readme.relative_to(root).as_posix(),
            event_json.relative_to(root).as_posix(),
        ],
        "creditPolicyInterpreted": False,
        "nextCommand": "python3 -m math_flow validate-tree",
    }
