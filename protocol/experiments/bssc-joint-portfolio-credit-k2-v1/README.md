# BSSC joint portfolio credit K2 V1

This additive, unpublished experiment completes the successful K2 joint
portfolio/W+ result from GitHub Actions run 33564954137. It does not ask a
second judge to recreate the topology or W+ estimates. The exact accepted
response is checked in, rebound to the canonical K2 submission evidence, run
through the trusted joint reducer, and required to reproduce the original
post-state and W+ digests before any new provider call is possible.

The remaining flow is:

```text
frozen joint K2 topology and W+
        |
        v
counterfactual-safe fact extraction (submission evidence available)
        |
        v
direct W- estimate (no submission evidence; frozen numeric W+ visible)
        |
        v
trusted D = W- - W+ and submission allocation
```

Only safe-fact extraction and W- estimation call the provider. W- is a sparse
patch from the old live K1 accounting state on the exact K2 post-topology; it
is not a patch on W+. The provider never authors total work, D, node effects,
credit shares, or percentages. Trusted code rejects `D <= 0` without clamping
and preserves the validated safe-fact checkpoint while invalidating a rejected
W- checkpoint.

The final candidate allocates all raw work value directly to the canonical K2
submission, because `x` is the submission. Its node effects are an additive
explanation of where the difference arose, not separate credit recipients.
Signed node effects must sum exactly to the submission allocation.

Publication and continuation are forbidden. A hosted run requires explicit
approval and must use `continue=false`.
