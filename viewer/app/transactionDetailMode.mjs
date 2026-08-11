const transactionDetailModes = new Set(["transaction", "judgment", "credit"]);

export function preferredTransactionDetailMode(detailMode) {
  return transactionDetailModes.has(detailMode) ? detailMode : "transaction";
}

export function resolveTransactionDetailMode(detailMode, { hasJudgment, hasCredit }) {
  const preferred = preferredTransactionDetailMode(detailMode);
  if (preferred === "judgment" && !hasJudgment) return "transaction";
  if (preferred === "credit" && !hasCredit) return "transaction";
  return preferred;
}
