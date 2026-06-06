# OrdoStack Draft Edition Release Checklist

## Product

- [x] Product-facing name is shown.
- [x] Internal implementation hints are removed from visible UI.
- [x] Major item and subitem workflow is available.
- [x] Daily Top 3 recommendation is available.
- [x] Progress summary is available.
- [ ] Customer-facing onboarding copy is finalized.
- [ ] Visual QA completed on desktop and mobile.

## Engineering

- [x] Core logic is separated in `app/core.js`.
- [x] UI behavior is separated in `app/browser.js`.
- [x] Static web app runs without installing dependencies.
- [x] PWA manifest exists.
- [x] Service worker exists and is disabled for `file://` usage.
- [x] Core tests pass through Node REPL MCP.
- [ ] Browser interaction test completed with a real browser automation tool.

## Documentation

- [x] Product specification exists.
- [x] Release checklist exists.
- [x] Memory Bank updated.
- [ ] Customer demo script exists.
- [ ] API specification is not required for current static MVP.

## Known Limits

- No native mobile app codebase yet.
- No account system or cloud sync.
- No calendar integration.
- No push notification.
- No team collaboration.
