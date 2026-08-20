"use client";

import { Fragment, type CSSProperties, type ReactNode, useCallback, useEffect, useMemo, useRef, useState } from "react";
import katex from "katex";
import { validKnowledgeProjectionIndex } from "./catalogValidation.mjs";
import { compatibleCreditProjections as compatibleCreditProjectionList, creditRunAssignmentCount, formatCreditFraction, hierarchicalCreditForTransaction, isHierarchicalCreditProjection, isHierarchicalCreditRun } from "./creditPresentation.mjs";
import { splitDisplayMath, splitInlineMath } from "./markdownMath.mjs";
import { collectProgramContributionIds } from "./programContributions.mjs";
import { creditRunSelectionPatch, historicalOverlaySelection, knowledgeRunSelectionPatch, latestOverlaySelectionPatch, projectionByIdentity, publishedHeadSelectionPatch } from "./projectionHeadState.mjs";
import { createViewerReferenceResolver } from "./referenceLinks.mjs";
import { preferredTransactionDetailMode, resolveTransactionDetailMode } from "./transactionDetailMode.mjs";
import { validityReferenceGroups } from "./validityPresentation.mjs";
import { applyViewerStateToSearch, parseViewerState } from "./viewerState.mjs";

type Ref = {
  kind: string;
  id: string;
  ledgerPosition?: number;
  digest?: string | null;
  relation?: string;
};

type RevisionPointer = {
  revisionId: string;
  revisionNumber: number;
};

type AdjudicationPointer = RevisionPointer & {
  adjudicationId: string;
};

type KnowledgeNode = {
  id: string;
  parentId: string | null;
  type: string;
  title: string;
  summary: string;
  status: string;
  contentMarkdown: string;
  subjects: Ref[];
  evidence: Ref[];
  lineage?: Array<{ relation: "split-from" | "split-into" | "merged-from" | "merged-into"; nodeId: string }>;
  currentRevision?: RevisionPointer | null;
  currentAdjudication?: AdjudicationPointer | null;
  reportRef: { digest: string; section: string } | null;
  digest: string;
};

type Revision = {
  revisionId: string;
  adjudicationId?: string;
  revisionNumber: number;
  action: string;
  baseRevisionId: string | null;
  nodeId: string;
  subjects: Ref[];
  evidence: Ref[];
  facets?: Array<"topology" | "content" | "lifecycle" | "provenance">;
  issuedAtLedgerHead?: string;
  recordedAtLedgerHead?: string;
  changeRationale?: string;
  changeRef?: { digest: string; section: string };
  summary: string;
};

type Run = {
  id: string;
  ordinal: number;
  ledgerHead: string;
  problemLedgerHead?: string;
  runDigest: string;
  baseRun: string | null;
  cost: number;
  selection: { selectedNodeIds: string[]; rationale: string };
  normalizations: Array<Record<string, unknown>>;
  state: { nodes: Record<string, KnowledgeNode>; stateDigest: string };
  revisionIds: string[];
  addedRevisionIds: string[];
  changedNodeIds: string[];
  reportDigest: string;
  revisionSemantics?: "neutral-knowledge" | "legacy-adjudication";
  delta?: { contribution?: Record<string, unknown> } | Record<string, unknown>;
  runKind?: string;
  inputs?: { judgmentIds?: string[] } | null;
};

type Transaction = {
  ordinal: number;
  transactionId: string;
  contributionId: string;
  author: { displayName: string };
  contentMarkdown: string;
};

type ResearchDirectionEvent = {
  ordinal: number;
  canonicalOrdinal: number;
  transactionId: string;
  committedAt: number;
  eventId: string;
  directionId: string;
  eventType: "register" | "update" | "release" | "complete";
  path: string;
  author: { displayName: string };
  contentDigest: string;
  contentMarkdown: string;
  data: Record<string, unknown>;
};

type ResearchDirection = {
  directionId: string;
  title: string;
  summary: string;
  relatedKnowledgeNodeIds: string[];
  status: "active" | "released" | "completed";
  registeredEventId: string;
  registeredTransactionId: string;
  registeredAt: number;
  registeredBy: { displayName: string };
  currentEventId: string;
  currentTransactionId: string;
  currentAt: number;
  completionTransactionIds: string[];
  eventIds: string[];
};

type ResearchDirectionLedger = {
  problemId: string;
  directionLedgerHead: string | null;
  directionLedgerDigest: string;
  events: ResearchDirectionEvent[];
  directions: ResearchDirection[];
};

type JudgmentFinding = {
  claimKey: string;
  stance: string;
  summary: string;
  subjectTransactionIds: string[];
  evidenceTransactionIds: string[];
};

type ValidityAssessment = {
  claimKey: string;
  status: "valid" | "invalid" | "indeterminate";
  premiseStatus: "satisfied" | "missing" | "disputed" | "not-required";
  summary: string;
  scopeQualifications: string[];
  evidenceIssues: string[];
  evidenceTransactionIds: string[];
  requiredDependencyTransactionIds?: string[];
};

type JudgmentRecord = {
  schemaVersion: number;
  judgmentId: string;
  judgmentKind: "primary" | "reconciliation";
  problemId: string;
  ledgerHead: string;
  judgeSpec: { id: string; digest: string };
  subjects: Ref[];
  assessments?: ValidityAssessment[];
  findings: JudgmentFinding[];
  reportDigest: string;
  reconciliation?: {
    conflictId: string;
    inputJudgmentIds: string[];
    outcome: string;
    summary: string;
  };
};

type PublishedJudgment = {
  judgmentId: string;
  runDigest: string;
  judgmentKind: "primary" | "reconciliation";
  ledgerHead: string;
  problemLedgerHead: string;
  judgeSpec: { id: string; digest: string };
  models: string[];
  cost: number;
  reportDigest: string;
  reportMarkdown: string;
  declaredReferenceTransactionIdsByClaim?: Record<string, string[]>;
  record: JudgmentRecord;
};

type CreditKnowledgeRef = {
  nodeId: string;
  revisionId: string | null;
};

type CreditAssignment = {
  transactionId: string;
  significance: "foundational" | "major" | "supporting" | "minor" | "none" | "uncertain";
  roles: string[];
  knowledgeRefs: CreditKnowledgeRef[];
  reservationTransactionIds?: string[];
  directionRegistrationTransactionIds?: string[];
  reportSection: string;
};

type CreditRun = {
  id: string;
  runDigest: string;
  ledgerHead: string;
  problemLedgerHead: string;
  problemLedgerDigest: string;
  projectionId: string;
  projectionSpecDigest: string;
  dependencyLockDigest: string;
  dependency: {
    projectionId: string;
    runDigest: string;
    artifact: { digest: string; path: string; role: string };
  };
  assignments: CreditAssignment[];
  reportMarkdown: string;
  creditInput: Record<string, unknown>;
  dependencyLock: Record<string, unknown>;
  models: string[];
  cost: number;
  knowledgeProjectionIds: string[];
  currentProblemLedger: boolean;
  currentKnowledgeDependency: boolean;
  stale: boolean;
  staleReasons: string[];
};

type CreditFraction = {
  numerator: string;
  denominator: string;
};

type HierarchicalCreditEffect = {
  threadId: string;
  withoutWork: string;
  withWork: string;
  rationale: string;
};

type HierarchicalCreditChild = {
  kind: "program" | "contribution";
  id: string;
  referenceBaseStateDigest: string;
  referencePostStateDigest: string;
  horizonStateDigest: string;
  horizonLedgerHead: string;
  counterfactual: string;
  directEffects: HierarchicalCreditEffect[];
  obviatedEffects: HierarchicalCreditEffect[];
  directWork: string;
  obviatedWork: string;
  totalWork: string;
  confidence: "low" | "medium" | "high";
  evidenceRefs: string[];
  allocationShare: CreditFraction;
};

type HierarchicalCreditEvaluation = {
  programId: string;
  unattributedWork: string;
  unattributedShare: CreditFraction;
  unattributedHorizonStateDigest: string;
  rationale: string;
  children: HierarchicalCreditChild[];
  digest: string;
};

type HierarchicalCreditRun = Omit<CreditRun, "assignments" | "reportMarkdown"> & {
  creditState: {
    programStateDigest: string;
    horizonStateDigest: string;
    evaluations: Record<string, HierarchicalCreditEvaluation>;
    allocations: Record<string, CreditFraction>;
    residualAllocations: Record<string, CreditFraction>;
    stateDigest: string;
  };
};

type AnyCreditRun = CreditRun | HierarchicalCreditRun;

export type ViewerData = {
  problem: { id: string; title: string; statementMarkdown: string };
  ledgerHead: string;
  transactions: Transaction[];
  judgments?: PublishedJudgment[];
  runs: Run[];
  revisions: Revision[];
  reports: Array<{ runId: string; digest: string; markdown: string }>;
  latestRunId: string;
};

type RepositoryProjection = {
  id: string;
  problemId: string;
  label: string;
  builder: { id: string; digest: string };
  latestRunDigest: string;
  runCount: number;
  data: ViewerData;
};

type RepositoryCreditProjection = {
  id: string;
  problemId: string;
  label: string;
  knowledgeProjectionIds: string[];
  latestRunDigest: string | null;
  selectionStatus: "pending" | "current" | "historical" | "ambiguous";
  runCount: number;
  runs: CreditRun[];
};

type RepositoryHierarchicalCreditProjection = {
  id: string;
  problemId: string;
  label: string;
  researchProjectionIds: string[];
  latestRunDigest: string | null;
  selectionStatus: "pending" | "current" | "historical" | "ambiguous";
  runCount: number;
  runs: HierarchicalCreditRun[];
};

type AnyCreditProjection = RepositoryCreditProjection | RepositoryHierarchicalCreditProjection;

type ObjectiveAttestation = {
  problemId: string;
  transactionId: string;
  contributionId: string;
  requestDigest: string;
  verifier: { id: string; specDigest: string; implementation: string };
  environmentDigest: string;
  selectionStatus: "pending" | "passed" | "failed" | "error";
  run: null | {
    attestationId: string;
    runDigest: string;
    status: "passed" | "failed" | "error";
    result: { status: string; exitCode: number | null; timedOut: boolean };
    verifier: { id: string; specDigest: string; implementation: string };
    environmentDigest: string;
    producer: Record<string, unknown>;
    stdout: { text: string; truncated: boolean; bytes: number; digest: string };
    stderr: { text: string; truncated: boolean; bytes: number; digest: string };
    record: Record<string, unknown>;
  };
};

export type ViewerCatalog = {
  schemaVersion: number;
  repository: { slug: string; canonicalRef: string; projectionRef: string };
  projections: RepositoryProjection[];
  creditProjections?: RepositoryCreditProjection[];
  hierarchicalCreditProjections?: RepositoryHierarchicalCreditProjection[];
  researchDirections?: ResearchDirectionLedger[];
  objectiveAttestations?: ObjectiveAttestation[];
  defaultProjectionId: string | null;
};

