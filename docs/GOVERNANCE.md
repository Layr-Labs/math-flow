# Governed problem and projection admission

Problems and logical projections are named protocol namespaces. Creating one is
therefore governed separately from submitting an ordinary research contribution.

## Approved projection registry

Every runnable repository projection has one declarative specification at:

```text
protocol/projections/<projection-id>.json
```

Schema-version-1 knowledge specifications bind the primary judge,
reconciliation judge, knowledge builder, allowed problems, concurrency, and
knowledge-build cadence. Schema-version-2 overlay specifications instead bind an
allowlisted runner, typed projection dependencies, allowed problems, and overlay
cadence. The repository workflows accept only a projection ID and problem ID.
They resolve implementation paths from the registry at canonical `main`, reject
the wrong execution engine, and refuse a dispatch from any other ref. A digest
of the entire specification is part of run and lane identity, so projections do
not share logical state merely because they reuse one component.

### Referenced builder upgrades

Do not edit a knowledge-builder specification in place while an active governed
projection references it. Governed lane identity uses the projection-spec digest,
while each existing lane also retains the exact builder-spec digest with which it
was created. Changing only the referenced builder file leaves the projection
digest—and therefore the lane ID—unchanged, but the next build request still
belongs to a lane carrying the old builder digest. The scheduler rejects the
mismatched builder before claiming work, and formation independently rejects a
claim/spec mismatch. This failure is intentional: silently changing the
executable semantics of an established projection chain would undermine replay.

Instead, add a versioned builder with a new `id` and implementation version, then
add or edit a governed projection so its own specification digest changes. Use a
new shadow projection when the old chain must remain active for comparison or as
a dependency. The new projection receives a fresh scheduler lane and does not
inherit a base state unless a separately governed migration mechanism explicitly
provides one. Keep the old builder file byte-for-byte available for replay while
published runs or active projections reference its digest.

Roll out the runtime and versioned builder before admitting the projection that
uses them. A projection addition or edit remains a separate one-file governed PR
under the admission policy below.

The validity-v3/hierarchical-research-v3 and validity-v4/hierarchical-research-v4
upgrades followed this rule. Each runtime and its versioned components merged
before a separate one-file projection admission. The resulting production
knowledge identity is `openrouter-research-v3`; it adds claim-bounded terminal
objective evidence for declared references and uses the v4 builder without
editing the earlier v1, v2, or v3 component identities. Its active producer
states cover the two retained problems, `bssc-sum-capacity` and
`no-three-in-line-77`. `openrouter-research-credit-v3` was admitted only after
both producer states were current and locks that exact producer family. Its
required runtime fix is deployed, its governed status is active again, and its
first assignments are current for both retained problems. The v1/v2 producer
lanes and v2 credit consumer remain temporarily active; they may now be disabled
in dependency order. They remain available for explicit historical replay. See
`docs/HIERARCHICAL_RESEARCH_PROTOCOL_V4.md`.

The additive hierarchical builder v5 follows the same rollout boundary. Its
runtime, profile, audited batch-delta schema, and versioned builder merge first.
A later one-file governed edit may pair the existing validity-v4 primary with
builder v5 under `openrouter-research-v3`; the changed projection digest starts
a fresh lane and leaves the builder-v4 chain replayable. See
`docs/HIERARCHICAL_RESEARCH_PROTOCOL_V5.md`.

Overlay cadence is governed projection identity, not an advisory runner hint.
With only `minimumIntervalSeconds`, a rolling overlay becomes eligible when its
verified dependency state changes and the interval after the preceding run has
elapsed; changes arriving during the interval coalesce. An optional
`utcCalendarPeriod` of `{ "unit": "hour" }` or `{ "unit": "day" }` targets
the latest closed UTC period instead. Each period has one immutable allocation
window and at most one published run. A rolling interval controls execution
pressure but does not itself define an award period. For a calendar policy,
`minimumIntervalSeconds` cannot exceed the selected hour/day, preventing a
configuration that necessarily accumulates backlog faster than it can drain.

