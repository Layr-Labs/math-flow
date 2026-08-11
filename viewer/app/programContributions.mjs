export function collectProgramContributionIds(nodes, programId) {
  const program = nodes?.[programId];
  if (!program || program.type !== "program") return [];

  const children = new Map();
  Object.values(nodes).forEach((node) => {
    if (!node || typeof node !== "object" || typeof node.id !== "string") return;
    const parentId = typeof node.parentId === "string" ? node.parentId : null;
    if (!parentId) return;
    const siblings = children.get(parentId) ?? [];
    siblings.push(node.id);
    children.set(parentId, siblings);
  });

  const subtree = new Set();
  const pending = [programId];
  while (pending.length) {
    const nodeId = pending.pop();
    if (!nodeId || subtree.has(nodeId)) continue;
    subtree.add(nodeId);
    pending.push(...(children.get(nodeId) ?? []));
  }

  const contributionIds = new Set();
  subtree.forEach((nodeId) => {
    const node = nodes[nodeId];
    if (!node) return;
    [...(node.subjects ?? []), ...(node.evidence ?? [])].forEach((reference) => {
      if (reference?.kind === "transaction" && typeof reference.id === "string") {
        contributionIds.add(reference.id);
      }
    });
  });
  return [...contributionIds].sort();
}
