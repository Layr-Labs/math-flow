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
  --projection openrouter-research-v1 \
  --problem triangle-midpoints \
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
also protects changes to projection definitions and to its own policy,
CODEOWNERS, and workflow.

Governed changes use a one-file PR:

- a problem PR adds `problems/<problem-id>/problem.md`;
- a projection PR adds or edits one `protocol/projections/<id>.json`;
- a policy PR edits one governance-control file.

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
