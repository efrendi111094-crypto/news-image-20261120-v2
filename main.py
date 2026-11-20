#!/usr/bin/env python3
"""Friday 20 November 2026 front page — one self-contained program.

Draws a 1024x1024 newspaper front page from news.json (12 verified stories)
and writes it to $MAKEFUN_OUTPUT_DIR/entry.png. Standard library only,
fully deterministic: the same input always produces the same bytes.
"""
import sys

sys.dont_write_bytecode = True

import json
import math
import os
import struct
import zlib

# ---------------------------------------------------------------- font ----
# 5x7 pixel font, each glyph is 7 rows of 5 bits (bit 4 = leftmost pixel).
# Written for this entry. Unknown characters render as a blank.
FONT = {
    " ": [0, 0, 0, 0, 0, 0, 0],
    "A": [14, 17, 17, 31, 17, 17, 17],
    "B": [30, 17, 17, 30, 17, 17, 30],
    "C": [14, 17, 16, 16, 16, 17, 14],
    "D": [30, 17, 17, 17, 17, 17, 30],
    "E": [31, 16, 16, 30, 16, 16, 31],
    "F": [31, 16, 16, 30, 16, 16, 16],
    "G": [14, 17, 16, 23, 17, 17, 15],
    "H": [17, 17, 17, 31, 17, 17, 17],
    "I": [14, 4, 4, 4, 4, 4, 14],
    "J": [7, 2, 2, 2, 2, 18, 12],
    "K": [17, 18, 20, 24, 20, 18, 17],
    "L": [16, 16, 16, 16, 16, 16, 31],
    "M": [17, 27, 21, 21, 17, 17, 17],
    "N": [17, 25, 21, 19, 17, 17, 17],
    "O": [14, 17, 17, 17, 17, 17, 14],
    "P": [30, 17, 17, 30, 16, 16, 16],
    "Q": [14, 17, 17, 17, 21, 18, 13],
    "R": [30, 17, 17, 30, 20, 18, 17],
    "S": [15, 16, 16, 14, 1, 1, 30],
    "T": [31, 4, 4, 4, 4, 4, 4],
    "U": [17, 17, 17, 17, 17, 17, 14],
    "V": [17, 17, 17, 17, 17, 10, 4],
    "W": [17, 17, 17, 21, 21, 21, 10],
    "X": [17, 17, 10, 4, 10, 17, 17],
    "Y": [17, 17, 10, 4, 4, 4, 4],
    "Z": [31, 1, 2, 4, 8, 16, 31],
    "0": [14, 17, 19, 21, 25, 17, 14],
    "1": [4, 12, 4, 4, 4, 4, 14],
    "2": [14, 17, 1, 6, 8, 16, 31],
    "3": [31, 2, 4, 2, 1, 17, 14],
    "4": [2, 6, 10, 18, 31, 2, 2],
    "5": [31, 16, 30, 1, 1, 17, 14],
    "6": [6, 8, 16, 30, 17, 17, 14],
    "7": [31, 1, 2, 4, 8, 8, 8],
    "8": [14, 17, 17, 14, 17, 17, 14],
    "9": [14, 17, 17, 15, 1, 2, 12],
    "a": [0, 0, 14, 1, 15, 17, 15],
    "b": [16, 16, 30, 17, 17, 17, 30],
    "c": [0, 0, 14, 17, 16, 17, 14],
    "d": [1, 1, 15, 17, 17, 17, 15],
    "e": [0, 0, 14, 17, 31, 16, 14],
    "f": [6, 9, 8, 30, 8, 8, 8],
    "g": [0, 15, 17, 17, 15, 1, 14],
    "h": [16, 16, 30, 17, 17, 17, 17],
    "i": [4, 0, 12, 4, 4, 4, 14],
    "j": [2, 0, 6, 2, 2, 18, 12],
    "k": [16, 16, 18, 20, 24, 20, 18],
    "l": [12, 4, 4, 4, 4, 4, 14],
    "m": [0, 0, 26, 21, 21, 21, 21],
    "n": [0, 0, 30, 17, 17, 17, 17],
    "o": [0, 0, 14, 17, 17, 17, 14],
    "p": [0, 0, 30, 17, 17, 30, 16],
    "q": [0, 0, 15, 17, 17, 15, 1],
    "r": [0, 0, 22, 25, 16, 16, 16],
    "s": [0, 0, 15, 16, 14, 1, 30],
    "t": [8, 8, 28, 8, 8, 9, 6],
    "u": [0, 0, 17, 17, 17, 19, 13],
    "v": [0, 0, 17, 17, 17, 10, 4],
    "w": [0, 0, 17, 21, 21, 21, 10],
    "x": [0, 0, 17, 10, 4, 10, 17],
    "y": [0, 0, 17, 17, 15, 1, 14],
    "z": [0, 0, 31, 2, 4, 8, 31],
    ".": [0, 0, 0, 0, 0, 12, 12],
    ",": [0, 0, 0, 0, 12, 4, 8],
    ":": [0, 12, 12, 0, 12, 12, 0],
    ";": [0, 12, 12, 0, 12, 4, 8],
    "!": [4, 4, 4, 4, 4, 0, 4],
    "?": [14, 17, 1, 6, 4, 0, 4],
    "-": [0, 0, 0, 31, 0, 0, 0],
    "(": [2, 4, 8, 8, 8, 4, 2],
    ")": [8, 4, 2, 2, 2, 4, 8],
    "'": [4, 4, 8, 0, 0, 0, 0],
    '"': [10, 10, 10, 0, 0, 0, 0],
    "%": [25, 26, 2, 4, 8, 11, 19],
    "$": [4, 15, 20, 14, 5, 30, 4],
    "&": [12, 18, 20, 8, 21, 18, 13],
    "/": [1, 1, 2, 4, 8, 16, 16],
    "+": [0, 4, 4, 31, 4, 4, 0],
    "=": [0, 0, 31, 0, 31, 0, 0],
    "·": [0, 0, 0, 12, 12, 0, 0],
    "•": [0, 0, 14, 17, 17, 14, 0],
    "★": [4, 14, 31, 14, 4, 10, 17],
    "↑": [4, 14, 21, 4, 4, 4, 4],
    "↓": [4, 4, 4, 4, 21, 14, 4],
}
# Em/en dashes and the pound sign map onto drawn equivalents.
FONT["–"] = FONT["-"]
FONT["—"] = FONT["-"]
FONT["£"] = [6, 8, 8, 30, 8, 8, 31]