A new calendar chain considers only the latest closed period and remains
unstarted when that period is empty. Thereafter
the predecessor window is its durable cursor: recovery selects the earliest
subsequent closed period containing transactions and skips intervening empty
periods deterministically. Thus downtime does not permanently omit an earlier
nonempty award period once the chain exists.

Validate or inspect the registry without making a provider call:

```bash
python -m math_flow validate-projections
python -m math_flow resolve-projection \
  --projection openrouter-research-v3 \
  --problem bssc-sum-capacity \
  --head HEAD
python -m math_flow list-active-projections \
  --problem no-three-in-line-77 \
  --engine overlay-repository-v1 \
  --head HEAD
```

The repository continues to use one orphan `projections` branch as a
content-addressed publication layer. Logical projection isolation comes from the
registry digest and scheduler lane, not from additional Git branches.

## Admission policy

`.github/math-flow-governance.json` lists GitHub logins authorized to admit a new
problem or projection and the number of approvals required. The admission check
also protects the reversible problem-lifecycle registry, changes to projection
definitions, and its own policy, CODEOWNERS, and workflow.

Governed changes use a one-file PR:

- a problem PR adds `problems/<problem-id>/problem.md`;
- a problem-lifecycle PR adds or edits `protocol/problem-registry.json`;
- a projection PR adds or edits one `protocol/projections/<id>.json`;
- a policy PR edits one governance-control file.

`protocol/problem-registry.json` stores only the sorted IDs of archived
problems. Archiving never deletes or rewrites the problem statement,
contributions, directions, judgments, or published projection objects. It
removes the problem from ordinary discovery, new participant admission, active
projection resolution, recovery scheduling, and the live viewer catalog.
Removing an ID from the same governed registry restores the problem.

### Projection retirement operations

Changing a governed projection from `active` to `disabled` stops new scheduling
but does not rewrite its published objects. Disable a consumer before the
producer it depends on, and do not retire the old producer until its replacement
is current for every retained problem. After the retirement PRs merge, manually
refresh the projection-branch catalog:

```bash
gh workflow run refresh-viewer-catalog.yml --ref main
gh run list --workflow refresh-viewer-catalog.yml --branch main \
  --event workflow_dispatch --limit 1
gh run watch <run-id> --exit-status
```

`refresh-viewer-catalog.yml` is dispatch-only. Without this step, the published
catalog can continue to expose or default to a lane that canonical governance
has already disabled.

The check counts either an approving review against the PR's current head commit
or an exact head-bound command comment from a configured administrator:

```text
/approve-admission <full-40-character-head-SHA>
```

The command must be the comment's only non-whitespace text. Short SHAs, stale
head SHAs, surrounding prose, duplicate comments from one administrator, and
comments from logins outside the base branch's administrator allowlist do not
count. Pushing a commit changes the head and invalidates every earlier command;
editing or deleting a command comment also removes it from the next check. A PR
author may use the command if they are an allowlisted administrator, avoiding
GitHub's prohibition on self-approving reviews while retaining the configured
permission set and `minimumApprovals` threshold.

Ordinary contribution-only PRs are explicitly not subject to this approval
policy and retain the atomic transaction validator.

The workflow uses `pull_request_target` and `issue_comment` so its definition and
Python validator come from the trusted base/default branch. It fetches the
proposed head only into the Git object database and treats every candidate file
as inert data: it never checks out or executes PR code and exposes no secrets.
Repository, PR, and issue access is read-only. The narrowly scoped
`checks: write` permission is used only to publish the trusted validation result
on the resolved PR head, because an `issue_comment` workflow run is attached to
the default-branch commit. CODEOWNERS also covers the base-branch Python package
that this workflow executes, preventing an unreviewed change from weakening a
later admission check. These are important invariants; do not add build,
package-manager, or candidate-script execution to that workflow.

## Required repository settings

The workflow reports policy but cannot prevent a merge by itself. On the
protected `main` branch, configure the following effective policy. GitHub can
compose classic branch protection, repository rulesets, and organization
rulesets; inspect the effective rules rather than assuming that one settings
page is authoritative.

