"""art: the shading toolkit for Terraria sprites (a gdada Art run's answer to flat fills).

Terraria's art is lit from the top left: a one-pixel dark outline, three to five tones per material, light on the upper-left edge, shade on the lower-right,
and a bright specular pixel or two. This module draws that from primitives (never hand-typed rows):

    ramp("#c88a40")                     five tones from one colour, hue-shifted (shadows go cool, highlights go warm)
    lit_ellipse(c, cx, cy, rx, ry, r)   a sphere lit from the upper left, banded with an ordered dither
    lit_poly(c, pts, r)                 a polygon lit from the upper left: lit upper-left edge, shaded lower-right edge, a gradient between
    lit_line(c, p0, p1, r0, r1, r)      a tapering limb, blade or haft
    outline_sel(c)                      a selective outline: each outline pixel is a dark version of the tone it surrounds
    silhouette(c, colour)               every opaque pixel in one flat colour (the flat read gdada judges first)
"""
import colorsys
import math
from .psprite import Canvas, CLEAR, hexc

LIGHT = (-0.55, -0.72)
BAYER = ((0.0, 0.5), (0.75, 0.25))


def _tone(rgb, dh, ds, vm):
    r, g, b = [v / 255.0 for v in rgb[:3]]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + dh) % 1.0
    s = max(0.0, min(1.0, s + ds))
    v = max(0.0, min(1.0, v * vm))
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255), 255)


def ramp(base):
    """Five tones: deep, shadow, base, light, high. Accepts '#rrggbb' or an (r, g, b, a) tuple."""
    rgb = hexc(base) if isinstance(base, str) else base
    return [_tone(rgb, -0.035, 0.12, 0.42), _tone(rgb, -0.018, 0.06, 0.70), _tone(rgb, 0, 0, 1.0), _tone(rgb, 0.014, -0.10, 1.18), _tone(rgb, 0.03, -0.34, 1.42)]


def _pick(v, x, y, bands=4.0, bias=0.0):
    """Quantise a 0..1 light value to a tone index 0..4 with an ordered dither at the band edges."""
    """Hard bands, no dither: clean cel shading reads as drawn, noise reads as unfinished (sprite-lessons L42)."""
    t = max(0.0, min(0.999, v + bias)) * bands
    return max(0, min(4, int(t)))


def lit_ellipse(c, cx, cy, rx, ry, r, light=LIGHT, bias=0.0):
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            nx, ny = (x + 0.5 - cx) / max(rx, 0.5), (y + 0.5 - cy) / max(ry, 0.5)
            d2 = nx * nx + ny * ny
            if d2 <= 1.0:
                nz = math.sqrt(1.0 - d2)
                v = 0.52 + 0.5 * (nx * light[0] + ny * light[1]) * 0.95 + (nz - 0.5) * 0.12
                c.set(x, y, r[_pick(v, x, y, 4.2, bias)])


def _mask(pts):
    ys = [p[1] for p in pts]
    cells = set()
    for y in range(int(min(ys)), int(max(ys)) + 1):
        xs = []
        for i in range(len(pts)):
            (xa, ya), (xb, yb) = pts[i], pts[(i + 1) % len(pts)]
            if (ya <= y + 0.5 < yb) or (yb <= y + 0.5 < ya):
                xs.append(xa + (y + 0.5 - ya) * (xb - xa) / (yb - ya))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(int(round(xs[i])), int(round(xs[i + 1]))):
                cells.add((x, y))
    return cells


