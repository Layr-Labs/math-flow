import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import test from "node:test";
import { collectProgramContributionIds } from "../app/programContributions.mjs";
import { createViewerReferenceResolver } from "../app/referenceLinks.mjs";
import { applyViewerStateToSearch, parseViewerState } from "../app/viewerState.mjs";

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
  const initialMarkup = html.slice(0, html.indexOf('<script type="module"'));
  assert.match(html, /<title>Math Flow · Research Atlas<\/title>/i);
  assert.match(initialMarkup, /Math Flow · research atlas/);
  assert.match(initialMarkup, /Loading repository state/);
  assert.match(initialMarkup, /checked-in demonstration will be used only if the live projection is unavailable/i);
  assert.doesNotMatch(initialMarkup, /Triangle midpoint quadrilateral/);
  assert.doesNotMatch(initialMarkup, /State[^<]*<!-- -->03/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|SkeletonPreview/i);
});

test("keeps the viewer data-driven with contextual artifact details", async () => {
  const [page, layout, packageJson, data, viewer, styles] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
    readFile(new URL("../app/math-flow-data.json", import.meta.url), "utf8"),
    readFile(new URL("../app/KnowledgeViewer.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/globals.css", import.meta.url), "utf8"),
  ]);

  assert.match(page, /math-flow-data\.json/);
  assert.match(page, /<RepositoryKnowledgeViewer/);
  assert.match(page, /fallbackData=/);
  assert.match(layout, /Math Flow · Research Atlas/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton|site-creator-vinext-starter/);
  assert.match(viewer, /detail-tabs-transaction/);
  assert.match(viewer, /Submission<\/button>/);
  assert.match(viewer, /Judgment<\/button>/);
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
  assert.match(viewer, /collectProgramContributionIds/);
  assert.match(styles, /\.action-create/);
  assert.match(styles, /\.action-update/);
  assert.match(styles, /\.action-retire/);
  assert.match(styles, /\.action-restore/);

  const parsed = JSON.parse(data);
  assert.equal(parsed.runs.length, 3);
  assert.equal(parsed.transactions.length, 3);
  assert.equal(parsed.judgments.length, 1);
  assert.equal(parsed.judgments[0].judgmentKind, "primary");
  assert.match(parsed.judgments[0].reportMarkdown, /^#/);
  assert.equal(parsed.judgments[0].record.judgmentId, parsed.judgments[0].judgmentId);
  assert.equal(parsed.latestRunId, "run-live-3");
  assert.ok(parsed.runs.every((run) => run.revisionIds.length > 0));
  const previewAssets = await readdir(new URL("app/_sites-preview", templateRoot)).catch((error) => {
    if (error?.code === "ENOENT") return [];
    throw error;
  });
  assert.deepEqual(previewAssets, []);
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
    runId: "run-3",
    nodeId: "claim/midpoint",
    transactionId: "abc123",
    judgmentId: "sha256:def456",
    query: "parallel lines",
    detailMode: "judgment",
  });

  assert.deepEqual(parseViewerState(search), {
    problemId: "triangle-problem",
    projectionId: "builder:main",
    runId: "run-3",
    nodeId: "claim/midpoint",
    transactionId: "abc123",
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
