# Math Flow Research Atlas

Interactive viewer for a Math Flow transaction ledger and a chain of
hierarchical Markdown v2 judge runs.

The checked-in `app/math-flow-data.json` is a deterministic demo export. Refresh
it from the repository root with `python -m math_flow export-viewer`; see the
root README for the full command.

```bash
npm install
npm run dev
```

The viewer supports run-by-run time travel, transaction evidence filtering,
knowledge-tree search, adjudication revision history, and source report review.

Use `npm test` for a production build plus rendered-HTML smoke tests, and
`npm run lint` for static checks.
