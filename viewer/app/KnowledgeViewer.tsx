"use client";

import { Fragment, type CSSProperties, type ReactNode, useEffect, useMemo, useState } from "react";

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
};

type Transaction = {
  ordinal: number;
  transactionId: string;
  contributionId: string;
  author: { displayName: string };
  contentMarkdown: string;
};

export type ViewerData = {
  problem: { id: string; title: string; statementMarkdown: string };
  ledgerHead: string;
  transactions: Transaction[];
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
    repository: { slug: "mooselumph/math-flow", canonicalRef: "main", projectionRef: "projections" },
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

function inline(text: string): ReactNode[] {
  return text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).map((part, index) => {
    if (part.startsWith("`") && part.endsWith("`")) {
      return <code key={index}>{part.slice(1, -1)}</code>;
    }
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    return <Fragment key={index}>{part}</Fragment>;
  });
}

function Markdown({ value }: { value: string }) {
  return (
    <div className="markdown">
      {value.split("\n").map((raw, index) => {
        const line = raw.trim();
        if (!line || line === "---") return <div className="markdown-gap" key={index} />;
        if (line.startsWith("### ")) return <h4 key={index}>{inline(line.slice(4))}</h4>;
        if (line.startsWith("## ")) return <h3 key={index}>{inline(line.slice(3))}</h3>;
        if (line.startsWith("# ")) return <h2 key={index}>{inline(line.slice(2))}</h2>;
        if (/^\d+\. /.test(line)) return <p className="numbered" key={index}>{inline(line)}</p>;
        if (line.startsWith("- ")) return <p className="bullet" key={index}>{inline(line.slice(2))}</p>;
        if (line === "\\[" || line === "\\]") return null;
        return <p key={index}>{inline(line)}</p>;
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
  const [runId, setRunId] = useState(data.latestRunId);
  const [nodeId, setNodeId] = useState("root");
  const [transactionId, setTransactionId] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [detailMode, setDetailMode] = useState<"node" | "report">("node");

  const run = data.runs.find((item) => item.id === runId) ?? data.runs.at(-1)!;
  const runLedgerPosition = data.transactions.find(
    (item) => item.transactionId === (run.problemLedgerHead ?? run.ledgerHead),
  )?.ordinal ?? data.transactions.length;
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
    if (!needle && !transactionId) return new Set(Object.keys(nodes));
    const direct = Object.values(nodes)
      .filter((node) => {
        const textMatch = !needle || `${node.id} ${node.title} ${node.summary}`.toLowerCase().includes(needle);
        const transactionMatch =
          !transactionId ||
          node.subjects.some((item) => item.id === transactionId) ||
          node.evidence.some((item) => item.id === transactionId);
        return textMatch && transactionMatch;
      })
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
  }, [nodes, query, transactionId]);

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
    setDetailMode("node");
  }

  function TreeNode({ id, depth = 0 }: { id: string; depth?: number }) {
    const node = nodes[id];
    if (!node || !visibleIds.has(id)) return null;
    const nodeRelation = relation(node);
    const changed = run.changedNodeIds.includes(id);
    return (
      <div
        className="tree-branch"
        style={{ "--indent": `${Math.min(depth, 4) * 26}px` } as CSSProperties}
      >
        <button
          className={`node-card ${selectedNode.id === id ? "selected" : ""} ${nodeRelation ?? ""}`}
          onClick={() => { setNodeId(id); setDetailMode("node"); }}
          aria-pressed={selectedNode.id === id}
        >
          <TypeMark type={node.type} />
          <span className="node-copy">
            <span className="node-topline">
              <span className="node-type">{node.type}</span>
              {changed && <span className="change-dot">changed in run {run.ordinal}</span>}
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

  return (
    <main className="app-shell">
      <header className="masthead">
        <div className="brand-block">
          <span className="brand-mark">MF</span>
          <div><span className="eyebrow">Math Flow · research atlas</span><h1>{data.problem.title}</h1></div>
        </div>
        <div className="run-strip" aria-label="Adjudication runs">
          {data.runs.map((item) => (
            <button key={item.id} onClick={() => chooseRun(item.id)} aria-pressed={item.id === run.id}>
              <span>Run {String(item.ordinal).padStart(2, "0")}</span>
              <small>{short(item.ledgerHead)} · +{item.addedRevisionIds.length}</small>
            </button>
          ))}
        </div>
        <div className="run-metrics">
          <span><strong>{Object.keys(nodes).length}</strong> nodes</span>
          <span><strong>{run.revisionIds.length}</strong> revisions</span>
          <span><strong>${run.cost.toFixed(4)}</strong> run cost</span>
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
              return (
                <button
                  className={`transaction-card ${active ? "selected" : ""} ${available ? "" : "future"}`}
                  key={transaction.transactionId}
                  onClick={() => setTransactionId(active ? null : transaction.transactionId)}
                  disabled={!available}
                  aria-pressed={active}
                >
                  <span className="ordinal">{String(transaction.ordinal).padStart(2, "0")}</span>
                  <span className="transaction-copy">
                    <strong>{label(transaction.contributionId)}</strong>
                    <span>{transaction.author.displayName} · {short(transaction.transactionId)}</span>
                  </span>
                </button>
              );
            })}
          </div>
          <div className="ledger-footnote">
            <span className="pulse" /> Ledger at <code>{short(run.ledgerHead)}</code>
          </div>
          {selectedTransaction && (
            <div className="transaction-preview">
              <span className="eyebrow">Selected evidence</span>
              <h3>{label(selectedTransaction.contributionId)}</h3>
              <Markdown value={selectedTransaction.contentMarkdown} />
            </div>
          )}
        </aside>

        <section className="knowledge-panel panel">
          <div className="panel-heading knowledge-heading">
            <div><span className="eyebrow">Judge projection · run {run.ordinal}</span><h2>Knowledge state</h2></div>
            <label className="search-box">
              <span>⌕</span>
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Find a claim, proof, or lemma" />
            </label>
          </div>
          {(query || transactionId) && (
            <div className="filter-banner">
              Showing {visibleIds.size} connected node{visibleIds.size === 1 ? "" : "s"}
              <button onClick={() => { setQuery(""); setTransactionId(null); }}>Clear filter</button>
            </div>
          )}
          <div className="tree-canvas">
            <div className="tree-legend">
              <span><i className="legend-swatch changed" /> changed this run</span>
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
          <div className="detail-tabs" role="tablist">
            <button role="tab" aria-selected={detailMode === "node"} onClick={() => setDetailMode("node")}>Node</button>
            <button role="tab" aria-selected={detailMode === "report"} onClick={() => setDetailMode("report")}>Source report</button>
          </div>
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
                <div className="chip-row">{selectedNode.subjects.length ? selectedNode.subjects.map((item) => <button key={item.id} onClick={() => setTransactionId(item.id)}>tx {item.ledgerPosition ?? "·"} · {short(item.id)}</button>) : <span className="muted">No transaction subjects</span>}</div>
                <h3>Evidence</h3>
                <div className="chip-row">{selectedNode.evidence.length ? selectedNode.evidence.map((item) => <button key={`${item.id}-${item.relation}`} onClick={() => item.kind === "transaction" && setTransactionId(item.id)}>{item.relation} · {short(item.id)}</button>) : <span className="muted">No linked evidence</span>}</div>
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
                <Markdown value={selectedNode.contentMarkdown} />
              </details>
            </>
          ) : (
            <section className="source-report">
              <span className="eyebrow">{report?.runId ?? "No source report"}</span>
              <h2>{selectedNode.reportRef?.section ?? "Structural root"}</h2>
              {report ? <Markdown value={report.markdown} /> : <p className="muted">This node predates a judge-authored report.</p>}
            </section>
          )}
        </aside>
      </section>
      <footer>
        <span>Projection, not canon.</span>
        <span>Run <code>{short(run.runDigest, 12)}</code> · state <code>{short(run.state.stateDigest, 12)}</code></span>
      </footer>
    </main>
  );
}
