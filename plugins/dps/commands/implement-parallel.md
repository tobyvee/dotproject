---
description: Implement a wave of independent tickets in parallel, one subagent per ticket in its own git worktree, then land them one at a time, each reviewed, recorded and committed (and pushed, if the repo pushes after each ticket)
argument-hint: "wave N | T-NNN T-NNN ..."
---

# Implement tickets in parallel

Run several tickets at once, each in an isolated worktree, then land them on the current branch one at a time, keeping history linear. Each ticket is merged, reviewed, recorded and committed (and pushed, where the repo pushes after each ticket) before the next one starts landing. `$ARGUMENTS` is either `wave N` (read from `.project/tickets/INDEX.md`; run `/dps:prioritise-tickets` first if there are no waves) or a list of ticket IDs.

Read the repo's `CLAUDE.md` first. If it has no `## Workflow` section, stop and suggest `/dps:workflow-init`. Every "**Workflow → …**" reference below is a subsection of it.

## 1. Preflight (stop on any failure)

- The repo has at least one commit, and the working tree is clean (`git status --porcelain` is empty, including `.project/`). Worktrees branch from `HEAD`, so uncommitted code or ticket edits would be invisible to them. `.project/` must be committed, not gitignored, for the same reason.
- **If Workflow → Git and deploy says to push after each ticket:** the current branch has an upstream and matches it. Run `git fetch`, then `git rev-list --left-right --count @{u}...HEAD` must print `0	0`. Each ticket is pushed as it lands, so a branch that's behind would have its push rejected, and one that's ahead would publish commits this run didn't review. If there's no upstream, stop and ask the user; don't create one. Skip this check when the repo doesn't push after each ticket.
- Every ticket is `todo`, and every `depends_on` is `done`.
- **Re-check parallel safety yourself:** no two tickets' `touches` overlap (directories overlap with the files inside them), and at most one ticket changes the dependency manifest or lockfile. If a pair clashes, drop the lower-priority one from this run and say so.
- At most 4 tickets.
- Note `HEAD` as the base commit. Don't change ticket statuses yet; each ticket is recorded as it lands (step 3).

## 2. Fan out

Launch one agent per ticket **in a single message**, each with `isolation: "worktree"`. Pick each ticket's agent from **Workflow → Implementers**: a project specialist for the paths and tags it lists, `dps:ticket-implementer` for everything else.

All implementers follow the same ticket rules. The prompt only needs the ticket ID and, for UI tickets, the design artboard to match. The agent reads the ticket, spec, `CLAUDE.md`, the decision log and the test conventions from its worktree. Its definition holds the rules: stay inside `touches`, write nothing under `.project/` except new decision files, write tests with the code, commit with the ticket ID, and never push.

Don't do anything else while they run. Wait for every agent to finish.

Read each result before landing anything. A ticket whose agent returned `blocked`, or reported editing files outside `touches`, isn't landed. Record it as `blocked` in step 4, and leave its worktree for inspection.

## 3. Land each ticket: merge, verify, record, push

Take the tickets one at a time, in wave order (highest priority first, then most downstream dependants). Finish each one before starting the next. That way every commit that lands (and every push) is a ticket that's been reviewed and recorded.

