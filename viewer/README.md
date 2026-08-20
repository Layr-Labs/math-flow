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

The viewer does not embed a problem snapshot. While the governed repository
catalog is unavailable it shows an explicit empty state, so an archived problem
cannot reappear as outage data. Local development therefore needs a reachable
catalog endpoint (or the ordinary repository binding) to display research state.

```bash
npm install
npm run dev
```

The viewer supports repository projection selection, run-by-run time travel,
full submission inspection, raw and structured primary/reconciliation judgment
review, transaction evidence filtering, knowledge-tree search, adjudication
revision history, KaTeX rendering for inline and display LaTeX, and
knowledge-build report review. Validity-v2 judgments foreground claim status,
premise sufficiency, scope qualifications, and evidence issues.
Validity-v3 assessments additionally separate submission-declared references
and provenance from the narrower set of premises the judge found logically
required. Validity-v4 packets also bind terminal objective evidence for the
subject and requesting transactions in its declared-reference union;
validity-v2/v3 presentation remains readable. Serialized
research-program states distinguish programs, local work threads, and accepted
results or methods, while the hierarchical two-term credit overlay exposes both
direct and obviated work, local and overall allocation shares, counterfactuals,
and unattributed program residuals. Legacy judgment and qualitative-credit
artifacts remain readable. The complete active view is
mirrored in the query string, so its URL can be refreshed or shared without
losing the selected projection, state, artifact, detail tab, or search filter.

Use `npm test` for a production build plus rendered-HTML smoke tests, and
`npm run lint` for static checks.
