# OrdoStack Draft Edition Product Specification

## 1. Product Summary

OrdoStack Draft Edition is a mobile-first study planning tool for users preparing for graduate exams, machine learning engineer transitions, coding interviews, and portfolio projects.

The product helps users break large learning goals into actionable subitems, estimate effort, assign priority, and generate a focused daily Top 3 task list.

## 2. Target Users

- Students preparing for graduate school exams.
- Early-career candidates preparing for machine learning engineering roles.
- Users balancing coursework, coding practice, English study, and portfolio projects.

## 3. Core Problem

Users often collect tasks in notes, spreadsheets, or generic to-do apps, but still spend too much time deciding what to do first. OrdoStack reduces planning friction by turning major goals into prioritized tasks and highlighting the best actions for today.

## 4. MVP Scope

### Included

- Create custom major items.
- Create custom subitems under each major item.
- Delete major items and subitems.
- Mark subitems complete or incomplete.
- Set estimated minutes and priority per subitem.
- Generate daily Top 3 recommendations.
- Show progress summary by major item.
- Preserve data locally in the browser.
- Provide a PWA manifest and service worker shell for installable web app readiness.

### Excluded

- Native iOS / Android codebase.
- Calendar sync.
- Push notifications.
- Team collaboration.
- Cloud sync.
- AI scheduling.
- Billing and accounts.

## 5. Functional Requirements

| ID | Requirement | Acceptance Criteria |
| --- | --- | --- |
| FR-001 | Create major item | User can add a custom major item such as "Graduate Exam". |
| FR-002 | Create subitem | User can add a subitem under a selected major item. |
| FR-003 | Delete major item | User can delete a major item after confirmation. |
| FR-004 | Delete subitem | User can delete a single subitem without deleting the major item. |
| FR-005 | Complete subitem | User can mark a subitem complete or restore it. |
| FR-006 | Recommend Top 3 | App recommends up to three incomplete subitems using priority and estimated time. |
| FR-007 | Progress summary | App shows completed count, total count, and estimated minutes by major item. |

## 6. UX Copy Rules

- Do not expose implementation terms such as `localStorage`, `No Login`, or internal storage names in the UI.
- Empty states must be product-facing, short, and neutral.
- Labels should describe user intent, not technical behavior.
- Chinese interface copy uses readable system UI fonts.
- English metadata and numeric values may use Consolas-style monospace.

## 7. Release Readiness

- Core logic tests must pass.
- Mobile layout must remain usable below 620px viewport width.
- PWA files must not break direct `file://` usage.
- Sensitive personal data must not be requested in MVP.

## 8. Market Reference Summary

- Todoist validates projects, priorities, sections, and subtasks as core task organization concepts.
- TickTick validates task lists, calendar planning, Pomodoro, habits, and priority-based productivity workflows.
- Clockify validates project-level time tracking and estimated effort as a commercial productivity pattern.
- Lark validates integrated planning, tasks, calendars, and collaboration as a team-productivity direction for later phases.

## 9. Next Release Candidates

- Focus timer for selected subitem.
- Manual sort order for major items and subitems.
- Due date and daily planning view.
- Weekly review screen.
- Import / export data.
- Lightweight tags.
