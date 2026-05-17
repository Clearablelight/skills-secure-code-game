# gitlens-tui

**Explore your git history without leaving the terminal.**

A fast, keyboard-driven terminal UI built in Rust for browsing commits, inspecting diffs, and viewing author statistics.

---

## Demo

```
┌─ gitlens-tui — my-project  [Log | Stats] ──────────────────────────────────────┐
│ ┌ Commits [1/42] ──────────────────────────────────────────────────────────┐ │
│ │ Hash   │ Author               │ Time         │ Message                  │ │
│ ├────────┼──────────────────────┼──────────────┼──────────────────────────┤ │
│ │ abc1234│ Alice                │ 2 hours ago  │ fix: null check in parse │ │
│ │ def5678│ Bob                  │ 1 day ago    │ feat: add search feature │ │
│ └────────┴──────────────────────┴──────────────┴──────────────────────────┘ │
│ ┌ Commit Detail ──────────────────────────────────────────────────────────┐  │
│ │ Commit:  abc1234f8a91...                                               │  │
│ │ Author:  Alice <alice@example.com>                                     │  │
│ │ Date:    2024-01-15 14:32:01                                           │  │
│ │ Files changed:                                                         │  │
│ │   src/parser.rs (+42 -8)                                               │  │
│ └───────────────────────────────────────────────────────────────────────┘  │
│ [j/k↑↓] scroll  [g/G] top/bottom  [Tab] switch view  [q/Esc] quit           │
└────────────────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
git clone https://github.com/clearablelight/gitlens-tui
cd gitlens-tui
cargo build --release
# binary at ./target/release/gitlens-tui
```

## Usage

```bash
gitlens-tui                        # current directory
gitlens-tui --path /path/to/repo   # specific repo
```

## Key Bindings

| Key | Action |
|-----|--------|
| `j` / `↓` | Scroll down |
| `k` / `↑` | Scroll up |
| `g` | Jump to top |
| `G` | Jump to bottom |
| `Tab` | Switch Log / Stats view |
| `q` / `Esc` | Quit |

## Why it's fast

- Written in **Rust** — zero GC pauses
- Uses **git2** (libgit2 bindings) — no shelling out to `git`
- All data loaded once at startup; navigation is pure in-memory
- Renders with **ratatui** — only redraws what changes

## License

MIT
