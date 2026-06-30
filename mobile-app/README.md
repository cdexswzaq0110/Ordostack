# Mobile App Decision

Status: planned module, not shipped in this beta.

The web dashboard already covers the end-to-end planner workflow. A second client would add authentication storage, release, accessibility, offline sync, and app-store maintenance before beta demand is proven, so the minimum credible beta keeps mobile documented rather than shipping a placeholder client.

## Target User Flows

1. Sign in to the existing backend API.
2. View today's generated plan and fixed events.
3. Start, pause, complete, skip, or reopen a task.
4. Review schedule changes and execution progress.

Task authoring, schedule generation settings, analytics administration, model operations, and account recovery remain web-first until mobile usage is validated.

## Planned Screens

- Sign in.
- Today plan.
- Task detail with execution controls.
- Schedule history read-only view.
- Profile and sign out.

## API Dependency

The client must call `backend-api` only. It must not call MySQL, scheduler-service, or ml-service directly. Required contracts already exist under `/api/auth`, `/api/tasks`, `/api/task-execution-logs`, and `/api/schedules` and are documented in `docs/api.md`.

## Future Architecture

Use React Native with Expo and TypeScript only when implementation starts. Keep API types generated or shared from the documented backend contract, store tokens in platform secure storage, and treat offline mutation sync as a later feature rather than silently queuing writes.

## Implementation Roadmap

1. Validate mobile demand with private-beta users.
2. Confirm hosted auth session and token-storage design.
3. Build read-only Today and schedule history screens.
4. Add task execution mutations with error and retry states.
5. Run accessibility, device, offline, and release-channel QA.

No app-store release, push notification, background sync, or offline-write claim is made by the current repository.

