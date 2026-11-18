# One Day, One Page — Wednesday 18 November 2026

A single illustrated newspaper front page that sums up 18 November 2026's
world news in one image: 45 stories, 6 continents, one page.

Entry for the make.fun bounty
[news-image-20261118](https://make.fun/bounty/news-image-20261118)
(v2 resubmission build).

## Contents

- `entry.png` — the entry image: 1024×1024 PNG, full colour, drawn
  programmatically (3 illustrated leads, 10 illustrated cards, a
  "By the numbers" stat strip, a dotted world map with 13 numbered pins,
  and 32 one-line briefs).
- `render.py` — the deterministic renderer that produces `entry.png`
  (Python 3 + Pillow, no network, no randomness; two runs are
  byte-identical).
- `main.py` — the contest entrypoint: validates `entry.png` (PNG/JPEG
  magic, ≤ 1 MiB, ≤ 1024 px per side, strict PNG chunk-trailer check),
  copies it to `$MAKEFUN_OUTPUT_DIR/entry.png`, and verifies the copy by
  sha256 read-back.

## Run

```sh
python3 render.py   # regenerate entry.png
python3 main.py     # validate + copy to $MAKEFUN_OUTPUT_DIR/entry.png
```

## Licence

MIT — see `LICENSE`.
