# Math Flow Research Atlas

Interactive viewer for Math Flow repository projections and their canonical
transaction ledgers.

The deployed worker proxies `viewer/catalog.json` from the repository's orphan
`projections` branch. The client refreshes it every 30 seconds and exposes
problem and projection selectors. Set the optional `MATH_FLOW_CATALOG_URL`
worker binding to point at another public catalog.

The checked-in `app/math-flow-data.json` is only a deterministic development and
outage fallback. Refresh it from the repository root with
`python -m math_flow export-viewer`; see the root README for the full command.

```bash
npm install
npm run dev
```

The viewer supports repository projection selection, run-by-run time travel,
transaction evidence filtering, knowledge-tree search, adjudication revision
history, and source report review.

Use `npm test` for a production build plus rendered-HTML smoke tests, and
`npm run lint` for static checks.
