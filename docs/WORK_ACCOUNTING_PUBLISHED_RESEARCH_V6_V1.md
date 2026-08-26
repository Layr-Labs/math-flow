# Published research-v6 consumption for work accounting V1

Work accounting does not call the knowledge-state builder. The admitted
research-v6 projection owns the program/thread topology and publishes one
content-addressed adjacent transition per accepted submission. The work lane
consumes that exact published chain through
`math_flow.work_accounting_research_v6`.

## Verified transition boundary

`load_published_research_v6_transition` verifies the complete run bundle and
binds its problem, projection-spec digest, builder-spec digest, subject, base
run, submission input, base state, transition, post-state, topology alignment,
and same-world handoff. It independently applies the v6 reducer and requires
exact equality with all three derived artifacts. Judge-emitted or manifest-only
derived values are never trusted.

`load_published_research_v6_chain` follows `baseRun` content addresses from a
terminal to the zero origin, rejects cycles and gaps, and requires adjacent
state equality and increasing submission ordinals. A
`PublishedResearchV6TransitionProvider` exposes that verified chain through the
existing pipeline builder-provider protocol. On each call it requires exact
base-state equality and matches the normalized work submission's transaction,
ordinal, judgment, accepted claims, and evidence-manifest digest before
returning the already-published transition. It performs no provider call.

The governed dependency role is `research-builder-handoff`. Resolving that role
verifies the terminal bundle as research-v6, including reducer replay, rather
than accepting any artifact that merely carries the role name. The dependency
lock's exact terminal `runDigest` is the input to chain loading.

## Catalog boundary

Research-v6 states are rendered through the existing research projection
surface. Each run additionally exposes its exact topology alignment and
same-world handoff.

The catalog discovers work-accounting lanes only for active governed overlay
specifications whose runner is `openrouter-work-accounting-v1` and which declare
exactly one `research-builder-handoff` dependency. Lane scope is derived from
the exact `(problemId, projectionId, projectionSpecDigest)`. A lane is shown
only when it has a valid publication marker and at least one evaluated
submission, and its terminal knowledge-state digest must occur in the declared
research projection.

Catalog reads are non-mutating. They verify the marker, publication manifest,
lane head, retained-object byte digests, pipeline, schedule, work bundles, and
terminal states. Immutable objects not reachable from the selected publication
manifest are ignored; this preserves the last complete catalog after an
object-first publication crash. They are never treated as canonical and remain
eligible only for the repository's deletion-free retention audit.
