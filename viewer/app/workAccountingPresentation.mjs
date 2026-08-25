const CANONICAL_DECIMAL = /^(?:0|[1-9][0-9]*)(?:\.[0-9]*[1-9])?$/;
const TRANSACTION = /^[0-9a-f]{40}$/;
const DIGEST = /^sha256:[0-9a-f]{64}$/;

function decimalParts(value) {
  if (typeof value !== "string" || !CANONICAL_DECIMAL.test(value)) {
    throw new TypeError("work accounting requires a canonical non-negative decimal string");
  }
  const [integer, fraction = ""] = value.split(".");
  return { coefficient: BigInt(`${integer}${fraction}`), scale: fraction.length };
}

function powerOfTen(exponent) {
  return 10n ** BigInt(exponent);
}

function fractionForDecimal(value) {
  const parts = decimalParts(value);
  return {
    numerator: parts.coefficient,
    denominator: powerOfTen(parts.scale),
  };
}

function decimalFromCoefficient(coefficient, scale) {
  const digits = coefficient.toString().padStart(scale + 1, "0");
  if (!scale) return digits;
  const integer = digits.slice(0, -scale);
  const fraction = digits.slice(-scale).replace(/0+$/, "");
  return fraction ? `${integer}.${fraction}` : integer;
}

export function addCanonicalDecimals(values) {
  const parsed = values.map(decimalParts);
  const scale = parsed.reduce((maximum, item) => Math.max(maximum, item.scale), 0);
  const coefficient = parsed.reduce(
    (total, item) => total + item.coefficient * powerOfTen(scale - item.scale),
    0n,
  );
  return decimalFromCoefficient(coefficient, scale);
}

export function subtractCanonicalDecimals(left, right) {
  const leftParts = decimalParts(left);
  const rightParts = decimalParts(right);
  const scale = Math.max(leftParts.scale, rightParts.scale);
  const difference =
    leftParts.coefficient * powerOfTen(scale - leftParts.scale) -
    rightParts.coefficient * powerOfTen(scale - rightParts.scale);
  if (difference < 0n) throw new RangeError("work reduction cannot be negative");
  return decimalFromCoefficient(difference, scale);
}

export function formatWorkShare(value, values, digits = 1) {
  if (!Number.isInteger(digits) || digits < 0 || digits > 6) {
    throw new RangeError("work share digits must be an integer from zero through six");
  }
  const total = addCanonicalDecimals(values);
  const numerator = fractionForDecimal(value);
  const denominator = fractionForDecimal(total);
  if (denominator.numerator === 0n) return "unallocated";
  const scale = powerOfTen(digits);
  const scaledNumerator =
    numerator.numerator * denominator.denominator * 100n * scale;
  const scaledDenominator = numerator.denominator * denominator.numerator;
  const rounded = (scaledNumerator * 2n + scaledDenominator) / (scaledDenominator * 2n);
  const text = rounded.toString().padStart(digits + 1, "0");
  if (!digits) return `${text}%`;
  const integer = text.slice(0, -digits);
  const fraction = text.slice(-digits).replace(/0+$/, "");
  return `${fraction ? `${integer}.${fraction}` : integer}%`;
}

export function isWorkAccountingProjection(projection) {
  return projection?.workAccounting?.id === "competent-human-researcher-hour";
}

export function isWorkAccountingRun(run) {
  return run?.unit?.id === "competent-human-researcher-hour" &&
    Array.isArray(run?.evaluations);
}

export function validWorkAccountingRun(run) {
  if (
    !isWorkAccountingRun(run) ||
    run.id !== run.runDigest ||
    run.runDigest !== run.scheduleDigest ||
    run.inputStatus !== "exact-committed" ||
    run.unit.storedValues !== "canonical-decimal-hours" ||
    run.unit.displayShares !== "derived-from-exact-values"
  ) {
    return false;
  }
  try {
    let priorOrdinal = 0;
    const subjects = new Set();
    for (const evaluation of run.evaluations) {
      if (
        !TRANSACTION.test(evaluation?.subjectTransactionId) ||
        subjects.has(evaluation.subjectTransactionId) ||
        !Number.isInteger(evaluation?.canonicalOrdinal) ||
        evaluation.canonicalOrdinal <= priorOrdinal ||
        subtractCanonicalDecimals(
          evaluation.exAnteWorkHours,
          evaluation.exPostWorkHours,
        ) !== evaluation.workReductionHours ||
        evaluation.workReductionHours === "0" ||
        !DIGEST.test(evaluation.evaluationDigest) ||
        !DIGEST.test(evaluation.publicationManifestDigest) ||
        !DIGEST.test(evaluation.committedAccountingStateDigest) ||
        !Array.isArray(evaluation.nodeAnnotations) ||
        !evaluation.nodeAnnotations.every((annotation, index, annotations) => {
          const key = `${annotation?.nodeRef?.kind}:${annotation?.nodeRef?.id}`;
          const prior = index ? `${annotations[index - 1]?.nodeRef?.kind}:${annotations[index - 1]?.nodeRef?.id}` : null;
          return ["program", "thread"].includes(annotation?.nodeRef?.kind) &&
            typeof annotation?.nodeRef?.id === "string" &&
            (prior === null || prior < key) &&
            DIGEST.test(annotation?.knowledgeNodeDigest) &&
            CANONICAL_DECIMAL.test(annotation?.directWorkHours) &&
            (annotation?.conditionalIncidence === null || CANONICAL_DECIMAL.test(annotation?.conditionalIncidence)) &&
            CANONICAL_DECIMAL.test(annotation?.globalReach) &&
            CANONICAL_DECIMAL.test(annotation?.conditionalSubtreeWorkHours) &&
            CANONICAL_DECIMAL.test(annotation?.expectedDirectWorkHours);
        }) ||
        typeof evaluation.prospectiveCorrection !== "boolean" ||
        typeof evaluation.affectedHistory !== "boolean" ||
        !Array.isArray(evaluation.affectedByRepairDigests) ||
        evaluation.affectedByRepairDigests.some((digest) => !DIGEST.test(digest)) ||
        evaluation.affectedByRepairDigests.join("\n") !== [...new Set(evaluation.affectedByRepairDigests)].sort().join("\n") ||
        evaluation.prospectiveCorrection !== Boolean(evaluation.affectedByRepairDigests.length) ||
        evaluation.affectedHistory !== Boolean(evaluation.affectedByRepairDigests.length)
      ) {
        return false;
      }
      subjects.add(evaluation.subjectTransactionId);
      priorOrdinal = evaluation.canonicalOrdinal;
    }
  } catch {
    return false;
  }
  return true;
}

export function workAccountingForTransaction(run, transactionId) {
  if (!isWorkAccountingRun(run) || !transactionId) return null;
  return run.evaluations.find(
    (evaluation) => evaluation.subjectTransactionId === transactionId,
  ) ?? null;
}

export function workAccountingNodeRef(node) {
  if (node?.type === "program") return { kind: "program", id: node.id };
  if (typeof node?.id === "string" && node.id.startsWith("thread:")) {
    return { kind: "thread", id: node.id.slice("thread:".length) };
  }
  return null;
}

export function workAccountingForNode(run, node) {
  const ref = workAccountingNodeRef(node);
  if (!isWorkAccountingRun(run) || !ref) return [];
  return run.evaluations.flatMap((evaluation) => {
    const annotation = evaluation.nodeAnnotations.find(
      (item) => item.nodeRef.kind === ref.kind && item.nodeRef.id === ref.id,
    );
    return annotation ? [{ evaluation, annotation }] : [];
  });
}