type DetailMode = "node" | "transaction" | "judgment" | "verification" | "credit" | "report" | "direction";

type ViewerState = {
  problemId?: string;
  projectionId?: string;
  creditProjectionId?: string;
  creditRunId?: string;
  runId?: string;
  nodeId?: string;
  transactionId?: string;
  directionId?: string;
  judgmentId?: string;
  query?: string;
  detailMode?: DetailMode;
};

const short = (value: string | null, size = 7) =>
  value ? value.replace(/^sha256:/, "").slice(0, size) : "genesis";

const label = (value: string) => value.replaceAll("-", " ");

const currentRevision = (node: KnowledgeNode) =>
  node.currentRevision ?? node.currentAdjudication ?? null;

const revisionLedgerHead = (revision: Revision) =>
  revision.recordedAtLedgerHead ?? revision.issuedAtLedgerHead ?? null;

type ViewerReference = {
  kind: "transaction" | "judgment";
  id: string;
  text: string;
};

type ViewerReferenceResolver = {
  resolve(value: string): ViewerReference | null;
  split(value: string): Array<string | ViewerReference>;
};

type ReferenceActions = {
  resolver: ViewerReferenceResolver;
  openTransaction(id: string): void;
  openJudgment(id: string): void;
};

function judgmentMentionsTransaction(judgment: PublishedJudgment, transactionId: string) {
  return judgment.record.subjects.some((item) => item.id === transactionId) ||
    judgment.record.findings.some((finding) =>
      finding.subjectTransactionIds.includes(transactionId) ||
      finding.evidenceTransactionIds.includes(transactionId),
    );
}

function judgmentOutcomeSummary(judgment: PublishedJudgment) {
  const statuses = judgment.record.assessments?.map((assessment) => assessment.status) ?? [];
  if (statuses.length) return [...new Set(statuses)].join(" · ");
  return judgment.record.findings.map((finding) => finding.stance).join(" · ") || "no findings";
}

function transactionValiditySummary(judgments: PublishedJudgment[]) {
  const statuses = judgments.flatMap(
    (judgment) => judgment.record.assessments?.map((assessment) => assessment.status) ?? [],
  );
  if (!statuses.length) return null;
  const unique = [...new Set(statuses)];
  return unique.length === 1 ? unique[0] : "mixed";
}

function isViewerCatalog(value: unknown): value is ViewerCatalog {
  if (!value || typeof value !== "object") return false;
  const catalog = value as Partial<ViewerCatalog>;
  const validCredits = catalog.creditProjections === undefined || (
    Array.isArray(catalog.creditProjections) &&
    catalog.creditProjections.every((projection) =>
      typeof projection?.id === "string" &&
      typeof projection?.problemId === "string" &&
      Array.isArray(projection?.knowledgeProjectionIds) &&
      Array.isArray(projection?.runs) &&
      (projection.latestRunDigest === null || typeof projection.latestRunDigest === "string") &&
      typeof projection.selectionStatus === "string" &&
      ["pending", "current", "historical", "ambiguous"].includes(projection.selectionStatus) &&
      projection.runs.every((run) =>
        run?.id === run?.runDigest &&
        Array.isArray(run?.assignments) &&
        typeof run?.reportMarkdown === "string" &&
        typeof run?.dependencyLockDigest === "string" &&
        typeof run?.stale === "boolean",
      ),
    )
  );
  const validHierarchicalCredits = catalog.hierarchicalCreditProjections === undefined || (
    Array.isArray(catalog.hierarchicalCreditProjections) &&
    catalog.hierarchicalCreditProjections.every((projection) =>
      typeof projection?.id === "string" &&
      typeof projection?.problemId === "string" &&
      Array.isArray(projection?.researchProjectionIds) &&
      Array.isArray(projection?.runs) &&
      (projection.latestRunDigest === null || typeof projection.latestRunDigest === "string") &&
      typeof projection.selectionStatus === "string" &&
      ["pending", "current", "historical", "ambiguous"].includes(projection.selectionStatus) &&
      projection.runs.every((run) =>
        run?.id === run?.runDigest &&
        typeof run?.creditState?.evaluations === "object" &&
        typeof run?.creditState?.allocations === "object" &&
        typeof run?.dependencyLockDigest === "string" &&
        typeof run?.stale === "boolean",
      ),
    )
  );
  const validDirections = catalog.researchDirections === undefined || (
    Array.isArray(catalog.researchDirections) &&
    catalog.researchDirections.every((item) =>
      typeof item?.problemId === "string" &&
      typeof item?.directionLedgerDigest === "string" &&
      Array.isArray(item?.events) &&
      Array.isArray(item?.directions),
    )
  );
  const validAttestations = catalog.objectiveAttestations === undefined || (
    Array.isArray(catalog.objectiveAttestations) &&
    catalog.objectiveAttestations.every((item) =>
      typeof item?.problemId === "string" &&
      typeof item?.transactionId === "string" &&
      typeof item?.requestDigest === "string" &&
      ["pending", "passed", "failed", "error"].includes(item?.selectionStatus) &&
      (item.run === null || (
        typeof item.run?.runDigest === "string" &&
        typeof item.run?.attestationId === "string" &&
        typeof item.run?.stdout?.text === "string" &&
        typeof item.run?.stderr?.text === "string"
      )),
    )
  );
  return catalog.schemaVersion === 1 &&
    !!catalog.repository &&
    validKnowledgeProjectionIndex(catalog.projections) &&
    validCredits && validHierarchicalCredits && validDirections && validAttestations;
}

const unavailableCatalog: ViewerCatalog = {
  schemaVersion: 1,
  repository: { slug: "Layr-Labs/math-flow", canonicalRef: "main", projectionRef: "projections" },
  projections: [],
  creditProjections: [],
  hierarchicalCreditProjections: [],
  researchDirections: [],
  objectiveAttestations: [],
  defaultProjectionId: null,
};

