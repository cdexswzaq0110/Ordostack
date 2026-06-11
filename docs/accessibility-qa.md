# Manual Accessibility QA

Issue 52 adds the manual accessibility QA baseline for the dashboard MVP.

## Scope

This checklist covers the customer demo dashboard, authentication panel, task queue, fixed events, generated schedule timeline, schedule history, export controls, and language switcher.

This is not a formal third-party accessibility audit. It is the minimum manual gate before a private beta demo.

## Keyboard Checks

1. Open the dashboard.
2. Use `Tab` and `Shift+Tab` from the browser address bar through the full application.
3. Confirm every interactive control has a visible focus indicator.
4. Confirm tab order follows the visual order: navigation, date controls, account controls, filters, task actions, schedule actions, timeline actions.
5. Confirm `Enter` or `Space` activates buttons.
6. Confirm disabled buttons are skipped or announced as disabled.
7. Confirm the language switcher can be reached and changed by keyboard.

## Screen Reader Checks

1. Confirm top-level navigation has a readable label.
2. Confirm auth mode tabs expose selected state.
3. Confirm icon-only buttons have accessible names.
4. Confirm schedule item lock and move controls announce the intended action.
5. Confirm status messages are readable after login, logout, failed login, schedule export, and mutation errors.
6. Confirm empty states explain what changed without requiring visual-only context.

## Contrast Checks

1. Confirm primary text, secondary text, inputs, borders, and focus outlines remain visible on white backgrounds.
2. Confirm disabled controls still look disabled without becoming unreadable.
3. Confirm timeline labels remain legible for focus blocks, protected blocks, and manual override labels.
4. Confirm Traditional Chinese text does not clip inside buttons or compact labels.

## Responsive Checks

1. Check desktop width near `1440px`.
2. Check tablet width near `900px`.
3. Check mobile width near `390px`.
4. Confirm auth controls wrap without overlapping search or language controls.
5. Confirm timeline action buttons do not cover schedule item text.
6. Confirm task rows, fixed event rows, and schedule history actions stay readable.

## Exit Criteria

- Static a11y audit passes.
- Manual keyboard pass has no blocking issue.
- Manual screen reader pass has no blocking issue.
- No text overlap is visible in English or Traditional Chinese at tested widths.
- Any remaining non-blocking issue is documented in `docs/project-status-report.md`.
