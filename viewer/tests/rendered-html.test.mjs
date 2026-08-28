import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import test from "node:test";
import katex from "katex";
import { validKnowledgeProjectionIndex } from "../app/catalogValidation.mjs";
import { allCreditProjections, compatibleCreditProjections, creditRunAssignmentCount, formatCreditFraction, hierarchicalCreditForTransaction, isHierarchicalCreditProjection } from "../app/creditPresentation.mjs";
import { collectProgramContributionIds } from "../app/programContributions.mjs";
import { splitDisplayMath, splitInlineMath } from "../app/markdownMath.mjs";
import { createViewerReferenceResolver } from "../app/referenceLinks.mjs";
import { preferredTransactionDetailMode, resolveTransactionDetailMode } from "../app/transactionDetailMode.mjs";
import { validityReferenceGroups } from "../app/validityPresentation.mjs";
import { creditRunSelectionPatch, historicalOverlaySelection, knowledgeRunSelectionPatch, latestOverlaySelectionPatch, projectionByIdentity, publishedHeadSelectionPatch } from "../app/projectionHeadState.mjs";
import { applyViewerStateToSearch, parseViewerState } from "../app/viewerState.mjs";
import { addCanonicalDecimals, addSignedCanonicalDecimals, formatWorkShare, isWorkAccountingProjection, isWorkAccountingRun, subtractCanonicalDecimals, subtractCanonicalDecimalsSigned, terminalWorkAccountingForNode, validWorkAccountingRun, workAccountingForNode, workAccountingForTransaction } from "../app/workAccountingPresentation.mjs";

const templateRoot = new URL("../", import.meta.url);

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders a stable loading state before repository data arrives", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  const initialMarkup = html.split(/<script[^>]*\bid="_R_"/)[0];
  assert.match(html, /<title>Math Flow · Research Atlas<\/title>/i);
  assert.match(initialMarkup, /Math Flow · research atlas/);
  assert.match(initialMarkup, /Loading repository state/);
  assert.match(initialMarkup, /remains empty unless the live governed catalog is available/i);
  assert.doesNotMatch(initialMarkup, /Triangle midpoint quadrilateral/);
  assert.doesNotMatch(initialMarkup, /State[^<]*<!-- -->03/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|SkeletonPreview/i);
});

test("accepts an empty knowledge projection index without inventing a fallback", () => {
  assert.equal(validKnowledgeProjectionIndex([]), true);
  assert.equal(validKnowledgeProjectionIndex(undefined), false);
  assert.equal(validKnowledgeProjectionIndex([{ id: "incomplete" }]), false);
});

