"""Provider-free frontier planning for the serial BSSC builder-v7 producer."""

from __future__ import annotations

from pathlib import Path

from .bssc_research_v4_producer import (
    SerialBSSCResearchLane,
    _plan_bssc_research_frontier,
    load_json_file,
)


V5_LANE = SerialBSSCResearchLane(
    projection_id="openrouter-research-v5",
    builder_path="protocol/judges/openrouter-hierarchical-research-builder-v7.json",
    builder_profile="math-flow/hierarchical-research-v7",
    builder_implementation="openrouter-hierarchical-research-builder-v7",
    label="builder-v7",
    state_schema_version=3,
)


def plan_bssc_research_v5_frontier(
    repository_root: Path,
    *,
    projection_root: Path,
    scheduler_file: Path,
    materialization_root: Path,
    replay_source: object,
    projection: object,
    expected_projection_digest: str | None = None,
) -> dict[str, object]:
    """Expose one canonical accepted submission for a state-v3 V5 transition."""

    return _plan_bssc_research_frontier(
        repository_root,
        projection_root=projection_root,
        scheduler_file=scheduler_file,
        materialization_root=materialization_root,
        replay_source=replay_source,
        projection=projection,
        lane=V5_LANE,
        expected_projection_digest=expected_projection_digest,
    )


__all__ = ["load_json_file", "plan_bssc_research_v5_frontier"]
