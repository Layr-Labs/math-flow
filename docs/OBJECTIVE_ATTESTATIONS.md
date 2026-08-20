# Durable objective verifier attestations

Objective attestations make exact checks durable without moving a verifier's
conclusion into the participant ledger. The canonical contribution may contain
an optional `verification.json` recipe. A trusted post-merge worker executes
that recipe and publishes a separate, content-addressed
`verifier-attestation` run bundle on the orphan `projections` branch.

This is an additive version-1 profile. Contributions without a verification
request remain valid, and existing contributions are not retrofitted or
rewritten.

## Protocol boundary

The participant-authored file records intent, not a result:

```json
{
  "schemaVersion": 1,
  "verifier": {
    "id": "python-stdlib-3-13-v1",
    "specDigest": "sha256:fc7ed06b77396fabc1da84694b4d8a08800843f41ad8ca4b9cd666b67ba60884"
  },
  "entrypoint": "verify.py",
  "arguments": ["configuration.txt"]
}
```

It contains no `passed`, `accepted`, confidence, or knowledge-state field. The
repository validator requires the entrypoint to be an artifact in the same
contribution and the verifier digest to match a spec under
`protocol/verifiers/` at the canonical transaction commit. All files in the
contribution directory—not only the named entrypoint—become attestation inputs.
This prevents a recipe from silently omitting a certificate, imported module,
or README that affects the claim being checked.

Compute a spec's canonical digest with:

```bash
python3 -m math_flow verifier-spec-digest \
  --verifier protocol/verifiers/python-stdlib-3-13-v1.json
```

The initial allowlisted runner is `oci-command-v1`. Its spec pins an OCI image
by SHA-256 digest, platform, executable, fixed arguments, success exit codes,
timeout, a combined stdout/stderr byte limit, resource limits, disabled
networking, a read-only root filesystem, and a bounded temporary filesystem.
The worker drains output while the command runs and terminates it before output
can grow beyond that governed limit. Execution never uses a shell. New environment
or command policies require a new versioned spec and a new digest.

## Producing and replaying a bundle

Production happens only after the contribution's squash commit is part of the
canonical first-parent ledger, because that commit is the attestation subject:

```bash
python3 -m math_flow attestation-plan \
  --problem <problem-id> \
  --transaction <full-canonical-transaction-sha> \
  --head main \
  --projection-dir <projection-worktree>
```

Planning is provider-free and does not execute participant code. It reports
whether this exact immutable request already has an authoritative published
outcome. Publication rejects a second, different outcome for the same request.

```bash
python3 -m math_flow attest \
  --problem <problem-id> \
  --transaction <full-canonical-transaction-sha> \
  --head main \
  --output-dir /tmp/attestation
```

The command materializes the contribution bytes from the exact transaction and
runs Docker with the pinned image and isolation policy. It emits:

```text
run.json
attestation.json
stdout.log
stderr.log
```

`run.json` is the generic Math Flow artifact envelope with
`runKind: verifier-attestation`. `attestation.json` binds:

- the canonical transaction, contribution ID, and path;
- every contribution-relative path, byte count, and SHA-256 digest;
- the exact verifier-spec and environment digests;
- the non-shell invocation and resource policy;
- exit status plus content-addressed stdout and stderr; and
- the protocol producer implementation.

The attestation ID hashes all of those fields. The run digest additionally
hashes the complete artifact manifest. The existing `publish-batch` transport
accepts this run kind and stores it at its normal content-addressed object path.
Publication should be performed by the same protected GitHub-signed projection
publisher used for judgments and knowledge runs; generated bundles must never be
committed to `main`.

Verify content, canonical ancestry, spec, environment, inputs, and manifest
without executing untrusted code:

```bash
python3 -m math_flow verify-attestation \
  --bundle /tmp/attestation \
  --head main
```

Replay the OCI verifier and require the result and both output streams to match
byte-for-byte:

```bash
python3 -m math_flow verify-attestation \
  --bundle /tmp/attestation \
  --head main \
  --replay
```

Later unrelated commits and later contributions do not make an attestation
stale. Its subject and verifier remain pinned to the original canonical
transaction. Rewritten history, a transaction that is no longer canonical, a
changed input, a mismatched verifier digest, or a production head outside the
current ancestry is rejected.

## Trust and threat model

There are two distinct claims:

1. **Bundle validity** is deterministic. Anyone can recompute all digests,
   resolve the canonical transaction, inspect the environment pin, and replay
   the verifier.
2. **Production authenticity** belongs to the projection transport. A bundle
   copied from an arbitrary directory can make a self-consistent claim that a
   command passed; JSON alone cannot prove that the command ran. Consumers that
   do not replay must trust only bundles reached through an authenticated,
   GitHub-signed `projections` commit produced by the governed workflow.

The validator therefore rejects common forged or stale shapes but does not
pretend a producer string is a signature. A hostile participant cannot select a
mutable image tag, enable networking, make the root writable, or change the
success policy inside an admitted request: those values come from the exact
protected verifier spec. Participant code is still untrusted and must only run
inside the constrained OCI worker.

The OCI digest pins userspace bytes, not the host kernel, Docker daemon, CPU
microcode, or hardware. The v1 profile also captures only bounded stdout and stderr; a
future profile can add declared file outputs, proof-assistant-specific result
indexes, signed workload identity, transparency logs, or hardware-backed remote
attestation.

The trusted `project-attestation.yml` workflow is dispatched automatically for
a merged contribution containing `verification.json`. It performs a provider-free
preflight, executes only the pinned networkless OCI command, rechecks canonical
main and the projection branch, and publishes through the GitHub-signed orphan
projection transport. The viewer and `math-flow context` show pending and
published outcomes separately from judgments and credit.

For the validity-v3 path, pending objective verification is a subject-local
dispatch gate. Coverage defers only the requesting transaction; unrelated
primary judgments continue in parallel. After either a passing or failing
terminal bundle is published, the trusted workflow redispatches the active v3
projection streams for that problem. The next coverage plan includes the
formerly deferred subject and reuses all independently completed judgments.

## Use by judges and knowledge builders

An objective attestation is evidence, not an automatic adjudication. Judgment
and knowledge profiles may cite its content-addressed attestation or run digest
using the existing `verifier-attestation` evidence kind. A judge may explain
what the exact checker establishes, whether the encoded statement matches the
mathematical claim, and what assumptions remain. That separation is important:
a successful program run can verify its encoded predicate without proving that
the encoding answers the intended research question.

The validity-v3 dependency packet embeds the verified terminal request digest,
run digest, attestation ID, environment and artifact identities, result, and
bounded output. Its packet digest and resulting judgment identity therefore bind
the exact evidence. A request without a terminal published bundle cannot produce
a v3 primary judgment.