test("keeps the viewer data-driven with contextual artifact details", async () => {
  const [page, layout, packageJson, viewer, styles] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
    readFile(new URL("../app/KnowledgeViewer.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/globals.css", import.meta.url), "utf8"),
  ]);

  assert.match(page, /<RepositoryKnowledgeViewer/);
  assert.doesNotMatch(page, /math-flow-data\.json|fallbackData=/);
  assert.match(layout, /Math Flow · Research Atlas/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton|site-creator-vinext-starter/);
  assert.match(viewer, /detail-tabs-transaction/);
  assert.match(viewer, /Submission<\/button>/);
  assert.match(viewer, /Judgment<\/button>/);
  assert.match(viewer, /Verification<\/button>/);
  assert.match(viewer, /Credit<\/button>/);
  assert.match(viewer, /Objective verifier attestation · separate evidence/);
  assert.match(viewer, /className="selector-bubble knowledge-selector-bubble"/);
  assert.match(viewer, /className="selector-bubble credit-selector-bubble"/);
  assert.match(viewer, /aria-label="Knowledge projection"/);
  assert.match(viewer, /aria-label="Knowledge state"/);
  assert.match(viewer, /aria-label="Credit projection"/);
  assert.match(viewer, /aria-label="Credit state"/);
  assert.match(viewer, /View latest knowledge &amp; credit|View latest knowledge & credit/);
  assert.match(viewer, /publishedHeadSelectionPatch/);
  assert.match(viewer, /latestOverlaySelectionPatch/);
  assert.match(viewer, /Repository catalog unavailable/);
  assert.match(viewer, /No problem or archived snapshot is shown/);
  assert.match(viewer, /projections: \[\]/);
  assert.doesNotMatch(viewer, /checked-in demonstration|fallback:/);
  assert.doesNotMatch(page + viewer, /triangle-midpoints|Triangle midpoint/i);
  assert.doesNotMatch(viewer, /className="run-strip"/);
  assert.match(viewer, /Historical state/);
  assert.match(viewer, /Historical input lock/);
  assert.match(viewer, /detailMode: preferredTransactionDetailMode\(viewerState\.detailMode\)/);
  assert.match(viewer, /No published credit yet/);
  assert.match(viewer, /Qualitative credit · separate overlay/);
  assert.match(viewer, /Two-term hierarchical credit · separate overlay/);
  assert.match(viewer, /Hierarchical work credit · separate committed overlay/);
  assert.match(viewer, /Unit: competent human researcher hours/);
  assert.match(viewer, /Raw hours are stable canonical-decimal accounting values/);
  assert.match(viewer, /D = W− − W\+/);
  assert.match(viewer, /No-access W−/);
  assert.match(viewer, /New live W\+/);
  assert.match(viewer, /Current live work parameterization/);
  assert.match(viewer, /Direct updates/);
  assert.match(viewer, /Propagated/);
  assert.match(viewer, /subtree \(non-additive\)/);
  assert.match(viewer, /topology-only/);
  assert.match(viewer, /topology-associated/);
  assert.match(viewer, /Direct patch previews/);
  assert.match(viewer, /union of directly patched W− and W\+ nodes/);
  assert.match(viewer, /Prospective correction affects this history/);
  assert.match(viewer, /Credit belongs to the submission/);
  assert.match(viewer, /semantic result and method items carry no numeric accounting/);
  assert.match(viewer, /Validity assessments/);
  assert.match(viewer, /Declared references \/ provenance/);
  assert.match(viewer, /Required premises/);
  assert.match(viewer, /validityReferenceGroups/);
  assert.match(viewer, /Knowledge-routing findings/);
  assert.match(viewer, /Research program state/);
  assert.match(viewer, /Local program credit/);
  assert.match(viewer, /Ex-post counterfactual/);
  assert.match(viewer, /Direct work avoided/);
  assert.match(viewer, /Obviated work/);
  assert.match(viewer, /Knowledge references/);
  assert.match(viewer, /Prior reservations/);
  assert.match(viewer, /Full raw credit report/);
  assert.match(viewer, /Locked credit input/);
  assert.match(viewer, /Projection dependency lock/);
  assert.match(viewer, /openCreditKnowledgeRef/);
  assert.match(viewer, /detail-tabs-node/);
  assert.match(viewer, /Node<\/button>/);
  assert.match(viewer, /Build report<\/button>/);
  assert.match(viewer, /primary judgment/);
  assert.match(viewer, /the full state remains visible/);
  assert.match(viewer, /markdown-reference/);
  assert.match(viewer, /createViewerReferenceResolver/);
  assert.match(viewer, /currentRevision \?\? node\.currentAdjudication/);
  assert.match(viewer, /Knowledge revision lineage/);
  assert.match(viewer, /Changed knowledge facets/);
  assert.match(viewer, /Change rationale/);
  assert.match(viewer, /inline\(revision\.changeRationale, referenceActions\)/);
  assert.match(viewer, /revision\.changeRef\.section/);
  assert.match(viewer, /Related contributions/);
  assert.match(viewer, /Research directions/);
  assert.match(viewer, /Registration is evidence, not ownership/);
  assert.match(viewer, /Direction event history/);
  assert.match(viewer, /collectProgramContributionIds/);
  assert.match(styles, /\.action-create/);
  assert.match(styles, /\.action-update/);
  assert.match(styles, /\.action-retire/);
  assert.match(styles, /\.action-restore/);
  assert.match(styles, /\.selector-bubble/);
  assert.match(styles, /\.credit-selector-bubble/);
  assert.match(styles, /\.latest-state-button/);
  assert.match(styles, /\.validity-assessment/);
  assert.match(styles, /\.validity-reference-groups/);
  assert.match(styles, /\.hierarchical-credit-summary/);
  assert.match(styles, /\.program-credit-context/);
  assert.doesNotMatch(styles, /\.run-strip/);
  assert.match(packageJson, /"katex"/);
  assert.match(layout, /katex\/dist\/katex\.min\.css/);
  assert.match(viewer, /katex\.renderToString/);
  assert.match(styles, /\.math-display/);

  const previewAssets = await readdir(new URL("app/_sites-preview", templateRoot)).catch((error) => {
    if (error?.code === "ENOENT") return [];
    throw error;
  });
  assert.deepEqual(previewAssets, []);
});

