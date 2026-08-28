export const TWO_ENTITY_SEMANTIC_PROFILE = "programs-and-intermediate-results-v1";

export function validTwoEntityMachineState(machineState, expectedDigest) {
  return Boolean(
    machineState &&
    machineState.schemaVersion === 3 &&
    typeof machineState.problemId === "string" &&
    typeof machineState.programs === "object" &&
    !Array.isArray(machineState.programs) &&
    typeof machineState.intermediateResults === "object" &&
    !Array.isArray(machineState.intermediateResults) &&
    typeof machineState.contributions === "object" &&
    !Array.isArray(machineState.contributions) &&
    machineState.threads === undefined &&
    machineState.items === undefined &&
    typeof machineState.stateDigest === "string" &&
    machineState.stateDigest === expectedDigest
  );
}

export function validTwoEntityKnowledgeState(state) {
  const nodes = state?.nodes;
  if (
    state?.semanticProfile !== TWO_ENTITY_SEMANTIC_PROFILE ||
    typeof state?.stateDigest !== "string" ||
    !nodes ||
    typeof nodes !== "object" ||
    Array.isArray(nodes) ||
    !nodes.root ||
    nodes.root.type !== "program" ||
    nodes.root.parentId !== null
  ) return false;

  const entries = Object.entries(nodes);
  if (!entries.length) return false;
  return entries.every(([nodeId, node]) => {
    if (
      !node ||
      typeof node !== "object" ||
      node.id !== nodeId ||
      !["program", "intermediate-result"].includes(node.type) ||
      typeof node.title !== "string" ||
      typeof node.summary !== "string" ||
      typeof node.status !== "string" ||
      typeof node.contentMarkdown !== "string" ||
      typeof node.digest !== "string" ||
      !Array.isArray(node.subjects) ||
      !Array.isArray(node.evidence)
    ) return false;
    if (!node.evidence.every((reference) =>
      reference?.kind !== "knowledge-node" ||
      (typeof reference.id === "string" && Boolean(nodes[reference.id])),
    )) return false;

    if (node.type === "program") {
      return node.parentId === null || nodes[node.parentId]?.type === "program";
    }
    if (
      typeof node.parentId !== "string" ||
      nodes[node.parentId]?.type !== "program" ||
      !nodeId.startsWith("result:")
    ) return false;
    return true;
  });
}

export function validKnowledgeProjectionIndex(projections) {
  return Array.isArray(projections) && projections.every((projection) =>
    typeof projection?.id === "string" &&
    typeof projection?.problemId === "string" &&
    Array.isArray(projection?.data?.runs) &&
    projection.data.runs.length > 0 &&
    projection.data.runs.every((run) =>
      run?.state?.semanticProfile !== TWO_ENTITY_SEMANTIC_PROFILE ||
      (
        validTwoEntityKnowledgeState(run.state) &&
        validTwoEntityMachineState(run.machineState, run.state.stateDigest)
      ),
    ),
  );
}
