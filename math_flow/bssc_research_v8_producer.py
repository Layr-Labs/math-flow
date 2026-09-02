"""Provider-free frontier planning for the serial BSSC Builder V10 lane."""

from __future__ import annotations

from pathlib import Path

from .bssc_research_v4_producer import (
    SerialBSSCResearchLane,
    _plan_bssc_research_frontier,
    load_json_file,
)


V8_LANE = SerialBSSCResearchLane(
    projection_id="openrouter-research-v8",
    builder_path="protocol/judges/openrouter-hierarchical-research-builder-v10.json",
    builder_profile="math-flow/hierarchical-research-v10",
    builder_implementation="openrouter-hierarchical-research-builder-v10",
    label="builder-v10",
    state_schema_version=3,
)


def plan_bssc_research_v8_frontier(
    repository_root: Path,
    *,
    projection_root: Path,
    scheduler_file: Path,
    materialization_root: Path,
    replay_source: object,
    projection: object,
    expected_projection_digest: str | None = None,
) -> dict[str, object]:
    """Expose one canonical accepted submission for a fresh V10 transition."""

    return _plan_bssc_research_frontier(
        repository_root,
        projection_root=projection_root,
        scheduler_file=scheduler_file,
        materialization_root=materialization_root,
        replay_source=replay_source,
        projection=projection,
        lane=V8_LANE,
        expected_projection_digest=expected_projection_digest,
    )


__all__ = ["load_json_file", "plan_bssc_research_v8_frontier"]