test("derives work-accounting shares exactly without floating point", async () => {
  const fixture = JSON.parse(await readFile(
    new URL("fixtures/work-accounting-overlay-v1.json", import.meta.url),
    "utf8",
  ));
  const run = fixture.runs[0];
  const values = run.evaluations.map((item) => item.workReductionHours);

  assert.equal(isWorkAccountingProjection(fixture), true);
  assert.equal(isHierarchicalCreditProjection(fixture), false);
  assert.equal(isWorkAccountingRun(run), true);
  assert.equal(validWorkAccountingRun(run), true);
  assert.equal(addCanonicalDecimals(values), "0.9");
  assert.equal(formatWorkShare("0.3", values), "33.3%");
  assert.equal(formatWorkShare("0.6", values), "66.7%");
  assert.equal(
    subtractCanonicalDecimals(
      "100000000000000000000000000000000000000.2",
      "99999999999999999999999999999999999999.9",
    ),
    "0.3",
  );
  assert.equal(
    workAccountingForTransaction(run, "1111111111111111111111111111111111111111")?.canonicalOrdinal,
    18,
  );
  assert.equal(workAccountingForNode(run, { type: "result", id: "item:root/result" }).length, 0);
  assert.equal(workAccountingForNode(run, { type: "question", id: "thread:root/direct-line" }).length, 1);
  assert.deepEqual(
    allCreditProjections({ workAccountingProjections: [fixture] }),
    [fixture],
  );
  assert.equal(validWorkAccountingRun({
    ...run,
    evaluations: [{ ...run.evaluations[0], workReductionHours: "0.4" }],
  }), false, "R-C tampering fails catalog validation");
});

test("validates detailed W-minus/W-plus node effects while retaining V1", async () => {
  const fixture = JSON.parse(await readFile(
    new URL("fixtures/work-accounting-overlay-v1.json", import.meta.url),
    "utf8",
  ));
  const run = fixture.runs[0];
  const detailedEvaluations = run.evaluations.map((evaluation) => {
    const annotation = evaluation.nodeAnnotations[0];
    const noExpected = evaluation.workReductionHours === "0.3" ? "1.55" : "2";
    const noDirect = evaluation.workReductionHours === "0.3" ? "3.1" : "2";
    return {
      ...evaluation,
      noAccessWorkHours: evaluation.exAnteWorkHours,
      newLiveWorkHours: evaluation.exPostWorkHours,
      directUpdateCount: 1,
      propagatedEffectCount: 0,
      topologyOnlyCount: 0,
      nodeEffectsDigest: `sha256:${"9".repeat(64)}`,
      nodeEffects: [{
        nodeRef: annotation.nodeRef,
        knowledgeNodeDigest: annotation.knowledgeNodeDigest,
        knowledgeStatus: "active",
        effectKind: "direct",
        directUpdateBranches: ["no-access", "new-live"],
        topologyRequiredBranches: [],
        topologyReasons: [],
        topologyRequirements: [],
        topologyClassification: "none",
        topologyOnly: false,
        primitiveDifferenceFields: ["directWorkHours"],
        derivedDifferenceFields: ["conditionalSubtreeWorkHours", "expectedDirectWorkHours"],
        noAccess: {
          directWorkHours: noDirect,
          conditionalIncidence: annotation.conditionalIncidence,
          globalReach: annotation.globalReach,
          conditionalSubtreeWorkHours: noDirect,
          expectedDirectWorkHours: noExpected,
        },
        newLive: {
          directWorkHours: annotation.directWorkHours,
          conditionalIncidence: annotation.conditionalIncidence,
          globalReach: annotation.globalReach,
          conditionalSubtreeWorkHours: annotation.conditionalSubtreeWorkHours,
          expectedDirectWorkHours: annotation.expectedDirectWorkHours,
        },
        noAccessPatch: {
          changes: { directWorkHours: noDirect },
          rationalePreview: "No-access estimate.",
          rationaleTruncated: false,
          evidenceRefPreviews: [evaluation.subjectTransactionId],
          evidenceRefCount: 1,
          evidenceRefsTruncated: false,
        },
        newLivePatch: {
          changes: { directWorkHours: annotation.directWorkHours },
          rationalePreview: "New live estimate.",
          rationaleTruncated: false,
          evidenceRefPreviews: [evaluation.subjectTransactionId],
          evidenceRefCount: 1,
          evidenceRefsTruncated: false,
        },
        workReductionHours: evaluation.workReductionHours,
      }],
    };
  });
  const detailed = {
    ...run,
    evaluations: detailedEvaluations,
    terminalNodeAnnotations: [
      { ...run.evaluations[1].nodeAnnotations[0], knowledgeStatus: "active" },
      { ...run.evaluations[0].nodeAnnotations[0], knowledgeStatus: "active" },
    ],
  };
  assert.equal(validWorkAccountingRun(run), true, "published V1 remains readable");
  assert.equal(validWorkAccountingRun(detailed), true);
  assert.equal(addSignedCanonicalDecimals(["5", "-3.5", "0.5"]), "2");
  assert.equal(subtractCanonicalDecimalsSigned("1.25", "2"), "-0.75");
  assert.equal(
    terminalWorkAccountingForNode(detailed, { type: "program", id: "root" })?.directWorkHours,
    "1.4",
  );
  assert.equal(validWorkAccountingRun({
    ...detailed,
    evaluations: [{
      ...detailed.evaluations[0],
      nodeEffects: [{ ...detailed.evaluations[0].nodeEffects[0], workReductionHours: "-0.3" }],
    }, detailed.evaluations[1]],
  }), false, "signed node effects must exactly sum to D");
});

