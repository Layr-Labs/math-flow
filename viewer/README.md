# Math Flow Research Atlas

Interactive viewer for Math Flow repository projections and their canonical
transaction ledgers.

The deployed worker proxies `viewer/catalog.json` from the repository's orphan
`projections` branch through GitHub's Contents API. The client refreshes it every
30 seconds and exposes problem and projection selectors. For a private
repository, configure `MATH_FLOW_GITHUB_TOKEN` as a server-side secret containing
a fine-grained token scoped only to this repository with read-only Contents
permission. Set the optional `MATH_FLOW_CATALOG_URL` worker binding to point at
another catalog endpoint.

The checked-in `app/math-flow-data.json` is only a deterministic development and
outage fallback. Refresh it from the repository root with
`python -m math_flow export-viewer`; see the root README for the full command.

```bash
npm install
npm run dev
```

The viewer supports repository projection selection, run-by-run time travel,
full submission inspection, raw and structured primary/reconciliation judgment
review, transaction evidence filtering, knowledge-tree search, adjudication
revision history, and knowledge-build report review. The complete active view is
mirrored in the query string, so its URL can be refreshed or shared without
losing the selected projection, state, artifact, detail tab, or search filter.

Use `npm test` for a production build plus rendered-HTML smoke tests, and
`npm run lint` for static checks.
