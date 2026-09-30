# Surfaces

A surface is a screen described as data. The producer sends a JSON tree of
components (panels, stats, tables, small desktops). The host draws it with its
own components. No producer code runs in the viewer, and the host never fetches
anything the surface names.

`surface-v1.schema.json` is the format. This page covers what the schema cannot
say.

## Who produces one

Anything that can answer an HTTP request with JSON: a remote server panel
(ServerKit's Agent GUI extension describes a managed server as a surface), a
companion app, a Vela app. How the host reaches the producer is not part of
this format. A Vela host uses a connection or companion endpoint it already
trusts.

## Shape

```json
{
  "surface": 1,
  "title": "web-01",
  "refresh": { "every": 4 },
  "actions": [{ "id": "restart-service", "title": "Restart service", "danger": true }],
  "root": {
    "type": "desktop",
    "wallpaper": "dusk",
    "windows": [
      { "type": "window", "id": "services", "title": "Services", "children": [
        { "type": "table", "columns": [{ "key": "name", "label": "Service" }], "rows": [{ "name": "nginx" }] },
        { "type": "button", "label": "Restart nginx", "action": "restart-service", "input": { "service": "nginx" } }
      ]}
    ],
    "dock": [{ "label": "nginx", "window": "services" }]
  }
}
```

`root` is one node. Every node has a `type`.

| Kind | Types |
| --- | --- |
| Containers | `stack`, `grid`, `panel`, `desktop` (with `window` children and a `dock`) |
| Values | `text`, `stat`, `progress`, `keyvalue`, `chart`, `table`, `list`, `badge` |
| Other | `button`, `image`, `divider`, `empty` |

`stat`, `progress`, `list`, `chart` and `keyvalue` use the same drawings as the
desk's widget layouts, so a host can use one component for both.

## Limits the host enforces

The schema bounds each field. The host also enforces these, which the schema
cannot express:

- **At most 1 MB** for the whole document. A capture in an `image` is the only
  thing that should come close.
- **At most 1,000 nodes and eight levels of nesting.** A deeper tree is
  refused, not trimmed.
- **A `button` names a declared action.** An `action` that is not in the
  surface's `actions` is refused.
- **`dockItem.window` names a window in the same desktop.** Otherwise the dock
  item is drawn without the link.
- **`refresh.every` is a floor.** The host may poll less often, never more.

A host that refuses a surface shows that it could not draw it. It does not draw
the part that did validate.

## Text and values

- **Text is plain.** Nothing is parsed as markup, links or Markdown.
- **The producer writes text in its own language** and says which in `lang`.
- **The host formats values** (numbers, percentages, bytes, durations, times)
  for the viewer's locale, following the `format` on a stat, key/value row or
  table column. Send raw values, not formatted strings, wherever a `format`
  applies.

## Actions

An action is a title, an optional confirmation question and a `danger` flag,
never a command. A `button` asks the host to run one, with up to eight flat
`input` values. The host decides:

- whether this viewer may run it at all;
- whether to ask first (always for `danger`, and whenever `confirm` is set);
- how to deliver it to the producer.

The surface cannot skip any of these. Delivery is the producer's own protocol
(ServerKit: a POST to the extension's action route), not this format's.

## Desktops

A `desktop` is windows on a named wallpaper preset with a dock. Window `size`
is a hint (`s`, `m`, `l`, `wide`, `tall`). The host lays the windows out and
may let the viewer move, minimize and restore them. Those positions belong to
the viewer, and the host keeps them across refreshes by window `id`. A surface
cannot place or focus a window.

## Versioning

`surface` is `1`. New optional node types or fields can be added within v1, and
a host draws an unknown node type as "cannot show this part" rather than
refusing the whole document. Removing or changing the meaning of anything is a
new version. A host that does not know the version shows that instead of
guessing.