test("separates validity-v3 declared references from judge-selected premises", () => {
  const declaredA = "1".repeat(40);
  const declaredB = "2".repeat(40);
  const assessment = {
    claimKey: "fixture/claim",
    requiredDependencyTransactionIds: [declaredA],
  };
  assert.deepEqual(
    validityReferenceGroups(
      {
        declaredReferenceTransactionIdsByClaim: {
          "fixture/claim": [declaredA, declaredB],
        },
      },
      assessment,
    ),
    {
      declaredReferenceTransactionIds: [declaredA, declaredB],
      requiredDependencyTransactionIds: [declaredA],
    },
  );
  assert.equal(
    validityReferenceGroups({}, { claimKey: "fixture/claim" }),
    null,
    "validity-v2 assessments retain their existing presentation",
  );
});

test("recognizes and renders inline and display LaTeX without consuming code", () => {
  assert.deepEqual(splitInlineMath("Let \\(x^2\\) and $y_1$ vary."), [
    { type: "text", value: "Let " },
    { type: "math", value: "x^2" },
    { type: "text", value: " and " },
    { type: "math", value: "y_1" },
    { type: "text", value: " vary." },
  ]);
  assert.deepEqual(splitDisplayMath("Before\\[\\frac{a}{b}\\]After"), [
    { type: "text", value: "Before" },
    { type: "math", value: "\\frac{a}{b}" },
    { type: "text", value: "After" },
  ]);
  assert.deepEqual(splitDisplayMath("$$x+y$$"), [{ type: "math", value: "x+y" }]);
  assert.deepEqual(splitInlineMath("Unclosed \\(x remains text"), [
    { type: "text", value: "Unclosed \\(x remains text" },
  ]);
  assert.deepEqual(splitInlineMath("Keep `$code$` and \\$5 literal."), [
    { type: "text", value: "Keep `$code$` and \\$5 literal." },
  ]);
  assert.deepEqual(splitDisplayMath("Keep `$$code$$` literal."), [
    { type: "text", value: "Keep `$$code$$` literal." },
  ]);

  const rendered = katex.renderToString("\\frac{a}{b}", { displayMode: true });
  assert.match(rendered, /class="katex-display"/);
  assert.match(rendered, /<math/);
});

