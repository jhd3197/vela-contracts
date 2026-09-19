# Changelog

## Unreleased

### Added

- `manifest-v3.schema.json`: a separate manifest version for **managed web
  apps** — existing self-hosted web servers that a host installs, runs as a
  local native service and publishes on their own web address. A v3 manifest
  declares its upstream source and licence, per-OS *and* per-architecture
  release artifacts pinned by SHA-256 and exact size (there is no combined
  `posix` target), an explicit argument vector with a bounded set of
  placeholders instead of a shell string, a loopback HTTP endpoint, an HTTP
  readiness probe, restart and graceful-stop policy, and one relative
  persistent data directory. `service.trust` accepts only `trusted-native`,
  which says the executable runs with the host user's own operating-system
  permissions rather than inside a sandbox. Install, migration and repair hooks
  are not expressible, and `integration.sdk`/`integration.agent` can only be
  `false`: installing a managed app grants no bridge, storage, action, widget
  or agent access. v1 and v2 manifests are untouched, and a host that does not
  implement `compatibility.managedService` refuses a v3 package rather than
  ignoring what it cannot honour. That field is a bounded integer rather than
  a constant, so the refusal comes from the host and names the revision it
  does implement instead of arriving as a schema error. `service.lifetime` is
  optional: every field in it has a default.
- `view.appearance`: an optional hint, one of `light`, `dark` or `auto`
  (default `auto`), for the theme Vela should draw an embedded app's window
  chrome in. `auto` follows the hub theme; `dark` keeps the app's title bar dark
  even under a light hub so a dark app does not sit beneath a light strip. It
  does not change the `theme` the host reports to the app.
- `widgets`: an optional array of up to four widget declarations an app offers
  the Vela desk. Each is `{ id, name, layout, size }` with `id` matching
  `^[a-z][a-z0-9-]{0,31}$`, `layout` one of `stat`, `progress`, `list`,
  `actions`, `chart` or `keyvalue`, and `size` one of `s`, `m` or `l`.
  A `chart` widget publishes a `series` of between two and twenty-four finite
  numbers, optionally with a `domain` of `[min, max]` to read them against; a
  `keyvalue` widget publishes `rows` and is drawn as label left, value right.
  The engine additionally requires the `widgets` capability alongside the array,
  and renders the summaries an app publishes itself — no app code runs on the
  desk.

## 0.5.0 - 2026-09-14

### Added

- Manifest v2 JSON Schema for Vela apps.
- Independent GitHub downloads, artifact checks and automatic releases after main updates.
- Contributor, security and funding information with shared changelog instructions.
