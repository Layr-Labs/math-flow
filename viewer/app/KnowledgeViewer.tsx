"use client";

import { Fragment, type CSSProperties, type ReactNode, useEffect, useMemo, useState } from "react";
import { createViewerReferenceResolver } from "./referenceLinks.mjs";

type Ref = {
  kind: string;
  id: string;
  ledgerPosition?: number;
  digest?: string | null;
  relation?: string;
};

type Adjudication = {
  adjudicationId: string;
  revisionId: string;
  revisionNumber: number;
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
  currentAdjudication: Adjudication | null;
  reportRef: { digest: string; section: string } | null;
  digest: string;
};

type Revision = {
  revisionId: string;
  adjudicationId: string;
  revisionNumber: number;
  action: string;
  baseRevisionId: string | null;
  nodeId: string;
  subjects: Ref[];
  evidence: Ref[];
  issuedAtLedgerHead: string;
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

type JudgmentFinding = {
  claimKey: string;
  stance: string;
  summary: string;
  subjectTransactionIds: string[];
  evidenceTransactionIds: string[];
};

type JudgmentRecord = {
  schemaVersion: number;
  judgmentId: string;
  judgmentKind: "primary" | "reconciliation";
  problemId: string;
  ledgerHead: string;
  judgeSpec: { id: string; digest: string };
  subjects: Ref[];
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
  record: JudgmentRecord;
};

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

export type ViewerCatalog = {
  schemaVersion: number;
  repository: { slug: string; canonicalRef: string; projectionRef: string };
  projections: RepositoryProjection[];
  defaultProjectionId: string | null;
};

const short = (value: string | null, size = 7) =>
  value ? value.replace(/^sha256:/, "").slice(0, size) : "genesis";

const label = (value: string) => value.replaceAll("-", " ");

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

function isViewerCatalog(value: unknown): value is ViewerCatalog {
  if (!value || typeof value !== "object") return false;
  const catalog = value as Partial<ViewerCatalog>;
  return catalog.schemaVersion === 1 &&
    !!catalog.repository &&
    Array.isArray(catalog.projections) &&
    catalog.projections.length > 0 &&
    catalog.projections.every((projection) =>
      typeof projection?.id === "string" &&
      typeof projection?.problemId === "string" &&
      Array.isArray(projection?.data?.runs) &&
      projection.data.runs.length > 0,
    );
}

export function RepositoryKnowledgeViewer({ fallbackData }: { fallbackData: ViewerData }) {
  const fallbackProjection: RepositoryProjection = {
    id: `fallback:${fallbackData.problem.id}`,
    problemId: fallbackData.problem.id,
    label: "checked-in demonstration",
    builder: { id: "demo", digest: "local" },
    latestRunDigest: fallbackData.runs.at(-1)?.runDigest ?? "local",
    runCount: fallbackData.runs.length,
    data: fallbackData,
  };
  const fallbackCatalog: ViewerCatalog = {
    schemaVersion: 1,
    repository: { slug: "Layr-Labs/math-flow", canonicalRef: "main", projectionRef: "projections" },
    projections: [fallbackProjection],
    defaultProjectionId: fallbackProjection.id,
  };
  const [catalog, setCatalog] = useState(fallbackCatalog);
  const [source, setSource] = useState<"checking" | "repository" | "fallback">("checking");
  const [problemId, setProblemId] = useState(fallbackProjection.problemId);
  const [projectionId, setProjectionId] = useState(fallbackProjection.id);

  useEffect(() => {
    let active = true;
    async function refresh() {
      try {
        const response = await fetch("/api/catalog", { cache: "no-store" });
        if (!response.ok) throw new Error(`catalog returned ${response.status}`);
        const next: unknown = await response.json();
        if (!isViewerCatalog(next)) throw new Error("catalog shape is invalid");
        if (!active) return;
        setCatalog(next);
        const preferred = next.projections.find((item) => item.id === next.defaultProjectionId) ?? next.projections[0];
        setProblemId((current) => next.projections.some((item) => item.problemId === current) ? current : preferred.problemId);
        setProjectionId((current) => next.projections.some((item) => item.id === current) ? current : preferred.id);
        setSource("repository");
      } catch {
        if (active) setSource("fallback");
      }
    }
    void refresh();
    const interval = window.setInterval(refresh, 30_000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  const problems = [...new Set(catalog.projections.map((item) => item.problemId))].sort();
  const effectiveProblem = problems.includes(problemId) ? problemId : problems[0];
  const problemProjections = catalog.projections.filter((item) => item.problemId === effectiveProblem);
  const projection = problemProjections.find((item) => item.id === projectionId) ?? problemProjections[0];

  function chooseProblem(nextProblem: string) {
    const nextProjection = catalog.projections.find((item) => item.problemId === nextProblem);
    if (!nextProjection) return;
    setProblemId(nextProblem);
    setProjectionId(nextProjection.id);
  }

  if (source === "checking") {
    return (
      <main className="repository-loading" aria-live="polite">
        <div className="loading-mark">MF</div>
        <span className="eyebrow">Math Flow · research atlas</span>
        <h1>Loading repository state</h1>
        <p>The checked-in demonstration will be used only if the live projection is unavailable.</p>
        <span className="loading-line" aria-hidden="true" />
      </main>
    );
  }

  return (
    <div className="repository-shell">
      <nav className="repository-toolbar" aria-label="Repository projection selection">
        <div className="repository-source">
          <span className={`source-light source-${source}`} />
          <span>
            <strong>{catalog.repository.slug}</strong>
            <small>{catalog.repository.canonicalRef} → {catalog.repository.projectionRef} · {source === "repository" ? "live repository state" : source === "checking" ? "checking repository" : "local fallback"}</small>
          </span>
        </div>
        <label>
          <span>Problem</span>
          <select value={effectiveProblem} onChange={(event) => chooseProblem(event.target.value)}>
            {problems.map((problem) => <option value={problem} key={problem}>{label(problem)}</option>)}
          </select>
        </label>
        <label>
          <span>Projection</span>
          <select value={projection.id} onChange={(event) => setProjectionId(event.target.value)}>
            {problemProjections.map((item) => <option value={item.id} key={item.id}>{item.label} · {short(item.latestRunDigest)}</option>)}
          </select>
        </label>
      </nav>
      <KnowledgeViewer key={`${projection.id}:${projection.latestRunDigest}`} data={projection.data} />
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
      return <strong key={index}>{referenceText(part.slice(2, -2), `${index}-strong`, actions)}</strong>;
    }
    return <Fragment key={index}>{referenceText(part, `${index}-text`, actions)}</Fragment>;
  });
}

function Markdown({ value, actions }: { value: string; actions?: ReferenceActions }) {
  return (
    <div className="markdown">
      {value.split("\n").map((raw, index) => {
        const line = raw.trim();
        if (!line || line === "---") return <div className="markdown-gap" key={index} />;
        if (line.startsWith("### ")) return <h4 key={index}>{inline(line.slice(4), actions)}</h4>;
        if (line.startsWith("## ")) return <h3 key={index}>{inline(line.slice(3), actions)}</h3>;
        if (line.startsWith("# ")) return <h2 key={index}>{inline(line.slice(2), actions)}</h2>;
        if (/^\d+\. /.test(line)) return <p className="numbered" key={index}>{inline(line, actions)}</p>;
        if (line.startsWith("- ")) return <p className="bullet" key={index}>{inline(line.slice(2), actions)}</p>;
        if (line === "\\[" || line === "\\]") return null;
        return <p key={index}>{inline(line, actions)}</p>;
      })}
    </div>
  );
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
    result: "="
  };
  return <span className={`type-mark type-${type}`} aria-hidden="true">{marks[type] ?? "·"}</span>;
}

export function KnowledgeViewer({ data }: { data: ViewerData }) {
  const judgments = useMemo(() => data.judgments ?? [], [data.judgments]);
  const [runId, setRunId] = useState(data.latestRunId);
  const [nodeId, setNodeId] = useState("root");
  const [transactionId, setTransactionId] = useState<string | null>(null);
  const [judgmentId, setJudgmentId] = useState<string | null>(judgments.at(-1)?.judgmentId ?? null);
  const [query, setQuery] = useState("");
  const [detailMode, setDetailMode] = useState<"node" | "transaction" | "judgment" | "report">("node");

  const run = data.runs.find((item) => item.id === runId) ?? data.runs.at(-1)!;
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
  const selectedJudgment = runJudgments.find((item) => item.judgmentId === judgmentId) ?? runJudgments.at(-1);
  const nodes = run.state.nodes;
  const selectedNode = nodes[nodeId] ?? nodes.root;
  const runRevisionSet = useMemo(() => new Set(run.revisionIds), [run.revisionIds]);
  const nodeRevisions = data.revisions.filter(
    (item) => item.nodeId === selectedNode.id && runRevisionSet.has(item.revisionId),
  );
  const report = data.reports.find((item) => item.digest === selectedNode.reportRef?.digest);

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

  function chooseRun(nextId: string) {
    const next = data.runs.find((item) => item.id === nextId)!;
    setRunId(nextId);
    if (!next.state.nodes[nodeId]) setNodeId("root");
    setTransactionId(null);
    setDetailMode("node");
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
    setTransactionId(relevantTransaction);
    setJudgmentId(nextJudgmentId);
    setDetailMode("judgment");
  }

  function openTransaction(nextTransactionId: string) {
    setTransactionId(nextTransactionId);
    const linked = runJudgments.find((item) => judgmentMentionsTransaction(item, nextTransactionId));
    if (linked) setJudgmentId(linked.judgmentId);
    setDetailMode("transaction");
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
          onClick={() => { setNodeId(id); setTransactionId(null); setDetailMode("node"); }}
          aria-pressed={selectedNode.id === id}
        >
          <TypeMark type={node.type} />
          <span className="node-copy">
            <span className="node-topline">
              <span className="node-type">{node.type}</span>
              {changed && <span className="change-dot">changed in state {run.ordinal}</span>}
              {nodeRelation && <span className={`relation ${nodeRelation}`}>{nodeRelation}</span>}
            </span>
            <strong>{node.title}</strong>
            <span className="node-summary">{node.summary}</span>
          </span>
          <span className="revision-number">r{node.currentAdjudication?.revisionNumber ?? 0}</span>
        </button>
        {(children[id] ?? []).map((child) => <TreeNode id={child} depth={depth + 1} key={child} />)}
      </div>
    );
  }

  const selectedTransaction = data.transactions.find((item) => item.transactionId === transactionId);
  const transactionJudgments = selectedTransaction
    ? runJudgments.filter((item) => judgmentMentionsTransaction(item, selectedTransaction.transactionId))
    : [];
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
        <div className="run-strip" aria-label="Knowledge state versions">
          {data.runs.map((item) => (
            <button key={item.id} onClick={() => chooseRun(item.id)} aria-pressed={item.id === run.id}>
              <span>State {String(item.ordinal).padStart(2, "0")}</span>
              <small>{short(item.ledgerHead)} · +{item.addedRevisionIds.length}</small>
            </button>
          ))}
        </div>
        <div className="run-metrics">
          <span><strong>{Object.keys(nodes).length}</strong> nodes</span>
          <span><strong>{run.revisionIds.length}</strong> revisions</span>
          <span><strong>{runJudgments.length}</strong> judgments</span>
          <span><strong>${run.cost.toFixed(4)}</strong> build cost</span>
        </div>
      </header>

      <section className="workspace">
        <aside className="ledger-panel panel">
          <div className="panel-heading">
            <div><span className="eyebrow">Canonical history</span><h2>Transactions</h2></div>
            <span className="count">{data.transactions.length}</span>
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
              return (
                <button
                  className={`transaction-card ${active ? "selected" : ""} ${available ? "" : "future"}`}
                  key={transaction.transactionId}
                  onClick={() => {
                    if (active) {
                      setTransactionId(null);
                      setDetailMode("node");
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
                    <small className={primaryJudgments.length ? "coverage-complete" : "coverage-missing"}>
                      {primaryJudgments.length
                        ? `${primaryJudgments.length} primary judgment${primaryJudgments.length === 1 ? "" : "s"}`
                        : evidenceJudgments.length
                          ? `unjudged · evidence in ${evidenceJudgments.length}`
                          : "unjudged"}
                    </small>
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
            <div><span className="eyebrow">Knowledge build · state {run.ordinal}</span><h2>Knowledge state</h2></div>
            <label className="search-box">
              <span>⌕</span>
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Find a claim, proof, or lemma" />
            </label>
          </div>
          {(query || transactionId) && (
            <div className="filter-banner">
              <span>
                {transactionId
                  ? `Highlighting ${transactionDirectIds.size} direct connection${transactionDirectIds.size === 1 ? "" : "s"} to transaction ${selectedTransaction?.ordinal ?? "·"}; the full state remains visible.`
                  : `Showing ${visibleIds.size} search-connected node${visibleIds.size === 1 ? "" : "s"}.`}
              </span>
              <button onClick={() => { setQuery(""); setTransactionId(null); setDetailMode("node"); }}>Clear</button>
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
          {selectedTransaction ? (
            <div className="detail-tabs detail-tabs-transaction" role="tablist" aria-label="Transaction details">
              <button role="tab" aria-selected={detailMode === "transaction"} onClick={() => setDetailMode("transaction")}>Submission</button>
              <button role="tab" aria-selected={detailMode === "judgment"} disabled={!transactionJudgments.length} onClick={() => setDetailMode("judgment")}>Judgment</button>
            </div>
          ) : (
            <div className="detail-tabs detail-tabs-node" role="tablist" aria-label="Knowledge node details">
              <button role="tab" aria-selected={detailMode === "node"} onClick={() => setDetailMode("node")}>Node</button>
              <button role="tab" aria-selected={detailMode === "report"} onClick={() => setDetailMode("report")}>Build report</button>
            </div>
          )}
          {detailMode === "node" ? (
            <>
              <div className="detail-title">
                <TypeMark type={selectedNode.type} />
                <div><span className="eyebrow">{selectedNode.type} · {selectedNode.status}</span><h2>{selectedNode.title}</h2></div>
              </div>
              <p className="detail-summary">{selectedNode.summary}</p>
              <div className="provenance-grid">
                <div><span>Node digest</span><code>{short(selectedNode.digest, 12)}</code></div>
                <div><span>Current revision</span><strong>r{selectedNode.currentAdjudication?.revisionNumber ?? 0}</strong></div>
              </div>
              <div className="relation-block">
                <h3>Subjects</h3>
                <div className="chip-row">{selectedNode.subjects.length ? selectedNode.subjects.map((item) => <button key={item.id} onClick={() => openTransaction(item.id)}>tx {item.ledgerPosition ?? "·"} · {short(item.id)}</button>) : <span className="muted">No transaction subjects</span>}</div>
                <h3>Evidence</h3>
                <div className="chip-row">{selectedNode.evidence.length ? selectedNode.evidence.map((item) => item.kind === "transaction" ? <button key={`${item.id}-${item.relation}`} onClick={() => openTransaction(item.id)}>{item.relation} · {short(item.id)}</button> : item.kind === "judgment" && referenceResolver.resolve(item.id)?.kind === "judgment" ? <button key={`${item.id}-${item.relation}`} onClick={() => openJudgment(item.id)}>judgment · {short(item.id)}</button> : <span className="reference-chip" key={`${item.id}-${item.relation}`}>{item.kind} · {short(item.id)}</span>) : <span className="muted">No linked evidence</span>}</div>
              </div>
              <section className="revision-section">
                <div className="section-label"><h3>Revision lineage</h3><span>{nodeRevisions.length}</span></div>
                {[...nodeRevisions].reverse().map((revision) => (
                  <article className="revision-card" key={revision.revisionId}>
                    <div><span className={`action action-${revision.action}`}>{revision.action}</span><strong>Revision {revision.revisionNumber}</strong><code>{short(revision.revisionId)}</code></div>
                    <p>{revision.summary}</p>
                    <small>Issued at ledger {short(revision.issuedAtLedgerHead)}</small>
                  </article>
                ))}
                {!nodeRevisions.length && <p className="muted">Structural node; no adjudication yet.</p>}
              </section>
              <details className="node-body" open>
                <summary>Current mathematical assessment</summary>
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
                    <span>{judgment.judgmentKind}</span>
                    <strong>{judgment.record.findings.map((finding) => finding.stance).join(" · ") || "no findings"}</strong>
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
              <span className="eyebrow">Raw {selectedJudgment.judgmentKind} judgment</span>
              <h2>{selectedJudgment.judgeSpec.id}</h2>
              {transactionJudgments.length > 1 && (
                <label className="judgment-picker">
                  <span>Published judgment</span>
                  <select value={selectedJudgment.judgmentId} onChange={(event) => setJudgmentId(event.target.value)}>
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
              <section className="finding-list">
                <div className="section-label"><h3>Structured findings</h3><span>{selectedJudgment.record.findings.length}</span></div>
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
