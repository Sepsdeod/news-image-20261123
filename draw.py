#!/usr/bin/env python3
"""Draw the news poster for Monday 23 November 2026.

Renders a 1024x1024 newspaper front page: one wide lead story (the
IG Metall strike in Germany) above a 2x2 grid of four more stories
(Nepal-India talks, the Java factory fire, the Wellington Test final day,
and China's vice-premier in Singapore). Every pictogram is drawn from
scratch with Pillow primitives: no photos, no copied images, no network,
no randomness, no timestamps -- so repeated runs produce byte-identical
PNG output.

Run:  python3 draw.py   (writes entry.png next to this file)
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = 1024
H = 1024

PAPER = (247, 243, 235)
TEAL = (13, 71, 80)
TEAL_DARK = (9, 52, 59)
RED = (178, 34, 34)
GOLD = (198, 160, 40)
INK = (30, 30, 30)
GREY = (96, 96, 92)
WHITE = (255, 255, 255)
PANEL = (255, 255, 255)
SKY = (168, 208, 224)
ORANGE = (232, 116, 28)
GREEN = (46, 125, 50)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines = []
    for raw in text.split("\n"):
        words = raw.split(" ")
        cur = ""
        for word in words:
            trial = (cur + " " + word).strip()
            if draw.textlength(trial, font=fnt) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, color, max_w, leading=None):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def panel(draw, box, border=TEAL, width=3):
    """A white story panel with a teal frame."""
    draw.rectangle(box, fill=PANEL, outline=border, width=width)


def kicker(draw, x, y, text):
    """Small red uppercase section label with a short rule after it."""
    fnt = font(SANS_B, 18)
    draw.text((x, y), text, font=fnt, fill=RED)
    tw = draw.textlength(text, font=fnt)
    draw.line([(x + tw + 10, y + 9), (x + tw + 42, y + 9)], fill=RED, width=3)
    return y + 28


def headline(draw, x, y, text, size, max_w, color=INK):
    """Bold serif headline, wrapped; returns y below it."""
    fnt = font(SERIF_B, size)
    return draw_wrapped(draw, x, y, text, fnt, color, max_w,
                         leading=int(size * 1.12))


def deck(draw, x, y, text, size, max_w, color=GREY):
    """Small sans-serif deck text; returns y below it."""
    fnt = font(SANS, size)
    return draw_wrapped(draw, x, y, text, fnt, color, max_w,
                         leading=int(size * 1.35))


# ---------------------------------------------------------------- pictograms
# Each draws a small flat illustration inside the given box (x0, y0, x1, y1).

def pic_factory(draw, box):
    """IG Metall: chimney, sawtooth factory and a big gear."""
    x0, y0, x1, y1 = box
    base = y1 - 8
    # tall chimney on the left, with a puff of smoke
    draw.rectangle([x0 + 8, y0 + 26, x0 + 30, base], fill=TEAL_DARK, outline=TEAL)
    draw.ellipse([x0 + 2, y0 + 2, x0 + 24, y0 + 24], fill=GREY)
    draw.ellipse([x0 + 22, y0 - 2, x0 + 44, y0 + 20], fill=GREY)
    # sawtooth factory body
    draw.polygon([(x0 + 34, base), (x0 + 34, base - 66),
                  (x0 + 78, base - 96), (x0 + 122, base - 66),
                  (x0 + 166, base - 96), (x0 + 210, base - 66),
                  (x0 + 210, base)],
                 fill=TEAL, outline=TEAL_DARK)
    for wx in (52, 96, 140):
        draw.rectangle([x0 + wx, base - 40, x0 + wx + 24, base - 14],
                       fill=GOLD)
    # gear on the right, overlapping the roof
    gx, gy, gr = x1 - 44, y0 + 44, 30
    for a in range(0, 360, 45):
        x = gx + int(gr * 1.4 * math.cos(math.radians(a)))
        y = gy + int(gr * 1.4 * math.sin(math.radians(a)))
        draw.rectangle([x - 8, y - 8, x + 8, y + 8], fill=GOLD, outline=TEAL_DARK)
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=GOLD,
                 outline=TEAL_DARK, width=3)
    draw.ellipse([gx - 11, gy - 11, gx + 11, gy + 11], fill=PAPER,
                 outline=TEAL_DARK, width=3)


def pic_flags(draw, box):
    """Nepal-India: the two flags side by side on poles."""
    x0, y0, x1, y1 = box
    # poles
    draw.line([(x0 + 30, y0 + 6), (x0 + 30, y1 - 6)], fill=TEAL_DARK, width=4)
    draw.line([(x0 + 250, y0 + 6), (x0 + 250, y1 - 6)], fill=TEAL_DARK, width=4)
    # India tricolour, hanging from the left pole
    ix, iy, iw, ih = x0 + 34, y0 + 10, 190, 96
    draw.rectangle([ix, iy, ix + iw, iy + ih // 3], fill=(255, 153, 51))
    draw.rectangle([ix, iy + ih // 3, ix + iw, iy + 2 * ih // 3], fill=WHITE)
    draw.rectangle([ix, iy + 2 * ih // 3, ix + iw, iy + ih], fill=(19, 136, 8))
    cx, cy = ix + iw // 2, iy + ih // 2
    draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], outline=TEAL_DARK, width=3)
    for a in range(0, 360, 30):
        x2 = cx + int(14 * math.cos(math.radians(a)))
        y2 = cy + int(14 * math.sin(math.radians(a)))
        draw.line([(cx, cy), (x2, y2)], fill=TEAL_DARK, width=1)
    # Nepal double pennant, hanging from the right pole
    nx, ny = x0 + 254, y0 + 10
    draw.polygon([(nx, ny), (nx + 84, ny + 34), (nx, ny + 68),
                  (nx + 34, ny + 68), (nx + 84, ny + 96), (nx, ny + 96)],
                 fill=(220, 20, 60), outline=TEAL_DARK)
    draw.polygon([(nx + 10, ny + 12), (nx + 62, ny + 34), (nx + 10, ny + 56),
                  (nx + 30, ny + 56), (nx + 62, ny + 78), (nx + 10, ny + 84)],
                 fill=WHITE)
    draw.ellipse([nx + 16, ny + 20, nx + 28, ny + 32], fill=(220, 20, 60))
    draw.ellipse([nx + 16, ny + 58, nx + 28, ny + 70], fill=(220, 20, 60))


def pic_flame(draw, box):
    """Java fire: a flame over a small factory outline, with a search beam."""
    x0, y0, x1, y1 = box
    base = y1 - 8
    # factory outline, dark against the smoke
    draw.rectangle([x0 + 20, base - 56, x0 + 150, base], fill=TEAL_DARK)
    draw.rectangle([x0 + 120, base - 84, x0 + 142, base - 56], fill=TEAL_DARK)
    for wx in (36, 70, 104):
        draw.rectangle([x0 + wx, base - 40, x0 + wx + 16, base - 18],
                       fill=GOLD)
    # flame rising from the roof
    cx = x0 + 85
    draw.polygon([(cx - 52, base - 52), (cx - 40, base - 108),
                  (cx - 8, base - 92), (cx + 6, base - 138),
                  (cx + 26, base - 96), (cx + 52, base - 110),
                  (cx + 48, base - 52)],
                 fill=ORANGE, outline=RED)
    draw.polygon([(cx - 22, base - 52), (cx - 12, base - 92),
                  (cx + 4, base - 84), (cx + 14, base - 108),
                  (cx + 22, base - 52)],
                 fill=GOLD)
    # search beam from the right
    draw.polygon([(x1 - 10, y0 + 10), (x1 - 90, y0 + 60), (x1 - 70, y0 + 84),
                  (x1 - 6, y0 + 34)], fill=(255, 236, 160))
    draw.ellipse([x1 - 34, y0 + 2, x1 - 6, y0 + 30], fill=GOLD,
                 outline=TEAL_DARK, width=2)


def pic_cricket(draw, box):
    """Wellington Test: bat, ball and stumps on a green strip."""
    x0, y0, x1, y1 = box
    base = y1 - 8
    draw.rectangle([x0 + 8, base - 10, x1 - 8, base], fill=GREEN)
    # red ball, top left
    bx, by = x0 + 52, y0 + 42
    draw.ellipse([bx - 24, by - 24, bx + 24, by + 24], fill=RED,
                 outline=TEAL_DARK, width=3)
    draw.arc([bx - 17, by - 17, bx + 17, by + 17], 30, 210, fill=WHITE, width=3)
    # bat, leaning across the middle
    draw.polygon([(x0 + 150, y0 + 4), (x0 + 182, y0 + 14),
                  (x0 + 156, base - 16), (x0 + 130, base - 22)],
                 fill=(222, 184, 135), outline=TEAL_DARK)
    draw.rectangle([x0 + 158, y0 - 2, x0 + 170, y0 + 16],
                   fill=(222, 184, 135), outline=TEAL_DARK)
    # stumps on the right
    cx = x1 - 70
    for dx in (-22, 0, 22):
        draw.rectangle([cx + dx - 6, base - 62, cx + dx + 6, base - 10],
                       fill=(232, 190, 90), outline=TEAL_DARK, width=2)
    draw.rectangle([cx - 28, base - 70, cx + 28, base - 62], fill=TEAL_DARK)


def pic_skyline(draw, box):
    """Singapore: towers, sun and harbour water."""
    x0, y0, x1, y1 = box
    base = y1 - 14
    # sun, top right
    draw.ellipse([x1 - 84, y0 + 8, x1 - 24, y0 + 68], fill=GOLD,
                 outline=TEAL_DARK, width=2)
    # three towers of different heights
    towers = [(0, 92, 64), (72, 118, 64), (144, 78, 64)]
    for dx, hgt, wdt in towers:
        tx = x0 + 16 + dx
        draw.rectangle([tx, base - hgt, tx + wdt, base], fill=TEAL,
                       outline=TEAL_DARK)
        for wy in range(base - hgt + 16, base - 10, 26):
            for wx in range(tx + 12, tx + wdt - 10, 20):
                draw.rectangle([wx, wy, wx + 9, wy + 11], fill=GOLD)
    # a low dome between the towers
    draw.pieslice([x0 + 216, base - 34, x0 + 276, base], 180, 360,
                  fill=RED, outline=TEAL_DARK)
    # harbour water
    draw.line([(x0 + 10, base + 3), (x1 - 10, base + 3)], fill=(0, 121, 107),
              width=4)
    draw.line([(x0 + 34, base + 11), (x1 - 44, base + 11)], fill=(0, 121, 107),
              width=2)


# ------------------------------------------------------------------- page

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # masthead
    d.rectangle([0, 0, W, 132], fill=TEAL)
    d.rectangle([0, 132, W, 138], fill=GOLD)
    title = font(SERIF_B, 56)
    d.text((24, 14), "THE WORLD IN ONE IMAGE", font=title, fill=WHITE)
    date = font(SANS_B, 28)
    d.text((24, 84), "MONDAY  23  NOVEMBER  2026", font=date, fill=GOLD)
    tag = "No. 327  ·  ONE DAY, FIVE STORIES"
    d.text((W - 24 - d.textlength(tag, font=font(SANS, 20)), 92), tag,
           font=font(SANS, 20), fill=WHITE)

    # --- lead: IG Metall strike (wide banner)
    panel(d, (24, 156, 1000, 352))
    y = kicker(d, 52, 174, "LABOUR  ·  GERMANY")
    y = headline(d, 52, y, "23,000 WALK OUT AS IG METALL STRIKES FOR A DAY",
                 33, 620)
    deck(d, 52, y + 10,
         "IG Metall calls a 24-hour walkout at 19 northern firms — "
         "Mercedes-Benz, Meyer Werft, Siemens Gamesa — seeking a 5% rise.",
         17, 620)
    pic_factory(d, (700, 172, 976, 336))

    # --- row 1, left: Nepal-India talks
    panel(d, (24, 372, 500, 668))
    pic_flags(d, (44, 388, 480, 500))
    y = kicker(d, 44, 512, "DIPLOMACY  ·  NEW DELHI")
    y = headline(d, 44, y, "NEPAL'S PM MEETS MODI IN DELHI", 24, 436)
    deck(d, 44, y + 6,
         "Balendra Shah's first state visit as PM: talks, MoUs and a joint "
         "vision for trade, energy and connectivity.",
         17, 436)

    # --- row 1, right: Java factory fire
    panel(d, (524, 372, 1000, 668))
    pic_flame(d, (544, 388, 980, 500))
    y = kicker(d, 544, 512, "DISASTER  ·  JAVA")
    y = headline(d, 544, y, "SEARCH RESUMES FOR DOZENS AFTER FACTORY FIRE",
                 24, 436)
    deck(d, 544, y + 6,
         "24 body bags recovered at the Cikande candy factory; at least "
         "three confirmed dead, about 37 still missing.",
         17, 436)

    # --- row 2, left: Wellington Test
    panel(d, (24, 688, 500, 940))
    pic_cricket(d, (44, 700, 480, 808))
    y = kicker(d, 44, 820, "SPORT  ·  WELLINGTON")
    y = headline(d, 44, y, "NEW ZEALAND DIG IN ON THE FINAL DAY", 24, 436)
    deck(d, 44, y + 6,
         "157 for 4 at lunch, six wickets left.",
         17, 436)

    # --- row 2, right: Singapore visit
    panel(d, (524, 688, 1000, 940))
    pic_skyline(d, (544, 700, 980, 808))
    y = kicker(d, 544, 820, "DIPLOMACY  ·  SINGAPORE")
    y = headline(d, 544, y, "CHINA'S VICE-PREMIER IN SINGAPORE, DAY TWO",
                 24, 436)
    deck(d, 544, y + 6,
         "Day two of Ding Xuexiang's visit to Singapore.",
         17, 436)

    # --- footer
    d.line([(24, 958), (1000, 958)], fill=TEAL, width=2)
    foot = font(SANS, 18)
    d.text((24, 968),
           "Every story above happened or was first reported on Monday 23 November 2026.",
           font=foot, fill=INK)
    d.text((24, 992),
           "Sources: Reuters, India's Ministry of External Affairs, ESPNcricinfo.",
           font=foot, fill=GREY)

    img.save(os.path.join(HERE, "entry.png"), format="PNG")
    return os.path.join(HERE, "entry.png")


if __name__ == "__main__":
    path = build()
    print("wrote", path, os.path.getsize(path), "bytes")
