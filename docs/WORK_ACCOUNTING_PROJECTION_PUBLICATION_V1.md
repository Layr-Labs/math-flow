# Work-Accounting Projection Publication V1

Status: production-oriented adapter foundation, inactive. This document defines
how the provider-neutral work-accounting CAS is stored and published through
Math Flow's existing orphan `projections` branch. It does not activate a
projection, add a hosted workflow, or change the projection registry.

## 1. Lane identity and paths

`ProjectionBranchWorkAccountingStore` implements the exact `CASObjectStore`
protocol consumed by `work_accounting_pipeline`; the pipeline does not know
about GitHub or Git. An adapter instance is bound to one problem, logical
projection ID, and exact projection-spec digest. Their canonical tuple derives
a `laneScopeDigest`, so a specification revision cannot reuse an older lane.

The branch layout is:

```text
objects/work-accounting-cas-v1/<problem>/<scope>/
  identity.json
  data/<pipeline CAS key>

objects/work-accounting-publication-v1/<problem>/<scope>/
  <publication-manifest-digest>.json

indexes/problems/<problem>/work-accounting-v1/<scope>/
  head.json
  publication.json
```

Every logical immutable key is nested under the lane's content-addressed scope;
keys cannot escape, cross into a second lane, or traverse symlinks. `head.json`
is the sole pipeline CAS reference. `publication.json` is the latest atomic
publication marker. The existing GitHub projection publisher already permits
`objects/` and `indexes/` while rejecting every unrelated path.

## 2. Immutable-first publication

Before transport, the adapter validates the exact pipeline head and writes an
immutable publication manifest. That manifest binds:

- the problem, projection, specification, and lane scope;
- the exact pipeline-state digest and head byte digest;
- the previous publication manifest, when one exists;
- the immutable lane-identity object; and
- every immutable CAS object currently retained in the lane, with logical key,
  physical path, exact digest, and byte count.

The final mutable marker points at that manifest and repeats the exact head
bindings. `publish_work_accounting_projection` then delegates to
`publish_github_projection`. The established publisher chunks `objects/` into
at most 100 files per GitHub commit and sends all `indexes/` changes in one
final metadata commit. Thus every immutable object and manifest is durable
before the head and marker become visible, while the head and marker advance
atomically together.

Immediately before delegation, the adapter audits the complete Git status. It
permits only new immutable files inside this exact lane and the exact
`head.json`/`publication.json` pair. A deletion, immutable rewrite, rename,
extra metadata file, or change belonging to any other projection lane fails
before transport is invoked. This narrower preflight is required even though
the shared publisher intentionally supports the broader projection tree.

Every returned commit is required to form one optimistic expected-head chain.
All immutable phases must precede exactly one final metadata phase, and every
commit must carry the existing boundary's valid GitHub-generated signature.
Unsigned, reordered, missing-metadata, or stale-head publication fails closed.
Tokens are passed only to the established publisher and are absent from adapter
artifacts and result reports.

## 3. CAS and recovery

Local writers use an exact content digest as their CAS version. A stale
expected version cannot overwrite `head.json`. Cross-run and cross-host races
are rejected again by GitHub's `expectedHeadOid` when the branch commits are
created.

All writes use a temporary regular file, `fsync`, and atomic replacement.
Immutable puts are idempotent only for identical bytes. A conflicting value at
an existing logical key is rejected.

Crash recovery follows the existing refetch-and-retry architecture:

- before any remote commit, the same prepared worktree can retry;
- after an immutable chunk commit, a fresh branch checkout reuses the identical
  content-addressed objects and republishes only missing objects plus metadata;
- after the final metadata commit, a fresh checkout validates the marker and
  returns `already-published` without another network call; and
- a competing final metadata commit causes optimistic publication failure, so
  the caller must refetch and replan rather than overwrite the winner.

The adapter never treats a locally prepared marker as remotely published: any
remaining scoped Git changes still require transport.

## 4. Limits and retention

The store rejects unsafe keys, symlinks, non-byte values, oversized objects,
oversized publication manifests, and lanes above their configured object-count
limit. Defaults are 5 MiB per CAS object, 5 MiB per publication manifest,
50,000 objects per lane, and 25 MiB of raw file content per transport commit.
The adapter reproduces the established publisher's lexical 100-file immutable
chunking during preflight and rejects any chunk over the byte ceiling. This
bounds base64 request growth without changing the shared publisher. The
upstream evidence builder retains its own 1 MiB chunk ceiling, and the existing
GitHub publisher retains its 100-file immutable commit chunks and 100-file
final-metadata ceiling.

V1 retention is conservative. Every publication manifest is a canonical root,
and `plan_retention` verifies all referenced bytes before returning a plan. It
reports objects not yet reached by a publication as `unpublishedPaths`, but
always returns an empty `deletionPaths`. No automatic garbage collection is
authorized. A future deletion implementation must separately prove that an
object is absent from every historical publication manifest, branch reference,
and retained signed commit; failure or scale exhaustion must retain bytes and
stop rather than delete a canonical object.

## 5. Activation boundary

The adapter uses the real signed GitHub publisher by default but is not wired to
a CLI or workflow. Activation still requires a governed projection admission,
a trusted workflow that refetches the current orphan branch before every retry,
credential and permission review, branch-retention monitoring, and hosted
failure drills. Tests inject or mock transport and use no credentials or
network.

The provider-free research-v6 consumption and automatic catalog-read boundary
are specified in `docs/WORK_ACCOUNTING_PUBLISHED_RESEARCH_V6_V1.md`.
