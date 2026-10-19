# Jungxt API

The Urban Dictionary for texting — as a JSON API. Free for non-commercial use.
For commercial licensing, contact **Zukitnerd@gmail.com**.

## Quick start

```bash
python3 server.py          # runs on http://localhost:8000/
python3 server.py 8080     # custom port
```

No dependencies. Python 3.8+.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/definitions` | All entries. Query params: `q` (search), `cat` (category), `limit`, `sort` (`top`\|`new`\|`az`) |
| GET | `/api/definition/{term}` | Single entry, e.g. `/api/definition/sven` |
| GET | `/api/random` | Random entry |
| GET | `/api/word-of-day` | Today's featured entry (stable per date) |
| GET | `/api/categories` | List of categories |
| GET | `/` | Human-readable docs page |

## Example

```bash
$ curl localhost:8000/api/definition/sven
{
  "term": "sven",
  "pronunciation": "...",
  "part_of_speech": "noun",
  "category": "Sleepy Text",
  "definition": "...",
  "meant_to_type": "...",
  "example_thread": [{"from": "them", "text": "..."}],
  "coined_by": "@thefounder",
  "votes": 318
}
```

## Data

`definitions.json` holds every entry. Add new ones there following the same shape —
`term`, `pron`, `pos`, `cat`, `def`, `meant`, `ex` (list of `[who, text]` pairs),
`by`, `votes` — and restart the server.
