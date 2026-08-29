# BSSC research-v5 serial producer

Status: active hosted producer for the governed `openrouter-research-v5`
experiment.

V5 rebuilds the fixed BSSC accepted history from the structural state-v3 zero
state using Builder V7's two-entity model. It reuses the immutable validity-v4
record and publishes exactly one adjacent knowledge transition per accepted
canonical submission. It does not migrate or use the V4 knowledge state as a
base.

## Exact frontier

`protocol/runtime/bssc-research-v4-validity-source-v1.json` pins the canonical
25-submission ledger and the already-published validity bundles. The
provider-free `bssc-research-v5-frontier` command verifies that source and the
published V5 predecessor chain before exposing one of the 16 accepted subjects:

```text
3, 4, 5, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 21, 24, 25
```

Every published predecessor must be a state-v3 Builder V7 bundle bound to the
governed projection digest, exact validity judgment, and canonical accepted
prefix. A cycle, stale scheduler, alternate order, wrong state version, or
foreign run stops before a provider call.

Existing content-entity `baseDigest` values are deterministic concurrency
tokens, not AI judgments. The trusted Builder V7 adapter replaces those fields
with the exact digest from the bound base state before reducer validation.
Likewise, an intermediate result's `judgmentIds` are derived in either operation
stream from the result's AI-chosen `claimRefs` and `sourceTransactionIds` using
the bound current judgment and prior accepted contributions. New entity and
topology-operation digest rules remain fail-closed, duplicate operations and
unknown provenance still fail, and replay revalidates every normalized
transition against its exact predecessor.

## Hosted route and inspection gate

`.github/workflows/project-research-v5-serial.yml` is the only hosted V5 route.
One invocation:

1. binds the admitted projection byte-for-byte to the active runtime candidate;
2. materializes the completed accepted prefix plus exactly one next validity
   bundle;
3. claims exactly that one judgment with a hard maximum of one;
4. calls Builder V7 at the subject's canonical commit and exact predecessor;
5. atomically publishes the content-addressed build and scheduler update.

The `continue` input defaults to `false`. Therefore the initial activation
publishes at most K1 and stops for human inspection. Setting `continue=true`
allows each successful publication to dispatch the next frontier. A failed
build publishes the normal failed-lease state but never auto-continues.

The generic `project-openrouter.yml` workflow rejects V5 before planning or
provider access. V5 does not rerun validity, perform work accounting, refresh
credit, or export a viewer catalog. Those remain separate downstream stages.