export function RepositoryKnowledgeViewer() {
  const [catalog, setCatalog] = useState(unavailableCatalog);
  const catalogRef = useRef(unavailableCatalog);
  const [source, setSource] = useState<"checking" | "repository" | "unavailable">("checking");
  const [viewerState, setViewerState] = useState<ViewerState>(() =>
    typeof window === "undefined" ? {} : parseViewerState(window.location.search) as ViewerState,
  );
  const viewerStateRef = useRef(viewerState);
  const updateViewerState = useCallback((patch: Partial<ViewerState>) => {
    const next = { ...viewerStateRef.current, ...patch };
    viewerStateRef.current = next;
    setViewerState(next);
  }, []);

  useEffect(() => {
    const restoreState = () => {
      const restored = parseViewerState(window.location.search) as ViewerState;
      viewerStateRef.current = restored;
      setViewerState(restored);
    };
    window.addEventListener("popstate", restoreState);
    return () => window.removeEventListener("popstate", restoreState);
  }, []);

  useEffect(() => {
    const search = applyViewerStateToSearch(window.location.search, viewerState);
    const nextUrl = `${window.location.pathname}${search}${window.location.hash}`;
    window.history.replaceState(window.history.state, "", nextUrl);
  }, [viewerState]);

  useEffect(() => {
    let active = true;
    async function refresh() {
      try {
        const response = await fetch("/api/catalog", { cache: "no-store" });
        if (!response.ok) throw new Error(`catalog returned ${response.status}`);
        const next: unknown = await response.json();
        if (!isViewerCatalog(next)) throw new Error("catalog shape is invalid");
        if (!active) return;
        const selectionPatch = publishedHeadSelectionPatch(
          catalogRef.current,
          next,
          viewerStateRef.current,
        ) as Partial<ViewerState>;
        catalogRef.current = next;
        setCatalog(next);
        if (Object.keys(selectionPatch).length) updateViewerState(selectionPatch);
        setSource("repository");
      } catch {
        if (active) {
          catalogRef.current = unavailableCatalog;
          setCatalog(unavailableCatalog);
          setSource("unavailable");
        }
      }
    }
    void refresh();
    const interval = window.setInterval(refresh, 30_000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [updateViewerState]);

  if (source === "checking") {
    return (
      <main className="repository-loading" aria-live="polite">
        <div className="loading-mark">MF</div>
        <span className="eyebrow">Math Flow · research atlas</span>
        <h1>Loading repository state</h1>
        <p>The atlas remains empty unless the live governed catalog is available.</p>
        <span className="loading-line" aria-hidden="true" />
      </main>
    );
  }

  if (!catalog.projections.length) {
    return (
      <main className="repository-loading repository-empty" aria-live="polite">
        <div className="loading-mark">MF</div>
        <span className="eyebrow">Math Flow · research atlas</span>
        <h1>{source === "unavailable" ? "Repository catalog unavailable" : "No active knowledge states"}</h1>
        <p>{source === "unavailable"
          ? "The governed projection catalog could not be loaded. No problem or archived snapshot is shown while repository state is unavailable."
          : "The live repository catalog contains no published knowledge projections for active problems."}</p>
      </main>
    );
  }

  const problems = [...new Set(catalog.projections.map((item) => item.problemId))].sort();
  const requestedProjection = projectionByIdentity(
    catalog,
    viewerState.problemId,
    viewerState.projectionId,
  ) as RepositoryProjection | null;
  const preferredProjection = catalog.projections.find((item) => item.id === catalog.defaultProjectionId) ?? catalog.projections[0];
  const effectiveProblem = requestedProjection?.problemId ??
    (viewerState.problemId && problems.includes(viewerState.problemId) ? viewerState.problemId : preferredProjection.problemId);
  const problemProjections = catalog.projections.filter((item) => item.problemId === effectiveProblem);
  const projection = requestedProjection ?? problemProjections[0];
  const compatibleCreditProjections = compatibleCreditProjectionList(
    catalog,
    effectiveProblem,
    projection.id,
  ) as AnyCreditProjection[];
  const requestedCreditProjection = compatibleCreditProjections.find(
    (item) => item.id === viewerState.creditProjectionId,
  );
  const creditProjection = requestedCreditProjection ?? compatibleCreditProjections[0];
  const knowledgeRun = projection.data.runs.find((item) => item.id === viewerState.runId)
    ?? projection.data.runs.find((item) => item.id === projection.data.latestRunId)
    ?? projection.data.runs.at(-1)!;
  const creditRun = creditProjection?.runs.find(
    (item) => item.runDigest === viewerState.creditRunId,
  ) ?? creditProjection?.runs.find(
    (item) => item.runDigest === creditProjection.latestRunDigest,
  ) as AnyCreditRun | undefined;
  const researchDirections = (catalog.researchDirections ?? []).find(
    (item) => item.problemId === effectiveProblem,
  );
  const objectiveAttestations = (catalog.objectiveAttestations ?? []).filter(
    (item) => item.problemId === effectiveProblem,
  );
  const historicalSelection = historicalOverlaySelection({
    knowledgeRunId: knowledgeRun.id,
    knowledgeLatestRunId: projection.data.latestRunId,
    creditRunId: creditRun?.runDigest,
    creditLatestRunDigest: creditProjection?.latestRunDigest,
  });

  function chooseProblem(nextProblem: string) {
    const nextProjection = catalog.projections.find((item) => item.problemId === nextProblem);
    if (!nextProjection) return;
    updateViewerState({
      problemId: nextProblem,
      projectionId: nextProjection.id,
      creditProjectionId: undefined,
      creditRunId: undefined,
      runId: undefined,
      nodeId: undefined,
      transactionId: undefined,
      directionId: undefined,
      judgmentId: undefined,
      query: undefined,
      detailMode: undefined,
    });
  }

  function chooseProjection(nextProjectionId: string) {
    const nextProjection = problemProjections.find((item) => item.id === nextProjectionId);
    if (!nextProjection) return;
    updateViewerState({
      problemId: nextProjection.problemId,
      projectionId: nextProjection.id,
      creditProjectionId: undefined,
      creditRunId: undefined,
      runId: undefined,
      nodeId: undefined,
      transactionId: undefined,
      directionId: undefined,
      judgmentId: undefined,
      query: undefined,
      detailMode: undefined,
    });
  }

  function chooseCreditProjection(nextProjectionId: string) {
    const nextProjection = compatibleCreditProjections.find(
      (item) => item.id === nextProjectionId,
    );
    updateViewerState({
      creditProjectionId: nextProjection?.id,
      creditRunId: nextProjection?.latestRunDigest ?? undefined,
      detailMode: viewerState.detailMode === "credit" ? "transaction" : viewerState.detailMode,
    });
  }

  function chooseKnowledgeRun(nextRunId: string) {
    const nextRun = projection.data.runs.find((item) => item.id === nextRunId);
    if (!nextRun) return;
    const currentNodeId = viewerState.nodeId ?? "root";
    updateViewerState({
      ...knowledgeRunSelectionPatch({
        problemId: effectiveProblem,
        projectionId: projection.id,
        runId: nextRunId,
      }),
      nodeId: nextRun.state.nodes[currentNodeId] ? currentNodeId : "root",
      transactionId: undefined,
      directionId: undefined,
      judgmentId: undefined,
      detailMode: "node",
    });
  }

  function chooseCreditRun(nextRunDigest: string) {
    updateViewerState(creditRunSelectionPatch({
      projectionId: creditProjection?.id,
      runId: nextRunDigest || undefined,
    }) as Partial<ViewerState>);
  }

  function advanceToLatest() {
    updateViewerState(latestOverlaySelectionPatch({
      knowledgeRunId: knowledgeRun.id,
      knowledgeLatestRunId: projection.data.latestRunId,
      creditRunId: creditRun?.runDigest,
      creditLatestRunDigest: creditProjection?.latestRunDigest,
    }) as Partial<ViewerState>);
  }

  return (
    <div className="repository-shell">
      <nav className="repository-toolbar" aria-label="Repository projection selection">
        <div className="repository-source">
          <span className={`source-light source-${source}`} />
          <span>
            <strong>{catalog.repository.slug}</strong>
            <small>{catalog.repository.canonicalRef} → {catalog.repository.projectionRef} · live repository state</small>
          </span>
        </div>
        <div className="problem-control">
          <label className="problem-selector">
            <span>Problem</span>
            <select value={effectiveProblem} onChange={(event) => chooseProblem(event.target.value)}>
              {problems.map((problem) => <option value={problem} key={problem}>{label(problem)}</option>)}
            </select>
          </label>
          {historicalSelection.any && (
            <button type="button" className="latest-state-button" onClick={advanceToLatest}>
              {historicalSelection.knowledge && historicalSelection.credit
                ? "View latest knowledge & credit"
                : historicalSelection.knowledge
                  ? "View latest knowledge"
                  : "View latest credit"}
            </button>
          )}
        </div>
        <fieldset className="selector-bubble knowledge-selector-bubble">
          <legend>Knowledge</legend>
          <label>
            <span>Projection</span>
            <select aria-label="Knowledge projection" value={projection.id} onChange={(event) => chooseProjection(event.target.value)}>
              {problemProjections.map((item) => <option value={item.id} key={item.id}>{item.label} · {short(item.latestRunDigest)}</option>)}
            </select>
          </label>
          <label>
            <span>State</span>
            <select aria-label="Knowledge state" value={knowledgeRun.id} onChange={(event) => chooseKnowledgeRun(event.target.value)}>
              {projection.data.runs.map((item) => (
                <option value={item.id} key={item.id}>
                  State {String(item.ordinal).padStart(2, "0")} · {short(item.ledgerHead)} · {item.id === projection.data.latestRunId ? "current" : "historical"}
                </option>
              ))}
            </select>
            <small>{knowledgeRun.id === projection.data.latestRunId ? "Current state" : "Historical state"} · +{knowledgeRun.addedRevisionIds.length} revisions</small>
          </label>
        </fieldset>
        <fieldset className="selector-bubble credit-selector-bubble">
          <legend>Credit</legend>
          <label>
            <span>Projection</span>
            <select
              aria-label="Credit projection"
              value={creditProjection?.id ?? ""}
              onChange={(event) => chooseCreditProjection(event.target.value)}
              disabled={!compatibleCreditProjections.length}
            >
              {!compatibleCreditProjections.length && <option value="">No credit projection</option>}
              {compatibleCreditProjections.map((item) => (
                <option value={item.id} key={item.id}>
                  {item.label} · {isHierarchicalCreditProjection(item) ? "hierarchical two-term" : "qualitative"} · {item.latestRunDigest
                    ? short(item.latestRunDigest)
                    : item.runCount
                      ? `${item.runCount} runs · choose`
                      : "not run"}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>State</span>
            <select
              aria-label="Credit state"
              value={creditRun?.runDigest ?? ""}
              onChange={(event) => chooseCreditRun(event.target.value)}
              disabled={!creditProjection?.runs.length}
            >
              {!creditProjection?.runs.length && <option value="">No published credit yet</option>}
              {creditProjection?.runs.length && !creditRun && <option value="" disabled>Choose an assessment</option>}
              {creditProjection?.runs.map((item, index) => (
                <option value={item.runDigest} key={item.runDigest}>
                  {isHierarchicalCreditProjection(creditProjection) ? "Allocation" : "Assessment"} {String(index + 1).padStart(2, "0")} · {short(item.runDigest)} · {item.runDigest === creditProjection.latestRunDigest ? "current" : "historical"}
                </option>
              ))}
            </select>
            <small>{creditRun
              ? `${creditRun.runDigest === creditProjection?.latestRunDigest ? "Current state" : "Historical state"} · ${creditRun.stale ? "stale inputs" : "current inputs"} · ${creditRunAssignmentCount(creditRun)} allocations`
              : creditProjection?.runs.length
                ? "No credit terminal selected"
                : "Waiting for the first verified run"}</small>
          </label>
        </fieldset>
      </nav>
      <KnowledgeViewer
        key={`${projection.id}:${projection.latestRunDigest}`}
        data={projection.data}
        problemId={effectiveProblem}
        projectionId={projection.id}
        creditProjection={creditProjection}
        researchDirections={researchDirections}
        objectiveAttestations={objectiveAttestations}
        viewerState={viewerState}
        onViewerStateChange={updateViewerState}
      />
    </div>
  );
}

function ReferenceLink({ reference, actions }: { reference: ViewerReference; actions: ReferenceActions }) {
  const kindLabel = reference.kind === "transaction" ? "transaction" : "judgment";
  return (
    <button
      type="button"
      className={`markdown-reference reference-${reference.kind}`}
      onClick={() => reference.kind === "transaction"
        ? actions.openTransaction(reference.id)
        : actions.openJudgment(reference.id)}
      aria-label={`Open ${kindLabel} ${short(reference.id, 12)}`}
      title={`Open ${kindLabel} ${short(reference.id, 12)}`}
    >
      {reference.text}
    </button>
  );
}

function referenceText(text: string, key: string, actions?: ReferenceActions): ReactNode[] {
  if (!actions) return [<Fragment key={key}>{text}</Fragment>];
  return actions.resolver.split(text).map((part, index) =>
    typeof part === "string"
      ? <Fragment key={`${key}-${index}`}>{part}</Fragment>
      : <ReferenceLink reference={part} actions={actions} key={`${key}-${index}`} />,
  );
}

function MathExpression({ value, displayMode }: { value: string; displayMode: boolean }) {
  const html = katex.renderToString(value.trim(), {
    displayMode,
    strict: false,
    throwOnError: false,
    trust: false,
  });
  const Tag = displayMode ? "div" : "span";
  return <Tag className={displayMode ? "math-display" : "math-inline"} dangerouslySetInnerHTML={{ __html: html }} />;
}

function inlineText(text: string, key: string, actions?: ReferenceActions): ReactNode[] {
  return splitInlineMath(text).map((segment, index) => segment.type === "math"
    ? <MathExpression value={segment.value} displayMode={false} key={`${key}-${index}-math`} />
    : <Fragment key={`${key}-${index}-text`}>{referenceText(segment.value, `${key}-${index}`, actions)}</Fragment>);
}

function inline(text: string, actions?: ReferenceActions): ReactNode[] {
  return text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).map((part, index) => {
    if (part.startsWith("`") && part.endsWith("`")) {
      const value = part.slice(1, -1);
      const reference = actions?.resolver.resolve(value);
      return reference
        ? <ReferenceLink reference={reference} actions={actions} key={index} />
        : <code key={index}>{value}</code>;
    }
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{inlineText(part.slice(2, -2), `${index}-strong`, actions)}</strong>;
    }
    return <Fragment key={index}>{inlineText(part, `${index}-text`, actions)}</Fragment>;
  });
}

function MarkdownLines({ value, actions, segmentKey }: { value: string; actions?: ReferenceActions; segmentKey: number }) {
  return (
    <>
      {value.split("\n").map((raw, index) => {
        const key = `${segmentKey}-${index}`;
        const line = raw.trim();
        if (!line || line === "---") return <div className="markdown-gap" key={key} />;
        if (line.startsWith("### ")) return <h4 key={key}>{inline(line.slice(4), actions)}</h4>;
        if (line.startsWith("## ")) return <h3 key={key}>{inline(line.slice(3), actions)}</h3>;
        if (line.startsWith("# ")) return <h2 key={key}>{inline(line.slice(2), actions)}</h2>;
        if (/^\d+\. /.test(line)) return <p className="numbered" key={key}>{inline(line, actions)}</p>;
        if (line.startsWith("- ")) return <p className="bullet" key={key}>{inline(line.slice(2), actions)}</p>;
        return <p key={key}>{inline(line, actions)}</p>;
      })}
    </>
  );
}

function Markdown({ value, actions }: { value: string; actions?: ReferenceActions }) {
  return (
    <div className="markdown">
      {splitDisplayMath(value).map((segment, index) => segment.type === "math"
        ? <MathExpression value={segment.value} displayMode key={`${index}-math`} />
        : <MarkdownLines value={segment.value} actions={actions} segmentKey={index} key={`${index}-text`} />)}
    </div>
  );
}

function markdownSection(markdown: string, heading: string) {
  const lines = markdown.split("\n");
  const start = lines.findIndex((line) => line.trim() === heading);
  if (start < 0) return markdown;
  const relativeEnd = lines.slice(start + 1).findIndex((line) => line.trim().startsWith("## "));
  const end = relativeEnd < 0 ? lines.length : start + 1 + relativeEnd;
  return lines.slice(start, end).join("\n").trim();
}

function TypeMark({ type }: { type: string }) {
  const marks: Record<string, string> = {
    root: "◎",
    claim: "◇",
    method: "↗",
    lemma: "∴",
    question: "?",
    dispute: "!",
    program: "⌘",
    result: "=",
    proof: "∎",
    computation: "#",
    tool: "⚙"
  };
  return <span className={`type-mark type-${type}`} aria-hidden="true">{marks[type] ?? "·"}</span>;
}

export function KnowledgeViewer({
  data,
  problemId,
  projectionId,
  creditProjection,
  researchDirections,
  objectiveAttestations,
  viewerState,
  onViewerStateChange,
}: {
  data: ViewerData;
  problemId: string;
  projectionId: string;
  creditProjection?: AnyCreditProjection;
  researchDirections?: ResearchDirectionLedger;
  objectiveAttestations?: ObjectiveAttestation[];
  viewerState: ViewerState;
  onViewerStateChange(patch: Partial<ViewerState>): void;
}) {
  const judgments = useMemo(() => data.judgments ?? [], [data.judgments]);
  const query = viewerState.query ?? "";
  const run = data.runs.find((item) => item.id === viewerState.runId) ?? data.runs.at(-1)!;
  const creditRun = creditProjection?.runs.find(
    (item) => item.runDigest === viewerState.creditRunId,
  ) ?? creditProjection?.runs.find(
    (item) => item.runDigest === creditProjection.latestRunDigest,
  ) as AnyCreditRun | undefined;
  const hierarchicalCreditRun = creditRun && isHierarchicalCreditRun(creditRun)
    ? creditRun as HierarchicalCreditRun
    : undefined;
  const qualitativeCreditRun = creditRun && !isHierarchicalCreditRun(creditRun)
    ? creditRun as CreditRun
    : undefined;
  const runLedgerPosition = data.transactions.find(
    (item) => item.transactionId === (run.problemLedgerHead ?? run.ledgerHead),
  )?.ordinal ?? data.transactions.length;
  const judgmentIdsAtRun = useMemo(
    () => new Set(
      data.runs
        .filter((item) => item.ordinal <= run.ordinal)
        .flatMap((item) => item.inputs?.judgmentIds ?? []),
    ),
    [data.runs, run.ordinal],
  );
  const hasJudgmentRouting = data.runs.some((item) => (item.inputs?.judgmentIds?.length ?? 0) > 0);
  const runJudgments = useMemo(
    () => judgments.filter((item) =>
      hasJudgmentRouting
        ? judgmentIdsAtRun.has(item.judgmentId)
        : item.record.subjects.some((subject) => (subject.ledgerPosition ?? 0) <= runLedgerPosition),
    ),
    [judgments, judgmentIdsAtRun, hasJudgmentRouting, runLedgerPosition],
  );
  const referenceTransactions = useMemo(
    () => data.transactions.filter((item) => item.ordinal <= runLedgerPosition),
    [data.transactions, runLedgerPosition],
  );
  const referenceJudgments = useMemo(
    () => runJudgments.filter((judgment) =>
      referenceTransactions.some((transaction) =>
        judgmentMentionsTransaction(judgment, transaction.transactionId),
      ),
    ),
    [referenceTransactions, runJudgments],
  );
  const referenceResolver = useMemo<ViewerReferenceResolver>(
    () => createViewerReferenceResolver(referenceTransactions, referenceJudgments),
    [referenceTransactions, referenceJudgments],
  );
  const nodes = run.state.nodes;
  const isResearchProgramState = Boolean(
    (run.delta && "contribution" in run.delta) ||
    Object.keys(nodes).some((id) => id.startsWith("thread:") || id.startsWith("item:")),
  );
  const researchProgramCount = Object.values(nodes).filter((node) => node.type === "program" && node.id !== "root").length;
  const researchThreadCount = Object.keys(nodes).filter((id) => id.startsWith("thread:")).length;
  const researchItemCount = Object.keys(nodes).filter((id) => id.startsWith("item:")).length;
  const selectedNode = nodes[viewerState.nodeId ?? "root"] ?? nodes.root;
  const runRevisionSet = useMemo(() => new Set(run.revisionIds), [run.revisionIds]);
  const nodeRevisions = data.revisions.filter(
    (item) => item.nodeId === selectedNode.id && runRevisionSet.has(item.revisionId),
  );
  const report = data.reports.find((item) => item.digest === selectedNode.reportRef?.digest);
  const programContributionIds = useMemo(
    () => new Set(collectProgramContributionIds(nodes, selectedNode.id)),
    [nodes, selectedNode.id],
  );
  const relatedProgramContributions = useMemo(
    () => selectedNode.type === "program"
      ? data.transactions.filter((item) =>
        item.ordinal <= runLedgerPosition && programContributionIds.has(item.transactionId),
      )
      : [],
    [data.transactions, programContributionIds, runLedgerPosition, selectedNode.type],
  );
  const nodeCreditAssignments = useMemo(
    () => qualitativeCreditRun?.assignments.filter((assignment) =>
      assignment.knowledgeRefs.some((reference) => reference.nodeId === selectedNode.id),
    ) ?? [],
    [qualitativeCreditRun, selectedNode.id],
  );
  const selectedProgramCredit = selectedNode.type === "program"
    ? hierarchicalCreditRun?.creditState.evaluations[selectedNode.id]
    : undefined;

  const children = useMemo(() => {
    const result: Record<string, string[]> = {};
    Object.values(nodes).forEach((node) => {
      const parent = node.parentId ?? "__root__";
      result[parent] ??= [];
      result[parent].push(node.id);
    });
    Object.values(result).forEach((ids) =>
      ids.sort((a, b) => nodes[a].title.localeCompare(nodes[b].title)),
    );
    return result;
  }, [nodes]);

  const visibleIds = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return new Set(Object.keys(nodes));
    const direct = Object.values(nodes)
      .filter((node) => `${node.id} ${node.title} ${node.summary}`.toLowerCase().includes(needle))
      .map((node) => node.id);
    const visible = new Set(direct);
    direct.forEach((id) => {
      let parent = nodes[id]?.parentId;
      while (parent) {
        visible.add(parent);
        parent = nodes[parent]?.parentId;
      }
    });
    return visible;
  }, [nodes, query]);

  const selectedTransaction = data.transactions.find((item) =>
    item.transactionId === viewerState.transactionId && item.ordinal <= runLedgerPosition,
  );
  const selectedDirection = researchDirections?.directions.find(
    (item) => item.directionId === viewerState.directionId,
  );
  const selectedDirectionEvents = selectedDirection
    ? researchDirections?.events.filter(
      (item) => item.directionId === selectedDirection.directionId,
    ) ?? []
    : [];
  const transactionId = selectedTransaction?.transactionId;
  const selectedCreditAssignment = qualitativeCreditRun?.assignments.find(
    (item) => item.transactionId === transactionId,
  );
  const selectedHierarchicalCredit = hierarchicalCreditRun
    ? hierarchicalCreditForTransaction(hierarchicalCreditRun, transactionId) as {
      allocation: CreditFraction | null;
      child: HierarchicalCreditChild;
      evaluation: HierarchicalCreditEvaluation;
    } | null
    : null;
  const selectedAttestation = objectiveAttestations?.find(
    (item) => item.transactionId === transactionId,
  );
  const transactionJudgments = selectedTransaction
    ? runJudgments.filter((item) => judgmentMentionsTransaction(item, selectedTransaction.transactionId))
    : [];
  const selectedJudgment = transactionJudgments.find((item) => item.judgmentId === viewerState.judgmentId) ?? transactionJudgments.at(-1);
  const detailMode: DetailMode = selectedDirection
    ? "direction"
    : selectedTransaction
    ? resolveTransactionDetailMode(viewerState.detailMode, {
      hasJudgment: transactionJudgments.length > 0,
      hasVerification: Boolean(selectedAttestation),
      hasCredit: Boolean(selectedCreditAssignment || selectedHierarchicalCredit),
    })
    : viewerState.detailMode === "report" ? "report" : "node";

  useEffect(() => {
    onViewerStateChange({
      problemId,
      projectionId,
      creditProjectionId: creditProjection?.id,
      creditRunId: creditRun?.runDigest,
      runId: run.id,
      nodeId: selectedNode.id,
      transactionId,
      directionId: selectedDirection?.directionId,
      judgmentId: selectedTransaction ? selectedJudgment?.judgmentId : undefined,
      detailMode: selectedTransaction
        ? preferredTransactionDetailMode(viewerState.detailMode)
        : detailMode,
    });
  }, [creditProjection?.id, creditRun?.runDigest, detailMode, onViewerStateChange, problemId, projectionId, run.id, selectedDirection?.directionId, selectedJudgment?.judgmentId, selectedNode.id, selectedTransaction, transactionId, viewerState.detailMode]);

  const transactionDirectIds = useMemo(() => new Set(
    transactionId
      ? Object.values(nodes)
        .filter((node) =>
          node.subjects.some((item) => item.id === transactionId) ||
          node.evidence.some((item) => item.id === transactionId),
        )
        .map((node) => node.id)
      : [],
  ), [nodes, transactionId]);

  const transactionContextIds = useMemo(() => {
    if (!transactionId) return new Set(Object.keys(nodes));
    const context = new Set(transactionDirectIds);
    transactionDirectIds.forEach((id) => {
      let parent = nodes[id]?.parentId;
      while (parent) {
        context.add(parent);
        parent = nodes[parent]?.parentId;
      }
    });
    return context;
  }, [nodes, transactionDirectIds, transactionId]);

  function relation(node: KnowledgeNode) {
    if (!transactionId) return null;
    if (node.subjects.some((item) => item.id === transactionId)) return "subject";
    if (node.evidence.some((item) => item.id === transactionId)) return "evidence";
    return null;
  }

  function nodeKind(node: KnowledgeNode) {
    if (node.id.startsWith("thread:")) return "thread";
    if (node.id.startsWith("item:")) return node.type;
    return node.type;
  }

  function openCreditKnowledgeRef(reference: CreditKnowledgeRef) {
    const dependencyRun = data.runs.find(
      (item) => item.runDigest === creditRun?.dependency.runDigest,
    );
    const targetRun = dependencyRun?.state.nodes[reference.nodeId]
      ? dependencyRun
      : run.state.nodes[reference.nodeId]
        ? run
        : undefined;
    if (!targetRun) return;
    onViewerStateChange({
      runId: targetRun.id,
      nodeId: reference.nodeId,
      transactionId: undefined,
      directionId: undefined,
      judgmentId: undefined,
      detailMode: "node",
    });
  }

  function openJudgment(nextJudgmentId: string) {
    const judgment = runJudgments.find((item) => item.judgmentId === nextJudgmentId);
    if (!judgment) return;
    const relevantTransaction = transactionId && judgmentMentionsTransaction(judgment, transactionId)
      ? transactionId
      : referenceTransactions.find((item) =>
        judgmentMentionsTransaction(judgment, item.transactionId),
      )?.transactionId;
    if (!relevantTransaction) return;
    onViewerStateChange({ transactionId: relevantTransaction, directionId: undefined, judgmentId: nextJudgmentId, detailMode: "judgment" });
  }

  function openTransaction(nextTransactionId: string) {
    const linked = runJudgments.find((item) => judgmentMentionsTransaction(item, nextTransactionId));
    onViewerStateChange({
      transactionId: nextTransactionId,
      directionId: undefined,
      judgmentId: linked?.judgmentId,
      detailMode: preferredTransactionDetailMode(viewerState.detailMode),
    });
  }

  function TreeNode({ id, depth = 0 }: { id: string; depth?: number }) {
    const node = nodes[id];
    if (!node || !visibleIds.has(id)) return null;
    const nodeRelation = relation(node);
    const changed = run.changedNodeIds.includes(id);
    const dimmed = Boolean(transactionId) && !transactionContextIds.has(id);
    return (
      <div
        className="tree-branch"
        style={{ "--indent": `${Math.min(depth, 4) * 26}px` } as CSSProperties}
      >
        <button
          className={`node-card ${selectedNode.id === id ? "selected" : ""} ${nodeRelation ?? ""} ${dimmed ? "dimmed" : ""}`}
          onClick={() => onViewerStateChange({ nodeId: id, transactionId: undefined, directionId: undefined, judgmentId: undefined, detailMode: "node" })}
          aria-pressed={selectedNode.id === id}
        >
          <TypeMark type={node.type} />
          <span className="node-copy">
            <span className="node-topline">
              <span className="node-type">{nodeKind(node)}</span>
              {changed && <span className="change-dot">changed in state {run.ordinal}</span>}
              {nodeRelation && <span className={`relation ${nodeRelation}`}>{nodeRelation}</span>}
            </span>
            <strong>{node.title}</strong>
            <span className="node-summary">{node.summary}</span>
          </span>
          <span className="revision-number">r{currentRevision(node)?.revisionNumber ?? 0}</span>
        </button>
        {(children[id] ?? []).map((child) => <TreeNode id={child} depth={depth + 1} key={child} />)}
      </div>
    );
  }

  const referenceActions: ReferenceActions = {
    resolver: referenceResolver,
    openTransaction,
    openJudgment,
  };

  return (
    <main className="app-shell">
      <header className="masthead">
        <div className="brand-block">
          <span className="brand-mark">MF</span>
          <div><span className="eyebrow">Math Flow · research atlas</span><h1>{data.problem.title}</h1></div>
        </div>
        <div className="run-metrics">
          {isResearchProgramState ? (
            <>
              <span><strong>{researchProgramCount}</strong> subprograms</span>
              <span><strong>{researchThreadCount}</strong> threads</span>
              <span><strong>{researchItemCount}</strong> results & methods</span>
            </>
          ) : (
            <>
              <span><strong>{Object.keys(nodes).length}</strong> nodes</span>
              <span><strong>{run.revisionIds.length}</strong> revisions</span>
            </>
          )}
          <span><strong>{runJudgments.length}</strong> judgments</span>
          <span><strong>${run.cost.toFixed(4)}</strong> build cost</span>
        </div>
      </header>

      <section className="workspace">
        <aside className="ledger-panel panel">
          <div className="panel-heading">
            <div><span className="eyebrow">Canonical history</span><h2>Research activity</h2></div>
            <span className="count">{data.transactions.length}</span>
          </div>
          <section className="direction-list" aria-label="Research directions">
            <div className="section-label">
              <h3>Research directions</h3>
              <span>{researchDirections?.directions.length ?? 0}</span>
            </div>
            {researchDirections?.directions.map((direction) => {
              const active = selectedDirection?.directionId === direction.directionId;
              return (
                <button
                  className={`direction-card direction-${direction.status} ${active ? "selected" : ""}`}
                  key={direction.directionId}
                  onClick={() => onViewerStateChange(active
                    ? { directionId: undefined, detailMode: "node" }
                    : {
                      directionId: direction.directionId,
                      transactionId: undefined,
                      judgmentId: undefined,
                      detailMode: "direction",
                    })}
                  aria-pressed={active}
                >
                  <span className="direction-mark">↗</span>
                  <span>
                    <strong>{direction.title}</strong>
                    <small>{direction.registeredBy.displayName} · {label(direction.status)}</small>
                  </span>
                </button>
              );
            })}
            {!researchDirections?.directions.length && (
              <p className="muted">No research directions have been registered.</p>
            )}
          </section>
          <div className="ledger-subheading">
            <h3>Submissions</h3>
            <span>{data.transactions.length}</span>
          </div>
          <div className="ledger-line">
            {data.transactions.map((transaction) => {
              const available = transaction.ordinal <= runLedgerPosition;
              const active = transaction.transactionId === transactionId;
              const primaryJudgments = runJudgments.filter((judgment) =>
                judgment.judgmentKind === "primary" &&
                judgment.record.subjects.some((subject) => subject.id === transaction.transactionId),
              );
              const evidenceJudgments = runJudgments.filter((judgment) =>
                !judgment.record.subjects.some((subject) => subject.id === transaction.transactionId) &&
                judgment.record.findings.some((finding) =>
                  finding.evidenceTransactionIds.includes(transaction.transactionId),
                ),
              );
              const creditAssignment = qualitativeCreditRun?.assignments.find(
                (item) => item.transactionId === transaction.transactionId,
              );
              const hierarchicalCredit = hierarchicalCreditRun
                ? hierarchicalCreditForTransaction(
                  hierarchicalCreditRun,
                  transaction.transactionId,
                )
                : null;
              const validity = transactionValiditySummary(primaryJudgments);
              const attestation = objectiveAttestations?.find(
                (item) => item.transactionId === transaction.transactionId,
              );
              return (
                <button
                  className={`transaction-card ${active ? "selected" : ""} ${available ? "" : "future"}`}
                  key={transaction.transactionId}
                  onClick={() => {
                    if (active) {
                      onViewerStateChange({ transactionId: undefined, directionId: undefined, judgmentId: undefined, detailMode: "node" });
                    } else {
                      openTransaction(transaction.transactionId);
                    }
                  }}
                  disabled={!available}
                  aria-pressed={active}
                >
                  <span className="ordinal">{String(transaction.ordinal).padStart(2, "0")}</span>
                  <span className="transaction-copy">
                    <strong>{label(transaction.contributionId)}</strong>
                    <span>{transaction.author.displayName} · {short(transaction.transactionId)}</span>
                    <small className={validity ? `validity-badge validity-${validity}` : primaryJudgments.length ? "coverage-complete" : "coverage-missing"}>
                      {validity
                        ? `validity · ${validity}`
                        : primaryJudgments.length
                        ? `${primaryJudgments.length} primary judgment${primaryJudgments.length === 1 ? "" : "s"}`
                        : evidenceJudgments.length
                          ? `unjudged · evidence in ${evidenceJudgments.length}`
                          : "unjudged"}
                    </small>
                    {creditAssignment && (
                      <small className={`credit-badge significance-${creditAssignment.significance}`}>
                        credit · {creditAssignment.significance}
                      </small>
                    )}
                    {hierarchicalCredit && (
                      <small className="credit-badge hierarchical-credit-badge">
                        credit · {formatCreditFraction(hierarchicalCredit.allocation)} overall
                      </small>
                    )}
                    {attestation && (
                      <small className={`verification-badge verification-${attestation.selectionStatus}`}>
                        verification · {attestation.selectionStatus}
                      </small>
                    )}
                  </span>
                </button>
              );
            })}
          </div>
          <div className="ledger-footnote">
            <span className="pulse" /> Ledger at <code>{short(run.ledgerHead)}</code>
          </div>
        </aside>

        <section className="knowledge-panel panel">
          <div className="panel-heading knowledge-heading">
            <div><span className="eyebrow">{isResearchProgramState ? "Research formation" : "Knowledge build"} · state {run.ordinal}</span><h2>{isResearchProgramState ? "Research program state" : "Knowledge state"}</h2></div>
            <label className="search-box">
              <span>⌕</span>
              <input value={query} onChange={(event) => onViewerStateChange({ query: event.target.value })} placeholder={isResearchProgramState ? "Find a program, thread, result, or method" : "Find a claim, proof, or lemma"} />
            </label>
          </div>
          {(query || transactionId) && (
            <div className="filter-banner">
              <span>
                {transactionId
                  ? `Highlighting ${transactionDirectIds.size} direct connection${transactionDirectIds.size === 1 ? "" : "s"} to transaction ${selectedTransaction?.ordinal ?? "·"}; the full state remains visible.`
                  : `Showing ${visibleIds.size} search-connected node${visibleIds.size === 1 ? "" : "s"}.`}
              </span>
              <button onClick={() => onViewerStateChange({ query: undefined, transactionId: undefined, judgmentId: undefined, detailMode: "node" })}>Clear</button>
            </div>
          )}
          <div className="tree-canvas">
            <div className="tree-legend">
              <span><i className="legend-swatch changed" /> changed in this state version</span>
              <span><i className="legend-swatch subject" /> transaction subject</span>
              <span><i className="legend-swatch evidence" /> supporting evidence</span>
            </div>
            <TreeNode id="root" />
            {visibleIds.size === 0 && <div className="empty-state">No nodes match this view.</div>}
          </div>
          <div className="selection-note">
            <span className="eyebrow">Why these nodes?</span>
            <p>{run.selection.rationale}</p>
          </div>
        </section>

        <aside className="detail-panel panel">
          {selectedDirection ? (
            <div className="detail-tabs detail-tabs-direction" role="tablist" aria-label="Research direction details">
              <button role="tab" aria-selected="true">Direction</button>
            </div>
          ) : selectedTransaction ? (
            <div className="detail-tabs detail-tabs-transaction" role="tablist" aria-label="Transaction details">
              <button role="tab" aria-selected={detailMode === "transaction"} onClick={() => onViewerStateChange({ detailMode: "transaction" })}>Submission</button>
              <button role="tab" aria-selected={detailMode === "judgment"} disabled={!transactionJudgments.length} onClick={() => onViewerStateChange({ detailMode: "judgment" })}>Judgment</button>
              <button role="tab" aria-selected={detailMode === "verification"} disabled={!selectedAttestation} onClick={() => onViewerStateChange({ detailMode: "verification" })}>Verification</button>
              <button role="tab" aria-selected={detailMode === "credit"} disabled={!selectedCreditAssignment && !selectedHierarchicalCredit} onClick={() => onViewerStateChange({ detailMode: "credit" })}>Credit</button>
            </div>
          ) : (
            <div className="detail-tabs detail-tabs-node" role="tablist" aria-label="Knowledge node details">
              <button role="tab" aria-selected={detailMode === "node"} onClick={() => onViewerStateChange({ detailMode: "node" })}>Node</button>
              <button role="tab" aria-selected={detailMode === "report"} onClick={() => onViewerStateChange({ detailMode: "report" })}>Build report</button>
            </div>
          )}
          {detailMode === "direction" && selectedDirection ? (
            <section className="artifact-detail direction-detail">
              <span className="eyebrow">Participant intent · non-exclusive</span>
              <h2>{selectedDirection.title}</h2>
              <div className="direction-status-row">
                <span className={`direction-status direction-status-${selectedDirection.status}`}>
                  {selectedDirection.status}
                </span>
                <code>{selectedDirection.directionId}</code>
              </div>
              <p className="detail-summary direction-summary">{selectedDirection.summary}</p>
              <div className="provenance-grid artifact-provenance">
                <div><span>Registered by</span><strong>{selectedDirection.registeredBy.displayName}</strong></div>
                <div><span>Registration</span><code>{short(selectedDirection.registeredTransactionId, 12)}</code></div>
                <div><span>Current event</span><code>{selectedDirection.currentEventId}</code></div>
                <div><span>Direction ledger</span><code>{short(researchDirections?.directionLedgerDigest ?? null, 12)}</code></div>
              </div>
              <article className="direction-notice">
                <strong>Registration is evidence, not ownership.</strong>
                <span>Other solvers may pursue overlapping work, and mathematical validity is determined separately.</span>
              </article>
              <section className="credit-reference-list">
                <div className="section-label"><h3>Related knowledge nodes</h3><span>{selectedDirection.relatedKnowledgeNodeIds.length}</span></div>
                {selectedDirection.relatedKnowledgeNodeIds.map((nodeId) => (
                  nodes[nodeId] ? (
                    <button
                      key={nodeId}
                      onClick={() => onViewerStateChange({
                        nodeId,
                        directionId: undefined,
                        detailMode: "node",
                      })}
                    >
                      <strong>{nodes[nodeId].title}</strong>
                      <code>{nodeId}</code>
                    </button>
                  ) : (
                    <span className="reference-chip" key={nodeId}>{nodeId} · not present in selected state</span>
                  )
                ))}
                {!selectedDirection.relatedKnowledgeNodeIds.length && <p className="muted">No knowledge nodes were named by the participant.</p>}
              </section>
              {!!selectedDirection.completionTransactionIds.length && (
                <section className="credit-reference-list">
                  <div className="section-label"><h3>Completion submissions</h3><span>{selectedDirection.completionTransactionIds.length}</span></div>
                  {selectedDirection.completionTransactionIds.map((completionId) => {
                    const transaction = data.transactions.find((item) => item.transactionId === completionId);
                    return (
                      <button key={completionId} onClick={() => openTransaction(completionId)}>
                        <strong>{transaction ? label(transaction.contributionId) : short(completionId)}</strong>
                        <code>{short(completionId, 12)}</code>
                      </button>
                    );
                  })}
                </section>
              )}
              <section className="revision-section direction-history">
                <div className="section-label"><h3>Direction event history</h3><span>{selectedDirectionEvents.length}</span></div>
                {[...selectedDirectionEvents].reverse().map((event) => (
                  <article className="revision-card" key={event.transactionId}>
                    <div>
                      <span className={`action action-${event.eventType}`}>{event.eventType}</span>
                      <strong>{event.eventId}</strong>
                      <code>{short(event.transactionId)}</code>
                    </div>
                    <small>{event.author.displayName} · {new Date(event.committedAt * 1000).toISOString()}</small>
                    <details className="raw-artifact">
                      <summary>Participant-authored event detail</summary>
                      <Markdown value={event.contentMarkdown} actions={referenceActions} />
                    </details>
                  </article>
                ))}
              </section>
            </section>
          ) : detailMode === "node" ? (
            <>
              <div className="detail-title">
                <TypeMark type={selectedNode.type} />
                <div><span className="eyebrow">{nodeKind(selectedNode)} · {selectedNode.status}</span><h2>{selectedNode.title}</h2></div>
              </div>
              <p className="detail-summary">{selectedNode.summary}</p>
              <div className="provenance-grid">
                <div><span>Node digest</span><code>{short(selectedNode.digest, 12)}</code></div>
                <div><span>Current revision</span><strong>r{currentRevision(selectedNode)?.revisionNumber ?? 0}</strong></div>
              </div>
              <div className="relation-block">
                {(selectedNode.lineage?.length ?? 0) > 0 && (
                  <>
                    <h3>Taxonomy lineage</h3>
                    <div className="chip-row">{selectedNode.lineage?.map((item) => (
                      <button key={`${item.relation}-${item.nodeId}`} onClick={() => onViewerStateChange({ nodeId: item.nodeId, transactionId: undefined, directionId: undefined, judgmentId: undefined, detailMode: "node" })}>
                        {item.relation} · {label(item.nodeId)}
                      </button>
                    ))}</div>
                  </>
                )}
                <h3>Subjects</h3>
                <div className="chip-row">{selectedNode.subjects.length ? selectedNode.subjects.map((item) => <button key={item.id} onClick={() => openTransaction(item.id)}>tx {item.ledgerPosition ?? "·"} · {short(item.id)}</button>) : <span className="muted">No transaction subjects</span>}</div>
                <h3>Evidence</h3>
                <div className="chip-row">{selectedNode.evidence.length ? selectedNode.evidence.map((item) => item.kind === "transaction" ? <button key={`${item.id}-${item.relation}`} onClick={() => openTransaction(item.id)}>{item.relation} · {short(item.id)}</button> : item.kind === "judgment" && referenceResolver.resolve(item.id)?.kind === "judgment" ? <button key={`${item.id}-${item.relation}`} onClick={() => openJudgment(item.id)}>judgment · {short(item.id)}</button> : <span className="reference-chip" key={`${item.id}-${item.relation}`}>{item.kind} · {short(item.id)}</span>) : <span className="muted">No linked evidence</span>}</div>
              </div>
              {selectedNode.type === "program" && (
                <section className="program-contributions">
                  <div className="section-label"><h3>Related contributions</h3><span>{relatedProgramContributions.length}</span></div>
                  {relatedProgramContributions.map((transaction) => (
                    <button key={transaction.transactionId} onClick={() => openTransaction(transaction.transactionId)}>
                      <span className="ordinal">{String(transaction.ordinal).padStart(2, "0")}</span>
                      <span>
                        <strong>{label(transaction.contributionId)}</strong>
                        <small>{transaction.author.displayName} · {short(transaction.transactionId)}</small>
                      </span>
                    </button>
                  ))}
                  {!relatedProgramContributions.length && <p className="muted">No transaction provenance appears in this program subtree yet.</p>}
                </section>
              )}
              {selectedProgramCredit && hierarchicalCreditRun && (
                <section className="program-credit-context">
                  <div className="section-label"><h3>Local program credit</h3><span>{selectedProgramCredit.children.length} children</span></div>
                  <p>{selectedProgramCredit.rationale}</p>
                  <div className="program-credit-children">
                    {selectedProgramCredit.children.map((child) => (
                      <button
                        key={`${child.kind}:${child.id}`}
                        onClick={() => child.kind === "contribution"
                          ? openTransaction(child.id)
                          : onViewerStateChange({ nodeId: child.id, transactionId: undefined, judgmentId: undefined, detailMode: "node" })}
                      >
                        <span className="credit-share">{formatCreditFraction(child.allocationShare)}</span>
                        <strong>{child.kind === "contribution"
                          ? label(data.transactions.find((item) => item.transactionId === child.id)?.contributionId ?? short(child.id))
                          : nodes[child.id]?.title ?? label(child.id)}</strong>
                        <small>direct {child.directWork} · obviated {child.obviatedWork} · {child.confidence} confidence</small>
                      </button>
                    ))}
                  </div>
                  <div className="program-credit-residual">
                    <span>Unattributed local residual</span>
                    <strong>{formatCreditFraction(selectedProgramCredit.unattributedShare)}</strong>
                    <small>{selectedProgramCredit.unattributedWork} work units</small>
                  </div>
                </section>
              )}
              {qualitativeCreditRun && (
                <section className="node-credit-links">
                  <div className="section-label"><h3>Credit references</h3><span>{nodeCreditAssignments.length}</span></div>
                  {nodeCreditAssignments.map((assignment) => {
                    const transaction = data.transactions.find(
                      (item) => item.transactionId === assignment.transactionId,
                    );
                    return (
                      <button
                        key={assignment.transactionId}
                        onClick={() => onViewerStateChange({
                          transactionId: assignment.transactionId,
                          detailMode: "credit",
                        })}
                      >
                        <span className={`significance significance-${assignment.significance}`}>
                          {assignment.significance}
                        </span>
                        <strong>{transaction ? label(transaction.contributionId) : short(assignment.transactionId)}</strong>
                        <small>{assignment.roles.join(" · ") || "no classified role"}</small>
                      </button>
                    );
                  })}
                  {!nodeCreditAssignments.length && (
                    <p className="muted">The selected credit run does not cite this node.</p>
                  )}
                </section>
              )}
              {!isResearchProgramState && <section className="revision-section">
                <div className="section-label"><h3>Knowledge revision lineage</h3><span>{nodeRevisions.length}</span></div>
                {[...nodeRevisions].reverse().map((revision) => (
                  <article className="revision-card" key={revision.revisionId}>
                    <div><span className={`action action-${revision.action}`}>{revision.action}</span><strong>Revision {revision.revisionNumber}</strong><code>{short(revision.revisionId)}</code></div>
                    {!!revision.facets?.length && (
                      <div className="facet-row" aria-label="Changed knowledge facets">
                        {revision.facets.map((facet) => <span className={`facet facet-${facet}`} key={facet}>{facet}</span>)}
                      </div>
                    )}
                    {revision.changeRationale ? (
                      <div className="revision-rationale">
                        <span>Change rationale</span>
                        <p>{inline(revision.changeRationale, referenceActions)}</p>
                        {revision.changeRef && <code>{revision.changeRef.section}</code>}
                      </div>
                    ) : <p>{inline(revision.summary, referenceActions)}</p>}
                    <small>Recorded at ledger {short(revisionLedgerHead(revision))}</small>
                  </article>
                ))}
                {!nodeRevisions.length && <p className="muted">Structural node; no knowledge revision yet.</p>}
              </section>}
              <details className="node-body" open>
                <summary>{isResearchProgramState
                  ? selectedNode.type === "program" ? "Program objective" : selectedNode.id.startsWith("thread:") ? "Research thread" : "Result or method"
                  : run.revisionSemantics === "neutral-knowledge" ? "Current knowledge" : "Current mathematical assessment"}</summary>
                <Markdown value={selectedNode.contentMarkdown} actions={referenceActions} />
              </details>
            </>
          ) : detailMode === "transaction" && selectedTransaction ? (
            <section className="artifact-detail">
              <span className="eyebrow">Submission · transaction {selectedTransaction.ordinal}</span>
              <h2>{label(selectedTransaction.contributionId)}</h2>
              <div className="provenance-grid artifact-provenance">
                <div><span>Author</span><strong>{selectedTransaction.author.displayName}</strong></div>
                <div><span>Transaction</span><code>{short(selectedTransaction.transactionId, 12)}</code></div>
              </div>
              <section className="linked-judgments">
                <div className="section-label"><h3>Judgments involving this submission</h3><span>{transactionJudgments.length}</span></div>
                {transactionJudgments.map((judgment) => (
                  <button key={judgment.judgmentId} onClick={() => openJudgment(judgment.judgmentId)}>
                    <span>{judgment.record.assessments?.length ? "validity" : judgment.judgmentKind}</span>
                    <strong>{judgmentOutcomeSummary(judgment)}</strong>
                    <code>{short(judgment.judgmentId)}</code>
                  </button>
                ))}
                {!transactionJudgments.length && <p className="muted">No published judgment involves this submission in the selected run.</p>}
              </section>
              <details className="raw-artifact" open>
                <summary>Raw submission Markdown</summary>
                <Markdown value={selectedTransaction.contentMarkdown} actions={referenceActions} />
              </details>
            </section>
          ) : detailMode === "judgment" && selectedJudgment ? (
            <section className="artifact-detail judgment-detail">
              <span className="eyebrow">{selectedJudgment.record.assessments?.length ? "Mathematical validity judgment" : `${selectedJudgment.judgmentKind} judgment`}</span>
              <h2>{selectedJudgment.judgeSpec.id}</h2>
              {transactionJudgments.length > 1 && (
                <label className="judgment-picker">
                  <span>Published judgment</span>
                  <select value={selectedJudgment.judgmentId} onChange={(event) => onViewerStateChange({ judgmentId: event.target.value })}>
                    {transactionJudgments.map((judgment) => (
                      <option value={judgment.judgmentId} key={judgment.judgmentId}>
                        {judgment.judgmentKind} · {short(judgment.judgmentId)}
                      </option>
                    ))}
                  </select>
                </label>
              )}
              <div className="provenance-grid artifact-provenance">
                <div><span>Model</span><strong>{selectedJudgment.models.join(", ") || "unreported"}</strong></div>
                <div><span>Judgment ID</span><code>{short(selectedJudgment.judgmentId, 12)}</code></div>
              </div>
              {selectedJudgment.record.reconciliation && (
                <article className="reconciliation-card">
                  <span className="eyebrow">Reconciliation · {selectedJudgment.record.reconciliation.outcome}</span>
                  <p>{selectedJudgment.record.reconciliation.summary}</p>
                </article>
              )}
              {!!selectedJudgment.record.assessments?.length && (
                <section className="validity-assessment-list">
                  <div className="section-label"><h3>Validity assessments</h3><span>{selectedJudgment.record.assessments.length}</span></div>
                  {selectedJudgment.record.assessments.map((assessment) => {
                    const referenceGroups = validityReferenceGroups(selectedJudgment, assessment);
                    return (
                      <article className={`validity-assessment validity-${assessment.status}`} key={assessment.claimKey}>
                        <div className="validity-heading">
                          <span className={`validity-status validity-${assessment.status}`}>{assessment.status}</span>
                          <code>{assessment.claimKey}</code>
                          <span className={`premise-status premise-${assessment.premiseStatus}`}>premises · {label(assessment.premiseStatus)}</span>
                        </div>
                        <p>{assessment.summary}</p>
                        {!!assessment.scopeQualifications.length && (
                          <div className="validity-notes">
                            <strong>Scope qualifications</strong>
                            {assessment.scopeQualifications.map((qualification) => <span key={qualification}>{qualification}</span>)}
                          </div>
                        )}
                        {!!assessment.evidenceIssues.length && (
                          <div className="validity-notes evidence-issues">
                            <strong>Evidence issues</strong>
                            {assessment.evidenceIssues.map((issue) => <span key={issue}>{issue}</span>)}
                          </div>
                        )}
                        {referenceGroups && (
                          <div className="validity-reference-groups">
                            <div className="validity-reference-group declared-references">
                              <div className="validity-reference-label">
                                <strong>Declared references / provenance</strong>
                                <span>Submission-declared citations; declaration alone does not make them required premises.</span>
                              </div>
                              <div className="chip-row">
                                {referenceGroups.declaredReferenceTransactionIds.length
                                  ? referenceGroups.declaredReferenceTransactionIds.map((referenceId) => (
                                    <button key={referenceId} onClick={() => openTransaction(referenceId)}>declared · {short(referenceId)}</button>
                                  ))
                                  : <span className="muted">None declared</span>}
                              </div>
                            </div>
                            <div className="validity-reference-group required-premises">
                              <div className="validity-reference-label">
                                <strong>Required premises</strong>
                                <span>References whose mathematical content the judge found logically necessary for this claim.</span>
                              </div>
                              <div className="chip-row">
                                {referenceGroups.requiredDependencyTransactionIds.length
                                  ? referenceGroups.requiredDependencyTransactionIds.map((referenceId) => (
                                    <button key={referenceId} onClick={() => openTransaction(referenceId)}>required · {short(referenceId)}</button>
                                  ))
                                  : <span className="muted">No prior reference required</span>}
                              </div>
                            </div>
                          </div>
                        )}
                        {!!assessment.evidenceTransactionIds.length && (
                          <div className="chip-row validity-evidence">
                            {assessment.evidenceTransactionIds.map((evidenceId) => (
                              <button key={evidenceId} onClick={() => openTransaction(evidenceId)}>evidence · {short(evidenceId)}</button>
                            ))}
                          </div>
                        )}
                      </article>
                    );
                  })}
                </section>
              )}
              <section className="finding-list">
                <div className="section-label"><h3>{selectedJudgment.record.assessments?.length ? "Knowledge-routing findings" : "Structured findings"}</h3><span>{selectedJudgment.record.findings.length}</span></div>
                {selectedJudgment.record.findings.map((finding) => (
                  <article className="finding-card" key={`${finding.claimKey}-${finding.stance}`}>
                    <div><span className={`stance stance-${finding.stance}`}>{finding.stance}</span><code>{finding.claimKey}</code></div>
                    <p>{finding.summary}</p>
                  </article>
                ))}
              </section>
              <details className="raw-artifact" open>
                <summary>Raw judgment report</summary>
                <Markdown value={selectedJudgment.reportMarkdown} actions={referenceActions} />
              </details>
              <details className="raw-artifact structured-record">
                <summary>Structured judgment JSON</summary>
                <pre>{JSON.stringify(selectedJudgment.record, null, 2)}</pre>
              </details>
            </section>
          ) : detailMode === "verification" && selectedAttestation && selectedTransaction ? (
            <section className="artifact-detail verification-detail">
              <span className="eyebrow">Objective verifier attestation · separate evidence</span>
              <h2>{label(selectedTransaction.contributionId)}</h2>
              <article className={`credit-lock-card ${selectedAttestation.selectionStatus === "passed" ? "current" : "stale"}`}>
                <strong>{selectedAttestation.selectionStatus === "pending"
                  ? "Verification requested"
                  : `Verifier ${selectedAttestation.selectionStatus}`}</strong>
                <span>A passing execution checks the encoded predicate, not the fidelity of its mathematical encoding.</span>
              </article>
              <div className="provenance-grid artifact-provenance">
                <div><span>Verifier</span><strong>{selectedAttestation.verifier.id}</strong></div>
                <div><span>Request</span><code>{short(selectedAttestation.requestDigest, 12)}</code></div>
                <div><span>Verifier spec</span><code>{short(selectedAttestation.verifier.specDigest, 12)}</code></div>
                <div><span>Environment</span><code>{short(selectedAttestation.environmentDigest, 12)}</code></div>
                {selectedAttestation.run && <div><span>Attestation</span><code>{short(selectedAttestation.run.attestationId, 12)}</code></div>}
                {selectedAttestation.run && <div><span>Published run</span><code>{short(selectedAttestation.run.runDigest, 12)}</code></div>}
              </div>
              {selectedAttestation.run ? (
                <>
                  <section className="finding-list">
                    <div className="section-label"><h3>Execution result</h3><span>{selectedAttestation.run.result.status}</span></div>
                    <article className="finding-card">
                      <div>
                        <span className={`stance stance-${selectedAttestation.run.result.status}`}>
                          {selectedAttestation.run.result.status}
                        </span>
                        <code>exit {selectedAttestation.run.result.exitCode ?? "timeout"}</code>
                      </div>
                      <p>{selectedAttestation.run.result.timedOut ? "The governed verifier timed out." : "The governed verifier completed."}</p>
                    </article>
                  </section>
                  <details className="raw-artifact" open>
                    <summary>Verifier stdout · {selectedAttestation.run.stdout.bytes} bytes{selectedAttestation.run.stdout.truncated ? " · preview truncated" : ""}</summary>
                    <pre>{selectedAttestation.run.stdout.text || "(empty)"}</pre>
                  </details>
                  <details className="raw-artifact">
                    <summary>Verifier stderr · {selectedAttestation.run.stderr.bytes} bytes{selectedAttestation.run.stderr.truncated ? " · preview truncated" : ""}</summary>
                    <pre>{selectedAttestation.run.stderr.text || "(empty)"}</pre>
                  </details>
                  <details className="raw-artifact structured-record">
                    <summary>Structured attestation JSON</summary>
                    <pre>{JSON.stringify(selectedAttestation.run.record, null, 2)}</pre>
                  </details>
                </>
              ) : (
                <p className="muted">The canonical request is waiting for its first trusted hosted execution.</p>
              )}
            </section>
          ) : detailMode === "credit" && selectedHierarchicalCredit && hierarchicalCreditRun && selectedTransaction ? (
            <section className="artifact-detail credit-detail hierarchical-credit-detail">
              <span className="eyebrow">Two-term hierarchical credit · separate overlay</span>
              <h2>{label(selectedTransaction.contributionId)}</h2>
              <div className="hierarchical-credit-summary">
                <div><span>Overall allocation</span><strong>{formatCreditFraction(selectedHierarchicalCredit.allocation)}</strong></div>
                <div><span>Local allocation</span><strong>{formatCreditFraction(selectedHierarchicalCredit.child.allocationShare)}</strong></div>
                <div><span>Direct work avoided</span><strong>{selectedHierarchicalCredit.child.directWork}</strong></div>
                <div><span>Obviated work</span><strong>{selectedHierarchicalCredit.child.obviatedWork}</strong></div>
              </div>
              <div className="provenance-grid artifact-provenance">
                <div><span>Local program</span><strong>{nodes[selectedHierarchicalCredit.evaluation.programId]?.title ?? label(selectedHierarchicalCredit.evaluation.programId)}</strong></div>
                <div><span>Confidence</span><strong>{selectedHierarchicalCredit.child.confidence}</strong></div>
                <div><span>Credit run</span><code>{short(hierarchicalCreditRun.runDigest, 12)}</code></div>
                <div><span>Dependency lock</span><code>{short(hierarchicalCreditRun.dependencyLockDigest, 12)}</code></div>
              </div>
              <article className={`credit-lock-card ${hierarchicalCreditRun.stale ? "stale" : "current"}`}>
                <strong>{hierarchicalCreditRun.stale ? "Historical input lock" : "Current input lock"}</strong>
                <span>Research program run {short(hierarchicalCreditRun.dependency.runDigest, 12)}</span>
                {hierarchicalCreditRun.staleReasons.map((reason) => <small key={reason}>{label(reason)}</small>)}
              </article>
              <section className="counterfactual-card">
                <div className="section-label"><h3>Ex-post counterfactual</h3><span>{selectedHierarchicalCredit.child.totalWork} work units</span></div>
                <p>{selectedHierarchicalCredit.child.counterfactual}</p>
              </section>
              <section className="credit-effect-list">
                <div className="section-label"><h3>Direct effects</h3><span>{selectedHierarchicalCredit.child.directEffects.length}</span></div>
                {selectedHierarchicalCredit.child.directEffects.map((effect) => (
                  <article key={`direct:${effect.threadId}`}>
                    <div><strong>{nodes[`thread:${effect.threadId}`]?.title ?? label(effect.threadId)}</strong><code>{effect.withoutWork} → {effect.withWork}</code></div>
                    <p>{effect.rationale}</p>
                  </article>
                ))}
                {!selectedHierarchicalCredit.child.directEffects.length && <p className="muted">No direct local thread effect was assigned.</p>}
              </section>
              <section className="credit-effect-list">
                <div className="section-label"><h3>Obviated effects</h3><span>{selectedHierarchicalCredit.child.obviatedEffects.length}</span></div>
                {selectedHierarchicalCredit.child.obviatedEffects.map((effect) => (
                  <article key={`obviated:${effect.threadId}`}>
                    <div><strong>{nodes[`thread:${effect.threadId}`]?.title ?? label(effect.threadId)}</strong><code>{effect.withoutWork} → {effect.withWork}</code></div>
                    <p>{effect.rationale}</p>
                  </article>
                ))}
                {!selectedHierarchicalCredit.child.obviatedEffects.length && <p className="muted">No separately obviated work was assigned.</p>}
              </section>
              <section className="credit-reference-list">
                <div className="section-label"><h3>Credit evidence</h3><span>{selectedHierarchicalCredit.child.evidenceRefs.length}</span></div>
                {selectedHierarchicalCredit.child.evidenceRefs.map((evidenceRef) => {
                  const evidenceTransaction = data.transactions.find((item) => item.transactionId === evidenceRef);
                  return evidenceTransaction ? (
                    <button key={evidenceRef} onClick={() => openTransaction(evidenceRef)}>
                      <strong>{label(evidenceTransaction.contributionId)}</strong><code>{short(evidenceRef, 12)}</code>
                    </button>
                  ) : <span className="reference-chip" key={evidenceRef}>{evidenceRef}</span>;
                })}
              </section>
              <details className="raw-artifact structured-record">
                <summary>Hierarchical credit state</summary>
                <pre>{JSON.stringify(hierarchicalCreditRun.creditState, null, 2)}</pre>
              </details>
              <details className="raw-artifact structured-record">
                <summary>Locked credit input</summary>
                <pre>{JSON.stringify(hierarchicalCreditRun.creditInput, null, 2)}</pre>
              </details>
              <details className="raw-artifact structured-record">
                <summary>Projection dependency lock</summary>
                <pre>{JSON.stringify(hierarchicalCreditRun.dependencyLock, null, 2)}</pre>
              </details>
            </section>
          ) : detailMode === "credit" && selectedCreditAssignment && qualitativeCreditRun && selectedTransaction ? (
            <section className="artifact-detail credit-detail">
              <span className="eyebrow">Qualitative credit · separate overlay</span>
              <h2>{label(selectedTransaction.contributionId)}</h2>
              <div className="credit-assessment-heading">
                <span className={`significance significance-${selectedCreditAssignment.significance}`}>
                  {selectedCreditAssignment.significance}
                </span>
                <div className="role-row">
                  {selectedCreditAssignment.roles.map((role) => <span key={role}>{label(role)}</span>)}
                  {!selectedCreditAssignment.roles.length && <span>no classified role</span>}
                </div>
              </div>
              <div className="provenance-grid artifact-provenance">
                <div><span>Credit run</span><code>{short(qualitativeCreditRun.runDigest, 12)}</code></div>
                <div><span>Dependency lock</span><code>{short(qualitativeCreditRun.dependencyLockDigest, 12)}</code></div>
                <div><span>Model</span><strong>{qualitativeCreditRun.models.join(", ") || "unreported"}</strong></div>
                <div><span>Assessment cost</span><strong>${qualitativeCreditRun.cost.toFixed(4)}</strong></div>
              </div>
              <article className={`credit-lock-card ${qualitativeCreditRun.stale ? "stale" : "current"}`}>
                <strong>{qualitativeCreditRun.stale ? "Historical input lock" : "Current input lock"}</strong>
                <span>Knowledge run {short(qualitativeCreditRun.dependency.runDigest, 12)}</span>
                {qualitativeCreditRun.staleReasons.map((reason) => (
                  <small key={reason}>{label(reason)}</small>
                ))}
              </article>
              <section className="credit-reference-list">
                <div className="section-label"><h3>Knowledge references</h3><span>{selectedCreditAssignment.knowledgeRefs.length}</span></div>
                {selectedCreditAssignment.knowledgeRefs.map((reference) => (
                  <button
                    key={`${reference.nodeId}:${reference.revisionId ?? "structural"}`}
                    onClick={() => openCreditKnowledgeRef(reference)}
                  >
                    <strong>{reference.nodeId}</strong>
                    <code>{reference.revisionId ? `r ${short(reference.revisionId, 12)}` : "structural node"}</code>
                  </button>
                ))}
                {!selectedCreditAssignment.knowledgeRefs.length && <p className="muted">No knowledge node was cited for this assignment.</p>}
              </section>
              {selectedCreditAssignment.directionRegistrationTransactionIds ? (
                <section className="credit-reference-list">
                  <div className="section-label"><h3>Research direction registrations</h3><span>{selectedCreditAssignment.directionRegistrationTransactionIds.length}</span></div>
                  {selectedCreditAssignment.directionRegistrationTransactionIds.map((registrationId) => {
                    const event = researchDirections?.events.find((item) => item.transactionId === registrationId && item.eventType === "register");
                    return (
                      <button
                        key={registrationId}
                        onClick={() => event && onViewerStateChange({
                          directionId: event.directionId,
                          transactionId: undefined,
                          judgmentId: undefined,
                          detailMode: "direction",
                        })}
                        disabled={!event}
                      >
                        <strong>{event ? label(event.directionId) : short(registrationId)}</strong>
                        <code>{short(registrationId, 12)}</code>
                      </button>
                    );
                  })}
                  {!selectedCreditAssignment.directionRegistrationTransactionIds.length && <p className="muted">No formal research-direction registration was credited.</p>}
                </section>
              ) : (
              <section className="credit-reference-list">
                <div className="section-label"><h3>Prior reservations</h3><span>{selectedCreditAssignment.reservationTransactionIds?.length ?? 0}</span></div>
                {(selectedCreditAssignment.reservationTransactionIds ?? []).map((reservationId) => {
                  const reservation = data.transactions.find((item) => item.transactionId === reservationId);
                  return (
                    <button key={reservationId} onClick={() => openTransaction(reservationId)}>
                      <strong>{reservation ? label(reservation.contributionId) : short(reservationId)}</strong>
                      <code>{short(reservationId, 12)}</code>
                    </button>
                  );
                })}
                {!selectedCreditAssignment.reservationTransactionIds?.length && <p className="muted">No prior reservation was credited.</p>}
              </section>
              )}
              <details className="raw-artifact" open>
                <summary>Credit rationale for this contribution</summary>
                <Markdown
                  value={markdownSection(qualitativeCreditRun.reportMarkdown, selectedCreditAssignment.reportSection)}
                  actions={referenceActions}
                />
              </details>
              <details className="raw-artifact">
                <summary>Full raw credit report</summary>
                <Markdown value={qualitativeCreditRun.reportMarkdown} actions={referenceActions} />
              </details>
              <details className="raw-artifact structured-record">
                <summary>Locked credit input</summary>
                <pre>{JSON.stringify(qualitativeCreditRun.creditInput, null, 2)}</pre>
              </details>
              <details className="raw-artifact structured-record">
                <summary>Projection dependency lock</summary>
                <pre>{JSON.stringify(qualitativeCreditRun.dependencyLock, null, 2)}</pre>
              </details>
            </section>
          ) : (
            <section className="source-report">
              <span className="eyebrow">{report?.runId ?? "No source report"}</span>
              <h2>{selectedNode.reportRef?.section ?? "Structural root"}</h2>
              {report ? <Markdown value={report.markdown} actions={referenceActions} /> : <p className="muted">This node predates a judge-authored report.</p>}
            </section>
          )}
        </aside>
      </section>
      <footer>
        <span>Projection, not canon.</span>
        <span>Build <code>{short(run.runDigest, 12)}</code> · state <code>{short(run.state.stateDigest, 12)}</code></span>
      </footer>
    </main>
  );
}
