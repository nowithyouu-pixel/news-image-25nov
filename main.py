#!/usr/bin/env python3
"""Draw a 1024x1024 PNG summing up the world news of 25 November 2026.

Pure Python 3 standard library: no third-party packages, no network, no
wall clock, no unseeded randomness. The picture is a newspaper front page:
a masthead naming the day, one hero story, and six panels covering the
day's biggest stories across regions and fields.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   -> writes out/entry.png
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 233)
INK = (18, 24, 38)
NAVY = (20, 36, 61)
NAVY2 = (28, 52, 88)
GOLD = (201, 162, 39)
RED = (178, 34, 34)
RED2 = (214, 69, 65)
BLUE = (38, 84, 124)
TEAL = (23, 110, 110)
GREY = (105, 112, 122)
LIGHT = (232, 226, 212)
WHITE = (255, 255, 255)
SKY = (168, 205, 226)
SEA = (52, 96, 140)
ORANGE = (232, 120, 30)
YELLOW = (245, 196, 66)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells, '#' = ink. All text is upper-cased first.
FONT = {
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
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
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
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
}


def text_width(text, scale):
    """Pixel width of text drawn at the given scale (6 units per char)."""
    return len(text) * 6 * scale


def wrap(text, max_chars):
    """Greedy word wrap to at most max_chars per line."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.set(x, y, color)

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            for x in range(x0, x1):
                self.set(x, y + t, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            for y in range(y0, y1):
                self.set(x + t, y, color)

    def circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Scanline fill of a triangle.
        xs = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = xs
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / max(1, by - ay)
                xa = ax + (bx - ax) * t1
            else:
                xa = bx
            t2 = (y - ay) / max(1, cy - ay)
            xb = ax + (cx - ax) * t2
            lo, hi = sorted((int(xa), int(xb)))
            for x in range(lo, hi + 1):
                self.set(x, y, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i // steps
            y = y0 + (y1 - y0) * i // steps
            for dy in range(thick):
                for dx in range(thick):
                    self.set(x + dx, y + dy, color)

    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        for dy in range(scale):
                            for dx in range(scale):
                                self.set(cx + col * scale + dx,
                                         y + row * scale + dy, color)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)


def png_bytes(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- icons
def flame(c, x, y, s):
    """A stylised flame, base at (x, y), height ~5*s."""
    c.triangle(x, y - 5 * s, x - 2 * s, y, x + 2 * s, y, ORANGE)
    c.triangle(x, y - 3 * s, x - s, y, x + s, y, YELLOW)
    c.triangle(x, y - 5 * s, x + s // 2, y - 2 * s, x + 2 * s, y - s, RED2)


def icon_tanker(c, x, y, w, h):
    c.rect(x, y + h - 26, x + w, y + h - 14, SEA)
    c.rect(x + 8, y + h - 52, x + w - 8, y + h - 26, NAVY2)
    c.rect(x + w - 34, y + h - 74, x + w - 18, y + h - 52, RED)
    c.rect(x + 14, y + h - 66, x + 30, y + h - 52, WHITE)
    flame(c, x + w // 3, y + h - 52, 7)
    flame(c, x + 2 * w // 3, y + h - 60, 8)
    c.rect(x, y + h - 10, x + w, y + h - 6, (140, 180, 205))


def icon_refinery(c, x, y, w, h):
    c.rect(x + 10, y + h - 60, x + 30, y + h - 12, GREY)
    c.rect(x + 40, y + h - 80, x + 62, y + h - 12, NAVY2)
    c.rect(x + 72, y + h - 46, x + 96, y + h - 12, BLUE)
    flame(c, x + 21, y + h - 60, 4)
    flame(c, x + 51, y + h - 80, 5)
    c.rect(x, y + h - 12, x + w, y + h - 8, INK)


def icon_chart(c, x, y, w, h):
    c.rect(x, y + 8, x + w, y + h - 8, WHITE)
    c.rect(x, y + 8, x + w, y + h - 8, INK)  # placeholder cleared below
    c.rect(x + 4, y + 12, x + w - 4, y + h - 12, PAPER)
    pts = [(x + 12, y + 26), (x + 34, y + 40), (x + 56, y + 34),
           (x + 78, y + 62), (x + 100, y + 78)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        c.line(ax, ay, bx, by, RED, 4)
    c.triangle(x + 100, y + 78, x + 88, y + 72, x + 96, y + 92, RED)
    c.text(x + 12, y + h - 30, "-6.2%", 2, RED)


def icon_tower(c, x, y, w, h):
    c.rect(x + 44, y + 10, x + 68, y + h - 12, NAVY2)
    c.rect(x + 36, y + 26, x + 76, y + h - 12, BLUE)
    c.rect(x + 52, y + 2, x + 60, y + 10, INK)
    c.circle(x + 56, y + 34, 16, YELLOW)
    c.circle(x + 56, y + 34, 10, ORANGE)
    c.rect(x, y + h - 12, x + w, y + h - 8, INK)


def icon_gavel(c, x, y, w, h):
    c.rect(x + 18, y + 18, x + 78, y + 40, (120, 82, 40))
    c.rect(x + 44, y + 40, x + 56, y + h - 26, (90, 60, 25))
    c.rect(x + 12, y + h - 26, x + 92, y + h - 16, (150, 110, 60))


def icon_rocket(c, x, y, w, h):
    c.circle(x + 56, y + 40, 26, NAVY2)
    c.triangle(x + 56, y + 6, x + 38, y + 46, x + 74, y + 46, WHITE)
    c.rect(x + 46, y + 46, x + 66, y + 84, WHITE)
    c.triangle(x + 46, y + 60, x + 28, y + 88, x + 46, y + 84, RED)
    c.triangle(x + 66, y + 60, x + 84, y + 88, x + 66, y + 84, RED)
    c.circle(x + 56, y + 40, 7, SKY)
    flame(c, x + 56, y + 96, 4)


def icon_globe(c, x, y, w, h):
    c.circle(x + 56, y + 52, 42, SEA)
    c.circle(x + 56, y + 52, 34, (74, 140, 90))
    c.rect(x + 14, y + 52, x + 98, y + 56, SEA)
    c.rect(x + 52, y + 10, x + 60, y + 94, SEA)
    c.circle(x + 44, y + 38, 10, (74, 140, 90))
    c.circle(x + 70, y + 66, 12, (74, 140, 90))


# ---------------------------------------------------------------- page
def draw():
    c = Canvas(W, H, PAPER)

    # Masthead
    c.rect(0, 0, W, 118, NAVY)
    c.text_center(W // 2, 14, "THE WORLD TODAY", 6, WHITE)
    c.hline(60, W - 60, 66, GOLD, 3)
    c.text_center(W // 2, 78, "WEDNESDAY  -  25 NOVEMBER 2026", 3, GOLD)
    c.rect(0, 118, W, 124, RED)

    # Hero: Strait of Hormuz
    hx, hy, hw, hh = 16, 136, W - 32, 268
    c.rect(hx, hy, hx + hw, hy + hh, WHITE)
    c.rect(hx, hy, hx + hw, hy + hh, INK)  # border via inner clear
    c.rect(hx + 2, hy + 2, hx + hw - 2, hy + hh - 2, WHITE)
    c.rect(hx, hy, hx + hw, hy + 40, RED)
    c.text(hx + 16, hy + 8, "TOP STORY  |  MIDDLE EAST", 3, WHITE)
    icon_tanker(c, hx + 16, hy + 84, 320, 170)
    tx = hx + 348
    c.text(tx, hy + 56, "HORMUZ IN", 5, INK)
    c.text(tx, hy + 102, "FLAMES", 5, RED)
    body = ("TWO OIL TANKERS HIT NAVAL MINES AND CAUGHT FIRE "
            "IN THE STRAIT OF HORMUZ, IRAN'S REVOLUTIONARY "
            "GUARD SAID.")
    for i, line in enumerate(wrap(body, 44)):
        c.text(tx, hy + 158 + i * 26, line, 2, INK)

    # Six panels: 2 columns x 3 rows
    panels = [
        ("UKRAINE", icon_refinery, BLUE,
         "DRONES SET TWO RUSSIAN REFINERIES ABLAZE",
         "UKRAINIAN DRONES HIT TWO ROSNEFT REFINERIES IN "
         "SAMARA OVERNIGHT. A STRIKE ON ODESA KILLED TWO."),
        ("MARKETS", icon_chart, RED,
         "STOCKS PLUNGE, DOW TOPS 50,000",
         "KOSPI -6.2%, NIKKEI -2.8% AS ASIAN STOCKS TUMBLED. "
         "THE DOW CLOSED ABOVE 50,000 FOR THE FIRST TIME."),
        ("RIYADH", icon_tower, NAVY2,
         "HOUTHI DRONE HITS RIYADH TOWER",
         "A HOUTHI DRONE STRUCK A TOWER IN RIYADH'S FINANCIAL "
         "DISTRICT, INJURING 11 PEOPLE, SAUDI OFFICIALS SAID."),
        ("HUAWEI", icon_gavel, TEAL,
         "HUAWEI CONVICTED IN US TRIAL",
         "A BROOKLYN JURY FOUND HUAWEI GUILTY ON 10 OF 12 "
         "COUNTS, INCLUDING BANK FRAUD AND TRADE SECRETS."),
        ("SPACE", icon_rocket, NAVY2,
         "PAKISTAN'S FIRST ASTRONAUT IN ORBIT",
         "CHINA'S SHENZHOU-24 DOCKED WITH TIANGONG CARRYING "
         "PAKISTAN'S FIRST ASTRONAUT, A HISTORIC FIRST."),
        ("ALSO TODAY", icon_globe, TEAL,
         "TREATY, CLIMATE, WAGES",
         "AUSTRALIA AND SOLOMON ISLANDS SIGN A SECURITY TREATY. "
         "COP31 TALKS FAIL. BANGLADESH RAISES GARMENT PAY "
         "36% TO $139 A MONTH."),
    ]
    gx, gy = 16, 420
    cw, ch, gap = 488, 186, 16
    for i, (kicker, icon, accent, head, body) in enumerate(panels):
        px = gx + (i % 2) * (cw + gap)
        py = gy + (i // 2) * (ch + gap)
        c.rect(px, py, px + cw, py + ch, WHITE)
        c.rect(px, py, px + cw, py + 4, accent)
        c.rect(px, py, px + cw, py + ch, INK)
        c.rect(px + 1, py + 1, px + cw - 1, py + ch - 1, WHITE)
        c.rect(px + 1, py + 1, px + cw - 1, py + 5, accent)
        icon(c, px + 12, py + 34, 120, 130)
        tx = px + 144
        c.text(tx, py + 14, kicker, 2, accent)
        for j, line in enumerate(wrap(head, 25)):
            c.text(tx, py + 40 + j * 24, line, 2, INK)
        for j, line in enumerate(wrap(body, 27)):
            c.text(tx, py + 94 + j * 19, line, 2, GREY)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(draw())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
