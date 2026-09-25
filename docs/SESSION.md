# Mentor Session Runbook (40 min)

Goal: every mentor leaves with the repo reading data from Box, having played a student for one week, and having run `/clinic-project-review` on the result.

Before the session (facilitator): Box folder `dsi-core/clinic/2026-sample` shared with all mentors as Editor; mentors added to this repo with Write; seed roles run and a sample review generated (both kept out of this repo, in `dsi-rse/clinic-automation` under `training/`, so the review can't read them).

## 0–5 · The week
Walk through [WEEKLY_FLOW.md](WEEKLY_FLOW.md). Point at the escalation page.

## 5–12 · Setup check
```bash
claude plugin marketplace add dsi-rse/skills
claude plugin install dsi-rse-skills@dsi-rse     # already installed? claude plugin update dsi-rse-skills@dsi-rse
gh auth status
git clone https://github.com/dsi-rse/clinic-2026-sample ~/clinic/clinic-2026-sample
cd ~/clinic/clinic-2026-sample
cp .env.example .env        # WSL: switch to the /mnt/Box line
make check-data             # uses uv if installed, else Docker; writes output/<you>-sync-test.txt
```
Check that your sync-test file shows up in the Box web app. If `make check-data` fails, pair with a neighbor and follow [box-wsl](https://clinic.ds.uchicago.edu/tutorials/box-wsl.html) afterward.

## 12–25 · Play student (tables of 3)
1. One person at the table plays mentor and **tells** each tablemate a task, out loud, with acceptance criteria. Ideas (each in its own new file under `src/utils/` to avoid merge conflicts):
   - median days to close a request, by service type (`creation_date`, `completion_date`)
   - share of requests still open, by community area
   - requests per month for one service type
2. Each person opens their own issue: **Issues → New issue → Weekly tasks**. Title `Week 3 tasks – <name>`.
3. `git switch -c <login>/<task>`, no `[student:…]` tag needed (you're playing yourself; tags are only for the seeded students), make the change (Claude Code is fine), push, open a PR linked to your issue.
4. On github.com, post your weekly report as a comment on your issue.
5. One person per table under-delivers on purpose: claim `complete` without a PR, or leave the criteria vague.

## 25–37 · Be the mentor
In `~/clinic/clinic-2026-sample`, start `claude` and run:
```
/clinic-project-review
```
Intake answers: review window = last 7 days · roster = your two tablemates plus the seeded students A, B, C (read from `[student:…]` tags; the skill switches to training mode for `clinic-YYYY-sample` repos) · 10 hours/week · history = 1 week · report path `~/clinic/review-<you>.md` · run the code? **No, read-only** (running it adds 15–30 min; try it after the session).

Read the per-student checks, especially whether each report matches the PRs and commits, then the task menu. Those are tasks you would **tell** students next week; they open the issues.

If the skill is slow, the facilitator shares the pre-generated sample review on screen.

## 37–40 · Wrap
- The skill sees GitHub only. Give it Box/Slack/meeting context at intake.
- Its report is evidence for your grade, not the grade.
- Next: set up your real project's Box folder `dsi-core/clinic/<slug>` using [PROJECT_SETUP.md](../PROJECT_SETUP.md).