1. **Merge.** Note `HEAD` as `<pre>`. Run the `dps:branch-integrator` agent (no worktree; it works on the current branch). Give it the current branch, the wave's base commit, and this one ticket's ID, branch name and `touches` list. It rebases the branch onto the current branch, fast-forwards, runs the tests, fixes only mechanical conflicts and removes the merged worktree. If it blocks the ticket, keep its reason for step 4 and move on to the next ticket.
2. **Verify `<pre>..HEAD`** the way `/dps:implement-ticket` step 3 does, except that every fix is committed (run the fixing agents with commits on):
   - **`dps:code-reviewer`:**
     - Must-fix findings: have the implementer for that area (**Workflow → Implementers**) fix them, then re-run the reviewer until the verdict isn't "changes required".
     - Should-fix findings: fix them if they're small. Otherwise put them under the ticket's `## Notes`.
   - **Extra audits:** for each row of **Workflow → Extra audits** whose paths the ticket touches, run that auditor and fix its failures with the agent the row names (committed).
   - **`dps:security-auditor`:** run it if the ticket touches a trust boundary listed in **Workflow → Security**.
     - Critical and high findings: `dps:security-fixer` fixes them, then re-run the auditor to confirm.
     - Medium findings: fix them the same way if the fix is small. Otherwise create a follow-up ticket with `/dps:plan-tickets "<finding>"` and give it top priority in the next wave.
     - Low findings: put them under the ticket's `## Notes`.
     - If the audit had findings, save it as `.project/review/<YYYY-MM-DD>-security-<ticket-id>-review.md` (frontmatter `type: review`, no `status`).
   - **`needs decision`** from any fixer: stop and ask the user before landing anything more.

   **If a must-fix, critical or high finding can't be resolved, don't land the ticket.**
   1. Keep its work on a branch: `git branch blocked/<ticket-id>`.
   2. Reset the current branch to `<pre>` with `git reset --hard <pre>`. Nothing after `<pre>` has been pushed.
   3. Record it as `blocked` in step 4, and move on to the next ticket.
3. **Record** it the way `/dps:implement-ticket` step 4 does:
   - **Decisions:** log each choice this step forced (`decided_by: main session`), such as a finding deferred or an acceptance criterion left unmet. Then add a `## Decisions` list to the ticket that links every decision file naming it. Find them with `git diff --name-only --diff-filter=A <pre>..HEAD -- .project/decisions/`, plus any you just wrote.
   - **Status:** set `status: done`, tick the acceptance criteria you've verified, and bump `updated:`.
   - **Indexes:** tick the ticket in `STATUS.md`, then update `INDEX.md`.
   - **Milestone:** if no other `todo` ticket shares its `milestone:`, run the `dps:milestone-reviewer` agent first. Its suggested commit message wins for this commit.
4. **Commit, then push if the repo pushes after each ticket.** Commit those `.project/` changes, including any review doc, e.g. `Record card list as done (T-012)`, ending with the attribution trailer Claude Code currently specifies. If **Workflow → Git and deploy** says to push after each ticket, run `git push`.

   If the push is rejected, stop. Never force-push, and don't pull or rebase over the rejection. Report the state and which tickets haven't landed yet.

## 4. Close the wave

Once every ticket is landed or blocked:

- **Security across the wave.** Run the `dps:security-auditor` agent on `<base>..HEAD`, because tickets that are each safe can combine into a hole. If this wave closes the final milestone, use scope `full` instead. Handle its findings as in step 3: `dps:security-fixer` commits each fix, you re-run the auditor, then push (if the repo pushes). If there were findings, save the audit as `.project/review/<YYYY-MM-DD>-security-wave-<N>-review.md` (frontmatter `type: review`, no `status`), with each finding's outcome and fix commit.
- **Decisions.** Log each choice this command made that step 3 didn't already log, following CLAUDE.md's **Decision log** (`decided_by: main session`):
  - a ticket not landed, or recorded as `blocked`
  - a finding deferred to a later wave
  - a ticket dropped from the wave for clashing `touches`

  Log the user's answer to any `needs decision` as `decided_by: user`.
- **Blocked tickets.** For each one:
  - Set `status: blocked`.
  - Put the reason under `## Notes`, with its `blocked/<ticket-id>` branch or worktree if it has one.
  - Add its `## Decisions` list.
- **Indexes.** Update `INDEX.md` and `STATUS.md`. Rewrite the Summary with `/dp:project-update`; if that plugin isn't installed, rewrite the first paragraph under `## Summary` yourself and bump `updated:`.
- **Commit and push.** Commit these `.project/` changes together, e.g. `Close wave 2: T-012 blocked`, then push if the repo pushes after each ticket. Skip this if nothing changed.
- **Report:**
  - A table with each ticket, its result (landed / blocked), its commits and whether they were pushed.
  - The security findings by severity, and what happened to each.
  - The final test results.
  - The time spent against the wave's estimate.
  - The next command: the next wave, or `/dps:prioritise-tickets` if anything was blocked.

Only the current branch is pushed, and only from step 3 and this step. Ticket branches and worktrees stay local, and nothing is force-pushed.
