---
description: Implement one ticket on the current branch, with tests, checks and a commit, then record it as done (and push it, if the repo pushes after each ticket)
argument-hint: "T-NNN"
---

# Implement a ticket

Implement `$ARGUMENTS` (one ticket ID) in the main working tree. For several independent tickets at once, use `/dps:implement-parallel`.

Read the repo's `CLAUDE.md` first. If it has no `## Workflow` section, stop and suggest `/dps:workflow-init`. Every "**Workflow → …**" reference below is a subsection of it.

## 1. Check it's ready

- Read `.project/tickets/$ARGUMENTS-*.md` and the spec sections it links to. For UI tickets, also read the design artboard it names, using the reading instructions in **Workflow → Sources of truth → Design**.
- Find the relevant decisions in `.project/decisions/`, following CLAUDE.md's **Reading the log**. They apply whether you build the ticket yourself or delegate it.
- Stop and report if any `depends_on` ticket isn't `done`, or if the working tree has uncommitted changes to files the ticket `touches`.
- **If Workflow → Git and deploy says to push after each ticket:** the current branch must have an upstream and match it. Run `git fetch`, then `git rev-list --left-right --count @{u}...HEAD` must print `0	0`. Step 4 pushes, so if the branch is behind, is ahead, or has no upstream, stop and ask the user. Skip this check when the repo doesn't push after each ticket.
- Set the ticket's `status: doing` and bump `updated:`. Move its STATUS.md line to `## In progress`.

## 2. Build it

Build it yourself in this session, or, to keep the build's output out of the main context, delegate it to an agent (no worktree) with the ticket ID. Pick the agent from **Workflow → Implementers**: a project specialist for the paths and tags it lists, `dps:ticket-implementer` for everything else.

A delegated agent commits its code and its own decision files, but nothing else under `.project/`. In that case, do step 4's records as a follow-up commit, and still run step 3's checks on its result.

- **Stay inside `touches`.** If the work needs another file, edit it only if no `todo`/`doing` ticket claims that file, and add it to this ticket's `touches`. Otherwise stop and say which ticket owns it.
- Follow CLAUDE.md's architecture rules, especially **Workflow → Architecture rules most often broken**.
- Write the module's tests in the same step, from the spec's test cases (**Workflow → Sources of truth → Test cases**). Use the `dps:test-writer` agent, or follow its conventions yourself.

## 3. Verify

- Run the test, type-check and lint commands from **Workflow → Commands** (lint only if it exists). All must pass.
- **Code review.** Run the `dps:code-reviewer` agent on the ticket's diff.
  - **must-fix findings:** fix them before going on, using the implementer for that area from **Workflow → Implementers**. Re-run the reviewer until the verdict isn't "changes required".
  - **should-fix findings:** fix them if they're inside this ticket's files. Otherwise note them under the ticket's `## Notes`.
  - **Nits:** fix them only if trivial.
- **Extra audits.** For each row of **Workflow → Extra audits** whose paths the ticket touches, run that auditor and fix its failures with the agent the row names.
- **Security.** If the ticket touches any trust boundary listed in **Workflow → Security**, run the `dps:security-auditor` agent on the ticket's diff. Then act on its findings:
  - **critical and high:** run the `dps:security-fixer` agent with those findings, uncommitted, so the fixes land in this ticket's commit. The ticket isn't done until they're fixed and the full suite passes again.
  - **medium:** fix the same way if the fix is small and inside this ticket's files. Otherwise create a follow-up ticket with `/dps:plan-tickets "<finding>"`.
  - **low:** list under the ticket's `## Notes`.
  - **`needs decision`** from the fixer: stop and ask the user.

  Save the audit as `.project/review/<YYYY-MM-DD>-security-<ticket-id>-review.md` (frontmatter `type: review`, no `status`) only if it had findings, recording each finding's outcome. If **Workflow → Security** says the repo is public, describe protections, never a working exploit.
- Tick each acceptance criterion in the ticket only once you've checked it. If one can't be met, leave it unticked and explain why under `## Notes`.

## 4. Commit and record

- **Decisions.** Make sure every decision taken on this ticket has a file in `.project/decisions/`, following CLAUDE.md's **Decision log**. That means the decisions you made building it yourself, the agents' decisions (already written by them), and every choice this command forced:
  - a should-fix or medium finding deferred rather than fixed
  - an acceptance criterion left unmet
  - a file added to `touches`
  - the user's answer to a `needs decision`, logged as `decided_by: user`

  Then add a `## Decisions` list to the ticket linking each file.
- Set `status: done`, bump `updated:`, tick the ticket in `STATUS.md`, and update `INDEX.md`. If the Summary no longer reflects where things stand, run `/dp:project-update`; if that plugin isn't installed, rewrite the first paragraph under `## Summary` yourself and bump `updated:`.
- If this ticket closes the final milestone (usually the README and deploy step), first run `dps:security-auditor` with scope `full`, and handle its findings as in step 3. If the spec's final milestone includes the README, the `dps:readme-writer` agent writes it.
- If this ticket finishes a milestone (no other `todo` tickets share its `milestone:`), first run the `dps:milestone-reviewer` agent. Its suggested commit message wins for the commit that closes the milestone.
- Commit this ticket's files **together with those `.project/` changes, including its decision files**, so the record moves with the code. Describe the change and end the subject with the ticket ID, e.g. `Card list with add and reorder (T-012)`. End the message with the attribution trailer Claude Code currently specifies.
- **Push, if Workflow → Git and deploy says to push after each ticket.** Once the ticket's code and records are committed, run `git push`. If the push is rejected, stop and report. Never force-push, and don't pull or rebase over the rejection. If the repo doesn't push after each ticket, leave the commit local and say so.
- Report what was built, the test results, the commits (and whether they were pushed) and the next ready ticket.

Only the current branch is ever pushed, and only after this step's commits.