def text_width(text, scale):
    """Pixel width of text at a scale (5 px glyph + 1 px gap)."""
    return len(text) * 6 * scale - scale


def wrap(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, rgb):
        self.w, self.h = w, h
        self.px = bytearray(rgb * (w * h))

    def set(self, x, y, rgb):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(rgb)

    def fill_rect(self, x, y, w, h, rgb):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        row = bytes(rgb) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect(self, x, y, w, h, rgb, t=1):
        self.fill_rect(x, y, w, t, rgb)
        self.fill_rect(x, y + h - t, w, t, rgb)
        self.fill_rect(x, y, t, h, rgb)
        self.fill_rect(x + w - t, y, t, h, rgb)

    def line(self, x0, y0, x1, y1, rgb, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx - dy
        while True:
            if t == 1:
                self.set(x0, y0, rgb)
            else:
                self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, rgb)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, rgb):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, rgb)

    def ellipse(self, cx, cy, rx, ry, rgb):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0:
                    self.set(xx, yy, rgb)

    def arc(self, cx, cy, r, a0, a1, rgb, t=1, step=0.02):
        a = a0
        while a <= a1:
            x = int(round(cx + r * math.cos(a)))
            y = int(round(cy + r * math.sin(a)))
            if t == 1:
                self.set(x, y, rgb)
            else:
                self.fill_rect(x - t // 2, y - t // 2, t, t, rgb)
            a += step

    def poly(self, points, rgb):
        """Scanline polygon fill (points = list of (x, y))."""
        if len(points) < 3:
            return
        ymin = min(p[1] for p in points)
        ymax = max(p[1] for p in points)
        for yy in range(ymin, ymax + 1):
            nodes = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    nodes.append(int(x0 + (yy - y0) * (x1 - x0) / (y1 - y0)))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                for xx in range(nodes[i], nodes[i + 1] + 1):
                    self.set(xx, yy, rgb)

    def draw_text(self, x, y, text, scale, rgb):
        cx = x
        for ch in text:
            glyph = FONT.get(ch)
            if glyph is None:
                cx += 6 * scale
                continue
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, rgb)
            cx += 6 * scale

    def text_centered(self, cx, y, text, scale, rgb):
        self.draw_text(cx - text_width(text, scale) // 2, y, text, scale, rgb)

    def text_right(self, x1, y, text, scale, rgb):
        self.draw_text(x1 - text_width(text, scale), y, text, scale, rgb)


# ----------------------------------------------------------------- png ----
def _chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def write_png(path, canvas):
    """Encode the canvas as an 8-bit RGB PNG (filter 0 rows)."""
    w, h = canvas.w, canvas.h
    raw = bytearray()
    for yy in range(h):
        raw.append(0)
        raw.extend(canvas.px[yy * w * 3:(yy + 1) * w * 3])
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    blob = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", zlib.compress(bytes(raw), 6)) +
            _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(blob)
    return len(blob)


# ---------------------------------------------------------- pictograms ----
PAPER = (247, 241, 222)
CARD = (255, 253, 245)
NAVY = (24, 33, 62)
RED = (178, 42, 42)
TEAL = (0, 122, 122)
GREY = (96, 96, 88)
SKY_TOP = (18, 42, 84)
SKY_MID = (38, 84, 138)
SKY_LOW = (96, 148, 190)
SEA = (16, 66, 110)
CLOUD = (232, 238, 244)
CLOUD_SH = (180, 198, 214)


def draw_cyclone(cv, x, y, w, h):
    """A cyclone over the sea, drawn from primitives: banded storm sky,
    a spiral of cloud bands around a pale eye, rain streaks, a dark coast."""
    # Banded storm sky.
    bands = [(SKY_TOP, 0.0), (SKY_MID, 0.45), (SKY_LOW, 0.72), (SEA, 0.86)]
    for i in range(len(bands)):
        c, f0 = bands[i]
        f1 = bands[i + 1][1] if i + 1 < len(bands) else 1.0
        cv.fill_rect(x, y + int(h * f0), w, int(h * (f1 - f0)) + 1, c)
    cx, cy = x + w // 2, y + int(h * 0.46)
    # Spiral cloud bands: several arms, each an arc chain widening outward.
    # Every disc is kept inside the panel so nothing spills into the masthead.
    for arm in range(3):
        base = arm * 2.094
        for k in range(34):
            t = k / 33.0
            r = 12 + t * (w * 0.30)
            a = base + t * 4.4
            px = int(cx + r * math.cos(a))
            py = int(cy + r * math.sin(a) * 0.82)
            rad = 4 + int(t * 14)
            if (px - rad < x or px + rad >= x + w or
                    py - rad < y or py + rad >= y + h):
                continue
            cv.disc(px, py, rad, CLOUD if k % 2 == 0 else CLOUD_SH)
    # Eye: pale calm centre with a dark ring.
    cv.disc(cx, cy, 26, NAVY)
    cv.disc(cx, cy, 21, (240, 236, 214))
    cv.disc(cx, cy, 12, (214, 206, 178))
    # Rain streaks on both flanks.
    for i in range(46):
        rx = x + (i * 37) % w
        ry = y + int(h * 0.10) + (i * 53) % int(h * 0.62)
        cv.line(rx, ry, rx - 5, ry + 14, (200, 216, 230), 2)
    # Dark coastline with a few low buildings along the bottom.
    coast_y = y + int(h * 0.88)
    cv.fill_rect(x, coast_y, w, h - int(h * 0.88), (14, 26, 20))
    for i, bw in enumerate((46, 30, 58, 26, 40, 34)):
        bx = x + 18 + i * 92
        cv.fill_rect(bx, coast_y - 14 - (i % 3) * 6, bw, 14 + (i % 3) * 6,
                     (20, 34, 26))
    # Foaming surf line.
    for i in range(0, w, 14):
        cv.disc(x + i, coast_y + 3, 4, (214, 226, 236))


def draw_chart_fall(cv, x, y, w, h):
    """A falling market chart: axes, descending line, red bars."""
    cv.fill_rect(x, y, w, h, (238, 240, 244))
    cv.rect(x, y, w, h, NAVY, 2)
    cv.line(x + 10, y + h - 12, x + w - 8, y + h - 12, NAVY, 2)
    cv.line(x + 10, y + 8, x + 10, y + h - 12, NAVY, 2)
    pts = [(x + 16, y + 14), (x + 34, y + 26), (x + 52, y + 22),
           (x + 70, y + 46), (x + 86, y + 58), (x + w - 12, y + h - 20)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, 3)
    for px, py in pts:
        cv.disc(px, py, 3, RED)
    cv.draw_text(x + w - 34, y + 6, "-6%", 2, RED)


def draw_three_flags(cv, x, y, w, h):
    """Three small flags side by side: US stripes, China red, Russia bands."""
    cv.fill_rect(x, y, w, h, (238, 240, 244))
    cv.rect(x, y, w, h, NAVY, 2)
    fw, fh = (w - 24) // 3, h - 28
    fy = y + 10
    # US: red/white stripes + blue canton.
    ux = x + 8
    for i in range(7):
        cv.fill_rect(ux, fy + i * fh // 7, fw, fh // 7 + 1,
                     RED if i % 2 == 0 else (245, 245, 245))
    cv.fill_rect(ux, fy, fw // 2, fh * 4 // 7, (30, 50, 110))
    for r in range(3):
        for c in range(2):
            cv.disc(ux + 4 + c * 8, fy + 4 + r * 7, 1, (255, 255, 255))
    # China: red field, one big yellow star + small stars.
    cx0 = ux + fw + 4
    cv.fill_rect(cx0, fy, fw, fh, (222, 40, 30))
    cv.disc(cx0 + 9, fy + 9, 5, (255, 222, 60))
    for sx, sy in ((22, 6), (26, 12), (22, 18)):
        cv.disc(cx0 + sx, fy + sy, 2, (255, 222, 60))
    # Russia: white / blue / red horizontal bands.
    rx0 = cx0 + fw + 4
    cv.fill_rect(rx0, fy, fw, fh // 3 + 1, (245, 245, 245))
    cv.fill_rect(rx0, fy + fh // 3, fw, fh // 3 + 1, (40, 90, 180))
    cv.fill_rect(rx0, fy + 2 * fh // 3, fw, fh - 2 * fh // 3, RED)


def draw_drone(cv, x, y, w, h):
    """A small quadcopter drone."""
    cv.fill_rect(x, y, w, h, (238, 240, 244))
    cv.rect(x, y, w, h, NAVY, 2)
    cx, cy = x + w // 2, y + h // 2 + 4
    cv.ellipse(cx, cy, 16, 9, NAVY)
    cv.disc(cx, cy, 5, RED)
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ex, ey = cx + sx * 24, cy + sy * 16
        cv.line(cx, cy, ex, ey, NAVY, 3)
        cv.line(ex - 9, ey - 3, ex + 9, ey - 3, NAVY, 2)
        cv.disc(ex, ey, 3, NAVY)
    cv.draw_text(x + 6, y + 4, "1,000+", 1, RED)


def draw_border_gate(cv, x, y, w, h):
    """A closed border gate: fence bars and a red CLOSED sign."""
    cv.fill_rect(x, y, w, h, (238, 240, 244))
    cv.rect(x, y, w, h, NAVY, 2)
    for i in range(7):
        bx = x + 6 + i * ((w - 12) // 7)
        cv.fill_rect(bx, y + 8, 3, h - 16, NAVY)
    cv.fill_rect(x + 4, y + h // 2 - 2, w - 8, 4, NAVY)
    cv.fill_rect(x + 8, y + h - 22, w - 16, 14, RED)
    cv.draw_text(x + 12, y + h - 20, "CLOSED", 1, (255, 255, 255))


def draw_cricket(cv, x, y, w, h):
    """A cricket bat, ball and stumps."""
    cv.fill_rect(x, y, w, h, (238, 240, 244))
    cv.rect(x, y, w, h, NAVY, 2)
    # Stumps.
    for i in range(3):
        sx = x + w - 22 + i * 6
        cv.fill_rect(sx, y + h - 26, 3, 18, (214, 178, 90))
    cv.fill_rect(x + w - 24, y + h - 29, 20, 3, (214, 178, 90))
    # Bat: angled blade + handle.
    cv.line(x + 14, y + h - 12, x + 34, y + 14, (196, 152, 80), 7)
    cv.line(x + 34, y + 14, x + 42, y + 6, (120, 84, 40), 4)
    # Ball.
    cv.disc(x + 16, y + 16, 7, RED)
    cv.arc(x + 16, y + 16, 7, 0.6, 2.2, (255, 255, 255), 1)


# -------------------------------------------------------------- layout ----
W, H = 1024, 1024


def render(data):
    cv = Canvas(W, H, PAPER)
    # Outer frame.
    cv.rect(0, 0, W, H, NAVY, 6)
    cv.rect(10, 10, W - 20, H - 20, NAVY, 1)

    # ---- Masthead -------------------------------------------------------
    cv.text_centered(W // 2, 26, data["masthead"], 5, NAVY)
    cv.fill_rect(24, 72, 976, 3, NAVY)
    cv.draw_text(24, 82, data["date"].upper(), 3, NAVY)
    cv.text_right(1000, 82, "%d STORIES · %d REGIONS" % (
        data["counts"]["stories"], data["counts"]["regions"]), 3, RED)
    cv.fill_rect(24, 112, 976, 4, RED)

    # ---- Hero: cyclone art left, story right ----------------------------
    hx, hy, hw, hh = 24, 122, 976, 380
    draw_cyclone(cv, hx, hy, 556, hh)
    cv.rect(hx, hy, 556, hh, NAVY, 2)
    tx, tw = 596, 404
    cv.fill_rect(tx, hy, tw, hh, CARD)
    cv.rect(tx, hy, tw, hh, NAVY, 2)
    hero = data["hero"]
    cv.draw_text(tx + 16, hy + 14, hero["kicker"], 2, RED)
    lines = wrap(hero["headline"], 15)
    yy = hy + 44
    for ln in lines:
        cv.draw_text(tx + 16, yy, ln, 4, NAVY)
        yy += 32
    cv.fill_rect(tx + 16, yy + 6, tw - 32, 2, GREY)
    yy += 20
    for ln in hero["lines"]:
        cv.draw_text(tx + 16, yy, ln, 2, NAVY)
        yy += 20
    cv.draw_text(tx + 16, hy + hh - 24, hero["source"], 1, GREY)

    # ---- Two medium cards ----------------------------------------------
    my, mh = 514, 184
    icons = [draw_chart_fall, draw_three_flags]
    for i, card in enumerate(data["medium"]):
        cx = 24 + i * 495
        cw = 481
        cv.fill_rect(cx, my, cw, mh, CARD)
        cv.rect(cx, my, cw, mh, NAVY, 2)
        icons[i](cv, cx + 12, my + 12, 96, 96)
        cv.draw_text(cx + 120, my + 14, card["kicker"], 2, RED)
        hl = wrap(card["headline"], 19)
        yy = my + 40
        for ln in hl:
            cv.draw_text(cx + 120, yy, ln, 3, NAVY)
            yy += 24
        yy = my + 118
        for ln in card["lines"]:
            cv.draw_text(cx + 12, yy, ln, 2, NAVY)
            yy += 16

    # ---- Three small cards ----------------------------------------------
    sy, sh = 710, 140
    sicons = [draw_drone, draw_border_gate, draw_cricket]
    for i, card in enumerate(data["small"]):
        cx = 24 + i * 328
        cw = 320
        cv.fill_rect(cx, sy, cw, sh, CARD)
        cv.rect(cx, sy, cw, sh, NAVY, 2)
        sicons[i](cv, cx + 10, sy + 10, 56, 56)
        cv.draw_text(cx + 76, sy + 12, card["kicker"], 1, RED)
        hl = wrap(card["headline"], 19)
        yy = sy + 28
        for ln in hl:
            cv.draw_text(cx + 76, yy, ln, 2, NAVY)
            yy += 16
        yy = sy + 78
        for ln in card["lines"]:
            cv.draw_text(cx + 10, yy, ln, 1, NAVY)
            yy += 13
        cv.draw_text(cx + cw - 10 - text_width(card["source"], 1),
                     sy + sh - 16, card["source"], 1, GREY)

    # ---- Also today ------------------------------------------------------
    ay = 862
    cv.draw_text(24, ay + 6, "ALSO TODAY", 2, RED)
    cv.fill_rect(24, ay + 28, 976, 2, NAVY)
    for i, brief in enumerate(data["briefs"]):
        bx = 24 + (i % 2) * 495
        by = ay + 38 + (i // 2) * 22
        cv.draw_text(bx, by, "• " + brief, 1, NAVY)

    # ---- Footer ----------------------------------------------------------
    cv.fill_rect(24, 968, 976, 2, NAVY)
    cv.text_centered(W // 2, 978, data["footer"], 1, GREY)
    cv.text_centered(W // 2, 996,
                     "All %d stories verified against reports published on %s."
                     % (data["counts"]["stories"], data["date"]), 1, GREY)
    return cv


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "news.json"), encoding="utf-8") as f:
        data = json.load(f)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    cv = render(data)
    path = os.path.join(outdir, "entry.png")
    size = write_png(path, cv)
    print("stories: %d (%d hero, %d medium, %d small, %d briefs)" % (
        data["counts"]["stories"], 1, len(data["medium"]),
        len(data["small"]), len(data["briefs"])))
    print("wrote %s (%d bytes, 1024x1024)" % (path, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