test("follows newly published overlay heads without moving historical selections", () => {
  const knowledge = (latestRunId) => ({
    id: "knowledge:one",
    problemId: "problem:one",
    data: { latestRunId },
  });
  const credit = (latestRunDigest, runs) => ({
    id: "credit:one",
    problemId: "problem:one",
    latestRunDigest,
    runs: runs.map((runDigest) => ({ runDigest })),
  });
  const catalog = (knowledgeHead, creditHead, creditRuns = [creditHead].filter(Boolean)) => ({
    projections: [knowledge(knowledgeHead)],
    creditProjections: [credit(creditHead, creditRuns)],
  });

  const previous = catalog("knowledge-2", "credit-2", ["credit-1", "credit-2"]);
  const next = catalog("knowledge-3", "credit-3", ["credit-1", "credit-2", "credit-3"]);

  assert.deepEqual(publishedHeadSelectionPatch(previous, next, {
    projectionId: "knowledge:one",
    runId: "knowledge-2",
    creditProjectionId: "credit:one",
    creditRunId: "credit-2",
  }), { runId: "knowledge-3", creditRunId: "credit-3" });

  assert.deepEqual(publishedHeadSelectionPatch(previous, next, {
    projectionId: "knowledge:one",
    runId: "knowledge-1",
    creditProjectionId: "credit:one",
    creditRunId: "credit-1",
  }), {}, "an explicit historical selection is stable across refreshes");

  assert.deepEqual(publishedHeadSelectionPatch(previous, next, {
    projectionId: "knowledge:one",
    runId: "knowledge-1",
    creditProjectionId: "credit:one",
    creditRunId: "credit-2",
  }), { creditRunId: "credit-3" }, "each overlay follows its head independently");

  assert.deepEqual(publishedHeadSelectionPatch(
    catalog("knowledge-2", null, []),
    catalog("knowledge-2", "credit-1", ["credit-1"]),
    { projectionId: "knowledge:one", runId: "knowledge-2", creditProjectionId: "credit:one" },
  ), { creditRunId: "credit-1" }, "the first credit publication becomes the selected head");

  const implicitDefault = {};
  const reselectedHeads = {
    ...implicitDefault,
    ...knowledgeRunSelectionPatch({
      problemId: "problem:one",
      projectionId: "knowledge:one",
      runId: "knowledge-2",
    }),
    ...creditRunSelectionPatch({ projectionId: "credit:one", runId: "credit-2" }),
  };
  assert.deepEqual(reselectedHeads, {
    problemId: "problem:one",
    projectionId: "knowledge:one",
    runId: "knowledge-2",
    creditProjectionId: "credit:one",
    creditRunId: "credit-2",
  }, "choosing a run materializes its formerly implicit projection identity");
  assert.deepEqual(
    publishedHeadSelectionPatch(previous, next, reselectedHeads),
    { runId: "knowledge-3", creditRunId: "credit-3" },
    "an implicitly defaulted projection follows after its head is explicitly re-selected",
  );
});

test("presents hierarchical two-term credit alongside legacy qualitative overlays", () => {
  const transactionId = "a".repeat(40);
  const hierarchicalRun = {
    runDigest: "hierarchical-1",
    creditState: {
      allocations: { [transactionId]: { numerator: "3", denominator: "5" } },
      evaluations: {
        root: {
          programId: "root",
          children: [{
            kind: "contribution",
            id: transactionId,
            directWork: "2",
            obviatedWork: "1",
            totalWork: "3",
            allocationShare: { numerator: "3", denominator: "4" },
          }],
        },
      },
    },
  };
  const catalog = {
    creditProjections: [{
      id: "qualitative",
      problemId: "problem",
      knowledgeProjectionIds: ["legacy-research"],
      runs: [],
    }],
    hierarchicalCreditProjections: [{
      id: "two-term",
      problemId: "problem",
      researchProjectionIds: ["research-v2"],
      latestRunDigest: "hierarchical-1",
      runs: [hierarchicalRun],
    }],
  };

  assert.equal(allCreditProjections(catalog).length, 2);
  assert.deepEqual(
    compatibleCreditProjections(catalog, "problem", "research-v2").map((item) => item.id),
    ["two-term"],
  );
  assert.equal(isHierarchicalCreditProjection(catalog.hierarchicalCreditProjections[0]), true);
  assert.equal(creditRunAssignmentCount(hierarchicalRun), 1);
  assert.equal(formatCreditFraction({ numerator: "3", denominator: "5" }), "60%");
  assert.deepEqual(hierarchicalCreditForTransaction(hierarchicalRun, transactionId), {
    allocation: { numerator: "3", denominator: "5" },
    child: hierarchicalRun.creditState.evaluations.root.children[0],
    evaluation: hierarchicalRun.creditState.evaluations.root,
  });
});

