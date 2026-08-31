"""Provider-free frontier planning for the serial BSSC Builder V9 experiment."""

from __future__ import annotations

from pathlib import Path

from .bssc_research_v4_producer import (
    SerialBSSCResearchLane,
    _plan_bssc_research_frontier,
    load_json_file,
)


V7_LANE = SerialBSSCResearchLane(
    projection_id="openrouter-research-v7",
    builder_path="protocol/judges/openrouter-hierarchical-research-builder-v9.json",
    builder_profile="math-flow/hierarchical-research-v9",
    builder_implementation="openrouter-hierarchical-research-builder-v9",
    label="builder-v9",
    state_schema_version=3,
)


def plan_bssc_research_v7_frontier(
    repository_root: Path,
    *,
    projection_root: Path,
    scheduler_file: Path,
    materialization_root: Path,
    replay_source: object,
    projection: object,
    expected_projection_digest: str | None = None,
) -> dict[str, object]:
    """Expose one canonical accepted submission for a fresh V9 transition."""

    return _plan_bssc_research_frontier(
        repository_root,
        projection_root=projection_root,
        scheduler_file=scheduler_file,
        materialization_root=materialization_root,
        replay_source=replay_source,
        projection=projection,
        lane=V7_LANE,
        expected_projection_digest=expected_projection_digest,
    )


__all__ = ["load_json_file", "plan_bssc_research_v7_frontier"]
