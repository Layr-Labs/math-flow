# Provider-free Work Accounting V2 context scale probe

`provider-free-report.json` is the deterministic output of
`experiments/work_accounting_context_scale_probe.py` at a nominal 128,000-token
input threshold. It contains no provider output and records zero external
provider calls.

The report uses the active `openrouter-work-accounting-v2` request adapter with
a local capture transport. It measures exact compact serialized bytes and
clearly labelled bytes/4 token estimates for safe facts, `W+`, and `W-` across
dependency, topology-revision, solving-zero-out, and broad-local-subtree cases.

See `docs/WORK_ACCOUNTING_CONTEXT_SCALE_EVALUATION.md` for interpretation and
reproduction instructions.
