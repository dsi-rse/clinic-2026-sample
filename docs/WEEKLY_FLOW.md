# The Clinic Week

Every week runs from one mentor session to the next, and all of it is tracked on GitHub.
This page summarizes the [weekly plan](https://clinic.ds.uchicago.edu/syllabus/weekly-plan.html); the clinic site is the source of truth.

```
 Mentor session ──► Students open ──► TA sessions x2 ──► Students post ──► Mentor runs ──► Mentor session
 (mentor assigns    weekly-tasks      PRs + TA review    weekly report     /clinic-project-  (next week)
  tasks out loud)   issue by midnight                    comment on the    review, grades
                    + Slack link                         issue, by midnight 0-5 + 0-5
                                                         the day before
```

## Who does what

| When | Mentor | Student | TA |
|---|---|---|---|
| Mentor session | Runs the meeting ([how to](https://clinic.ds.uchicago.edu/mentor-ta/how-to-run-a-meeting.html)): updates, discussion, then **tells** each student their task with acceptance criteria. One student per task. | Gives a ~2 minute update; restates their new task. | Attends. |
| Midnight, same day | | **Opens the weekly-tasks issue** (New issue → *Weekly tasks*) and posts the link in Slack. | |
| During the week | Answers Slack; escalates problems early. | Attends both TA sessions, pushes code to a PR, responds to review. | Runs two sessions, reviews PRs with `/clinic-pr-review`, checks students are pushing. |
| Midnight, day before next session | | Posts the **weekly report as a comment on that issue** (on github.com), with a status per criterion and PR links. | |
| Before next session | Runs `/clinic-project-review`, reads the report comments and open PRs, decides next week's tasks, grades weekly tasks (0-5) and weekly report (0-5) on Canvas. | | |

Grading: [weekly tasks rubric](https://clinic.ds.uchicago.edu/rubrics/weekly-tasks-rubric.html), [weekly report rubric](https://clinic.ds.uchicago.edu/rubrics/weekly-report-rubric.html). No pushed code on a code task means a 0 for the week.

## When things go wrong

See [escalation and common failure modes](https://clinic.ds.uchicago.edu/mentor-ta/escalation.html). The most common: the same task repeats week after week. That is a task-sizing problem; write smaller tasks with checkable criteria and ask for help at the mentor meetings.

## What `/clinic-project-review` can and can't see

It reads GitHub only: issues, issue comments, PRs, commits. It can't see Box, Slack, or your meetings, so tell it about that context when it asks. Its report is evidence for your grade, not the grade.
