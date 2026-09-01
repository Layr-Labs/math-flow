# Inactive provider-free Work Accounting local-slice probe

`provider-free-report.json` is the deterministic output of
`experiments/work_accounting_local_slice_probe.py`. It contains no model output,
uses no provider adapter, records zero external calls, and has no activation or
publication path.

The probe keeps every global accounting annotation in trusted code. The
experimental model-facing value contains only:

- exact writable nodes selected by the existing impact-context cut;
- pure-ancestor records with their exact primitive/base guards and the summed
  contribution of collapsed children;
- one digest-bound aggregate for every excluded child subtree; and
- exact state, knowledge, topology-alignment, impact-context, subject, and
  evaluation-mode bindings.

The default experimental bounds are 128 included programs and 256 collapsed
boundary roots. A case which exceeds either bound is reported as
`requires-explicit-widening`; no prefix, suffix, or semantic truncation occurs.
Reducer equivalence is conditional on the cut containing every patch target;
the report does not claim that routing always finds the semantically sufficient
scope.

See `docs/WORK_ACCOUNTING_LOCAL_SLICE_EXPERIMENT.md` for the contract,
measurements, limitations, and reproduction commands.
