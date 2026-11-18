#!/usr/bin/env python3
"""Render the news-image-20261118 entry: one newspaper front page that sums
up Wednesday 18 November 2026 in a single 1024x1024 PNG.

Deterministic: pure Pillow drawing from fixed data, no randomness, no
network, no clock. Running it twice produces a byte-identical entry.png.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
W = H = 1024
MARGIN = 26
CONTENT_W = W - 2 * MARGIN

PAPER = (248, 243, 230)
PANEL = (243, 236, 217)
INK = (24, 34, 54)
NAVY = (23, 42, 74)
RED = (176, 32, 40)
FAINT = (122, 118, 104)
HAIR = (168, 160, 140)
WATER = (206, 221, 226)
LAND_TAN = (222, 205, 164)
GOLD = (206, 158, 44)

FONT_DIR = "/usr/share/fonts/truetype/liberation"
SERIF = os.path.join(FONT_DIR, "LiberationSerif-Regular.ttf")
SERIF_B = os.path.join(FONT_DIR, "LiberationSerif-Bold.ttf")
SERIF_I = os.path.join(FONT_DIR, "LiberationSerif-Italic.ttf")
SANS = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")
SANS_B = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


# ---------------------------------------------------------------- text help
def text_w(d, s, f):
    return d.textlength(s, font=f)


def wrap(d, s, f, maxw):
    """Greedy word wrap by pixel width. Returns a list of lines."""
    lines = []
    cur = ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(d, trial, f) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def tracked_w(d, s, f, tracking):
    return sum(text_w(d, ch, f) for ch in s) + tracking * max(0, len(s) - 1)


def draw_tracked(d, x, y, s, f, fill, tracking=2):
    cx = x
    for ch in s:
        d.text((cx, y), ch, font=f, fill=fill)
        cx += text_w(d, ch, f) + tracking
    return cx - x


def fit_size(d, s, path, start, maxw, minimum=8):
    """Largest font size (<= start) at which s fits maxw."""
    size = start
    while size > minimum and text_w(d, s, font(path, size)) > maxw:
        size -= 1
    return font(path, size)


# ---------------------------------------------------------------- draw help
def dashed_line(d, p0, p1, fill, width=2, dash=7, gap=5):
    x0, y0 = p0
    x1, y1 = p1
    dist = math.hypot(x1 - x0, y1 - y0)
    if dist == 0:
        return
    ux, uy = (x1 - x0) / dist, (y1 - y0) / dist
    t = 0.0
    while t < dist:
        t2 = min(t + dash, dist)
        d.line([x0 + ux * t, y0 + uy * t, x0 + ux * t2, y0 + uy * t2],
               fill=fill, width=width)
        t += dash + gap


def dashed_arc(d, box, start, end, fill, width=2, dash_deg=9, gap_deg=7):
    a = start
    while a < end:
        a2 = min(a + dash_deg, end)
        d.arc(box, a, a2, fill=fill, width=width)
        a += dash_deg + gap_deg


def star_points(cx, cy, r_out, r_in, n=5, rot=-90.0):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        ang = math.radians(rot + i * 180.0 / n)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def burst(d, cx, cy, r, fill):
    """Small explosion star."""
    pts = []
    n = 8
    for i in range(2 * n):
        rr = r if i % 2 == 0 else r * 0.38
        ang = math.radians(i * 180.0 / n)
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def chip(d, x, y, num, dia=15):
    d.ellipse([x, y, x + dia, y + dia], fill=RED)
    f = font(SANS_B, 9 if num < 10 else 8)
    s = str(num)
    tw = text_w(d, s, f)
    d.text((x + (dia - tw) / 2, y + dia / 2 - 6), s, font=f, fill=(255, 255, 255))


def panel(d, x, y, w, h, fill=PANEL):
    d.rectangle([x, y, x + w, y + h], fill=fill, outline=HAIR, width=1)


def section_row(d, x, y, num, label, w):
    """Red chip + small caps section label; returns y below the row."""
    chip(d, x, y, num)
    f = fit_size(d, label, SANS_B, 10, w - 22)
    d.text((x + 21, y + 2), label, font=f, fill=NAVY)
    return y + 17


# ---------------------------------------------------------------- lead art
def art_gulf(d, x, y, w, h):
    """Persian Gulf sketch: land masses, dashed drone tracks, bursts."""
    panel(d, x, y, w, h, fill=WATER)
    # Iran (top right landmass)
    d.polygon([(x + w * 0.52, y), (x + w, y), (x + w, y + h * 0.52),
               (x + w * 0.86, y + h * 0.40), (x + w * 0.74, y + h * 0.34),
               (x + w * 0.66, y + h * 0.20), (x + w * 0.55, y + h * 0.16)],
              fill=LAND_TAN, outline=NAVY)
    # Arabia (bottom landmass)
    d.polygon([(x, y + h), (x, y + h * 0.58), (x + w * 0.16, y + h * 0.52),
               (x + w * 0.30, y + h * 0.60), (x + w * 0.44, y + h * 0.55),
               (x + w * 0.60, y + h * 0.72), (x + w * 0.78, y + h * 0.66),
               (x + w, y + h * 0.86), (x + w, y + h)],
              fill=LAND_TAN, outline=NAVY)
    # Qatar peninsula nub
    d.polygon([(x + w * 0.40, y + h * 0.56), (x + w * 0.45, y + h * 0.44),
               (x + w * 0.49, y + h * 0.56)], fill=LAND_TAN, outline=NAVY)
    kuw = (x + w * 0.30, y + h * 0.34)
    bah = (x + w * 0.44, y + h * 0.50)
    hor = (x + w * 0.80, y + h * 0.52)
    d.ellipse([kuw[0] - 3, kuw[1] - 3, kuw[0] + 3, kuw[1] + 3], fill=NAVY)
    d.ellipse([bah[0] - 3, bah[1] - 3, bah[0] + 3, bah[1] + 3], fill=NAVY)
    src = (x + w * 0.68, y + h * 0.22)
    dashed_line(d, src, kuw, RED, width=2)
    dashed_line(d, (x + w * 0.72, y + h * 0.28), bah, RED, width=2)
    dashed_line(d, (x + w * 0.90, y + h * 0.34), hor, RED, width=2)
    burst(d, kuw[0], kuw[1] - 8, 8, RED)
    burst(d, bah[0] + 6, bah[1] - 6, 7, RED)
    burst(d, hor[0], hor[1] - 6, 7, RED)
    f = font(SANS_B, 8)
    d.text((kuw[0] - 14, kuw[1] + 6), "KUWAIT", font=f, fill=NAVY)
    d.text((bah[0] - 16, bah[1] + 7), "BAHRAIN", font=f, fill=NAVY)
    d.text((x + w * 0.80, y + 5), "IRAN", font=f, fill=NAVY)
    d.text((hor[0] - 16, hor[1] + 8), "HORMUZ", font=f, fill=NAVY)


def art_summit(d, x, y, w, h):
    """Shenzhen skyline behind a summit table with three flags."""
    panel(d, x, y, w, h)
    base = y + h * 0.62
    towers = [(0.04, 0.30), (0.13, 0.42), (0.22, 0.26), (0.62, 0.36),
              (0.72, 0.48), (0.82, 0.30), (0.90, 0.40)]
    for fx, fh in towers:
        tx = x + w * fx
        tw = w * 0.075
        d.rectangle([tx, base - h * fh, tx + tw, base], fill=NAVY)
        for wy in range(int(base - h * fh) + 4, int(base) - 3, 7):
            d.point((tx + tw / 2, wy), fill=(250, 240, 200))
    # tapered landmark tower
    tx = x + w * 0.40
    d.polygon([(tx, base), (tx + w * 0.05, y + h * 0.06),
               (tx + w * 0.10, y + h * 0.06), (tx + w * 0.15, base)],
              fill=NAVY)
    d.line([tx + w * 0.075, y + h * 0.06, tx + w * 0.075, y + 1],
           fill=RED, width=2)
    # table
    ty = y + h * 0.78
    d.rectangle([x + w * 0.10, ty, x + w * 0.90, ty + 5], fill=(120, 84, 50))
    d.rectangle([x + w * 0.14, ty + 5, x + w * 0.17, y + h - 3], fill=(120, 84, 50))
    d.rectangle([x + w * 0.83, ty + 5, x + w * 0.86, y + h - 3], fill=(120, 84, 50))
    # three flags on the table
    flags_x = [0.24, 0.47, 0.70]
    for i, fx in enumerate(flags_x):
        px = x + w * fx
        d.line([px, ty, px, ty - h * 0.30], fill=INK, width=2)
        fw, fh = w * 0.13, h * 0.20
        top = ty - h * 0.30
        if i == 0:      # China
            d.rectangle([px, top, px + fw, top + fh], fill=(206, 44, 44))
            d.polygon(star_points(px + fw * 0.26, top + fh * 0.32,
                                   3.4, 1.4), fill=(250, 220, 60))
            d.ellipse([px + fw * 0.55, top + fh * 0.18, px + fw * 0.65,
                       top + fh * 0.30], fill=(250, 220, 60))
        elif i == 1:    # United States
            d.rectangle([px, top, px + fw, top + fh], fill=(250, 250, 250),
                        outline=HAIR)
            for s in range(3):
                sy = top + s * fh / 3
                d.rectangle([px, sy, px + fw, sy + fh / 6], fill=(178, 34, 52))
            d.rectangle([px, top, px + fw * 0.45, top + fh * 0.5],
                        fill=(40, 60, 130))
        else:           # Russia
            d.rectangle([px, top, px + fw, top + fh], fill=(250, 250, 250),
                        outline=HAIR)
            d.rectangle([px, top + fh / 3, px + fw, top + 2 * fh / 3],
                        fill=(40, 80, 160))
            d.rectangle([px, top + 2 * fh / 3, px + fw, top + fh],
                        fill=(200, 40, 40))


def art_bridge(d, x, y, w, h):
    """Crimea bridge: standing rail arch, road span fallen into the sea."""
    panel(d, x, y, w, h)
    water_y = y + h * 0.66
    d.rectangle([x, water_y, x + w, y + h], fill=WATER)
    for i in range(3):
        wy = water_y + 6 + i * 8
        dashed_line(d, (x + 8 + i * 14, wy), (x + w - 30 - i * 10, wy),
                    (140, 170, 182), width=1, dash=10, gap=8)
    deck_y = y + h * 0.40
    # piers
    for fx in (0.16, 0.44, 0.86):
        d.rectangle([x + w * fx, deck_y, x + w * fx + 6, water_y + 6],
                    fill=NAVY)
    # standing rail arch (left)
    d.arc([x + w * 0.06, deck_y - h * 0.30, x + w * 0.52, deck_y + h * 0.16],
          180, 360, fill=NAVY, width=3)
    for fx in (0.14, 0.22, 0.30, 0.38):
        top_y = deck_y - h * 0.30 * math.sin(math.pi * (fx - 0.06) / 0.46) - 2
        d.line([x + w * fx, deck_y - 4, x + w * fx, top_y + h * 0.16],
               fill=NAVY, width=1)
    d.line([x + 2, deck_y, x + w * 0.52, deck_y], fill=NAVY, width=3)
    # fallen road span (right), tilted into the water
    fx0, fy0 = x + w * 0.56, deck_y
    fx1, fy1 = x + w * 0.94, water_y + h * 0.16
    d.polygon([(fx0, fy0), (fx1, fy1), (fx1, fy1 + 7), (fx0, fy0 + 7)],
              fill=RED)
    d.line([fx0, fy0, fx0, fy0 - 12], fill=RED, width=2)
    # splash
    for dx in (-8, 0, 9):
        d.arc([fx1 + dx - 7, fy1 - 4, fx1 + dx + 7, fy1 + 9], 200, 320,
              fill=(90, 140, 160), width=2)
    d.line([x + w * 0.52, deck_y, x + w * 0.56, deck_y], fill=NAVY, width=3)


# ---------------------------------------------------------------- card art
def art_alaska(d, x, y, w, h):
    panel(d, x, y, w, h)
    ak = [(0.06, 0.55), (0.10, 0.30), (0.22, 0.18), (0.36, 0.22),
          (0.44, 0.34), (0.52, 0.30), (0.58, 0.42), (0.52, 0.52),
          (0.58, 0.62), (0.50, 0.66), (0.42, 0.58), (0.30, 0.66),
          (0.20, 0.60), (0.12, 0.66)]
    d.polygon([(x + w * fx, y + h * fy) for fx, fy in ak],
              fill=(172, 186, 152), outline=NAVY)
    for fx, fy in ((0.62, 0.70), (0.68, 0.76), (0.74, 0.80)):
        d.line([x + w * fx, y + h * fy, x + w * (fx + 0.03),
                y + h * (fy + 0.05)], fill=NAVY, width=1)
    # capitol dome
    bx = x + w * 0.66
    by = y + h * 0.52
    d.rectangle([bx, by, bx + w * 0.24, by + h * 0.16], fill=(250, 248, 240),
                outline=NAVY)
    d.pieslice([bx + w * 0.03, by - h * 0.20, bx + w * 0.21, by + h * 0.06],
               180, 360, fill=NAVY)
    d.line([bx + w * 0.12, by - h * 0.20, bx + w * 0.12, by - h * 0.30],
           fill=NAVY, width=2)
    # 56 / 44 bars
    f = font(SANS_B, 9)
    d.rectangle([x + w * 0.58, y + h * 0.76, x + w * 0.58 + w * 0.27,
                 y + h * 0.86], fill=(40, 80, 160))
    d.text((x + w * 0.865, y + h * 0.74), "56", font=f, fill=NAVY)
    d.rectangle([x + w * 0.58, y + h * 0.89, x + w * 0.58 + w * 0.21,
                 y + h * 0.99], fill=RED)
    d.text((x + w * 0.805, y + h * 0.87), "44", font=f, fill=NAVY)


def art_chip_chart(d, x, y, w, h):
    panel(d, x, y, w, h)
    cs = h * 0.60
    cx, cy = x + w * 0.07, y + h * 0.18
    d.rounded_rectangle([cx, cy, cx + cs, cy + cs], 4, fill=NAVY)
    d.rounded_rectangle([cx + cs * 0.24, cy + cs * 0.24, cx + cs * 0.76,
                         cy + cs * 0.76], 2, outline=(250, 240, 200), width=2)
    for i in range(3):
        px = cx + cs * (0.25 + 0.25 * i)
        d.line([px, cy - 3, px, cy], fill=NAVY, width=2)
        d.line([px, cy + cs, px, cy + cs + 3], fill=NAVY, width=2)
        py = cy + cs * (0.25 + 0.25 * i)
        d.line([cx - 3, py, cx, py], fill=NAVY, width=2)
        d.line([cx + cs, py, cx + cs + 3, py], fill=NAVY, width=2)
    ax, ay = x + w * 0.50, y + h * 0.84
    d.line([ax, y + h * 0.14, ax, ay], fill=FAINT, width=1)
    d.line([ax, ay, x + w * 0.96, ay], fill=FAINT, width=1)
    pts = [(ax + w * 0.02, ay - h * 0.10), (ax + w * 0.14, ay - h * 0.22),
           (ax + w * 0.24, ay - h * 0.18), (ax + w * 0.36, ay - h * 0.48),
           (ax + w * 0.43, ay - h * 0.58)]
    d.line(pts, fill=RED, width=2)
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 8, pts[-1][1] + 1),
               (pts[-1][0] - 1, pts[-1][1] + 8)], fill=RED)
    d.ellipse([pts[-1][0] - 3, pts[-1][1] - 3, pts[-1][0] + 3,
               pts[-1][1] + 3], fill=RED)


def art_knesset(d, x, y, w, h):
    panel(d, x, y, w, h)
    bx, bw = x + w * 0.08, w * 0.52
    top = y + h * 0.14
    d.polygon([(bx, top + h * 0.16), (bx + bw / 2, top),
               (bx + bw, top + h * 0.16)], fill=NAVY)
    for i in range(4):
        cx = bx + bw * (0.14 + 0.24 * i)
        d.rectangle([cx, top + h * 0.22, cx + bw * 0.09, top + h * 0.62],
                    fill=(250, 248, 240), outline=NAVY)
    d.rectangle([bx - 3, top + h * 0.66, bx + bw + 3, top + h * 0.74],
                fill=NAVY)
    # ballot box + tally
    kx = x + w * 0.68
    ky = y + h * 0.40
    d.rectangle([kx, ky, kx + w * 0.24, ky + h * 0.34], fill=(250, 248, 240),
                outline=NAVY, width=2)
    d.line([kx + 4, ky + 6, kx + w * 0.24 - 4, ky + 6], fill=INK, width=2)
    d.rectangle([kx + w * 0.07, ky - h * 0.16, kx + w * 0.17, ky + 4],
                fill=(255, 255, 255), outline=NAVY)
    f = font(SERIF_B, 13)
    d.text((kx - 2, y + h * 0.70), "66-52", font=f, fill=RED)


def art_eu_ukraine(d, x, y, w, h):
    panel(d, x, y, w, h)
    cx, cy, r = x + w * 0.24, y + h * 0.50, h * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 80, 160))
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        sx, sy = cx + r * 0.68 * math.cos(ang), cy + r * 0.68 * math.sin(ang)
        d.polygon(star_points(sx, sy, 3.2, 1.35), fill=(250, 205, 60))
    fx, fy, fw, fh = x + w * 0.52, y + h * 0.14, w * 0.42, h * 0.38
    d.rectangle([fx, fy, fx + fw, fy + fh / 2], fill=(60, 110, 190))
    d.rectangle([fx, fy + fh / 2, fx + fw, fy + fh], fill=(245, 205, 60))
    d.rectangle([fx, fy, fx + fw, fy + fh], outline=NAVY, width=1)
    f = font(SERIF_B, 14)
    d.text((fx + 2, fy + fh + 3), "€45bn", font=f, fill=NAVY)


def art_cyclone(d, x, y, w, h):
    panel(d, x, y, w, h, fill=WATER)
    d.polygon([(x, y), (x + w * 0.34, y), (x + w * 0.26, y + h * 0.4),
               (x + w * 0.38, y + h), (x, y + h)], fill=LAND_TAN,
              outline=NAVY)
    cx, cy = x + w * 0.68, y + h * 0.48
    pts = []
    for t in range(0, 321, 4):
        ang = math.radians(t)
        rr = 2 + t / 321.0 * h * 0.34
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang) * 0.82))
    d.line(pts, fill=(250, 250, 250), width=3)
    d.line(pts, fill=NAVY, width=1)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)
    f = font(SANS_B, 8)
    d.text((x + w * 0.06, y + h * 0.78), "ANDHRA", font=f, fill=NAVY)
    d.text((cx - 14, y + h * 0.84), "AKVAN", font=f, fill=RED)


def art_fuel(d, x, y, w, h):
    panel(d, x, y, w, h)
    px, py, pw, ph = x + w * 0.10, y + h * 0.16, w * 0.30, h * 0.68
    d.rounded_rectangle([px, py, px + pw, py + ph], 4, fill=(250, 248, 240),
                        outline=NAVY, width=2)
    d.rectangle([px + 6, py + 6, px + pw - 6, py + ph * 0.38], outline=NAVY)
    f = font(SANS_B, 10)
    d.text((px + 9, py + 10), "£", font=f, fill=NAVY)
    d.arc([px + pw - 2, py + ph * 0.3, px + pw + w * 0.14, py + ph * 0.8],
          270, 90, fill=NAVY, width=2)
    d.polygon([(px + pw + w * 0.10, py + ph * 0.62),
               (px + pw + w * 0.16, py + ph * 0.62),
               (px + pw + w * 0.15, py + ph * 0.80),
               (px + pw + w * 0.11, py + ph * 0.80)], fill=NAVY)
    ax, ay = x + w * 0.58, y + h * 0.84
    pts = [(ax, ay - h * 0.08), (ax + w * 0.14, ay - h * 0.24),
           (ax + w * 0.26, ay - h * 0.20), (ax + w * 0.38, ay - h * 0.52)]
    d.line(pts, fill=RED, width=2)
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 8, pts[-1][1]),
               (pts[-1][0], pts[-1][1] + 8)], fill=RED)
    f2 = font(SERIF_B, 15)
    d.text((ax + w * 0.04, y + h * 0.06), "3.6%", font=f2, fill=RED)


def drone_glyph(d, cx, cy, s, fill):
    d.line([cx - s, cy - s, cx + s, cy + s], fill=fill, width=2)
    d.line([cx - s, cy + s, cx + s, cy - s], fill=fill, width=2)
    d.ellipse([cx - s * 0.28, cy - s * 0.28, cx + s * 0.28, cy + s * 0.28],
              fill=fill)
    for dx, dy in ((-s, -s), (s, -s), (-s, s), (s, s)):
        d.ellipse([cx + dx - 2.5, cy + dy - 2.5, cx + dx + 2.5,
                   cy + dy + 2.5], outline=fill, width=1)


def art_drones_night(d, x, y, w, h):
    panel(d, x, y, w, h, fill=(26, 38, 64))
    d.ellipse([x + w * 0.78, y + h * 0.10, x + w * 0.92, y + h * 0.34],
              fill=(245, 238, 205))
    d.ellipse([x + w * 0.74, y + h * 0.07, x + w * 0.88, y + h * 0.31],
              fill=(26, 38, 64))
    for fx, fy in ((0.08, 0.16), (0.2, 0.3), (0.34, 0.12), (0.5, 0.22),
                   (0.62, 0.10), (0.14, 0.52), (0.44, 0.4)):
        d.point((x + w * fx, y + h * fy), fill=(240, 240, 220))
        d.point((x + w * fx + 1, y + h * fy), fill=(240, 240, 220))
    drone_glyph(d, x + w * 0.30, y + h * 0.52, 9, (235, 238, 245))
    drone_glyph(d, x + w * 0.58, y + h * 0.36, 7, (235, 238, 245))
    drone_glyph(d, x + w * 0.72, y + h * 0.62, 8, (235, 238, 245))
    for fx, fy in ((0.30, 0.52), (0.58, 0.36), (0.72, 0.62)):
        d.ellipse([x + w * fx - 1.5, y + h * fy + 8, x + w * fx + 1.5,
                   y + h * fy + 11], fill=RED)
    d.rectangle([x, y + h * 0.88, x + w, y + h], fill=(16, 24, 42))


def art_sudan(d, x, y, w, h):
    panel(d, x, y, w, h)
    su = [(0.16, 0.14), (0.38, 0.08), (0.62, 0.12), (0.80, 0.10),
          (0.86, 0.26), (0.78, 0.36), (0.84, 0.52), (0.72, 0.66),
          (0.74, 0.82), (0.55, 0.90), (0.34, 0.86), (0.18, 0.90),
          (0.10, 0.70), (0.14, 0.48), (0.08, 0.30)]
    d.polygon([(x + w * fx, y + h * fy) for fx, fy in su],
              fill=(216, 178, 110), outline=NAVY)
    ox, oy = x + w * 0.34, y + h * 0.52     # El Obeid, west-central
    d.ellipse([ox - 3, oy - 3, ox + 3, oy + 3], fill=RED)
    f = font(SANS_B, 8)
    d.text((ox + 6, oy - 4), "EL OBEID", font=f, fill=NAVY)
    drone_glyph(d, x + w * 0.70, y + h * 0.20, 8, INK)
    dashed_line(d, (x + w * 0.64, y + h * 0.28), (ox + 6, oy - 8),
                RED, width=1, dash=4, gap=3)


def art_gta(d, x, y, w, h):
    panel(d, x, y, w, h)
    gx, gy, gw, gh = x + w * 0.08, y + h * 0.30, w * 0.56, h * 0.46
    d.rounded_rectangle([gx, gy, gx + gw, gy + gh], 12, fill=NAVY)
    # d-pad
    cx, cy = gx + gw * 0.26, gy + gh / 2
    d.rectangle([cx - 3, cy - 9, cx + 3, cy + 9], fill=(250, 248, 240))
    d.rectangle([cx - 9, cy - 3, cx + 9, cy + 3], fill=(250, 248, 240))
    # buttons
    for dx, dy, col in ((0, -8, (250, 205, 60)), (8, 0, (206, 44, 44)),
                        (0, 8, (90, 170, 90)), (-8, 0, (90, 130, 220))):
        bx, by = gx + gw * 0.74 + dx, gy + gh / 2 + dy
        d.ellipse([bx - 3.5, by - 3.5, bx + 3.5, by + 3.5], fill=col)
    # clock at midnight
    kx, ky, kr = x + w * 0.82, y + h * 0.34, 14
    d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(250, 248, 240),
              outline=NAVY, width=2)
    d.line([kx, ky, kx, ky - kr * 0.72], fill=RED, width=2)
    d.line([kx, ky, kx + kr * 0.4, ky], fill=NAVY, width=2)
    f = font(SANS_B, 8)
    d.text((kx - 22, ky + kr + 2), "MIDNIGHT", font=f, fill=NAVY)


def art_voyager(d, x, y, w, h):
    panel(d, x, y, w, h, fill=(26, 38, 64))
    for fx, fy in ((0.1, 0.14), (0.3, 0.08), (0.52, 0.16), (0.7, 0.08),
                   (0.88, 0.2), (0.2, 0.34), (0.94, 0.44)):
        d.point((x + w * fx, y + h * fy), fill=(240, 240, 220))
    ex, ey, er = x + w * 0.15, y + h * 0.60, w * 0.085
    d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(70, 120, 190))
    d.polygon([(ex - er * 0.5, ey - er * 0.4), (ex + er * 0.1, ey - er * 0.6),
               (ex + er * 0.3, ey - er * 0.1), (ex - er * 0.3, ey)],
              fill=(110, 175, 110))
    px, py = x + w * 0.78, y + h * 0.36
    dashed_line(d, (ex + er * 0.8, ey - er * 0.7), (px - 12, py + 10),
                (240, 230, 180), width=1, dash=5, gap=4)
    # probe: dish + mast + boom
    d.arc([px - 13, py - 13, px + 13, py + 13], 300, 120,
          fill=(245, 245, 245), width=3)
    d.line([px, py, px + 10, py + 12], fill=(245, 245, 245), width=2)
    d.line([px + 10, py + 12, px + 24, py + 20], fill=(245, 245, 245),
           width=1)
    d.rectangle([px + 23, py + 18, px + 28, py + 23], fill=GOLD)
    f = font(SANS_B, 8)
    d.text((x + w * 0.30, y + h * 0.12), "1 LIGHT-DAY", font=f,
           fill=(240, 230, 180))
    f2 = font(SANS_B, 8)
    d.text((ex + er + 4, ey - 4), "EARTH", font=f2, fill=(200, 220, 250))

# ---------------------------------------------------------------- content
LEADS = [
    dict(num=1, label="MIDDLE EAST · IRAN WAR", art=art_gulf,
         headline="Kuwait, Bahrain say they intercepted Iranian drones",
         summary="Iran's army says it aimed at US forces at Ali Al Salem. "
                 "ADNOC says its ship was hit in Hormuz: 1 missing, "
                 "11 injured."),
    dict(num=2, label="ASIA · DIPLOMACY", art=art_summit,
         headline="Xi greets Trump on eve of Trump-Xi-Putin summit",
         summary="Xi and Putin vowed to 'lead' a multipolar world; at APEC "
                 "Xi urged AI and free-trade cooperation. Talks Thursday."),
    dict(num=3, label="EUROPE · WAR IN UKRAINE", art=art_bridge,
         headline="A span of the Crimea bridge falls into the sea",
         summary="Kyiv says a second strike in two days destroyed the road "
                 "arch. Moscow says it downed 1,441 drones; the rail arch "
                 "stands."),
]

CARDS = [
    dict(num=4, label="AMERICAS · US POLITICS", art=art_alaska,
         headline="Democrat Peltola wins Alaska; Senate now 56-44",
         summary="AP calls it: 144,302 votes to Sullivan's 131,844 - a ninth "
                 "Democratic gain, the most in a midterm since 1958."),
    dict(num=5, label="UNITED STATES · BUSINESS", art=art_chip_chart,
         headline="Nvidia's revenue doubles to $115.8bn",
         summary="Sales rose 103% as data-centre demand held up; data "
                 "centres brought in $107.6bn of it."),
    dict(num=6, label="MIDDLE EAST · POLITICS", art=art_knesset,
         headline="Knesset elects Kahana as speaker, 66-52",
         summary="Matan Kahana, of Eisenkot's party, replaces Netanyahu "
                 "ally Amir Ohana after a seven-hour debate."),
    dict(num=7, label="EUROPE · UKRAINE AID", art=art_eu_ukraine,
         headline="EU proposes a €45bn loan for Ukraine",
         summary="It would cover about two-thirds of Kyiv's €70bn gap for "
                 "2027, and is repaid only if Russia pays reparations."),
    dict(num=8, label="ASIA · WEATHER", art=art_cyclone,
         headline="Cyclone Akvan strengthens in the Bay of Bengal",
         summary="IMD: landfall in Andhra Pradesh around noon Friday. "
                 "Odisha is readying to move 204,070 people from the coast."),
    dict(num=9, label="EUROPE · ECONOMY", art=art_fuel,
         headline="UK inflation rises to 3.6%, highest in a year",
         summary="October CPI up from 3.5% as diesel hits a record high, "
                 "the ONS says."),
    dict(num=10, label="EUROPE · UKRAINE WAR", art=art_drones_night,
         headline="Russia fires 141 drones at Ukraine overnight",
         summary="Air force: 126 downed. Officials: 5 killed, 15 injured "
                 "in a day; power cut to 80+ Rivne settlements."),
    dict(num=11, label="AFRICA · SUDAN WAR", art=art_sudan,
         headline="Amnesty: RSF drone strikes killed 37 civilians in El Obeid",
         summary="It says the strikes should be investigated as war crimes; "
                 "the RSF denies responsibility."),
    dict(num=12, label="GLOBAL · GAMES", art=art_gta,
         headline="Grand Theft Auto VI goes on sale after a 13-year wait",
         summary="The midnight launch starts in New Zealand; Sensor Tower "
                 "estimates 14.9m digital pre-orders."),
    dict(num=13, label="SPACE · SCIENCE", art=art_voyager,
         headline="Voyager 1 is the first craft one light-day from Earth",
         summary="NASA's probe passes 25.9 billion km away - a radio "
                 "command sent today reaches it tomorrow."),
]

STATS = [
    ("141", "drones fired at Ukraine overnight"),
    ("$115.8bn", "Nvidia quarterly revenue, up 103%"),
    ("145 km/h", "Akvan's forecast gusts at landfall"),
    ("204,070", "people Odisha is moving off the coast"),
    ("25.9bn km", "Voyager 1's distance from Earth"),
]

BRIEFS = [
    "Riyadh: coalition says it downed a Houthi cruise missile",
    "Manila: Trump claims a trade deal; Manila says none signed",
    "Tokyo: Japan posts a sixth straight monthly trade deficit",
    "Seoul: court acquits Daegu mayor in martial-law case",
    "Shenzhen: Xi and Lee conclude FTA services talks",
    "Singapore: Princess Aiko on first imperial visit in 20 years",
    "Bangkok: Chinese director jailed over collapsed tower",
    "Lahore: world's most polluted big city again, AQI 339",
    "Rawalpindi: Sri Lanka all out for 98 against Pakistan",
    "Kuala Lumpur: ringgit falls to a five-month low",
    "Asia markets: Kospi +2%, Hang Seng -0.9%",
    "Oil: Brent falls 1.4% to $91.82",
    "China: Tencent revenue up 8%, below forecasts",
    "Cook Islands: Cyclone Xavier reaches Category 5",
    "New Zealand: tsunami advisory lifted after 60 cm surges",
    "Sydney: Tame Impala sweeps the ARIA Awards",
    "Canada: Carney says China trade no worry for Trump",
    "Peru: M5.9 quake off south coast, no damage reported",
    "Cincinnati: USA beat Haiti 2-0, into Nations League semis",
    "Los Angeles: Grimes scores 47 as Lakers win ninth straight",
    "Buenos Aires: deputies pass Malvinas sovereignty bill",
    "Bolivia: 99 bat species recorded in Madidi park",
    "Washington: NSA confirms outage on classified network",
    "Johannesburg: SA Rugby seeks full hearing on Erasmus ban",
    "Sudan: archaeologists reach Old Dongola church floor",
    "Siberia: An-12 crash near Kemerovo kills all 19 aboard",
    "Guinea: 224 jailed over illegal gold mining",
    "Jordan & Iraq: both block Telegram",
    "China-Canada: tariff cuts on pork and seafood",
    "India: Amazon's $7bn plan for renewables by 2030",
    "Senegal: first team into AFCON 2027",
    "DR Congo: Ebola adds 400-500 cases a week, WHO says",
]

# ---------------------------------------------------------------- world map
# Coarse continent polygons in (lon, lat), drawn as coloured dot grids.
CONTINENTS = [
    ("NORTH AMERICA", (168, 184, 148), [
        [(-165, 60), (-155, 71), (-140, 70), (-125, 71), (-115, 72),
         (-105, 72), (-95, 78), (-88, 72), (-85, 66), (-80, 70), (-76, 68),
         (-70, 62), (-65, 60), (-60, 52), (-65, 50), (-66, 45), (-70, 44),
         (-71, 41), (-74, 39), (-75, 36), (-76, 34), (-79, 33), (-80, 31),
         (-81, 25), (-82, 28), (-84, 30), (-87, 30), (-90, 29), (-94, 29),
         (-97, 28), (-97, 25), (-94, 19), (-90, 15), (-87, 13), (-83, 9),
         (-80, 8), (-84, 11), (-88, 14), (-92, 15), (-97, 16), (-102, 18),
         (-105, 20), (-108, 23), (-110, 24), (-114, 29), (-117, 33),
         (-121, 35), (-122, 37), (-124, 40), (-124, 46), (-127, 50),
         (-130, 54), (-135, 57), (-145, 60), (-152, 58), (-158, 59)],
        [(-46, 60), (-42, 65), (-38, 70), (-30, 68), (-22, 70), (-20, 76),
         (-26, 80), (-36, 80), (-46, 76), (-50, 70), (-53, 64), (-52, 60)],
    ]),
    ("SOUTH AMERICA", (126, 168, 132), [
        [(-78, 7), (-75, 10), (-72, 12), (-68, 11), (-64, 10), (-61, 9),
         (-55, 6), (-52, 5), (-50, 1), (-44, -2), (-38, -5), (-35, -8),
         (-37, -11), (-39, -13), (-39, -17), (-40, -21), (-42, 23 * -1),
         (-48, -26), (-50, -30), (-52, -33), (-55, -35), (-57, -38),
         (-62, -39), (-62, -41), (-65, -41), (-65, -45), (-67, -49),
         (-67, -52), (-68, -54), (-71, -54), (-73, -51), (-74, -50),
         (-74, -46), (-73, -44), (-73, -40), (-72, -35), (-71, -31),
         (-70, -27), (-70, -23), (-70, -19), (-72, -18), (-75, -15),
         (-77, -12), (-79, -8), (-80, -6), (-81, -3), (-80, 1), (-79, 3),
         (-77, 5)],
    ]),
    ("EUROPE", (138, 164, 198), [
        [(-9, 37), (-9, 43), (-4, 44), (-2, 44), (-1, 46), (-5, 48),
         (-2, 49), (0, 51), (3, 53), (7, 54), (8, 57), (10, 58), (13, 55),
         (18, 55), (21, 56), (24, 59), (29, 60), (30, 62), (27, 65),
         (25, 68), (30, 70), (32, 67), (30, 65), (26, 64), (24, 62),
         (21, 61), (22, 59), (20, 56), (18, 54), (14, 52), (10, 50),
         (8, 48), (6, 46), (3, 44), (3, 42), (7, 43), (10, 44), (12, 42),
         (15, 42), (18, 40), (20, 40), (22, 38), (23, 36), (22, 37),
         (19, 40), (16, 38), (15, 40), (13, 41), (10, 44), (7, 44),
         (3, 43), (0, 43), (-2, 38), (-2, 37)],
        [(-5, 50), (-3, 53), (-5, 55), (-7, 57), (-5, 58), (-3, 57),
         (-2, 55), (-1, 52), (-2, 51), (-4, 50)],
        [(-10, 52), (-6, 52), (-6, 55), (-8, 55), (-10, 54)],
        [(8, 44), (10, 44), (12, 42), (14, 42), (16, 40), (18, 40),
         (17, 41), (15, 42), (13, 41), (11, 42), (9, 43)],
    ]),
    ("AFRICA", (216, 178, 110), [
        [(-6, 35), (-2, 35), (3, 37), (9, 37), (10, 34), (11, 34),
         (15, 32), (20, 32), (25, 32), (30, 31), (32, 31), (33, 30),
         (34, 28), (35, 24), (37, 22), (38, 21), (39, 20), (39, 16),
         (41, 14), (43, 12), (44, 11), (48, 11), (51, 11), (50, 10),
         (48, 5), (42, 0), (41, -3), (40, -7), (40, -11), (39, -15),
         (37, -19), (36, -21), (35, -24), (34, -26), (33, -27), (31, -29),
         (28, -32), (25, -34), (20, -35), (19, -34), (17, -32), (16, -29),
         (15, -27), (14, -22), (13, -18), (13, -15), (12, -11), (13, -6),
         (12, -4), (9, -1), (9, 3), (6, 4), (0, 5), (-4, 5), (-8, 4),
         (-11, 6), (-13, 8), (-15, 11), (-16, 12), (-17, 15), (-17, 19),
         (-16, 22), (-16, 25), (-15, 27), (-14, 29), (-11, 31), (-9, 32),
         (-8, 33)],
        [(44, -16), (47, -15), (49, -17), (50, -20), (48, -23), (46, -25),
         (45, -25), (44, -22), (43, -20), (44, -17)],
    ]),
    ("ASIA", (206, 150, 128), [
        [(28, 41), (33, 42), (38, 43), (42, 43), (46, 42), (49, 43),
         (51, 45), (54, 47), (58, 49), (63, 50), (68, 51), (73, 52),
         (78, 53), (84, 54), (90, 55), (96, 56), (102, 57), (108, 58),
         (114, 59), (120, 61), (126, 62), (132, 63), (138, 64), (144, 65),
         (150, 67), (156, 68), (162, 69), (168, 69), (174, 68), (178, 66),
         (178, 64), (172, 64), (166, 63), (161, 61), (159, 57), (157, 52),
         (154, 50), (150, 47), (145, 46), (143, 43), (141, 41), (139, 38),
         (136, 35), (133, 34), (130, 33), (128, 34), (126, 37), (124, 39),
         (122, 38), (121, 34), (122, 30), (120, 27), (117, 24), (113, 22),
         (110, 20), (108, 17), (108, 13), (107, 10), (105, 5), (103, 2),
         (101, 3), (100, 6), (99, 9), (98, 13), (96, 16), (94, 18),
         (92, 21), (90, 22), (88, 22), (86, 20), (83, 18), (81, 15),
         (80, 13), (78, 9), (77, 8), (75, 12), (73, 17), (72, 20),
         (70, 22), (66, 24), (62, 25), (58, 25), (55, 26), (52, 27),
         (50, 29), (48, 30), (46, 32), (44, 35), (42, 37), (40, 39),
         (36, 40), (32, 41)],
        [(35, 29), (36, 34), (39, 36), (42, 37), (44, 38), (47, 38),
         (48, 36), (50, 31), (50, 29), (52, 26), (54, 26), (56, 27),
         (59, 24), (59, 22), (57, 19), (55, 17), (52, 15), (48, 14),
         (45, 12), (43, 12), (42, 15), (40, 16), (39, 20), (38, 24),
         (37, 27)],
        [(95, 5), (99, 2), (103, -2), (106, -5), (104, -4), (100, 0),
         (96, 3)],
        [(109, 1), (113, 3), (117, 5), (119, 2), (117, -2), (113, -3),
         (110, -2)],
        [(106, -6), (110, -7), (114, -8), (114, -9), (108, -8), (106, -7)],
        [(120, 13), (121, 16), (122, 18), (121, 14), (120, 12)],
        [(130, 31), (133, 34), (137, 35), (139, 37), (140, 39), (141, 41),
         (141, 43), (143, 44), (142, 45), (140, 42), (139, 38), (136, 35),
         (133, 33), (131, 32)],
    ]),
    ("OCEANIA", (178, 156, 196), [
        [(114, -22), (113, -26), (115, -32), (117, -35), (120, -34),
         (124, -33), (129, -32), (132, -32), (135, -35), (137, -35),
         (139, -37), (141, -38), (145, -38), (147, -38), (149, -37),
         (150, -34), (151, -32), (153, -28), (153, -25), (151, -21),
         (149, -18), (146, -16), (143, -13), (142, -11), (142, -14),
         (140, -18), (139, -20), (136, -16), (136, -12), (134, -12),
         (132, -11), (130, -13), (127, -14), (124, -16), (122, -17),
         (119, -20), (117, -21)],
        [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (147, -8),
         (142, -6), (137, -4), (132, -3)],
        [(167, -45), (170, -43), (172, -41), (174, -39), (176, -37),
         (178, -37), (175, -39), (173, -41), (171, -43), (168, -46)],
        [(145, -41), (148, -41), (148, -43), (146, -43)],
    ]),
]

PINS = [
    (1, 50.5, 26.2), (2, 114.1, 22.5), (3, 36.6, 45.3), (4, -152.0, 64.0),
    (5, -122.0, 37.4), (6, 34.9, 31.8), (7, 4.35, 50.85), (8, 88.0, 15.5),
    (9, -1.5, 52.6), (10, 31.5, 49.0), (11, 30.2, 13.2), (12, 172.6, -43.5),
    (13, -165.0, 28.0),
]


def _in_poly(lon, lat, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and \
                (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 232, 214), outline=HAIR)
    lon0, lon1 = -168.0, 192.0
    lat0, lat1 = 84.0, -58.0

    def proj(lon, lat):
        return (x + (lon - lon0) / (lon1 - lon0) * w,
                y + (lat0 - lat) / (lat0 - lat1) * h)

    step = 6.4
    gy = y + 3
    while gy < y + h - 2:
        gx = x + 3
        while gx < x + w - 2:
            lon = lon0 + (gx - x) / w * (lon1 - lon0)
            lat = lat0 - (gy - y) / h * (lat0 - lat1)
            for _name, colour, polys in CONTINENTS:
                if any(_in_poly(lon, lat, p) for p in polys):
                    d.ellipse([gx - 1.5, gy - 1.5, gx + 1.5, gy + 1.5],
                              fill=colour)
                    break
            gx += step
        gy += step
    for num, lon, lat in PINS:
        px, py = proj(lon, lat)
        r = 8 if num < 10 else 9
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=2)
        f = font(SANS_B, 9 if num < 10 else 8)
        s = str(num)
        d.text((px - text_w(d, s, f) / 2, py - 6), s, font=f,
               fill=(255, 255, 255))
    if True:  # pin 13 marks a spacecraft: dashed ring in the Pacific
        px, py = proj(-165.0, 28.0)
        dashed_arc(d, [px - 14, py - 14, px + 14, py + 14], 0, 360, NAVY,
                   width=1, dash_deg=24, gap_deg=18)


# ---------------------------------------------------------------- layout
def draw_lead(d, item, x, y, w, h):
    art_h = 78
    item["art"](d, x, y, w, art_h)
    cy = section_row(d, x, y + art_h + 6, item["num"], item["label"], w)
    hf = font(SERIF_B, 16)
    lines = wrap(d, item["headline"], hf, w)
    for ln in lines[:3]:
        d.text((x, cy), ln, font=hf, fill=INK)
        cy += 20
    cy += 2
    sf = font(SANS, 11)
    for ln in wrap(d, item["summary"], sf, w)[:3]:
        d.text((x, cy), ln, font=sf, fill=(52, 52, 48))
        cy += 14


def draw_card(d, item, x, y, w, h):
    art_h = 44
    item["art"](d, x, y, w, art_h)
    cy = section_row(d, x, y + art_h + 4, item["num"], item["label"], w)
    hf = font(SERIF_B, 12)
    lines = wrap(d, item["headline"], hf, w)
    for ln in lines[:3]:
        d.text((x, cy), ln, font=hf, fill=INK)
        cy += 15
    cy += 1
    sf = font(SANS, 10)
    for ln in wrap(d, item["summary"], sf, w)[:4]:
        d.text((x, cy), ln, font=sf, fill=(52, 52, 48))
        cy += 12


def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0 = MARGIN
    x1 = W - MARGIN

    # ---- masthead
    d.line([x0, 14, x1, 14], fill=NAVY, width=3)
    kf = font(SANS_B, 12)
    draw_tracked(d, x0, 22, "THE DAY IN WORLD NEWS", kf, NAVY, tracking=3)
    right = "45 STORIES · 6 CONTINENTS · ONE PAGE"
    rw = tracked_w(d, right, kf, 3)
    draw_tracked(d, x1 - rw, 22, right, kf, NAVY, tracking=3)
    title = "Wednesday 18 November 2026"
    tf = fit_size(d, title, SERIF_B, 62, CONTENT_W)
    tw = text_w(d, title, tf)
    d.text(((W - tw) / 2, 40), title, font=tf, fill=INK)
    d.line([x0, 106, x1, 106], fill=NAVY, width=1)
    d.line([x0, 109, x1, 109], fill=NAVY, width=3)

    # ---- leads
    lead_y = 120
    lead_h = 196
    lead_w = (CONTENT_W - 2 * 15) // 3
    for i, item in enumerate(LEADS):
        lx = x0 + i * (lead_w + 15)
        if i:
            d.line([lx - 8, lead_y, lx - 8, lead_y + lead_h], fill=HAIR,
                   width=1)
        draw_lead(d, item, lx, lead_y, lead_w, lead_h)
    d.line([x0, lead_y + lead_h + 6, x1, lead_y + lead_h + 6], fill=HAIR,
           width=1)

    # ---- cards
    card_y = lead_y + lead_h + 16
    card_h = 152
    card_w = (CONTENT_W - 4 * 10) // 5
    for idx, item in enumerate(CARDS):
        row, col = divmod(idx, 5)
        cx = x0 + col * (card_w + 10)
        cy = card_y + row * (card_h + 8)
        if col:
            d.line([cx - 5, cy, cx - 5, cy + card_h], fill=HAIR, width=1)
        draw_card(d, item, cx, cy, card_w, card_h)
    cards_end = card_y + 2 * card_h + 8
    d.line([x0, cards_end + 4, x1, cards_end + 4], fill=HAIR, width=1)

    # ---- stat strip
    stat_y = cards_end + 12
    hf = font(SANS_B, 11)
    label = "BY THE NUMBERS"
    lw = tracked_w(d, label, hf, 3)
    d.line([x0, stat_y + 6, (W - lw) / 2 - 12, stat_y + 6], fill=NAVY,
           width=1)
    d.line([(W + lw) / 2 + 12, stat_y + 6, x1, stat_y + 6], fill=NAVY,
           width=1)
    draw_tracked(d, (W - lw) / 2, stat_y, label, hf, NAVY, tracking=3)
    stat_w = (CONTENT_W - 4 * 10) // 5
    for i, (num, lab) in enumerate(STATS):
        sx = x0 + i * (stat_w + 10)
        nf = fit_size(d, num, SERIF_B, 27, stat_w)
        nw = text_w(d, num, nf)
        d.text((sx + (stat_w - nw) / 2, stat_y + 18), num, font=nf, fill=RED)
        lf = font(SANS, 10)
        ly = stat_y + 52
        for ln in wrap(d, lab, lf, stat_w - 4)[:3]:
            lnw = text_w(d, ln, lf)
            d.text((sx + (stat_w - lnw) / 2, ly), ln, font=lf, fill=INK)
            ly += 13
    stats_end = stat_y + 84
    d.line([x0, stats_end, x1, stats_end], fill=HAIR, width=1)

    # ---- bottom band: map + briefs
    bot_y = stats_end + 10
    bot_h = 200
    map_w = 446
    tf2 = font(SANS_B, 11)
    draw_tracked(d, x0, bot_y, "WHERE IT HAPPENED", tf2, NAVY, tracking=2)
    draw_map(d, x0, bot_y + 18, map_w, bot_h - 40)
    # legend
    lx = x0
    ly = bot_y + bot_h - 16
    lf = font(SANS_B, 8)
    for name, colour, _polys in CONTINENTS:
        d.rectangle([lx, ly + 1, lx + 9, ly + 10], fill=colour, outline=HAIR)
        d.text((lx + 13, ly + 1), name, font=lf, fill=NAVY)
        lx += 13 + text_w(d, name, lf) + 10
    # briefs
    bx = x0 + map_w + 18
    bw = x1 - bx
    draw_tracked(d, bx, bot_y, "ALSO ON WEDNESDAY 18 NOVEMBER", tf2, NAVY,
                 tracking=2)
    col_w = (bw - 14) // 2
    row_h = 11.6
    for j, brief in enumerate(BRIEFS):
        col, row = divmod(j, 16)
        cx = bx + col * (col_w + 14)
        cy = bot_y + 19 + row * row_h
        num_s = str(j + 14)
        nf = font(SANS_B, 10)
        nw = text_w(d, num_s, nf)
        bf = fit_size(d, brief, SANS, 10, col_w - nw - 5)
        d.text((cx, cy), num_s, font=nf, fill=RED)
        d.text((cx + nw + 5, cy), brief, font=bf, fill=INK)

    # ---- footer
    foot_y = bot_y + bot_h + 12
    d.line([x0, foot_y, x1, foot_y], fill=NAVY, width=1)
    f1 = font(SERIF_I, 11)
    line1 = ("Every story was reported on Wednesday 18 November 2026; "
             "disputed claims are attributed.")
    d.text(((W - text_w(d, line1, f1)) / 2, foot_y + 7), line1, font=f1,
           fill=(52, 52, 48))
    f2 = font(SANS, 10)
    line2 = ("Sources: Reuters, AP, AFP, BBC, Al Jazeera and others. "
             "Original drawings.")
    d.text(((W - text_w(d, line2, f2)) / 2, foot_y + 25), line2, font=f2,
           fill=(52, 52, 48))
    return img


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    img = draw_page()
    img.save(out, format="PNG", optimize=False)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
