import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import test from "node:test";

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

test("server-renders the research atlas with exported run data", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>Math Flow · Research Atlas<\/title>/i);
  assert.match(html, /Math Flow · research atlas/);
  assert.match(html, /Triangle midpoint quadrilateral/);
  assert.match(html, /Transactions/);
  assert.match(html, /Knowledge state/);
  assert.match(html, /Run[^<]*<!-- -->03/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|SkeletonPreview/i);
});

test("keeps the viewer data-driven and free of starter preview assets", async () => {
  const [page, layout, packageJson, data] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
    readFile(new URL("../app/math-flow-data.json", import.meta.url), "utf8"),
  ]);

  assert.match(page, /math-flow-data\.json/);
  assert.match(page, /<RepositoryKnowledgeViewer/);
  assert.match(page, /fallbackData=/);
  assert.match(layout, /Math Flow · Research Atlas/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton|site-creator-vinext-starter/);

  const parsed = JSON.parse(data);
  assert.equal(parsed.runs.length, 3);
  assert.equal(parsed.transactions.length, 3);
  assert.equal(parsed.latestRunId, "run-live-3");
  assert.ok(parsed.runs.every((run) => run.revisionIds.length > 0));
  const previewAssets = await readdir(new URL("app/_sites-preview", templateRoot)).catch((error) => {
    if (error?.code === "ENOENT") return [];
    throw error;
  });
  assert.deepEqual(previewAssets, []);
});

test("proxies repository projection state through the worker", async () => {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("catalog-test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  const catalog = { schemaVersion: 1, projections: [{ id: "live" }] };
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (request, init) => {
    assert.match(String(request), /api\.github\.com\/repos\/mooselumph\/math-flow\/contents\/viewer\/catalog\.json\?ref=projections/);
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
