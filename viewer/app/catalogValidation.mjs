export function validKnowledgeProjectionIndex(projections) {
  return Array.isArray(projections) && projections.every((projection) =>
    typeof projection?.id === "string" &&
    typeof projection?.problemId === "string" &&
    Array.isArray(projection?.data?.runs) &&
    projection.data.runs.length > 0,
  );
}
