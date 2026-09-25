# Companion apps

A companion app is a desktop app that already runs on the same computer as
Vela, in its own window, and offers Vela a few things to show and do: desk
widgets, a "needs you" flag and a handful of actions. Nothing is packaged or
installed through Vela. The app registers itself when it starts, the owner
connects it once, and from then on it appears on the desk, in the rail and on
every phone signed in to that Vela.

Companions are for apps you control that run next to Vela. An existing web
service belongs in a managed web app (manifest v3) or a connected website;
something written for Vela belongs in an SDK app (manifest v2).

## How it works

```
 your app                                   Vela
 ────────                                   ────
 starts a loopback HTTP server
 writes ~/.vela/companions/<id>.json   ──►  sees the file, shows "Found on this computer"
                                            owner presses Connect
                                      ◄──   GET  /vela/v1/status        (every few seconds)
                                      ◄──   GET  /vela/v1/widgets       (while online)
                                      ◄──   POST /vela/v1/actions/<id>  (when someone presses a button)
 removes the file on exit              ──►  shows it as offline, keeps its last summaries
```

Vela always calls the app. The app never needs Vela's address, a Vela account
or a Vela credential, and it never listens on anything but loopback.

## 1. The registration file

Write `<vela home>/companions/<id>.json`, where `<vela home>` is the
`VELA_DATA_DIR` environment variable when set and `~/.vela` otherwise. Create the
folder if it is missing. Write to a temporary file in the same folder and rename
it over the old one, so Vela never reads half a file. Remove the file when the
app exits.

The file is validated against
[`companion-v1.schema.json`](../companion-v1.schema.json):

```json
{
  "companion": 1,
  "id": "prompture-desk",
  "name": "Prompture Desk",
  "description": "AI usage and coding-agent automations.",
  "version": "0.4.0",
  "color": "#8b7ff6",
  "icon": "prompture-desk.png",
  "endpoint": "http://127.0.0.1:53211",
  "token": "q2oV1YwJmSgHkq8H1mZtV6z4B0Jf3r9WcXnL7pEaUuA",
  "pid": 18244,
  "executable": "C:\\Program Files\\Prompture Desk\\prompture-desk.exe",
  "widgets": [
    {"id": "today", "name": "Today", "layout": "stat", "size": "s"}
  ],
  "actions": [
    {"id": "pause", "title": "Pause automation"},
    {"id": "stop", "title": "Stop automation", "confirm": "Stop the running automation?"}
  ]
}
```

| Field | Meaning |
| --- | --- |
| `companion` | Always `1` for this version. |
| `id` | Stable identity and the file's name. Keep it forever: changing it makes a different companion. |
| `name`, `description`, `version`, `color` | Shown in Vela. Updated whenever the file changes, without asking the owner again. |
| `icon` | A PNG in the same folder, named by file name only, at most 256 KB. Copied when the owner connects. |
| `endpoint` | `http://127.0.0.1:<port>`, `http://localhost:<port>` or `http://[::1]:<port>`. Nothing else is accepted. |
| `token` | At least 32 random URL-safe characters, new on every start. Vela sends it on every request. |
| `pid` | The app's process id. A file whose process has exited is treated as not running. |
| `executable` | The app's program. Shown when connecting and used by **Start on this computer**. |
| `widgets` | Up to four desk widgets, the same declarations a v2 manifest uses. |
| `actions` | Up to eight buttons. Each has an `id`, a `title`, an optional `description` and an optional `confirm` question. |

The owner reviews `executable`, `widgets` and `actions` when connecting. If any
of them changes later, Vela stops polling the companion and asks the owner to
review the change before it trusts the new declarations. The other fields can
change freely.

## 2. The HTTP endpoint

Every request carries `Authorization: Bearer <token>`. Refuse any request
without the current token with `401`, and compare it in constant time. Answer
with JSON. Keep answers under 64 KB and answer within five seconds. Vela does
not follow redirects.

### `GET /vela/v1/status`

```json
{"id": "prompture-desk"}
```

This is how Vela tells the app is online. The `id` must match the registration.
Vela checks it every few seconds.

### `GET /vela/v1/widgets`

```json
{
  "widgets": {
    "today": {"value": "$4.12", "caption": "18 calls today", "attention": false}
  }
}
```

One summary per declared widget id, in exactly the format an SDK app publishes
with `Vela.widgets.publish`: `value`, `unit`, `delta`, `caption`, `progress`,
`series`, `domain`, `rows`, `actions`, `attention`, `badge` and `expiresAt`, at
most 4 KB each. A widget left out keeps its previous summary. An id that was
not declared is ignored.

`attention: true` puts a dot on the app's rail icon and lists it under **Needs
you**. Set it only when something is waiting for the person.

A summary's `actions` entries (`{"action": "<id>", "label": "..."}`) must name
the companion's own declared actions. Vela draws them as buttons on the widget
and runs the action when one is pressed.

### `POST /vela/v1/actions/<action id>`

The body is `{}`. Answer `200` with an optional message:

```json
{"message": "Paused after the current step."}
```

Answer `4xx` or `5xx` with `{"error": "Nothing is running."}` when the action
cannot be done. The message is shown to the person who pressed the button.
Vela waits ten seconds for an answer. An action that takes longer should start
the work and answer straight away.

Vela asks for a fresh `/vela/v1/widgets` right after an action succeeds, so the
widget shows the result.

## 3. Security

- Vela reads the companions folder of the user it runs as, which any program
  that user runs can also write. Nothing a registration says is trusted until
  the owner connects it, and the review shows the executable path.
- The token keeps other local programs from using the app's endpoint. It proves
  nothing about Vela to anyone else, and Vela never shows it or sends it
  anywhere but the registered loopback endpoint.
- A companion gets no Vela credential, no app storage, no SDK session and no
  agent access. It cannot call Vela at all.
- Everything a companion sends is data that Vela checks and draws itself. Text
  is shown as text.
- Removing a companion in Vela forgets the connection and its summaries. If the
  app is still running, it is listed under **Found on this computer** again,
  and connecting it asks the owner again.