| Control | Required value | Reason |
| --- | --- | --- |
| Pull request required | yes | No direct participant writes to the canonical ledger. |
| Required status check | `Admin admission approval` | Governed namespace changes fail closed; ordinary participant events receive a trusted success result. |
| Require branch to be up to date | **no** (`strict: false`) | The trusted auto-merge workflow revalidates an atomic participant event against latest `main`; requiring rebases needlessly serializes disjoint contributions and registrations. |
| General approving reviews | `1` | GitHub enforces CODEOWNER review only when required reviews are enabled; the trusted participant workflow supplies this review for atomic solver events. |
| CODEOWNER review | yes | Governed definitions and trusted executable surfaces require human review. |
| Pull-request bypass | user `mooselumph` only | A single maintainer cannot approve their own CODEOWNED PR. The explicit bypass avoids that lockout; all status checks still apply. |
| Dismiss stale approvals | yes | A changed governed head requires a new review. |
| Most-recent-push approval | no | Current-head admission approval and CODEOWNER review already cover governed changes. |
| Apply to administrators | yes | Administrators other than the explicitly listed maintainer do not silently bypass the protocol boundary. |
| Merge method on `main` | squash only | The squash commit is the canonical participant transaction. |
| Force pushes and deletion | blocked | Canonical history is append-only. |
| Ruleset target | `refs/heads/main`, not `~ALL` | Feature branches must remain updateable while `main` stays protected. |

The organization ruleset requires signed commits on all branches. The
repository `main` ruleset has no bypass actors and supplies the squash-only,
deletion, and non-fast-forward rules. Classic `main` protection supplies the
required status check, review requirement, CODEOWNER semantics, and the narrow
`mooselumph` user bypass. A `false` CODEOWNER field in the repository ruleset
does not cancel the classic protection; effective rules are additive.

The maintainer bypass does not bypass the required admission status check. The
default-branch auto-merge workflow accepts only one atomic contribution or
direction event, requires every check on the exact candidate head, and
revalidates that inert event against latest `main` before submitting the one
required GitHub Actions review and merging it. Non-participant changes remain
manual. Changes to CODEOWNED paths authored by anyone else require approval
from `mooselumph`; changes authored by `mooselumph` use the explicit bypass
because GitHub forbids self-approval.

`.github/CODEOWNERS` deliberately excludes ordinary contribution and direction
event paths. It covers governed problem/projection definitions, the governance
policy, the Python package used by trusted checks, and **every file under
`.github/workflows/`**. Protecting the workflow directory as a wildcard avoids
leaving a newly added write-capable workflow outside review.

Verify the live configuration with read-only GitHub API calls:

```bash
gh api repos/Layr-Labs/math-flow/branches/main/protection \
  --jq '{required_status_checks,required_pull_request_reviews,enforce_admins}'
gh api repos/Layr-Labs/math-flow/rules/branches/main --paginate \
  --jq '.[] | {type,ruleset_id,ruleset_source,parameters}'
gh api repos/Layr-Labs/math-flow/rulesets \
  --jq '.[] | {id,name,target,enforcement}'
```

Confirm in particular that `required_status_checks.strict` is `false`,
`required_approving_review_count` is `1`,
`require_code_owner_reviews` is `true`, and the repository ruleset's ref
condition is exactly `refs/heads/main`. Confirm that classic pull-request bypass
allowances contain only the user `mooselumph`, with no team or app bypasses. A
status check named "Admin admission approval" is not a GitHub approving review;
these are separate mechanisms.

The orphan `projections` branch should remain writable only by the trusted
publication workflows. Verify its effective rules separately before changing
publisher permissions; the organization signed-commit rule alone does not
provide actor restriction.

GitHub team membership is deliberately not inferred in this MVP because the
default workflow token cannot reliably enumerate private organization teams.
Use explicit GitHub logins in the policy. A GitHub App can later replace this
with organization/team identity and immutable user IDs.

The registered reconciliation judge is part of projection identity. After the
hosted workflow verifies the complete primary-judgment set, it deterministically
derives the current conflicts, reuses any matching published reconciliation
bundles, and fans out one reconciliation call for each missing conflict before
serialized knowledge formation. Only the relevant primary judgment reports,
their canonical subject evidence, and the derived conflict record are sent to
the configured OpenRouter reconciliation judge.
