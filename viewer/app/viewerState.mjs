const queryKeys = {
  problemId: "problem",
  projectionId: "projection",
  runId: "run",
  nodeId: "node",
  transactionId: "transaction",
  judgmentId: "judgment",
  query: "q",
  detailMode: "detail",
};

const detailModes = new Set(["node", "transaction", "judgment", "report"]);

export function parseViewerState(search) {
  const params = new URLSearchParams(search);
  const state = {};

  for (const [field, key] of Object.entries(queryKeys)) {
    const value = params.get(key);
    if (value !== null && value !== "") state[field] = value;
  }

  if (state.detailMode && !detailModes.has(state.detailMode)) delete state.detailMode;
  return state;
}

export function applyViewerStateToSearch(search, state) {
  const params = new URLSearchParams(search);

  for (const [field, key] of Object.entries(queryKeys)) {
    const value = state[field];
    if (typeof value === "string" && value !== "") params.set(key, value);
    else params.delete(key);
  }

  const serialized = params.toString();
  return serialized ? `?${serialized}` : "";
}
