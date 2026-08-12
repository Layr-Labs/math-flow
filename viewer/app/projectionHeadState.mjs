function projectionById(catalog, projectionId) {
  if (!projectionId) return null;
  return catalog.projections?.find((projection) => projection.id === projectionId) ?? null;
}

function creditProjectionById(catalog, projectionId) {
  if (!projectionId) return null;
  return catalog.creditProjections?.find((projection) => projection.id === projectionId) ?? null;
}

export function publishedHeadSelectionPatch(previousCatalog, nextCatalog, viewerState) {
  const patch = {};
  const previousKnowledge = projectionById(previousCatalog, viewerState.projectionId);
  const nextKnowledge = projectionById(nextCatalog, viewerState.projectionId);

  if (previousKnowledge && nextKnowledge) {
    const previousHead = previousKnowledge.data.latestRunId;
    const nextHead = nextKnowledge.data.latestRunId;
    const selectedRun = viewerState.runId ?? previousHead;

    if (selectedRun === previousHead && nextHead !== selectedRun) patch.runId = nextHead;
  }

  const previousCredit = creditProjectionById(previousCatalog, viewerState.creditProjectionId);
  const nextCredit = creditProjectionById(nextCatalog, viewerState.creditProjectionId);

  if (previousCredit && nextCredit && nextCredit.latestRunDigest) {
    const previousHead = previousCredit.latestRunDigest;
    const selectedRun = viewerState.creditRunId;
    const wasWaitingForFirstRun = previousHead === null && previousCredit.runs.length === 0 && selectedRun === undefined;
    const wasFollowingHead = previousHead !== null && (selectedRun ?? previousHead) === previousHead;

    if ((wasWaitingForFirstRun || wasFollowingHead) && nextCredit.latestRunDigest !== selectedRun) {
      patch.creditRunId = nextCredit.latestRunDigest;
    }
  }

  return patch;
}

export function knowledgeRunSelectionPatch({ problemId, projectionId, runId }) {
  return { problemId, projectionId, runId };
}

export function creditRunSelectionPatch({ projectionId, runId }) {
  return { creditProjectionId: projectionId, creditRunId: runId };
}

export function historicalOverlaySelection({
  knowledgeRunId,
  knowledgeLatestRunId,
  creditRunId,
  creditLatestRunDigest,
}) {
  const knowledge = Boolean(
    knowledgeRunId && knowledgeLatestRunId && knowledgeRunId !== knowledgeLatestRunId,
  );
  const credit = Boolean(
    creditRunId && creditLatestRunDigest && creditRunId !== creditLatestRunDigest,
  );

  return { knowledge, credit, any: knowledge || credit };
}

export function latestOverlaySelectionPatch(selection) {
  const historical = historicalOverlaySelection(selection);
  const patch = {};

  if (historical.knowledge) patch.runId = selection.knowledgeLatestRunId;
  if (historical.credit) patch.creditRunId = selection.creditLatestRunDigest;

  return patch;
}
