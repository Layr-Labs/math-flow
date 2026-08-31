# BSSC research-v7 Builder V9 context experiment

Status: inactive additive runtime candidate. It does not alter Builder V8,
`openrouter-research-v6`, or any published state. Activation requires a separate
one-file admission of `protocol/projections/openrouter-research-v7.json` whose
bytes match the runtime candidate.

## Question

Builder V8 passes the complete state-v3 predecessor to the organizer. The BSSC
V6 terminal is not materially larger than the earlier state-v2 terminal, but
most of its size is detailed proof, method, computation, tool, and artifact
support. The experiment asks whether the organizer can retain the complete
semantic portfolio while loading detailed support only where the accepted
submission declares a dependency.

## Exact V9 judge view

The trusted adapter derives `research-builder-context-v1` from the exact full
state-v3 predecessor and accepted validity-v4 assessments. The provider sees:

- every program with its complete objective, current synthesis, residual
  summary, hierarchy, result links, lifecycle, lineage, and source provenance;
- every intermediate result's title, statement, scope qualifications, program
  links, result dependencies, claim/source/judgment provenance, lifecycle, and
  supersession links;
- full proof, method, computation, tool, artifact-path, and attestation support
  for results mapped from the accepted claims' declared dependency transactions;
- the same full support for the recursive result-dependency closure of those
  seed results; and
- `support: null` for every other result, explicitly meaning omitted trusted
  history rather than absence of support.

The context excludes contribution records, entity digests, and prior artifact
digests. Their semantic information remains represented by result cores, while
the complete predecessor remains available to trusted validation. The context
has its own digest, is stored in the build bundle, is bound into sealed
submission input V3, and is re-derived during bundle loading.

## Additive support patch

The provider returns `supportAdditions`, not a complete replacement support
record. Trusted code:

1. unions all prior proof, method, computation, tool, attestation, and artifact
   support for an existing result;
2. binds selected current `artifactPaths` to the exact verified submission
   digests;
3. preserves the V8 additive claim, source, dependency, supersession, artifact,
   and judgment provenance rules; and
4. expands the proposal into the complete transition consumed by the unchanged
   state-v3 and V8 integrity reducers.

Consequently, hidden support cannot be deleted by omission. Existing erroneous
support is not silently edited in V9; a semantic correction must use the
existing supersession/retirement mechanisms or a later explicitly governed
revision policy.

All result statements remain visible, so the organizer can still recognize an
undeclared consolidation target. The detailed support for that target may be
hidden, but field-level additions are safely merged against the complete trusted
record.

## Leaf-program rubric

V9 retains the two-entity model and adds explicit guidance to form durable child
programs for coherent independently pursuable directions. A leaf program may
begin from one accepted result when it names a stable local objective, but it
must never mirror a submission, contributor, chronology, or display grouping.
This is a prompt-level experiment; deterministic validation can enforce a valid
strict tree but cannot prove that a model-authored boundary is scientifically
useful.

## Provider-free BSSC measurement

The exact V9 context constructor was applied to all 16 sequential V6
predecessors. For each transition, the dependency transaction IDs were read from
the corresponding accepted V6 contribution record. JSON bytes use the same
sorted compact serialization as the governed provider.

| Measure | Full V8 predecessor | V9 context |
| --- | ---: | ---: |
| Mean bytes across 16 transitions | 52,160 | 31,266 |
| Mean reduction | — | 34.1% |
| Median reduction | — | 38.9% |
| Predecessor before transition 16 | 98,042 | 54,136 |
| Transition-16 reduction | — | 44.8% |

The empty initial state grows from 701 to 739 bytes because of explicit context
metadata. Later reductions range from 10.7% to 44.8%. The transition-16 view
loads full support for one dependency-closure result, omits it for thirteen, and
retains all fourteen result cores.

This measurement excludes the problem, accepted assessment, current submission
evidence, and system prompts because those inputs are identical between V8 and
V9. It establishes deterministic context reduction and semantic-core retention;
it does not establish organizer quality.

## Hosted experiment route

The candidate projection is `openrouter-research-v7`, while the organizer is
Builder V9. It deliberately starts from the state-v3 zero state and replays the
same 16 accepted BSSC submissions as V5 and V6. It does not use a V6 state as a
predecessor.

`.github/workflows/project-research-v7-serial.yml` is the only intended hosted
route. It claims and publishes exactly one accepted submission per run, defaults
`continue` to false, and uses the existing governed retry/checkpoint boundary.
The generic OpenRouter workflow rejects this projection before provider access.

Evaluation should compare each adjacent V9 transition with its V6 counterpart:

- program and result identity, granularity, consolidation, and scope;
- creation of durable leaf programs rather than submission-shaped containers;
- preservation of accepted claim coverage and exact provenance;
- provider prompt/completion tokens, retry count, validation failures, and cost;
- support additions and any evidence that omitted support harmed synthesis; and
- terminal readability and downstream local-context usefulness.

Stop before another dispatch if the lane drops a qualification, duplicates a
known result, creates submission-shaped programs, repeatedly fails because
required support is hidden, or needs a topology/content operation combination
that the current reducer cannot express.
