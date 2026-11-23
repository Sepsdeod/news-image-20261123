# The World in One Day — Monday 23 November 2026

[![news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123)

A single 1024x1024 poster that sums up Monday 23 November 2026 in five
stories. It is laid out like a broadsheet front page: a masthead naming
the day, then five stacked bands, one per story, each with a coloured
spine, a kicker, a headline, a short factual body, and a small pictogram.

## The five stories

1. **Labour, Germany** — IG Metall calls a 24-hour strike for Monday:
   about 23,000 workers at 19 firms in northern Germany walk out in a
   pay dispute.
2. **Diplomacy, New Delhi** — Nepal's prime minister Balendra Shah holds
   delegation-level talks with Narendra Modi on his first bilateral trip
   abroad as PM.
3. **Disaster, Java, Indonesia** — The search resumes at 07:00 Monday at
   the PT Fonusa Agung Mulia candy factory in Cikande, Serang, after
   Saturday's fire left about 37 workers unaccounted for.
4. **Sport, Wellington** — Day five of the first Test at the Basin
   Reserve: New Zealand 157 for 4 at lunch, battling to save the match
   after India declared on a record 720 for 9.
5. **Diplomacy, Singapore** — China's vice-premier Ding Xuexiang is on
   the second day of his two-day visit for talks with Singapore's
   leaders.

Every story happened, or was first reported, on 23 November 2026.

## How it is made

`draw.py` renders the poster from scratch with the Python standard
library only: a small 5x7 bitmap font, a pixel buffer, and a hand-written
PNG encoder. Nothing is downloaded and nothing is read from disk at
draw time. Each story band carries a small flat pictogram on its right
edge — a placard, two flags, a flame, a cricket bat and ball, and a
columned building — drawn from rectangles, triangles and discs.
`main.py` first checks that `entry.png` is a real PNG under the 1 MiB
limit, then copies it into the output directory the grader provides.

## How to run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

To re-render the poster from the drawing code first:

```sh
python3 draw.py && mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The output is deterministic: running it twice produces byte-identical
`entry.png` files. You can check that yourself:

```sh
mkdir -p /tmp/a /tmp/b
MAKEFUN_OUTPUT_DIR=/tmp/a python3 main.py
MAKEFUN_OUTPUT_DIR=/tmp/b python3 main.py
cmp /tmp/a/entry.png /tmp/b/entry.png && echo identical
```

The finished poster is 1024x1024 pixels and well under the 1 MiB cap.
