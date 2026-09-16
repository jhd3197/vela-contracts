# Changelog

## Unreleased

### Added

- `widgets`: an optional array of up to four widget declarations an app offers
  the Vela desk. Each is `{ id, name, layout, size }` with `id` matching
  `^[a-z][a-z0-9-]{0,31}$`, `layout` one of `stat`, `progress`, `list` or
  `actions`, and `size` one of `s`, `m` or `l`. The engine additionally requires
  the `widgets` capability alongside the array, and renders the summaries an app
  publishes itself — no app code runs on the desk.

## 0.5.0 - 2026-09-14

### Added

- Manifest v2 JSON Schema for Vela apps.
- Independent GitHub downloads, artifact checks and automatic releases after main updates.
- Contributor, security and funding information with shared changelog instructions.
