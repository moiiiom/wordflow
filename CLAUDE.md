# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WordFlow is a static, single-file vocabulary memorization web app. No build tools, no dependencies, no Node.js. Everything lives in `index.html` with embedded CSS and JS.

## Running Locally

```bash
python3 -m http.server 8080
# open http://localhost:8080
```

Must be served over HTTP — `fetch('data/words.csv')` fails with `file://` protocol.

## Architecture

- **`index.html`** — the entire app (HTML + CSS + JS in one file)
- **`data/words.csv`** — data source, fetched at runtime; two columns: `Vocabulary`, `Notes`

### Key JS globals
| Variable | Purpose |
|---|---|
| `words` | Array of `{word, notes}` parsed from CSV |
| `colors` | Object mapping word → color, persisted in localStorage key `wordflow_colors` |
| `indices` | Array of indices into `words`, reordered for shuffle mode |
| `currentPos` | Current position in `indices` |
| `mode` | `'flash'` or `'gallery'` |
| `galleryFilter` | `'all'` \| `'gray'` \| `'red'` \| `'yellow'` \| `'green'` |

### Two modes
- **Flashcard** (`#flashcard-view`): single card, click to flip, `←`/`→` to navigate, color dots to mark
- **Gallery** (`#gallery-view`): CSS grid of all words, filter bar by color, click tile → jumps to that card in flashcard mode

### Color system
Four states stored per word: `gray` (default), `red`, `yellow`, `green`. CSS variables `--color-*` define backgrounds; `--color-*-dot` define dot colors.

### CSV parser
Hand-written RFC 4180 parser (`parseCSV`) handles quoted multi-line fields and escaped quotes. Notes are HTML-stripped via `div.textContent` after setting `innerHTML`.