test("follows a newly published hierarchical credit head", () => {
  const knowledge = {
    id: "research-v2",
    problemId: "problem",
    data: { latestRunId: "research-2" },
  };
  const hierarchical = (latestRunDigest, runs) => ({
    id: "two-term",
    problemId: "problem",
    researchProjectionIds: ["research-v2"],
    latestRunDigest,
    runs: runs.map((runDigest) => ({ runDigest })),
  });
  const previous = {
    projections: [knowledge],
    creditProjections: [],
    hierarchicalCreditProjections: [hierarchical("credit-1", ["credit-1"])],
  };
  const next = {
    ...previous,
    hierarchicalCreditProjections: [hierarchical("credit-2", ["credit-1", "credit-2"])],
  };

  assert.deepEqual(publishedHeadSelectionPatch(previous, next, {
    problemId: "problem",
    projectionId: "research-v2",
    runId: "research-2",
    creditProjectionId: "two-term",
    creditRunId: "credit-1",
  }), { creditRunId: "credit-2" });
});

test("resolves a shared projection id within the selected problem", () => {
  const previous = {
    projections: [
      { id: "openrouter-research-v1", problemId: "no-three-in-line-77", data: { latestRunId: "no-three-2" } },
      { id: "openrouter-research-v1", problemId: "triangle-midpoints", data: { latestRunId: "triangle-2" } },
    ],
    creditProjections: [],
  };
  const next = {
    ...previous,
    projections: [
      { id: "openrouter-research-v1", problemId: "no-three-in-line-77", data: { latestRunId: "no-three-3" } },
      { id: "openrouter-research-v1", problemId: "triangle-midpoints", data: { latestRunId: "triangle-3" } },
    ],
  };

  assert.equal(
    projectionByIdentity(previous, "triangle-midpoints", "openrouter-research-v1")?.problemId,
    "triangle-midpoints",
  );
  assert.deepEqual(publishedHeadSelectionPatch(previous, next, {
    problemId: "triangle-midpoints",
    projectionId: "openrouter-research-v1",
    runId: "triangle-2",
  }), { runId: "triangle-3" });
});

test("offers a precise latest-state patch only for historical overlays", () => {
  const selection = {
    knowledgeRunId: "knowledge-1",
    knowledgeLatestRunId: "knowledge-3",
    creditRunId: "credit-2",
    creditLatestRunDigest: "credit-3",
  };
  assert.deepEqual(historicalOverlaySelection(selection), {
    knowledge: true,
    credit: true,
    any: true,
  });
  assert.deepEqual(latestOverlaySelectionPatch(selection), {
    runId: "knowledge-3",
    creditRunId: "credit-3",
  });

  assert.deepEqual(latestOverlaySelectionPatch({
    ...selection,
    knowledgeRunId: "knowledge-3",
  }), { creditRunId: "credit-3" });
});

test("preserves transaction detail tabs with an explicit availability fallback", () => {
  assert.equal(preferredTransactionDetailMode("credit"), "credit");
  assert.equal(preferredTransactionDetailMode("judgment"), "judgment");
  assert.equal(preferredTransactionDetailMode("verification"), "verification");
  assert.equal(preferredTransactionDetailMode("transaction"), "transaction");
  assert.equal(preferredTransactionDetailMode("node"), "transaction");
  assert.equal(preferredTransactionDetailMode(undefined), "transaction");

  assert.equal(resolveTransactionDetailMode("credit", { hasJudgment: true, hasVerification: true, hasCredit: true }), "credit");
  assert.equal(resolveTransactionDetailMode("credit", { hasJudgment: true, hasVerification: true, hasCredit: false }), "transaction");
  assert.equal(resolveTransactionDetailMode("judgment", { hasJudgment: true, hasVerification: false, hasCredit: false }), "judgment");
  assert.equal(resolveTransactionDetailMode("judgment", { hasJudgment: false, hasVerification: true, hasCredit: true }), "transaction");
  assert.equal(resolveTransactionDetailMode("verification", { hasJudgment: false, hasVerification: true, hasCredit: false }), "verification");
  assert.equal(resolveTransactionDetailMode("verification", { hasJudgment: true, hasVerification: false, hasCredit: true }), "transaction");
  assert.equal(resolveTransactionDetailMode("transaction", { hasJudgment: true, hasVerification: true, hasCredit: true }), "transaction");
});

