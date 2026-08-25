import { isWorkAccountingProjection, isWorkAccountingRun } from "./workAccountingPresentation.mjs";

export function isHierarchicalCreditProjection(projection) {
  return !isWorkAccountingProjection(projection) && Array.isArray(projection?.researchProjectionIds);
}

export function allCreditProjections(catalog) {
  return [
    ...(catalog?.creditProjections ?? []),
    ...(catalog?.hierarchicalCreditProjections ?? []),
    ...(catalog?.workAccountingProjections ?? []),
  ];
}

export function compatibleCreditProjections(catalog, problemId, researchProjectionId) {
  return allCreditProjections(catalog).filter((projection) => {
    if (projection.problemId !== problemId) return false;
    const dependencyIds = isHierarchicalCreditProjection(projection) || isWorkAccountingProjection(projection)
      ? projection.researchProjectionIds
      : projection.knowledgeProjectionIds;
    return dependencyIds.includes(researchProjectionId);
  });
}

export function isHierarchicalCreditRun(run) {
  return Boolean(run?.creditState?.evaluations && run?.creditState?.allocations);
}

export function creditRunAssignmentCount(run) {
  return isWorkAccountingRun(run)
    ? (run?.evaluations?.length ?? 0)
    : isHierarchicalCreditRun(run)
    ? Object.keys(run.creditState.allocations ?? {}).length
    : (run?.assignments?.length ?? 0);
}

export function hierarchicalCreditForTransaction(run, transactionId) {
  if (!isHierarchicalCreditRun(run) || !transactionId) return null;
  for (const evaluation of Object.values(run.creditState.evaluations ?? {})) {
    const child = evaluation?.children?.find(
      (candidate) => candidate.kind === "contribution" && candidate.id === transactionId,
    );
    if (child) {
      return {
        allocation: run.creditState.allocations?.[transactionId] ?? null,
        child,
        evaluation,
      };
    }
  }
  return null;
}

export function formatCreditFraction(fraction, digits = 1) {
  if (!fraction) return "unallocated";
  const numerator = Number(fraction.numerator);
  const denominator = Number(fraction.denominator);
  if (!Number.isFinite(numerator) || !Number.isFinite(denominator) || denominator === 0) {
    return `${fraction.numerator}/${fraction.denominator}`;
  }
  const percent = (numerator / denominator) * 100;
  return `${percent.toFixed(digits).replace(/\.0$/, "")}%`;
}