def _edge_depth(cells, cap=3):
    """Chamfer distance of each cell to the outside (1 at the border), capped."""
    depth = {}
    frontier = [p for p in cells if any((p[0] + dx, p[1] + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for p in frontier:
        depth[p] = 1
    d = 1
    while frontier and d < cap:
        nxt = []
        for (x, y) in frontier:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q in cells and q not in depth:
                    depth[q] = d + 1
                    nxt.append(q)
        frontier = nxt
        d += 1
    return depth


def lit_cells(c, cells, r, light=LIGHT, bias=0.0, flat=False):
    if not cells:
        return
    xs = [p[0] for p in cells]
    ys = [p[1] for p in cells]
    cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
    rad = max(1.0, math.hypot(max(xs) - min(xs), max(ys) - min(ys)) / 2.0)
    depth = _edge_depth(cells)
    for (x, y) in cells:
        along = -((x - cx) * light[0] + (y - cy) * light[1]) / rad          # -1 on the lit side, +1 on the shaded side
        v = 0.55 - 0.34 * along
        if flat:
            v = 0.55
        d = depth.get((x, y), 9)
        if d == 1:
            v += 0.18 if along < -0.05 else -0.16
        elif d == 2:
            v += 0.06 if along < 0 else -0.05
        c.set(x, y, r[_pick(v, x, y, 4.2, bias)])


def lit_poly(c, pts, r, light=LIGHT, bias=0.0, flat=False):
    lit_cells(c, _mask(pts), r, light, bias, flat)


def lit_line(c, p0, p1, r0, r1, r, light=LIGHT, bias=0.0):
    """A tapering limb: a quad between two ends plus a lit disc at each end."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln, dx / ln
    pts = [(x0 + nx * r0, y0 + ny * r0), (x1 + nx * r1, y1 + ny * r1), (x1 - nx * r1, y1 - ny * r1), (x0 - nx * r0, y0 - ny * r0)]
    cells = _mask(pts)
    for (ex, ey, er) in ((x0, y0, r0), (x1, y1, r1)):
        for yy in range(int(ey - er - 1), int(ey + er + 2)):
            for xx in range(int(ex - er - 1), int(ex + er + 2)):
                if (xx + 0.5 - ex) ** 2 + (yy + 0.5 - ey) ** 2 <= er * er:
                    cells.add((xx, yy))
    lit_cells(c, cells, r, light, bias)


def outline_sel(c, k=0.30):
    """A selective outline: a transparent pixel next to an opaque one becomes a dark version of that neighbour."""
    src = list(c.px)
    for y in range(c.h):
        for x in range(c.w):
            if src[y * c.w + x][3] == 0:
                best = None
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < c.w and 0 <= ny < c.h and src[ny * c.w + nx][3] > 0:
                        n = src[ny * c.w + nx]
                        if best is None or sum(n[:3]) < sum(best[:3]):
                            best = n
                if best is not None:
                    c.px[y * c.w + x] = (int(best[0] * k), int(best[1] * k * 0.95), int(best[2] * k * 1.1 + 6), 255)


def silhouette(c, colour=(20, 20, 28, 255), bg=(200, 200, 210, 255)):
    out = Canvas(c.w, c.h)
    for i, p in enumerate(c.px):
        out.px[i] = colour if p[3] > 0 else bg
    return out


def specular(c, x, y, size=1):
    for dy in range(size):
        for dx in range(size):
            c.set(x + dx, y + dy, (255, 252, 240, 255))


def grid_label_font():
    """A 3 by 5 bitmap font for digits and the letters G, A, B, C, D (grading sheet labels)."""
    return {"0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111", "4": "101101111001001", "5": "111100111001111", "6": "111100111101111",
            "7": "111001001001001", "8": "111101111101111", "9": "111101111001111", "G": "111100101101111", "A": "010101111101101", "B": "110101110101110", "C": "111100100100111", "D": "110101101101110"}


def label(c, text, x, y, colour=(255, 255, 255, 255), k=2):
    font = grid_label_font()
    for ch in text:
        g = font.get(ch)
        if g:
            for i, bit in enumerate(g):
                if bit == "1":
                    for yy in range(k):
                        for xx in range(k):
                            c.set(x + (i % 3) * k + xx, y + (i // 3) * k + yy, colour)
        x += 4 * k
