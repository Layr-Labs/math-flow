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

function signedDecimalParts(value) {
  if (typeof value !== "string") {
    throw new TypeError("work accounting requires a canonical signed decimal string");
  }
  const negative = value.startsWith("-");
  const magnitude = negative ? value.slice(1) : value;
  const parts = decimalParts(magnitude);
  if (negative && parts.coefficient === 0n) {
    throw new TypeError("negative zero is not a canonical signed decimal");
  }
  return {
    coefficient: negative ? -parts.coefficient : parts.coefficient,
    scale: parts.scale,
  };
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

function signedDecimalFromCoefficient(coefficient, scale) {
  if (coefficient < 0n) {
    return `-${decimalFromCoefficient(-coefficient, scale)}`;
  }
  return decimalFromCoefficient(coefficient, scale);
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

export function addSignedCanonicalDecimals(values) {
  const parsed = values.map(signedDecimalParts);
  const scale = parsed.reduce((maximum, item) => Math.max(maximum, item.scale), 0);
  const coefficient = parsed.reduce(
    (total, item) => total + item.coefficient * powerOfTen(scale - item.scale),
    0n,
  );
  return signedDecimalFromCoefficient(coefficient, scale);
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

export function subtractCanonicalDecimalsSigned(left, right) {
  const leftParts = decimalParts(left);
  const rightParts = decimalParts(right);
  const scale = Math.max(leftParts.scale, rightParts.scale);
  const difference =
    leftParts.coefficient * powerOfTen(scale - leftParts.scale) -
    rightParts.coefficient * powerOfTen(scale - rightParts.scale);
  return signedDecimalFromCoefficient(difference, scale);
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

function validNodeRef(ref) {
  return ["program", "thread"].includes(ref?.kind) && typeof ref?.id === "string";
}

function nodeKey(value) {
  return `${value?.nodeRef?.kind}:${value?.nodeRef?.id}`;
}

function validValues(values) {
  return CANONICAL_DECIMAL.test(values?.directWorkHours) &&
    (values?.conditionalIncidence === null || CANONICAL_DECIMAL.test(values?.conditionalIncidence)) &&
    CANONICAL_DECIMAL.test(values?.globalReach) &&
    CANONICAL_DECIMAL.test(values?.conditionalSubtreeWorkHours) &&
    CANONICAL_DECIMAL.test(values?.expectedDirectWorkHours);
}

function canonicalOrdered(values, allowed) {
  return Array.isArray(values) &&
    values.every((value) => allowed.includes(value)) &&
    values.join("\n") === [...new Set(values)].sort((left, right) =>
      allowed.indexOf(left) - allowed.indexOf(right)).join("\n");
}

function validPatchSummary(summary) {
  if (summary === null) return true;
  const changes = summary?.changes;
  const keys = changes && typeof changes === "object" ? Object.keys(changes).sort() : [];
  const rationaleLength = typeof summary?.rationalePreview === "string"
    ? Array.from(summary.rationalePreview).length
    : 0;
  return keys.length > 0 &&
    keys.every((key) => ["conditionalIncidence", "directWorkHours"].includes(key)) &&
    keys.every((key) => CANONICAL_DECIMAL.test(changes[key])) &&
    rationaleLength > 0 && rationaleLength <= 240 &&
    typeof summary?.rationaleTruncated === "boolean" &&
    (!summary.rationaleTruncated || rationaleLength === 240) &&
    Array.isArray(summary?.evidenceRefPreviews) &&
    summary.evidenceRefPreviews.length > 0 && summary.evidenceRefPreviews.length <= 3 &&
    summary.evidenceRefPreviews.every((value) =>
      typeof value === "string" && Array.from(value).length > 0 && Array.from(value).length <= 160) &&
    Number.isInteger(summary?.evidenceRefCount) &&
    summary.evidenceRefCount >= summary.evidenceRefPreviews.length &&
    typeof summary?.evidenceRefsTruncated === "boolean" &&
    (summary.evidenceRefCount === summary.evidenceRefPreviews.length || summary.evidenceRefsTruncated);
}

function validTopologyRequirements(effect) {
  if (!Array.isArray(effect?.topologyRequirements)) return false;
  const branches = [];
  const reasons = new Set();
  const requirements = new Map();
  for (const requirement of effect.topologyRequirements) {
    if (
      !["no-access", "new-live"].includes(requirement?.branch) ||
      branches.includes(requirement.branch) ||
      !canonicalOrdered(requirement?.requiredChanges, ["conditionalIncidence", "directWorkHours"]) ||
      !requirement.requiredChanges.length ||
      !canonicalOrdered(requirement?.reasons, ["created", "inactive-zeroing", "reparented"]) ||
      !requirement.reasons.length
    ) return false;
    branches.push(requirement.branch);
    requirements.set(requirement.branch, new Set(requirement.requiredChanges));
    requirement.reasons.forEach((reason) => reasons.add(reason));
  }
  if (branches.join("\n") !== effect.topologyRequiredBranches.join("\n")) return false;
  if ([...reasons].sort().join("\n") !== effect.topologyReasons.join("\n")) return false;
  const patchEntries = [
    ["no-access", effect.noAccessPatch],
    ["new-live", effect.newLivePatch],
  ];
  for (const [branch, required] of requirements) {
    const patch = patchEntries.find(([name]) => name === branch)?.[1];
    if (!patch || [...required].some((field) => !(field in patch.changes))) return false;
  }
  const topologyOnly = Boolean(requirements.size) && patchEntries.every(([branch, patch]) =>
    patch === null || Object.keys(patch.changes).every((field) => requirements.get(branch)?.has(field)));
  const classification = requirements.size
    ? topologyOnly ? "topology-only" : "topology-associated"
    : "none";
  return effect.topologyOnly === topologyOnly &&
    effect.topologyClassification === classification;
}

function validNodeEffects(evaluation) {
  if (!Array.isArray(evaluation?.nodeEffects)) return false;
  let prior = null;
  let directCount = 0;
  let propagatedCount = 0;
  let topologyOnlyCount = 0;
  const directKeys = [];
  for (const effect of evaluation.nodeEffects) {
    const key = nodeKey(effect);
    if (
      !validNodeRef(effect?.nodeRef) ||
      (prior !== null && prior >= key) ||
      !DIGEST.test(effect?.knowledgeNodeDigest) ||
      typeof effect?.knowledgeStatus !== "string" || !effect.knowledgeStatus ||
      !["direct", "propagated"].includes(effect?.effectKind) ||
      !canonicalOrdered(effect?.directUpdateBranches, ["no-access", "new-live"]) ||
      !canonicalOrdered(effect?.topologyRequiredBranches, ["no-access", "new-live"]) ||
      !canonicalOrdered(effect?.topologyReasons, ["created", "inactive-zeroing", "reparented"]) ||
      !validTopologyRequirements(effect) ||
      !canonicalOrdered(effect?.primitiveDifferenceFields, ["conditionalIncidence", "directWorkHours"]) ||
      !canonicalOrdered(effect?.derivedDifferenceFields, ["conditionalSubtreeWorkHours", "expectedDirectWorkHours", "globalReach"]) ||
      !validValues(effect?.noAccess) || !validValues(effect?.newLive) ||
      !validPatchSummary(effect?.noAccessPatch) || !validPatchSummary(effect?.newLivePatch) ||
      (effect.noAccessPatch !== null) !== effect.directUpdateBranches.includes("no-access") ||
      (effect.newLivePatch !== null) !== effect.directUpdateBranches.includes("new-live") ||
      (effect.effectKind === "direct") !== Boolean(effect.directUpdateBranches.length) ||
      effect.primitiveDifferenceFields.join("\n") !== ["conditionalIncidence", "directWorkHours"]
        .filter((field) => effect.noAccess[field] !== effect.newLive[field]).join("\n") ||
      effect.derivedDifferenceFields.join("\n") !== ["conditionalSubtreeWorkHours", "expectedDirectWorkHours", "globalReach"]
        .filter((field) => effect.noAccess[field] !== effect.newLive[field]).join("\n") ||
      subtractCanonicalDecimalsSigned(
        effect.noAccess.expectedDirectWorkHours,
        effect.newLive.expectedDirectWorkHours,
      ) !== effect.workReductionHours ||
      typeof effect.topologyOnly !== "boolean"
    ) {
      return false;
    }
    prior = key;
    if (effect.effectKind === "direct") {
      directCount += 1;
      directKeys.push(key);
    } else {
      propagatedCount += 1;
    }
    if (effect.topologyOnly) topologyOnlyCount += 1;
  }
  return directCount === evaluation.directUpdateCount &&
    propagatedCount === evaluation.propagatedEffectCount &&
    topologyOnlyCount === evaluation.topologyOnlyCount &&
    addSignedCanonicalDecimals(evaluation.nodeEffects.map((item) => item.workReductionHours)) === evaluation.workReductionHours &&
    DIGEST.test(evaluation.nodeEffectsDigest) &&
    evaluation.nodeAnnotations.map(nodeKey).join("\n") === directKeys.join("\n");
}

function validTerminalAnnotations(run) {
  if (!Array.isArray(run?.terminalNodeAnnotations)) return false;
  return run.terminalNodeAnnotations.every((annotation, index, annotations) => {
    const key = nodeKey(annotation);
    const prior = index ? nodeKey(annotations[index - 1]) : null;
    return validNodeRef(annotation?.nodeRef) &&
      (prior === null || prior < key) &&
      DIGEST.test(annotation?.knowledgeNodeDigest) &&
      typeof annotation?.knowledgeStatus === "string" && Boolean(annotation.knowledgeStatus) &&
      validValues(annotation);
  });
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
    const detailed = run.evaluations.some((evaluation) => evaluation?.nodeEffects !== undefined);
    if (
      detailed && (
        run.evaluations.some((evaluation) => !Array.isArray(evaluation?.nodeEffects)) ||
        !validTerminalAnnotations(run)
      )
    ) return false;
    let priorOrdinal = 0;
    const subjects = new Set();
    for (const evaluation of run.evaluations) {
      if (
        !TRANSACTION.test(evaluation?.subjectTransactionId) ||
        subjects.has(evaluation.subjectTransactionId) ||
        !Number.isInteger(evaluation?.canonicalOrdinal) ||
        evaluation.canonicalOrdinal <= priorOrdinal ||
        subtractCanonicalDecimals(
          evaluation.noAccessWorkHours ?? evaluation.exAnteWorkHours,
          evaluation.newLiveWorkHours ?? evaluation.exPostWorkHours,
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
        (evaluation.nodeEffects !== undefined && (
          evaluation.noAccessWorkHours !== evaluation.exAnteWorkHours ||
          evaluation.newLiveWorkHours !== evaluation.exPostWorkHours ||
          !validNodeEffects(evaluation)
        )) ||
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
    if (Array.isArray(evaluation.nodeEffects)) {
      const effect = evaluation.nodeEffects.find(
        (item) => item.nodeRef.kind === ref.kind && item.nodeRef.id === ref.id,
      );
      return effect ? [{
        evaluation,
        effect,
        annotation: {
          nodeRef: effect.nodeRef,
          knowledgeNodeDigest: effect.knowledgeNodeDigest,
          ...effect.newLive,
        },
      }] : [];
    }
    const annotation = evaluation.nodeAnnotations.find(
      (item) => item.nodeRef.kind === ref.kind && item.nodeRef.id === ref.id,
    );
    return annotation ? [{ evaluation, annotation }] : [];
  });
}

export function terminalWorkAccountingForNode(run, node) {
  const ref = workAccountingNodeRef(node);
  if (!isWorkAccountingRun(run) || !ref || !Array.isArray(run.terminalNodeAnnotations)) {
    return null;
  }
  return run.terminalNodeAnnotations.find(
    (item) => item.nodeRef.kind === ref.kind && item.nodeRef.id === ref.id,
  ) ?? null;
}