test("derives related contributions from every node in a program subtree", () => {
  const nodes = {
    root: { id: "root", parentId: null, type: "root", subjects: [], evidence: [] },
    program: {
      id: "program",
      parentId: "root",
      type: "program",
      subjects: [{ kind: "transaction", id: "tx-program" }],
      evidence: [],
    },
    "program/method": {
      id: "program/method",
      parentId: "program",
      type: "method",
      subjects: [{ kind: "transaction", id: "tx-method" }],
      evidence: [{ kind: "transaction", id: "tx-shared" }],
    },
    "program/method/claim": {
      id: "program/method/claim",
      parentId: "program/method",
      type: "claim",
      subjects: [{ kind: "transaction", id: "tx-shared" }],
      evidence: [{ kind: "transaction", id: "tx-claim" }],
    },
    "other-program": {
      id: "other-program",
      parentId: "root",
      type: "program",
      subjects: [{ kind: "transaction", id: "tx-other" }],
      evidence: [],
    },
  };

  assert.deepEqual(collectProgramContributionIds(nodes, "program"), [
    "tx-claim",
    "tx-method",
    "tx-program",
    "tx-shared",
  ]);
  assert.deepEqual(collectProgramContributionIds(nodes, "program/method"), []);
});

test("links only unique repository-known transaction and judgment references", () => {
  const firstTransaction = "abcdef0123456789abcdef0123456789abcdef01";
  const secondTransaction = "abcdef0987654321abcdef0987654321abcdef09";
  const judgment = "sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef";
  const resolver = createViewerReferenceResolver(
    [{ transactionId: firstTransaction }, { transactionId: secondTransaction }],
    [{ judgmentId: judgment }],
  );

  assert.deepEqual(resolver.resolve("abcdef01"), {
    kind: "transaction",
    id: firstTransaction,
    text: "abcdef01",
  });
  assert.equal(resolver.resolve("abcdef0"), null, "ambiguous prefixes stay inert");
  assert.deepEqual(resolver.resolve("sha256:1234567"), {
    kind: "judgment",
    id: judgment,
    text: "sha256:1234567",
  });
  assert.equal(resolver.resolve("feedface"), null, "unknown hexadecimal text stays inert");

  const linked = resolver.split(
    "ledger tx abcdef01 and judgment sha256:1234567; [elsewhere](javascript:alert(1))",
  );
  assert.deepEqual(
    linked.filter((part) => typeof part !== "string").map(({ kind, id }) => ({ kind, id })),
    [
      { kind: "transaction", id: firstTransaction },
      { kind: "judgment", id: judgment },
    ],
  );
  assert.match(linked.filter((part) => typeof part === "string").join(""), /javascript:alert/);
});

test("round-trips viewer state through the query string", () => {
  const search = applyViewerStateToSearch("?campaign=atlas&run=stale", {
    problemId: "triangle-problem",
    projectionId: "builder:main",
    creditProjectionId: "credit:main",
    creditRunId: "sha256:credit-run",
    runId: "run-3",
    nodeId: "claim/midpoint",
    transactionId: "abc123",
    directionId: "modular-search",
    judgmentId: "sha256:def456",
    query: "parallel lines",
    detailMode: "judgment",
  });

  assert.deepEqual(parseViewerState(search), {
    problemId: "triangle-problem",
    projectionId: "builder:main",
    creditProjectionId: "credit:main",
    creditRunId: "sha256:credit-run",
    runId: "run-3",
    nodeId: "claim/midpoint",
    transactionId: "abc123",
    directionId: "modular-search",
    judgmentId: "sha256:def456",
    query: "parallel lines",
    detailMode: "judgment",
  });
  assert.match(search, /campaign=atlas/);
  assert.deepEqual(parseViewerState("?detail=unknown&node=root"), { nodeId: "root" });
});

test("proxies repository projection state through the worker", async () => {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("catalog-test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  const catalog = { schemaVersion: 1, projections: [{ id: "live" }] };
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (request, init) => {
    assert.match(String(request), /api\.github\.com\/repos\/Layr-Labs\/math-flow\/contents\/viewer\/catalog\.json\?ref=projections/);
    assert.equal(init.headers.authorization, "Bearer test-token");
    assert.equal(init.headers.accept, "application/vnd.github.raw+json");
    return Response.json(catalog);
  };
  try {
    const response = await worker.fetch(
      new Request("http://localhost/api/catalog"),
      {
        ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) },
        MATH_FLOW_GITHUB_TOKEN: "test-token",
      },
      { waitUntil() {}, passThroughOnException() {} },
    );
    assert.equal(response.status, 200);
    assert.equal(response.headers.get("x-math-flow-source")?.includes("ref=projections"), true);
    assert.deepEqual(await response.json(), catalog);
  } finally {
    globalThis.fetch = originalFetch;
  }
});
