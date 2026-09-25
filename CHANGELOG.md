# Changelog

## Unreleased

### Added

- **`companion-v1.schema.json`: companion apps.** A desktop app running on the
  same computer as Vela can register itself by writing
  `~/.vela/companions/<id>.json`: its name, a PNG icon, a loopback endpoint, a
  per-start token, up to four desk widgets (the same declarations as v2) and up
  to eight actions. The host polls the endpoint for widget summaries and calls
  it to run an action, and only after the owner connects it.
  [docs/COMPANIONS.md](docs/COMPANIONS.md) describes the file, the three HTTP
  routes and the security model. The endpoint must be loopback, the icon must be
  a PNG in the same folder, and an action is a title and an optional
  confirmation question, never a command.

- **`view.window`: an app can say what shape its window is.** A v2 manifest
  with an embedded surface may declare `view.window` with `resizable`,
  `maximizable` and a `defaultSize` of `{width, height}` in CSS pixels. A
  calculator that only works at one size can now say so, instead of offering a
  maximize button it cannot honour. Every field is optional and the defaults
  are today's behaviour, so an existing manifest is unaffected. `defaultSize`
  is bounded at 240x160 and 20000x20000, which is the range a host's own window
  geometry accepts, so a declared size cannot be one the desk would refuse.
  Only an embedded surface may declare it: an app that opens outside the host,
  or has no view at all, has no window to describe.

- **`topbar.menus`: an app can declare menus for the host's top bar.** Up to
  four menus, each with a label of at most 24 characters and up to eight items.
  An item's optional `action` is `return` or `close` — a closed set, so a menu
  is something the host knows how to perform rather than a name it has to
  interpret. An item with no action is a label the host draws and does not act
  on. Declaring `topbar` requires the `topbar` capability, which is the host's
  check rather than the schema's; the schema bounds the shape and the counts.

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
