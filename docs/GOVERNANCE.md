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
protected `main` branch, configure:

1. Require pull requests and the `Admin admission approval` status check.
2. Require CODEOWNER review.
3. Dismiss stale approvals when new commits are pushed.
4. Restrict direct pushes and branch-protection bypass to the intended admins.
5. Restrict creation and updates of the `projections` branch to GitHub Actions.

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
