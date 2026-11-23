#!/usr/bin/env python3
"""Draw the world-news poster for Monday 23 November 2026.

Pure standard library: a tiny 5x7 bitmap font, a pixel sheet, and a
hand-rolled PNG encoder. No network access, no system fonts, no files
read at draw time. The five stories are the verified ones for this day;
the layout is a broadsheet: a masthead, then five stacked story bands,
each with a coloured spine, a kicker, a headline, a short body, and a
small pictogram on the right.
"""

import math
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 240, 224)
INK = (28, 34, 58)
RED = (178, 34, 34)
TEAL = (0, 102, 102)
OCHRE = (176, 118, 20)
SLATE = (88, 96, 116)
LIGHT = (232, 222, 200)
FLAME = (214, 90, 20)
GREEN = (46, 110, 62)

# 5x7 bitmap glyphs, '#' = ink. Only capitals are needed: the poster
# is set entirely in upper case, broadsheet style.
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
}


class Sheet:
    """An RGB pixel buffer with rectangle, disc and bitmap-text drawing."""

    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.px = bytearray(background * (width * height))

    def _put(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self._put(xx, yy, colour)

    def disc(self, cx, cy, r, colour):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            for xx in range(cx - dx, cx + dx + 1):
                self._put(xx, cy + dy, colour)

    def triangle(self, x, y, w, h, colour):
        # Isosceles triangle, apex at top centre, base at the bottom.
        for row in range(h):
            half = int((row / max(h - 1, 1)) * (w / 2))
            cx = x + w // 2
            for xx in range(cx - half, cx + half + 1):
                self._put(xx, y + row, colour)

    def glyph(self, ch, x, y, scale, colour):
        rows = GLYPHS.get(ch.upper(), GLYPHS["?"])
        for r, bits in enumerate(rows):
            for c, bit in enumerate(bits):
                if bit == "1":
                    self.rect(x + c * scale, y + r * scale, scale, scale, colour)

    def text_width(self, text, scale):
        return sum(6 * scale for _ in text) - scale

    def text(self, text, x, y, scale, colour):
        cx = x
        for ch in text:
            self.glyph(ch, cx, y, scale, colour)
            cx += 6 * scale
        return cx

    def centred(self, text, cx, y, scale, colour):
        self.text(text, cx - self.text_width(text, scale) // 2, y, scale, colour)

    def wrap(self, text, max_width, scale):
        """Greedy word wrap; returns a list of lines that fit max_width."""
        words, lines, cur = text.split(" "), [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if self.text_width(trial, scale) <= max_width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def png_bytes(sheet):
    """Encode the sheet as a PNG (filter 0 on every scanline)."""
    raw = bytearray()
    for y in range(sheet.h):
        raw.append(0)
        raw += sheet.px[y * sheet.w * 3:(y + 1) * sheet.w * 3]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", sheet.w, sheet.h, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


# The five verified stories of Monday 23 November 2026.
# (kicker, accent colour, headline, body, pictogram kind)
STORIES = [
    (
        "LABOUR - GERMANY", RED,
        "IG METALL CALLS 24-HOUR STRIKE",
        "SOME 23,000 WORKERS AT 19 FIRMS IN NORTHERN GERMANY WALK OUT ON "
        "MONDAY IN A PAY DISPUTE. THE UNION SEEKS A 5% RISE; EMPLOYERS OFFER "
        "A ONE-OFF PAYMENT AND 1.3% FROM JULY 2028.",
        "placard",
    ),
    (
        "DIPLOMACY - NEW DELHI", TEAL,
        "NEPAL PM HOLDS TALKS WITH MODI",
        "BALENDRA SHAH, ON HIS FIRST BILATERAL TRIP ABROAD AS PM, MEETS "
        "NARENDRA MODI FOR TALKS, A JOINT PRESS CONFERENCE AND LUNCH. MOUS "
        "ON EDUCATION, HEALTH AND AGRICULTURE.",
        "flags",
    ),
    (
        "DISASTER - JAVA, INDONESIA", FLAME,
        "SEARCH RESUMES AT CIKANDE FACTORY FIRE",
        "RESCUERS RETURN AT 07:00 ON MONDAY TO THE PT FONUSA AGUNG MULIA "
        "CANDY FACTORY IN SERANG, BANTEN. ABOUT 37 WORKERS ARE UNACCOUNTED "
        "FOR AFTER SATURDAY'S FIRE; 24 BODY BAGS RECOVERED.",
        "flame",
    ),
    (
        "SPORT - WELLINGTON", GREEN,
        "NEW ZEALAND BATTLE TO SAVE THE TEST",
        "DAY FIVE AT THE BASIN RESERVE: NEW ZEALAND 157 FOR 4 AT LUNCH, SIX "
        "WICKETS LEFT, AFTER INDIA DECLARED ON A RECORD 720 FOR 9, THE "
        "HIGHEST TEST TOTAL EVER IN NEW ZEALAND.",
        "cricket",
    ),
    (
        "DIPLOMACY - SINGAPORE", OCHRE,
        "CHINA'S VICE-PREMIER ON DAY TWO IN SINGAPORE",
        "DING XUEXIANG CONTINUES THE SECOND DAY OF HIS TWO-DAY VISIT FOR "
        "TALKS WITH SINGAPORE'S LEADERS.",
        "building",
    ),
]


def draw_pictogram(sheet, kind, x, y, accent):
    """A small flat pictogram in a 96x96 box at (x, y)."""
    if kind == "placard":
        sheet.rect(x + 44, y + 30, 6, 66, INK)
        sheet.rect(x + 8, y + 6, 80, 34, accent)
        sheet.rect(x + 8, y + 6, 80, 5, INK)
        sheet.rect(x + 8, y + 35, 80, 5, INK)
        sheet.text("5%", x + 34, y + 14, 2, PAPER)
    elif kind == "flags":
        sheet.rect(x + 18, y + 8, 5, 84, INK)
        sheet.rect(x + 66, y + 8, 5, 84, INK)
        sheet.triangle(x + 23, y + 8, 42, 26, accent)
        sheet.triangle(x + 23, y + 34, 42, 26, TEAL)
        sheet.disc(x + 44, y + 21, 6, PAPER)
    elif kind == "flame":
        sheet.triangle(x + 18, y + 30, 60, 62, FLAME)
        sheet.triangle(x + 32, y + 52, 32, 40, (240, 170, 40))
        sheet.disc(x + 48, y + 20, 10, RED)
    elif kind == "cricket":
        # A cricket bat standing upright, ball beside its toe.
        sheet.rect(x + 42, y + 6, 12, 34, OCHRE)
        sheet.rect(x + 42, y + 6, 12, 5, INK)
        sheet.rect(x + 34, y + 40, 28, 48, OCHRE)
        sheet.rect(x + 34, y + 40, 28, 5, INK)
        sheet.rect(x + 34, y + 83, 28, 5, INK)
        sheet.disc(x + 78, y + 76, 12, RED)
        sheet.disc(x + 78, y + 76, 5, PAPER)
    elif kind == "building":
        sheet.rect(x + 14, y + 34, 68, 58, accent)
        sheet.triangle(x + 8, y + 12, 80, 24, INK)
        for i in range(4):
            sheet.rect(x + 22 + i * 16, y + 46, 8, 34, PAPER)
        sheet.rect(x + 10, y + 88, 76, 6, INK)


def build_poster():
    s = Sheet(W, H, PAPER)
    # Outer frame.
    s.rect(0, 0, W, 6, INK)
    s.rect(0, H - 6, W, 6, INK)
    s.rect(0, 0, 6, H, INK)
    s.rect(W - 6, 0, 6, H, INK)

    # Masthead.
    s.centred("THE WORLD IN ONE DAY", W // 2, 34, 6, INK)
    s.centred("MONDAY 23 NOVEMBER 2026", W // 2, 92, 3, RED)
    s.rect(40, 128, W - 80, 3, INK)
    s.rect(40, 136, W - 80, 1, SLATE)

    # Five stacked story bands.
    band_y, band_h, gap = 152, 156, 6
    for i, (kicker, accent, headline, body, pic) in enumerate(STORIES):
        y = band_y + i * (band_h + gap)
        s.rect(40, y, W - 80, band_h, LIGHT)
        s.rect(40, y, 12, band_h, accent)
        s.text(kicker, 72, y + 12, 2, accent)
        head_lines = s.wrap(headline, 792, 3)
        hy = y + 34
        for line in head_lines:
            s.text(line, 72, hy, 3, INK)
            hy += 26
        body_lines = s.wrap(body, 792, 2)
        by = hy + 6
        for line in body_lines[:3]:
            s.text(line, 72, by, 2, INK)
            by += 17
        draw_pictogram(s, pic, 884, y + 30, accent)

    # Footer.
    s.rect(40, 962, W - 80, 1, SLATE)
    s.centred(
        "FIVE STORIES, ONE DAY - SOURCES: REUTERS, ESPNCRICINFO, MEA / ANI",
        W // 2, 974, 2, SLATE,
    )
    return s


def main():
    poster = build_poster()
    with open("entry.png", "wb") as f:
        f.write(png_bytes(poster))


if __name__ == "__main__":
    main()
