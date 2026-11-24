"""sprites2: the redrawn Terraria sprites (gdada Art run, 2026-11-24).

Every piece is drawn from lit primitives (tlib/art.py): one light from the upper left, five tones per material from one base colour, hard bands, a selective
outline, a specular pixel where something shines. Each item has a silhouette plan: one shape that breaks the outline (a blade, a haft, a ring, a plume) and one thing
only it carries. Sizes follow the content specs; a Terraria item is drawn at about the size it is used.
"""
import math
from . import art
from .art import ramp, lit_ellipse, lit_poly, lit_line, outline_sel, specular
from .psprite import Canvas, CLEAR, hexc, PALETTES

W = (255, 255, 255, 255)


def R(name):
    """A five-tone ramp from a palette's base colour."""
    return ramp(PALETTES[name]["base"])


def finish(c, k=0.30):
    outline_sel(c, k)
    return c


# =============================================================== tiles (16 by 16, seamless)
def _brick_rows(c, r, rows, cols_a, cols_b, h):
    for row in range(rows):
        y0 = row * h
        off = 0 if row % 2 == 0 else cols_b
        bw = cols_a
        for k in range(-1, 16 // bw + 2):
            x0 = k * bw + off - (bw if off else 0)
            for yy in range(y0, y0 + h):
                for xx in range(x0, x0 + bw):
                    if not (0 <= xx < 16 and 0 <= yy < 16):
                        continue
                    ex, ey = xx - x0, yy - y0
                    tone = 2
                    if ey == 0 or ex == 0:
                        tone = 3
                    if ey == h - 1 or ex == bw - 1:
                        tone = 0 if (ey == h - 1 and ex != bw - 1) else 1
                    if ey == 0 and ex == 0:
                        tone = 4
                    c.set(xx, yy, r[tone])


def tile_brick(base="sand"):
    c = Canvas(16, 16)
    r = R(base)
    _brick_rows(c, r, 4, 8, 4, 4)
    for (x, y) in ((3, 1), (11, 2), (6, 5), (13, 6), (2, 9), (10, 10), (5, 13), (14, 14)):                 # a few deliberate pits
        c.set(x, y, r[1])
    return c


def tile_golden():
    c = Canvas(16, 16)
    r = R("gold")
    _brick_rows(c, r, 2, 16, 8, 8)
    for i in range(6):                                                                                       # a diagonal sheen across the courses
        c.set(2 + i * 2, 2 + i, r[4]); c.set(3 + i * 2, 2 + i, r[3])
    for i in range(5):
        c.set(10 + i, 10 + i % 3, r[4]) if i % 2 == 0 else None
    return c


def tile_hieroglyph():
    c = tile_brick("sand")
    lap, dk = R("lapis"), R("sand")
    glyphs = {(1, 0): ["01110", "11011", "01110"], (9, 4): ["00100", "01110", "00100", "00100"], (2, 8): ["10101", "11111", "10101"], (10, 12): ["11011", "00100"]}
    for (gx, gy), rows in glyphs.items():
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == "1" and 0 <= gx + i < 16 and 0 <= gy + j < 16:
                    c.set(gx + i, gy + j, lap[1] if j % 2 else lap[2])
                    c.set(gx + i, gy + j + 1, dk[1]) if False else None
    return c


def tile_lapis():
    c = Canvas(16, 16)
    r, g = R("lapis"), R("gold")
    for ty in range(2):
        for tx in range(2):
            for y in range(8):
                for x in range(8):
                    tone = 2
                    if y == 0 or x == 0:
                        tone = 3
                    if y == 7 or x == 7:
                        tone = 1
                    if (tx + ty) % 2:
                        tone = max(0, tone - 1)
                    c.set(tx * 8 + x, ty * 8 + y, r[tone])
    for (x, y) in ((3, 3), (11, 4), (5, 12), (13, 13), (9, 9)):                                             # gold flecks
        c.set(x, y, g[3]); c.set(x + 1, y, g[2])
    return c


def tile_marble(dark=False):
    c = Canvas(16, 16)
    r = ramp("#5a586c") if dark else R("marble")
    vein = r[3] if dark else r[1]
    for ty in range(2):
        for tx in range(2):
            for y in range(8):
                for x in range(8):
                    tone = 2
                    if y == 0 or x == 0:
                        tone = 3
                    if y == 7 or x == 7:
                        tone = 1
                    c.set(tx * 8 + x, ty * 8 + y, r[tone])
    pts = [((1, 5), (3, 3), (5, 3), (6, 1)), ((9, 7), (11, 5), (12, 4), (14, 2)), ((2, 14), (4, 12), (6, 12), (7, 10)), ((10, 15), (12, 13), (13, 12), (15, 10))]
    for p in pts:
        for a, b in zip(p, p[1:]):
            c.line(a[0], a[1], b[0], b[1], vein)
    return c


def tile_meander():
    c = tile_marble(False)
    lap = R("lapis")
    for k in range(2):                                                                                       # the Greek key, two repeats across, in a band through the middle
        x0 = k * 8
        for (x, y) in ((0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (0, 6), (0, 7), (0, 8), (0, 9), (2, 7), (2, 8), (3, 7), (4, 7), (4, 8), (4, 9), (6, 7), (6, 8), (6, 9), (5, 6), (6, 6), (7, 6)):
            c.set(x0 + x, y, lap[2])
    for x in range(16):
        c.set(x, 5, lap[3]); c.set(x, 11, lap[1])
    return c


def tile_bronze():
    c = Canvas(16, 16)
    r = R("bronze")
    for ty in range(2):
        for tx in range(2):
            for y in range(8):
                for x in range(8):
                    tone = 2
                    if y == 0 or x == 0:
                        tone = 3
                    if y == 7 or x == 7:
                        tone = 1
                    c.set(tx * 8 + x, ty * 8 + y, r[tone])
            c.set(tx * 8 + 2, ty * 8 + 2, r[4]); c.set(tx * 8 + 5, ty * 8 + 5, r[0])                         # rivets
            for i in range(3):
                c.set(tx * 8 + 3 + i, ty * 8 + 3 + i, r[3])
    return c


def tile_sheet(tile):
    out = Canvas(288, 270)
    for cy in range(15):
        for cx in range(16):
            out.paste(tile, cx * 18, cy * 18)
    return out


# =============================================================== projectiles and buffs
def proj_orb(pal, w=18, h=18):
    c = Canvas(w, h)
    r = R(pal)
    cx, cy = w / 2, h / 2
    lit_ellipse(c, cx, cy, w / 2 - 0.5, h / 2 - 0.5, r)
    lit_ellipse(c, cx, cy, w / 2 - 3, h / 2 - 3, [r[2], r[3], r[4], W, W])
    c.set(int(cx - 2), int(cy - 2), W)
    return finish(c, 0.45)


def proj_ray(pal, w=14, h=34):
    c = Canvas(w, h)
    r = R(pal)
    lit_poly(c, [(7, 0), (13, 20), (10, 33), (4, 33), (1, 20)], r)
    lit_poly(c, [(7, 4), (10, 20), (7, 30), (4, 20)], [r[2], r[3], r[4], W, W], flat=True)
    return finish(c, 0.45)


def proj_bolt(pal, w=14, h=40):
    c = Canvas(w, h)
    r = R(pal)
    lit_poly(c, [(9, 0), (2, 17), (7, 17), (3, 39), (12, 14), (7, 14), (12, 0)], r)
    c.line(8, 2, 5, 15, W); c.line(6, 17, 5, 32, r[4])
    return finish(c, 0.45)


def proj_rock(pal, w=18, h=18):
    c = Canvas(w, h)
    lit_poly(c, [(3, 6), (9, 1), (15, 5), (16, 12), (9, 17), (2, 12)], R(pal))
    c.set(6, 6, R(pal)[4])
    return finish(c)


def buff(pal, glyph, w=32, h=32):
    c = Canvas(w, h)
    r = R(pal)
    lit_ellipse(c, 16, 16, 14, 14, r)
    lit_ellipse(c, 16, 16, 10.5, 10.5, [r[0], r[1], r[2], r[2], r[3]], light=(0.5, 0.7))                   # a recessed face: lit from the other side
    g = [r[2], r[3], r[4], W, W]
    if glyph == "heart":
        lit_ellipse(c, 12, 13, 4.5, 4.5, g); lit_ellipse(c, 20, 13, 4.5, 4.5, g); lit_poly(c, [(7, 15), (25, 15), (16, 26)], g)
    elif glyph == "sun":
        lit_ellipse(c, 16, 16, 5, 5, g)
        for a in range(0, 360, 45):
            c.line(16 + 7 * math.cos(math.radians(a)), 16 + 7 * math.sin(math.radians(a)), 16 + 10 * math.cos(math.radians(a)), 16 + 10 * math.sin(math.radians(a)), g[3])
    elif glyph == "grape":
        for (x, y) in ((12, 11), (18, 11), (15, 16), (12, 21), (18, 21), (15, 25)):
            lit_ellipse(c, x, y, 3, 3, g)
        c.line(15, 7, 17, 4, hexc("#3a8a3a"))
    elif glyph == "bolt":
        lit_poly(c, [(19, 5), (10, 18), (15, 18), (12, 28), (22, 14), (17, 14), (21, 5)], g)
    return finish(c, 0.40)


# =============================================================== materials and potions
def mat_shard(pal, w=22, h=26):
    c = Canvas(w, h)
    r = R(pal)
    lit_poly(c, [(11, 1), (17, 8), (14, 24), (8, 24), (5, 8)], [r[1], r[2], r[3], r[3], r[4]], flat=True)
    lit_poly(c, [(11, 1), (5, 8), (11, 11)], [r[3], r[4], r[4], W, W], flat=True)                          # the upper-left facet, lit
    lit_poly(c, [(11, 1), (17, 8), (11, 11)], [r[2], r[3], r[3], r[3], r[3]], flat=True)
    lit_poly(c, [(11, 11), (17, 8), (14, 24)], [r[0], r[1], r[1], r[1], r[2]], flat=True)                   # the lower-right facet, shaded
    lit_poly(c, [(11, 11), (5, 8), (8, 24)], [r[1], r[2], r[2], r[2], r[3]], flat=True)
    return finish(c)


def mat_bar(pal, w=30, h=20):
    c = Canvas(w, h)
    r = R(pal)
    lit_poly(c, [(3, 15), (8, 6), (27, 6), (23, 15)], [r[1], r[2], r[2], r[2], r[2]], flat=True)             # the front face
    lit_poly(c, [(8, 6), (27, 6), (25, 9), (6, 9)], [r[3], r[3], r[4], r[4], r[4]], flat=True)               # the lit top
    lit_poly(c, [(23, 15), (27, 6), (25, 9), (22, 15)], [r[0], r[0], r[1], r[1], r[1]], flat=True)           # the shaded end
    c.line(6, 12, 20, 12, r[3]); specular(c, 10, 7)
    return finish(c)


def mat_flower(pal, w=26, h=30):
    c = Canvas(w, h)
    leaf = R("olive")
    c.line(13, 28, 13, 14, leaf[2]); c.line(14, 28, 14, 15, leaf[1])
    lit_poly(c, [(13, 24), (5, 18), (9, 24)], leaf); lit_poly(c, [(14, 22), (22, 17), (19, 23)], leaf)
    r = R(pal)
    for a in range(0, 360, 60):
        lit_ellipse(c, 13 + 6 * math.cos(math.radians(a)), 9 + 6 * math.sin(math.radians(a)), 3.4, 3.4, r)
    lit_ellipse(c, 13, 9, 3, 3, [r[2], r[3], r[4], W, W])
    return finish(c)


def mat_scale(pal, w=24, h=26):
    c = Canvas(w, h)
    r = R(pal)
    lit_poly(c, [(12, 1), (21, 8), (19, 23), (5, 23), (3, 8)], r)
    for (x, y) in ((8, 8), (15, 8), (12, 13), (8, 18), (16, 18)):                                           # scales within the scale
        lit_ellipse(c, x, y, 2.6, 2.6, [r[1], r[2], r[3], r[4], W])
    return finish(c)


def potion(pal, shape="flask", w=22, h=30):
    c = Canvas(w, h)
    r = R(pal)
    glass = ramp("#a8c8d8")
    if shape == "flask":
        lit_ellipse(c, 11, 20, 8.5, 8.5, glass); lit_poly(c, [(8, 5), (14, 5), (14, 14), (8, 14)], glass)
        lit_ellipse(c, 11, 21, 7, 6.8, r)
        lit_poly(c, [(9, 14), (13, 14), (13, 17), (9, 17)], r)
    else:
        lit_poly(c, [(4, 12), (18, 12), (18, 27), (4, 27)], glass); lit_poly(c, [(8, 5), (14, 5), (14, 12), (8, 12)], glass)
        lit_poly(c, [(5, 17), (17, 17), (17, 26), (5, 26)], r)
    lit_poly(c, [(7, 2), (15, 2), (14, 6), (8, 6)], ramp("#9a6a3a"))                                         # the cork
    c.set(7, 17, W); c.set(8, 16, W)
    return finish(c)


# =============================================================== weapons
def w_khopesh(pal, w=44, h=44):
    c = Canvas(w, h)
    r = R(pal)
    steel = ramp("#a8b4d0")
    # the blade: a sickle, curved up and over, thick at the belly, with a bright fuller
    pts_out, pts_in = [], []
    for i in range(0, 25):
        t = i / 24
        x = (1 - t) ** 2 * 16 + 2 * (1 - t) * t * 3 + t * t * 41
        y = (1 - t) ** 2 * 25 + 2 * (1 - t) * t * -4 + t * t * 9
        tx = 2 * (1 - t) * (3 - 16) + 2 * t * (41 - 3)
        ty = 2 * (1 - t) * (-4 - 25) + 2 * t * (9 + 4)
        ln = math.hypot(tx, ty) or 1
        nx, ny = -ty / ln, tx / ln
        wd = 4.6 * (1 - t * 0.8) + 0.5
        pts_out.append((x - nx * wd, y - ny * wd))
        pts_in.append((x + nx * wd * 0.75, y + ny * wd * 0.75))
    lit_poly(c, pts_out + pts_in[::-1], steel)
    for i in range(2, 21, 1):                                                                                # the fuller: a bright line along the blade
        t = i / 24
        c.set(int((1 - t) ** 2 * 16 + 2 * (1 - t) * t * 3 + t * t * 41), int((1 - t) ** 2 * 25 + 2 * (1 - t) * t * -4 + t * t * 9), steel[4])
    lit_poly(c, [(12, 22), (22, 22), (22, 27), (12, 27)], r)                                                 # the guard
    lit_line(c, (11, 30), (17, 25), 2, 2, ramp("#6a4a2a"))                                                   # the grip, wrapped
    lit_line(c, (4, 38), (11, 31), 2.2, 2, ramp("#6a4a2a"))
    lit_ellipse(c, 4, 39, 3.4, 3.4, r)                                                                       # the gold pommel
    c.set(4, 39, hexc("#3a6ad8")); specular(c, 3, 38)
    return finish(c)


def w_xiphos(pal, w=44, h=44):
    c = Canvas(w, h)
    r = R(pal)
    steel = ramp("#a8b4d0")
    lit_poly(c, [(41, 2), (43, 5), (34, 20), (24, 27), (18, 22), (25, 11)], steel)                            # a leaf-shaped blade: waist, belly, point
    for t in range(2, 14):                                                                                   # the midrib
        c.set(int(41 - t * 1.4), int(3 + t * 1.5), steel[4]); c.set(int(41 - t * 1.4) - 1, int(3 + t * 1.5) + 1, steel[1])
    lit_poly(c, [(14, 22), (23, 18), (26, 28), (17, 31)], r)                                                 # the bronze guard
    lit_line(c, (14, 31), (9, 36), 2, 2, ramp("#5a3a1a"))
    lit_ellipse(c, 6, 38, 3.2, 3.2, r); specular(c, 5, 37)
    return finish(c)


def w_labrys(pal, haft, w=44, h=44):
    c = Canvas(w, h)
    r = R(pal)
    wood = R(haft)
    lit_line(c, (5, 40), (31, 11), 1.8, 1.8, wood)
    for k in range(4):                                                                                       # leather wraps on the grip
        c.line(8 + k * 3, 37 - k * 3, 10 + k * 3, 39 - k * 3, ramp("#3a2a1a")[2])
    dx, dy, nx, ny = 27 / 41.0, -31 / 41.0, 31 / 41.0, 27 / 41.0
    tx, ty = 31, 10
    for sg in (-1, 1):                                                                                       # two crescent heads
        pts = [(tx - dx * 5, ty - dy * 5), (tx - dx * 12 + nx * sg * 11, ty - dy * 12 + ny * sg * 11), (tx + nx * sg * 15, ty + ny * sg * 15), (tx + dx * 12 + nx * sg * 11, ty + dy * 12 + ny * sg * 11), (tx + dx * 5, ty + dy * 5)]
        lit_poly(c, pts, r)
    lit_ellipse(c, tx, ty, 3.4, 3.4, r); specular(c, tx - 1, ty - 1)
    return finish(c)


def w_trident(pal, w=40, h=44):
    c = Canvas(w, h)
    r = R(pal)
    lit_line(c, (9, 42), (22, 14), 1.8, 1.8, ramp("#6a4a2a"))
    lit_poly(c, [(11, 15), (31, 13), (32, 18), (12, 20)], R("gold"))                                         # the crossbar, gold
    for (x, top) in ((13, 3), (22, 0), (31, 3)):                                                             # three long barbed prongs
        lit_poly(c, [(x - 1.6, 17), (x + 1.6, 17), (x + 1.4, top + 9), (x + 4, top + 7), (x, top), (x - 4, top + 7), (x - 1.4, top + 9)], r)
    return finish(c)


def w_thunderbolt(pal, w=36, h=44):
    c = Canvas(w, h)
    r = R(pal)
    lit_poly(c, [(24, 1), (9, 21), (17, 21), (9, 42), (30, 16), (21, 16), (29, 1)], r)                        # the fulmen: a jagged double-ended bolt
    lit_poly(c, [(15, 19), (25, 17), (26, 22), (14, 24)], R("gold"))                                         # the grip at the waist
    c.line(22, 3, 14, 18, W); c.line(18, 24, 12, 38, r[4])
    return finish(c, 0.38)


def w_staff(pal, accent, w=40, h=40):
    c = Canvas(w, h)
    wood, orb = R(pal), R(accent)
    lit_line(c, (6, 37), (26, 15), 1.8, 1.8, wood)
    lit_ellipse(c, 29, 11, 6.5, 6.5, [orb[1], orb[2], orb[3], orb[4], W])                                    # the orb
    ring = R("gold")
    for a in range(0, 360, 45):                                                                              # a crown of rays breaking the outline
        c.line(29 + 8 * math.cos(math.radians(a)), 11 + 8 * math.sin(math.radians(a)), 29 + 11 * math.cos(math.radians(a)), 11 + 11 * math.sin(math.radians(a)), ring[3])
    lit_poly(c, [(22, 14), (27, 18), (24, 21), (19, 17)], ring)                                              # the socket
    specular(c, 27, 9, 2)
    return finish(c)


def w_bow(pal, w=36, h=44):
    c = Canvas(w, h)
    r = R(pal)
    for i in range(0, 41):
        t = i / 40
        x = 7 + 17 * math.sin(t * math.pi)
        y = 2 + 40 * t
        lit_ellipse(c, x, y, 1.9 * (1 - 0.4 * abs(t - 0.5)), 1.9 * (1 - 0.4 * abs(t - 0.5)), r)
    c.line(7, 2, 7, 42, hexc("#e8e0c8"))                                                                     # the string
    lit_poly(c, [(21, 18), (27, 18), (27, 26), (21, 26)], ramp("#5a3a1a"))                                   # the wrapped grip
    for (x, y) in ((8, 2), (8, 42)):
        lit_ellipse(c, x, y, 2.2, 2.2, R("gold"))
    return finish(c)


# =============================================================== accessories
def a_ankh(pal, w=32, h=32):
    c = Canvas(w, h)
    r = R(pal)
    lit_ellipse(c, 16, 10, 7, 8, r); lit_ellipse(c, 16, 10, 3.6, 4.6, CLEARRAMP)                              # the loop, hollow
    lit_poly(c, [(13, 17), (19, 17), (19, 30), (13, 30)], r); lit_poly(c, [(6, 18), (26, 18), (26, 22), (6, 22)], r)
    lit_ellipse(c, 16, 20, 2.6, 2.6, R("lapis")); specular(c, 15, 19)
    return finish(c)


CLEARRAMP = [CLEAR] * 5


def a_charm(pal, accent, w=30, h=30):
    c = Canvas(w, h)
    r, g = R(pal), R(accent)
    for sx in (-1, 1):
        for i in range(3):                                                                                   # six legs
            c.line(15 + sx * 6, 13 + i * 4, 15 + sx * 12, 16 + i * 5, r[0])
    lit_ellipse(c, 15, 17, 8.5, 10.5, r)                                                                     # the shell
    lit_poly(c, [(14, 8), (16, 8), (16, 27), (14, 27)], g)                                                   # the gold seam
    lit_ellipse(c, 15, 8, 4.5, 3.2, [r[0], r[1], r[1], r[2], r[3]])                                          # the head
    c.set(12, 7, hexc("#ff4030")); c.set(18, 7, hexc("#ff4030"))
    specular(c, 11, 12)
    return finish(c)


def a_shield(pal, accent, w=36, h=36):
    c = Canvas(w, h)
    r, a = R(pal), R(accent)
    lit_ellipse(c, 18, 18, 16, 16, r)
    lit_ellipse(c, 18, 18, 12.5, 12.5, a, light=(0.5, 0.7))                                                  # a recessed field in the accent colour
    lit_ellipse(c, 18, 18, 9, 9, r)
    lit_poly(c, [(18, 10), (24, 17), (18, 27), (12, 17)], a)
    lit_ellipse(c, 18, 17, 3.2, 3.2, [r[2], r[3], r[4], W, W])                                               # the boss
    return finish(c)


def a_sandals(pal, accent, w=36, h=30):
    c = Canvas(w, h)
    r, wing = R(pal), R(accent)
    for i in range(5):                                                                                       # a big wing at the heel, five feathers fanning up and back
        a = math.radians(215 + i * 17)
        lit_poly(c, [(9, 14), (9 + 17 * math.cos(a), 14 + 17 * math.sin(a)), (9 + 13 * math.cos(a + 0.42), 14 + 13 * math.sin(a + 0.42)), (9 + 5 * math.cos(a + 0.5), 14 + 5 * math.sin(a + 0.5))], wing)
    lit_poly(c, [(8, 20), (31, 20), (35, 26), (33, 29), (7, 29)], ramp("#4a3220"))                           # the sole, toe curling up
    lit_poly(c, [(9, 14), (26, 14), (31, 21), (9, 21)], r)                                                   # the upper
    for x in (14, 19, 24):
        c.line(x, 14, x + 1, 21, r[4])
    return finish(c)


def a_laurel(pal, w=34, h=30):
    c = Canvas(w, h)
    r = R(pal)
    for k in range(10):
        for sx in (-1, 1):
            t = k / 9
            x = 17 + sx * (14 * math.cos(t * 2.2))
            y = 25 - 21 * math.sin(t * 2.2) * 0.9
            lit_ellipse(c, x, y, 3.6, 2.0, r)
    lit_ellipse(c, 17, 26, 3.2, 2.2, R("gold"))
    return finish(c)


def a_eye(pal, accent, w=30, h=38):
    c = Canvas(w, h)
    r, g = R(pal), R(accent)
    lit_ellipse(c, 15, 18, 13, 15, r)
    lit_poly(c, [(2, 18), (15, 8), (28, 18), (15, 28)], [g[0], g[1], g[2], g[3], g[4]], flat=True)             # the eye
    lit_ellipse(c, 15, 18, 5, 5, [g[1], g[2], g[3], g[4], W])
    lit_ellipse(c, 15, 18, 2, 4, ramp("#101010"))
    for a in range(0, 360, 36):                                                                              # snakes around the rim
        lit_ellipse(c, 15 + 14 * math.cos(math.radians(a)), 18 + 16 * math.sin(math.radians(a)), 1.8, 1.8, R("green"))
    return finish(c)


def a_cloak(pal, w=34, h=34):
    c = Canvas(w, h)
    r = R(pal)
    lit_poly(c, [(6, 5), (28, 5), (33, 31), (24, 27), (17, 32), (10, 27), (1, 31)], r)                       # a cloak with a scalloped hem
    for x in (10, 17, 24):
        c.line(x, 8, x - 1, 28, r[1])                                                                        # folds
    lit_ellipse(c, 17, 6, 4, 3, R("gold")); specular(c, 16, 5)                                               # the clasp
    return finish(c)


def a_disc(pal, w=34, h=34):
    c = Canvas(w, h)
    r = R(pal)
    for a in range(0, 360, 30):
        lit_poly(c, [(17 + 9 * math.cos(math.radians(a - 8)), 17 + 9 * math.sin(math.radians(a - 8))), (17 + 16 * math.cos(math.radians(a)), 17 + 16 * math.sin(math.radians(a))),
                     (17 + 9 * math.cos(math.radians(a + 8)), 17 + 9 * math.sin(math.radians(a + 8)))], r)
    lit_ellipse(c, 17, 17, 10, 10, r); lit_ellipse(c, 17, 17, 5, 5, [r[2], r[3], r[4], W, W])
    return finish(c)


# =============================================================== summons and bags
def s_cartouche(pal, accent, w=30, h=36):
    c = Canvas(w, h)
    r, a = R(pal), R(accent)
    lit_ellipse(c, 15, 17, 11, 15, r); lit_ellipse(c, 15, 17, 8, 12, [r[0], r[1], r[1], r[2], r[2]], light=(0.5, 0.7))
    for y in (8, 13, 18, 23):
        lit_poly(c, [(10, y), (20, y), (20, y + 2), (10, y + 2)], a)
    lit_poly(c, [(4, 31), (26, 31), (26, 35), (4, 35)], r)                                                   # the bar the name stands on
    return finish(c)


def s_scales(pal, accent, w=30, h=36):
    c = Canvas(w, h)
    r, a = R(pal), R(accent)
    lit_line(c, (15, 4), (15, 33), 1.6, 1.6, r); lit_poly(c, [(9, 32), (21, 32), (23, 35), (7, 35)], r)       # the stand
    lit_line(c, (3, 9), (27, 9), 1.3, 1.3, r)                                                                # the beam
    for x in (3, 27):
        c.line(x, 9, x - 2, 21, a[3]); c.line(x, 9, x + 2, 21, a[3])
        lit_poly(c, [(x - 5, 21), (x + 5, 21), (x + 3, 25), (x - 3, 25)], r)                                 # the pans
    lit_ellipse(c, 15, 4, 2.6, 2.6, R("gold"))
    return finish(c)


def s_relic(pal, accent, w=30, h=36):
    c = Canvas(w, h)
    r, a = R(pal), R(accent)
    for ang in range(0, 360, 30):
        lit_poly(c, [(15 + 8 * math.cos(math.radians(ang - 9)), 16 + 8 * math.sin(math.radians(ang - 9))), (15 + 14 * math.cos(math.radians(ang)), 16 + 14 * math.sin(math.radians(ang))),
                     (15 + 8 * math.cos(math.radians(ang + 9)), 16 + 8 * math.sin(math.radians(ang + 9)))], a)
    lit_ellipse(c, 15, 16, 8, 8, r); lit_ellipse(c, 15, 16, 4, 4, [a[2], a[3], a[4], W, W])
    lit_poly(c, [(9, 29), (21, 29), (23, 35), (7, 35)], R("basalt"))                                         # on a stand
    return finish(c)


def s_horn(pal, w=36, h=34):
    c = Canvas(w, h)
    r = R(pal)
    pts = []
    for i in range(0, 25):
        t = i / 24
        pts.append((5 + 28 * t, 27 - 22 * math.sin(t * 1.55), 5.2 - 4.4 * t))
    for (x, y, rr) in pts:
        lit_ellipse(c, x, y, rr, rr, r)
    for (x, y, rr) in pts[4:22:5]:
        c.line(x - rr, y + 1, x + rr, y - 1, r[1])                                                           # growth rings
    lit_ellipse(c, 5, 27, 5.5, 5.5, [r[0], r[0], r[1], r[1], r[2]])                                          # the mouth
    lit_ellipse(c, 5, 27, 3, 3, ramp("#2a2018"))
    return finish(c)


def s_mirror(pal, accent, w=30, h=38):
    c = Canvas(w, h)
    r, g = R(pal), R(accent)
    lit_line(c, (15, 24), (15, 36), 2, 2, r)
    lit_ellipse(c, 15, 13, 12, 13, r)
    lit_ellipse(c, 15, 13, 9, 10, [g[1], g[2], g[3], g[4], W], light=(0.4, 0.6))
    c.line(9, 8, 13, 12, W)
    for a in range(0, 360, 40):
        lit_ellipse(c, 15 + 12.5 * math.cos(math.radians(a)), 13 + 13.5 * math.sin(math.radians(a)), 1.6, 1.6, R("green"))
    return finish(c)


def s_offering(pal, accent, w=30, h=36):
    c = Canvas(w, h)
    r, a = R(pal), R(accent)
    lit_poly(c, [(5, 18), (25, 18), (21, 28), (9, 28)], r)                                                   # a bowl
    lit_poly(c, [(12, 28), (18, 28), (19, 34), (11, 34)], r); lit_poly(c, [(7, 34), (23, 34), (23, 36), (7, 36)], r)
    lit_poly(c, [(15, 2), (22, 14), (20, 18), (10, 18), (8, 14)], a)                                         # a flame rising from it
    lit_poly(c, [(15, 8), (19, 15), (17, 18), (12, 18), (11, 15)], [a[2], a[3], a[4], W, W], flat=True)
    return finish(c)


def s_bag(pal, accent, w=30, h=32):
    c = Canvas(w, h)
    r, a = R(pal), R(accent)
    lit_ellipse(c, 15, 21, 12, 10, r)                                                                        # the sack
    lit_poly(c, [(9, 15), (21, 15), (19, 5), (11, 5)], r)                                                    # the neck
    lit_poly(c, [(8, 12), (22, 12), (22, 15), (8, 15)], a)                                                   # the tie
    lit_poly(c, [(9, 2), (21, 2), (19, 6), (11, 6)], r)                                                      # the flared mouth
    lit_ellipse(c, 15, 23, 4.5, 4.5, a); specular(c, 13, 21)                                                 # the boss's emblem
    return finish(c)


# =============================================================== enemies (3 or 4 frames each, the same size as the hitbox)
def _legs(c, cx, hip, foot, swing, ra, rb, spread=5, thick=2.6):
    lit_line(c, (cx - spread + swing * 0.5, hip), (cx - spread - swing, foot), thick, thick - 0.4, rb)
    lit_line(c, (cx + spread - swing * 0.5, hip), (cx + spread + swing, foot), thick, thick - 0.4, ra)


def enemy_hoplite(frame, w=36, h=52):
    c = Canvas(w, h)
    br, sk, cl = R("bronze"), R("skin"), R("blood")
    sw = [0, 3, -3][frame % 3]
    bob = [0, -1, 0][frame % 3]
    cx = w // 2
    lit_line(c, (cx - 14, 4), (cx - 14, h - 3), 0.9, 0.9, ramp("#6a4a2a"))                                    # the spear, longer than the man
    lit_poly(c, [(cx - 17, 9), (cx - 14, 0), (cx - 11, 9)], ramp("#c8d0e0"))
    _legs(c, cx, 36 + bob, h - 3, sw, sk, ramp("#8a5a30"), 4.5, 3)
    lit_poly(c, [(cx - 9, 34 + bob), (cx + 9, 34 + bob), (cx + 8, 42 + bob), (cx - 8, 42 + bob)], cl)         # the red pteruges kilt
    lit_poly(c, [(cx - 9, 17 + bob), (cx + 9, 17 + bob), (cx + 8, 35 + bob), (cx - 8, 35 + bob)], br)        # the bronze cuirass
    c.line(cx - 6, 24 + bob, cx + 6, 24 + bob, br[4]); c.line(cx - 6, 29 + bob, cx + 6, 29 + bob, br[1])
    lit_line(c, (cx + 8, 19 + bob), (cx + 13, 30 + bob), 2.4, 2.2, sk)                                         # the free arm
    lit_ellipse(c, cx - 11, 28 + bob, 7, 11, br); lit_ellipse(c, cx - 11, 28 + bob, 4.2, 7.5, [br[3], br[3], br[4], br[4], W], light=(0.5, 0.7)); lit_ellipse(c, cx - 11, 28 + bob, 1.8, 1.8, [br[0]] * 5)   # the round shield on the spear arm
    lit_ellipse(c, cx, 12 + bob, 6.5, 6.5, sk)
    lit_ellipse(c, cx, 11 + bob, 7.6, 7.6, br); lit_poly(c, [(cx - 2, 11 + bob), (cx + 2, 11 + bob), (cx + 2, 19 + bob), (cx - 2, 19 + bob)], sk)     # a Corinthian helm, face in the slot
    lit_poly(c, [(cx - 8, 6 + bob), (cx - 3, 0), (cx + 4, -1), (cx + 9, 6 + bob), (cx + 4, 4 + bob), (cx - 3, 4 + bob)], cl)                       # the horsehair crest over the helm
    c.set(cx - 2, 14 + bob, hexc("#201008")); c.set(cx + 2, 14 + bob, hexc("#201008"))
    return finish(c)


def enemy_satyr(frame, w=36, h=52):
    c = Canvas(w, h)
    fur, sk, ho = R("wood"), R("skin"), R("bone")
    sw = [0, 2, -2][frame % 3]
    bob = [0, -1, 0][frame % 3]
    cx = w // 2
    for sx in (-1, 1):                                                                                       # goat legs: thigh forward, shin back, a hoof
        k = sx * sw * 0.6
        hip = (cx + sx * 4, 33 + bob)
        knee = (cx + sx * 4 + k + 3, 42)
        hoof = (cx + sx * 4 + k - 2, h - 3)
        lit_line(c, hip, knee, 3.4, 2.4, fur if sx > 0 else ramp("#4a3220")); lit_line(c, knee, hoof, 2.2, 1.6, fur if sx > 0 else ramp("#4a3220"))
        lit_poly(c, [(hoof[0] - 2, h - 5), (hoof[0] + 2, h - 5), (hoof[0] + 3, h - 1), (hoof[0] - 3, h - 1)], ramp("#2a1c14"))
    lit_poly(c, [(cx - 8, 18 + bob), (cx + 8, 18 + bob), (cx + 7, 36 + bob), (cx - 7, 36 + bob)], sk)       # the bare torso
    c.line(cx - 4, 26 + bob, cx + 4, 26 + bob, sk[1])
    lit_poly(c, [(cx - 8, 33 + bob), (cx + 8, 33 + bob), (cx + 9, 38 + bob), (cx - 9, 38 + bob)], R("olive"))
    lit_line(c, (cx - 8, 19 + bob), (cx - 13, 28 + bob), 2.4, 2, sk); lit_line(c, (cx + 8, 19 + bob), (cx + 11, 25 + bob), 2.4, 2, sk)
    lit_poly(c, [(cx + 6, 22 + bob), (cx + 14, 22 + bob), (cx + 14, 26 + bob), (cx + 6, 26 + bob)], ho)       # the pan-pipes, held out
    for x in (7, 9, 11, 13):
        c.line(cx + x, 26 + bob, cx + x, 28 + bob + (x % 3), ho[1])
    lit_ellipse(c, cx, 12 + bob, 6.5, 7, sk)
    for sx in (-1, 1):                                                                                       # horns curling out and up: they break the outline
        lit_poly(c, [(cx + sx * 5, 8 + bob), (cx + sx * 10, 5 + bob), (cx + sx * 13, -1 + bob), (cx + sx * 11, 6 + bob), (cx + sx * 6, 11 + bob)], ho)
    lit_poly(c, [(cx - 2, 17 + bob), (cx + 2, 17 + bob), (cx + 1, 22 + bob), (cx - 1, 22 + bob)], fur)       # a goatee
    c.set(cx - 3, 12 + bob, hexc("#201008")); c.set(cx + 3, 12 + bob, hexc("#201008"))
    return finish(c)


def enemy_cyclops(frame, w=40, h=56):
    c = Canvas(w, h)
    sk, wd = R("skin"), R("wood")
    sw = [0, 3, -3][frame % 3]
    bob = [0, -1, 0][frame % 3]
    cx = w // 2
    _legs(c, cx, 38 + bob, h - 3, sw, sk, ramp("#a06a38"), 6, 4)
    lit_poly(c, [(cx - 14, 40 + bob), (cx + 14, 40 + bob), (cx + 12, 48 + bob), (cx - 12, 48 + bob)], wd)    # a hide loincloth
    lit_poly(c, [(cx - 14, 18 + bob), (cx + 14, 18 + bob), (cx + 11, 42 + bob), (cx - 11, 42 + bob)], sk)    # a big barrel torso
    lit_poly(c, [(cx - 14, 18 + bob), (cx + 14, 18 + bob), (cx + 8, 24 + bob), (cx - 8, 24 + bob)], wd)      # a pelt over the shoulders
    lit_line(c, (cx - 14, 20 + bob), (cx - 18, 36 + bob), 4, 3.4, sk); lit_line(c, (cx + 14, 20 + bob), (cx + 17, 30 + bob), 4, 3.4, sk)
    lit_line(c, (cx + 17, 6 + bob), (cx + 17, 44 + bob), 2.2, 2.2, wd)                                       # a club: a trimmed tree
    lit_ellipse(c, cx + 17, 8 + bob, 5.4, 8, wd)
    lit_ellipse(c, cx, 12 + bob, 8.5, 9, sk)
    lit_ellipse(c, cx, 11 + bob, 4.4, 4.4, [ramp("#f0ece0")[1], ramp("#f0ece0")[2], ramp("#f0ece0")[3], ramp("#f0ece0")[4], W])               # the one great eye
    lit_ellipse(c, cx, 11 + bob, 2.0, 2.0, ramp("#101010")); c.set(cx - 1, 10 + bob, W)
    lit_poly(c, [(cx - 7, 6 + bob), (cx + 7, 6 + bob), (cx + 6, 8 + bob), (cx - 6, 8 + bob)], sk[0] and R("skin"))
    for sx in (-1, 1):
        lit_poly(c, [(cx + sx * 4, 18 + bob), (cx + sx * 6, 18 + bob), (cx + sx * 5, 23 + bob)], R("bone"))   # tusks
    return finish(c)


def enemy_bird(frame, w=34, h=28):
    c = Canvas(w, h)
    br = R("bronze")
    flap = [-6, 0, 7, 2][frame % 4]
    cx = w // 2
    for sx in (-1, 1):                                                                                       # two bronze wings, five feathers each, beating
        for i in range(5):
            tipx, tipy = cx + sx * (6 + i * 3.2), 9 - flap + i * 1.7
            lit_poly(c, [(cx + sx * 3, 14), (tipx, tipy), (tipx - sx * 2.5, tipy + 6), (cx + sx * 4, 17)], br if i % 2 else R("sand"))
    lit_ellipse(c, cx, 15, 5.5, 4.5, br)
    lit_ellipse(c, cx + 6, 11, 3.4, 3.2, R("bronze"))
    lit_poly(c, [(cx + 8, 10), (cx + 14, 12), (cx + 8, 14)], R("sun"))                                       # a long beak
    c.set(cx + 6, 10, hexc("#ff4030"))
    lit_poly(c, [(cx - 4, 16), (cx - 13, 23), (cx - 5, 19)], R("bronze"))                                     # the tail
    return finish(c)


def enemy_snake(frame, w=34, h=48):
    c = Canvas(w, h)
    g = R("green")
    for i in range(0, 40):
        t = i / 39
        x = 17 + 6.5 * math.sin(t * 8 + frame * 1.1) * (1 - t * 0.35)
        rr = 3.8 - 1.4 * t
        lit_ellipse(c, x, 47 - i, rr, rr, g)
        if i % 5 == 0:
            c.set(int(x), 47 - i, g[4])                                                                      # a diamond pattern down the back
    hx, hy = 17 + [0, 1, -1][frame % 3] * 1.0, 8
    lit_ellipse(c, hx, hy + 2, 6, 5, g)
    lit_poly(c, [(hx - 4, hy - 1), (hx + 4, hy - 1), (hx + 6, hy + 6), (hx - 6, hy + 6)], g)
    c.set(int(hx - 3), int(hy), hexc("#ffe040")); c.set(int(hx + 3), int(hy), hexc("#ffe040"))
    c.line(hx, hy + 7, hx, hy + 12, hexc("#d02830")); c.line(hx, hy + 12, hx - 2, hy + 14, hexc("#d02830")); c.line(hx, hy + 12, hx + 2, hy + 14, hexc("#d02830"))
    return finish(c)


def enemy_cobra(frame, w=34, h=48):
    c = Canvas(w, h)
    sa, gd = R("sand"), R("gold")
    for i in range(0, 38):
        t = i / 37
        x = 17 + 5 * math.sin(t * 7 + frame * 0.9) * (1 - t * 0.5)
        rr = 4.4 - 1.4 * t
        lit_ellipse(c, x, 47 - i, rr, rr, sa)
        if i % 6 == 0:
            lit_poly(c, [(x - rr, 47 - i - 1), (x + rr, 47 - i - 1), (x + rr, 47 - i + 1), (x - rr, 47 - i + 1)], sa[:1] * 0 + [sa[1]] * 5, flat=True)
    hx, hy = 17 + [0, 1, -1][frame % 3], 13
    lit_ellipse(c, hx, hy + 6, 14, 8, gd)                                                                    # the flared hood
    lit_ellipse(c, hx, hy + 7, 9, 5, [gd[0], gd[1], gd[2], gd[2], gd[3]], light=(0.4, 0.6))
    lit_ellipse(c, hx - 3, hy + 7, 1.8, 2, ramp("#201808")); lit_ellipse(c, hx + 3, hy + 7, 1.8, 2, ramp("#201808"))        # the spectacle mark
    lit_ellipse(c, hx, hy - 2, 6, 5, sa)
    c.set(hx - 3, hy - 4, hexc("#ff4030")); c.set(hx + 3, hy - 4, hexc("#ff4030"))
    c.line(hx - 1, hy - 1, hx - 1, hy + 2, W); c.line(hx + 1, hy - 1, hx + 1, hy + 2, W)                      # fangs
    return finish(c)


def enemy_guardian(frame, w=40, h=56):
    c = Canvas(w, h)
    st, gd, bas = R("sand"), R("gold"), R("basalt")
    sw = [0, 2, -2][frame % 3]
    bob = [0, -1, 0][frame % 3]
    cx = w // 2
    _legs(c, cx, 38 + bob, h - 4, sw, st, ramp("#a89868"), 5.5, 4)
    for sx in (-1, 1):
        lit_poly(c, [(cx + sx * 6 - 5, h - 6), (cx + sx * 6 + 5, h - 6), (cx + sx * 6 + 6, h - 2), (cx + sx * 6 - 6, h - 2)], gd)
    lit_poly(c, [(cx - 11, 17 + bob), (cx + 11, 17 + bob), (cx + 9, 38 + bob), (cx - 9, 38 + bob)], st)       # a stone torso
    lit_poly(c, [(cx - 12, 32 + bob), (cx + 12, 32 + bob), (cx + 13, 42 + bob), (cx - 13, 42 + bob)], gd)    # the gold kilt
    for x in range(cx - 10, cx + 11, 4):
        c.line(x, 33 + bob, x, 41 + bob, gd[1])
    lit_poly(c, [(cx - 12, 14 + bob), (cx + 12, 14 + bob), (cx + 10, 20 + bob), (cx - 10, 20 + bob)], gd)    # the broad collar
    lit_poly(c, [(cx - 2, 21 + bob), (cx + 2, 21 + bob), (cx + 2, 30 + bob), (cx - 2, 30 + bob)], gd); lit_poly(c, [(cx - 6, 24 + bob), (cx + 6, 24 + bob), (cx + 6, 26 + bob), (cx - 6, 26 + bob)], gd)   # an ankh on the chest
    lit_line(c, (cx - 11, 19 + bob), (cx - 15, 34 + bob), 3.6, 3, st); lit_line(c, (cx + 11, 19 + bob), (cx + 15, 31 + bob), 3.6, 3, st)
    lit_line(c, (cx + 16, 3 + bob), (cx + 15, 50 + bob), 1.2, 1.2, gd)                                       # a was-sceptre, taller than the head
    lit_ellipse(c, cx, 8 + bob, 6.4, 6.4, bas)                                                               # the jackal head
    lit_poly(c, [(cx + 1, 5 + bob), (cx + 13, 9 + bob), (cx + 13, 13 + bob), (cx + 1, 13 + bob)], bas)       # a long snout, in profile
    lit_poly(c, [(cx - 5, 3 + bob), (cx - 4, -3 + bob), (cx, 3 + bob)], bas); lit_poly(c, [(cx + 1, 3 + bob), (cx + 4, -3 + bob), (cx + 5, 3 + bob)], bas)    # ears that break the outline
    c.set(cx + 3, 7 + bob, hexc("#60f0ff")); c.set(cx + 4, 7 + bob, W)
    return finish(c)


def enemy_scarab(frame, w=30, h=24):
    c = Canvas(w, h)
    sc, gd = R("scarab"), R("gold")
    flap = [0, 4, 7, 4][frame % 4]
    cx = w // 2
    wing = ramp("#b8f0e8")
    for sx in (-1, 1):
        lit_poly(c, [(cx + sx * 3, 13), (cx + sx * 13, 6 - flap), (cx + sx * 14, 12 - flap), (cx + sx * 4, 16)], wing)
    lit_ellipse(c, cx, 15, 7.5, 7, sc)
    lit_poly(c, [(cx - 1, 9), (cx + 1, 9), (cx + 1, 21), (cx - 1, 21)], gd)
    lit_ellipse(c, cx, 9, 4, 3, [sc[0], sc[1], sc[1], sc[2], sc[2]])
    c.set(cx - 2, 8, hexc("#ff4030")); c.set(cx + 2, 8, hexc("#ff4030"))
    for dy in (14, 17, 20):
        c.line(cx - 7, dy, cx - 11, dy + 2, sc[0]); c.line(cx + 7, dy, cx + 11, dy + 2, sc[0])
    return finish(c)


# =============================================================== bosses (each with a silhouette plan that reads at 1x)
def _glow(c, cx, cy, r, tone):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r and c.get(cx + dx, cy + dy) == CLEAR:
                c.set(cx + dx, cy + dy, tone)


def boss_forgotten(frame, w=100, h=120):
    """Forgotten Pharaoh: a T. Arms stretched wide with crook and flail, the tall double crown breaks the top, a wrapped skirt below."""
    c = Canvas(w, h)
    gd, wr, bl = R("gold"), R("bone"), R("lapis")
    cx = w // 2
    b = [7, 5, 7, 9][frame % 4]
    lit_poly(c, [(cx - 22, 62 + b), (cx + 22, 62 + b), (cx + 30, h - 2), (cx - 30, h - 2)], wr)               # the wrapped skirt, a wide tapering mass
    for y in range(66 + b, h - 4, 6):
        c.line(cx - 24 + (y - 66) // 4, y, cx + 24 - (y - 66) // 4, y + 2, wr[1])
    lit_poly(c, [(cx - 20, 26 + b), (cx + 20, 26 + b), (cx + 24, 64 + b), (cx - 24, 64 + b)], wr)             # the torso
    for y in range(32 + b, 62 + b, 5):
        c.line(cx - 20, y, cx + 20, y + 2, wr[1])
    lit_poly(c, [(cx - 30, 24 + b), (cx + 30, 24 + b), (cx + 22, 38 + b), (cx - 22, 38 + b)], gd)             # the usekh collar
    for i in range(-4, 5):
        c.set(cx + i * 6, 30 + b, bl[2]); c.set(cx + i * 6, 34 + b, bl[3])
    for sx in (-1, 1):                                                                                       # arms out wide, bandaged
        el = (cx + sx * 40, 36 + b)
        lit_line(c, (cx + sx * 20, 28 + b), el, 5.5, 4.4, wr)
        hand = (cx + sx * 46, 16 + b + (frame % 2) * 2) if sx < 0 else (cx + sx * 46, 52 + b - (frame % 2) * 2)
        lit_line(c, el, hand, 4.4, 3.6, wr)
    # the crook, left: a long pole with a hooked head, the flail, right: three beaded lashes
    lit_line(c, (cx - 46, 6 + b), (cx - 46, 66 + b), 1.8, 1.8, gd)
    lit_poly(c, [(cx - 52, 2 + b), (cx - 40, 2 + b), (cx - 38, 8 + b), (cx - 44, 8 + b), (cx - 44, 12 + b), (cx - 50, 12 + b), (cx - 50, 8 + b)], gd)
    lit_line(c, (cx + 46, 50 + b), (cx + 46, 74 + b), 1.6, 1.6, gd)
    for k, dx in enumerate((-7, 0, 7)):
        for j in range(5):
            lit_ellipse(c, cx + 46 + dx * (j + 1) / 3.0 + (3 if frame % 2 else 0) * (k - 1), 76 + b + j * 6, 2.2, 2.2, gd)
    lit_ellipse(c, cx, 15 + b, 11, 12, gd)                                                                   # the death mask
    lit_poly(c, [(cx - 12, 16 + b), (cx + 12, 16 + b), (cx + 9, 40 + b), (cx - 9, 40 + b)], gd, flat=False) if False else None
    lit_poly(c, [(cx - 10, 20 + b), (cx - 15, 36 + b), (cx - 5, 30 + b)], bl); lit_poly(c, [(cx + 10, 20 + b), (cx + 15, 36 + b), (cx + 5, 30 + b)], bl)    # the lappets
    lit_poly(c, [(cx - 3, 24 + b), (cx + 3, 24 + b), (cx + 2, 38 + b), (cx - 2, 38 + b)], bl)                # the false beard
    for sx in (-1, 1):
        lit_ellipse(c, cx + sx * 4, 14 + b, 2.2, 1.7, ramp("#101820")); c.set(cx + sx * 4, 14 + b, hexc("#60f0ff"))
    lit_poly(c, [(cx - 12, 6 + b), (cx + 12, 6 + b), (cx + 8, 2 + b), (cx - 8, 2 + b)], bl)                   # the nemes headband
    lit_poly(c, [(cx - 7, 6 + b), (cx + 7, 6 + b), (cx + 5, -2 + b), (cx - 5, -2 + b)], R("sand"))            # the white crown of Upper Egypt, tall
    lit_poly(c, [(cx - 4, 0 + b), (cx + 4, 0 + b), (cx + 5, -2 + b), (cx - 5, -2 + b)], bl)
    lit_poly(c, [(cx - 5, 0), (cx + 5, 0), (cx + 4, 12), (cx - 4, 12)], R("blood")) if False else None
    return finish(c)


def boss_anubis(frame, w=90, h=130):
    """Anubis: tall and narrow. A jackal head in profile with two huge ears, a kilt, a was-staff in one hand and the scales of Maat in the other."""
    c = Canvas(w, h)
    bas, gd, sa = R("basalt"), R("gold"), R("sand")
    cx = w // 2 - 4
    b = [0, -2, 0, 2][frame % 4]
    sw = [0, 3, 0, -3][frame % 4]
    for sx in (-1, 1):
        lit_line(c, (cx + sx * 6, 74 + b), (cx + sx * 8 + sw * sx, h - 10), 7, 5, bas)                         # long legs
        lit_poly(c, [(cx + sx * 8 + sw * sx - 7, h - 12), (cx + sx * 8 + sw * sx + 8, h - 12), (cx + sx * 8 + sw * sx + 10, h - 3), (cx + sx * 8 + sw * sx - 8, h - 3)], gd)
    lit_poly(c, [(cx - 16, 66 + b), (cx + 16, 66 + b), (cx + 20, 92 + b), (cx - 20, 92 + b)], sa)             # the shendyt kilt
    for x in range(cx - 16, cx + 17, 5):
        c.line(x, 68 + b, x + (x - cx) // 8, 90 + b, sa[1])
    lit_poly(c, [(cx - 15, 66 + b), (cx + 15, 66 + b), (cx + 16, 72 + b), (cx - 16, 72 + b)], gd)
    lit_poly(c, [(cx - 18, 28 + b), (cx + 18, 28 + b), (cx + 13, 68 + b), (cx - 13, 68 + b)], bas)             # a narrow torso, a wide chest
    lit_poly(c, [(cx - 24, 24 + b), (cx + 24, 24 + b), (cx + 16, 40 + b), (cx - 16, 40 + b)], gd)             # the collar
    for i in range(-3, 4):
        c.set(cx + i * 6, 31 + b, R("lapis")[3])
    lit_line(c, (cx - 20, 30 + b), (cx - 34, 58 + b), 6, 4.6, bas)                                             # the right arm lowered, the scales hung from the hand
    lit_line(c, (cx - 34, 58 + b), (cx - 36, 74 + b), 4.4, 3.8, bas)
    sx0, sy0 = cx - 38, 76 + b
    c.line(sx0, sy0, sx0, sy0 + 3, gd[3]); lit_line(c, (sx0 - 14, sy0 + 5), (sx0 + 14, sy0 + 5), 1.4, 1.4, gd)
    for sx in (-14, 14):
        c.line(sx0 + sx, sy0 + 5, sx0 + sx, sy0 + 12, gd[1]); lit_ellipse(c, sx0 + sx, sy0 + 15, 7, 3, gd)
    lit_ellipse(c, sx0 + 14, sy0 + 11, 3, 3, R("blood"))                                                       # the heart on one pan
    lit_line(c, (cx + 20, 30 + b), (cx + 36, 44 + b), 6, 4.6, bas); lit_line(c, (cx + 36, 44 + b), (cx + 36, 56 + b), 4.4, 3.8, bas)
    lit_line(c, (cx + 38, 4 + b), (cx + 38, h - 4), 2.2, 2.2, gd)                                              # the was-staff, the tallest thing on the sheet
    lit_poly(c, [(cx + 33, 4 + b), (cx + 43, 4 + b), (cx + 47, -1 + b), (cx + 43, 10 + b), (cx + 33, 10 + b)], gd)
    lit_ellipse(c, cx, 14 + b, 10, 10, bas)                                                                    # the head
    lit_poly(c, [(cx + 2, 8 + b), (cx + 26, 14 + b), (cx + 27, 20 + b), (cx + 2, 22 + b)], bas)               # the snout
    lit_poly(c, [(cx + 24, 14 + b), (cx + 28, 14 + b), (cx + 28, 18 + b), (cx + 24, 18 + b)], ramp("#101010"))
    for dx, ht in ((-7, 20), (2, 24)):                                                                         # two enormous ears
        lit_poly(c, [(cx + dx - 3, 8 + b), (cx + dx + 4, 8 + b), (cx + dx + 2, 8 - ht + b), (cx + dx - 2, 8 - ht + 2 + b)], bas)
    lit_poly(c, [(cx - 11, 8 + b), (cx + 11, 8 + b), (cx + 9, 12 + b), (cx - 9, 12 + b)], gd)                 # the gold brow band
    c.line(cx + 4, 15 + b, cx + 20, 18 + b, gd[3])
    c.set(cx + 3, 14 + b, hexc("#ffe060")); c.set(cx + 4, 14 + b, W)
    return finish(c)


def boss_sun(frame, w=140, h=150):
    """Sun Pharaoh: a burning disc halo as large as the body with fifteen rays and a hovering gold torso whose hands carry a sun orb."""
    c = Canvas(w, h)
    gd, su = R("gold"), R("sun")
    cx, cy = w // 2, 62
    b = [0, -2, 0, 2][frame % 4]
    cy += b
    rot = frame * 0.12
    for i in range(16):                                                                                        # rays, long and short alternating, turning
        a = rot + i * math.tau / 16
        ln = 66 if i % 2 == 0 else 50
        lit_poly(c, [(cx + 30 * math.cos(a - 0.1), cy + 30 * math.sin(a - 0.1)), (cx + ln * math.cos(a), cy + ln * math.sin(a)), (cx + 30 * math.cos(a + 0.1), cy + 30 * math.sin(a + 0.1))], su, flat=True)
    lit_ellipse(c, cx, cy, 42, 42, ramp("#ff8a20"))                                                            # the disc
    lit_ellipse(c, cx, cy, 33, 33, [su[1], su[2], su[3], su[4], W], light=(0.0, -0.4))
    lit_poly(c, [(cx - 20, cy + 14), (cx + 20, cy + 14), (cx + 26, cy + 70), (cx + 8, cy + 84), (cx - 8, cy + 84), (cx - 26, cy + 70)], gd)       # the body, a robe fading to a tail of light
    lit_poly(c, [(cx - 8, cy + 84), (cx + 8, cy + 84), (cx + 3, h - 2), (cx - 3, h - 2)], su)
    for sx in (-1, 1):
        lit_line(c, (cx + sx * 18, cy + 22), (cx + sx * 34, cy + 44 - (frame % 2) * 4), 5, 4, gd)
        lit_line(c, (cx + sx * 34, cy + 44 - (frame % 2) * 4), (cx + sx * 16, cy + 56), 4, 3.4, gd)
    lit_ellipse(c, cx, cy + 56, 9, 9, [su[2], su[3], su[4], W, W]); lit_ellipse(c, cx, cy + 56, 13, 13, su) if False else None
    _glow(c, cx, cy + 56, 12, su[1])
    lit_ellipse(c, cx, cy + 56, 8, 8, [su[3], su[3], su[4], W, W])
    lit_poly(c, [(cx - 19, cy - 14), (cx + 19, cy - 14), (cx + 21, cy + 22), (cx + 8, cy + 24), (cx - 8, cy + 24), (cx - 21, cy + 22)], R("lapis"))   # the nemes, behind the face
    lit_ellipse(c, cx, cy - 2, 11, 13, gd)                                                                     # the face in the disc
    lit_poly(c, [(cx - 3, cy + 8), (cx + 3, cy + 8), (cx + 2, cy + 22), (cx - 2, cy + 22)], gd)
    for sx in (-1, 1):
        lit_ellipse(c, cx + sx * 5, cy - 2, 2.4, 1.8, ramp("#101820")); c.set(cx + sx * 5, cy - 2, hexc("#ffffff"))
    lit_poly(c, [(cx - 5, cy - 12), (cx - 1, cy - 20), (cx + 1, cy - 20), (cx + 5, cy - 12)], R("blood"))    # the uraeus
    return finish(c)


def boss_minotaur(frame, w=90, h=110):
    """Minotaur: a hunched bulk, shoulders higher than the head, a bull's head with horns spread wider than the body, the double axe over the shoulder."""
    c = Canvas(w, h)
    fur, sk, br = R("wood"), R("skin"), R("bronze")
    cx = w // 2
    b = [9, 7, 9, 11][frame % 4]
    sw = [0, 5, 0, -5][frame % 4]
    for sx in (-1, 1):
        lit_line(c, (cx + sx * 12, 66 + b), (cx + sx * 14 + sw * sx, h - 6), 12, 9, fur if sx > 0 else ramp("#4a3220"))
        lit_poly(c, [(cx + sx * 14 + sw * sx - 9, h - 10), (cx + sx * 14 + sw * sx + 9, h - 10), (cx + sx * 14 + sw * sx + 11, h - 1), (cx + sx * 14 + sw * sx - 11, h - 1)], ramp("#2a1c14"))
    lit_poly(c, [(cx - 22, 58 + b), (cx + 22, 58 + b), (cx + 24, 76 + b), (cx - 24, 76 + b)], R("blood"))     # a loin guard
    lit_poly(c, [(cx - 34, 26 + b), (cx + 34, 26 + b), (cx + 24, 66 + b), (cx - 24, 66 + b)], sk)              # a huge chest, wider than anything
    for y in (36, 46, 56):
        c.line(cx - 20, y + b, cx + 20, y + b, sk[1])
    c.line(cx, 28 + b, cx, 62 + b, sk[1])
    lit_poly(c, [(cx - 36, 22 + b), (cx + 36, 22 + b), (cx + 28, 36 + b), (cx - 28, 36 + b)], fur)              # the shoulder fur
    lit_line(c, (cx - 32, 30 + b), (cx - 37, 56 + b), 10, 8, sk); lit_line(c, (cx - 37, 56 + b), (cx - 33, 74 + b), 8, 7, sk)
    lit_line(c, (cx + 32, 30 + b), (cx + 37, 14 + b - (frame % 2) * 3), 10, 8, sk)
    lit_line(c, (cx + 38, 2 + b), (cx + 38, 50 + b), 2.4, 2.4, ramp("#6a4a2a"))                                         # the haft, crossing the shoulder
    lit_poly(c, [(cx + 30, 0 + b), (cx + 38, 4 + b), (cx + 44, 0 + b), (cx + 43, 18 + b), (cx + 38, 14 + b), (cx + 32, 18 + b)], br)               # the double-headed labrys
    pass
    lit_ellipse(c, cx - 2, 18 + b, 14, 13, fur)                                                                # the bull's head
    lit_poly(c, [(cx - 8, 22 + b), (cx + 10, 22 + b), (cx + 8, 38 + b), (cx - 6, 38 + b)], fur)                 # the muzzle
    lit_ellipse(c, cx + 1, 36 + b, 5, 3, R("bone")); c.set(cx - 1, 36 + b, hexc("#201008")); c.set(cx + 3, 36 + b, hexc("#201008"))
    lit_ellipse(c, cx + 1, 38 + b, 3.4, 1.6, br)
    for sx in (-1, 1):                                                                                         # the horns sweep out and up past the shoulders
        lit_poly(c, [(cx + sx * 9, 12 + b), (cx + sx * 24, 10 + b), (cx + sx * 38, -2 + b), (cx + sx * 36, 6 + b), (cx + sx * 24, 17 + b), (cx + sx * 12, 19 + b)], R("bone"))
        c.set(cx + sx * 12, 17 + b, hexc("#ff3020")); lit_ellipse(c, cx + sx * 6 - 2, 14 + b, 2.4, 1.8, ramp("#ff3020"))
    return finish(c)


def boss_medusa(frame, w=100, h=120):
    """Medusa: a coiled serpent body in a tall S below a woman's torso, a burst of snake hair around the head, one hand lifted."""
    c = Canvas(w, h)
    gr, sk, gd = R("green"), R("olive"), R("gold")
    cx = w // 2
    b = [9, 7, 9, 11][frame % 4]
    for i in range(0, 64):                                                                                     # the tail: a sine coil, thick at the waist
        t = i / 63
        x = cx + 22 * math.sin(t * 9 + frame * 0.6) * (0.4 + t * 0.6)
        y = 56 + b + t * (h - 60)
        rr = 13 - 9 * t
        lit_ellipse(c, x, y, rr, rr, gr)
        if i % 4 == 0:
            lit_poly(c, [(x - rr * 0.7, y), (x, y - 2), (x + rr * 0.7, y), (x, y + 2)], R("sun"), flat=True)
    lit_poly(c, [(cx - 14, 30 + b), (cx + 14, 30 + b), (cx + 12, 62 + b), (cx - 12, 62 + b)], sk)              # the torso
    lit_poly(c, [(cx - 16, 30 + b), (cx + 16, 30 + b), (cx + 12, 46 + b), (cx - 12, 46 + b)], gd)              # a gold breastplate
    lit_line(c, (cx - 14, 32 + b), (cx - 30, 52 + b), 5, 4, sk)
    lit_line(c, (cx + 14, 32 + b), (cx + 28, 16 + b), 5, 4, sk); lit_line(c, (cx + 28, 16 + b), (cx + 24, 2 + b - (frame % 2) * 3), 4, 3.4, sk)
    lit_ellipse(c, cx + 25, -2 + b, 5.5, 5.5, ramp("#80ffa0")); c.set(cx + 24, -3 + b, W)                       # a glowing petrifying orb in the raised hand
    for k in range(10):                                                                                        # snake hair bursting out all round the head
        a = math.pi * (1.0 + k / 9.0) + math.sin(frame * 0.8 + k) * 0.12
        pts = [(cx + 8 * math.cos(a), 16 + b + 8 * math.sin(a))]
        for j in range(1, 6):
            aa = a + math.sin(frame * 0.9 + k + j * 0.9) * 0.55 * j / 5
            pts.append((pts[-1][0] + 5.2 * math.cos(aa), pts[-1][1] + 5.2 * math.sin(aa) * 0.9 + (1.6 if j > 3 else 0)))
        for j in range(5):
            lit_line(c, pts[j], pts[j + 1], 2.0 - j * 0.28, 1.7 - j * 0.28, gr)
        c.set(int(pts[-1][0]), int(pts[-1][1]), hexc("#ffe040"))
    lit_ellipse(c, cx, 18 + b, 9, 10, sk)
    for sx in (-1, 1):
        lit_ellipse(c, cx + sx * 4, 17 + b, 2.2, 1.8, ramp("#fff060")); c.set(cx + sx * 4, 17 + b, hexc("#102010"))
    c.line(cx - 3, 24 + b, cx + 3, 24 + b, hexc("#401010"))
    return finish(c)


def boss_zeus(frame, w=130, h=150):
    """Zeus: a bearded giant in white robes with one arm thrown up holding a lightning bolt that breaks the whole top of the outline, storm cloud for a base."""
    c = Canvas(w, h)
    ma, gd, sk = R("marble"), R("gold"), R("skin")
    cx = w // 2
    b = [28, 26, 28, 30][frame % 4]
    cl = ramp("#58607a")
    for k in range(6):                                                                                         # the storm cloud the god stands on
        lit_ellipse(c, cx - 50 + k * 20, h - 16 + (k % 2) * 4, 18, 13, cl)
    lit_poly(c, [(cx - 34, 46 + b), (cx + 34, 46 + b), (cx + 48, h - 14), (cx - 48, h - 14)], ma)            # the long himation
    for x in range(cx - 40, cx + 41, 12):
        c.line(x, 56 + b, x + (x - cx) // 4, h - 18, ma[1])
    lit_poly(c, [(cx - 34, 40 + b), (cx + 34, 40 + b), (cx + 20, 60 + b), (cx - 40, 56 + b)], R("lapis"))    # a blue mantle thrown over one shoulder
    lit_line(c, (cx - 30, 44 + b), (cx - 52, 70 + b), 9, 7, sk); lit_line(c, (cx - 52, 70 + b), (cx - 40, 90 + b), 7, 6, sk)
    lit_line(c, (cx + 30, 44 + b), (cx + 48, 18 + b), 9, 7, sk)                                                # the right arm raised
    hand = (cx + 52, 6 + b - (frame % 2) * 2)
    lit_line(c, (cx + 48, 18 + b), hand, 7, 6, sk)
    pts = [(hand[0], hand[1]), (hand[0] - 10, hand[1] - 10), (hand[0] + 2, hand[1] - 14), (hand[0] - 8, hand[1] - 26), (hand[0] + 8, hand[1] - 28), (hand[0] + 2, hand[1] - 32)]
    for j in range(len(pts) - 1):                                                                              # a long zigzag bolt rising above the sprite
        lit_line(c, pts[j], pts[j + 1], 3, 2, [R("sun")[2], R("sun")[3], R("sun")[4], W, W])
    for x, y in pts:
        _glow(c, int(x), int(y), 3, R("sun")[1])
    lit_ellipse(c, cx, 28 + b, 13, 14, sk)                                                                     # the head
    lit_poly(c, [(cx - 12, 30 + b), (cx + 12, 30 + b), (cx + 8, 56 + b), (cx, 62 + b), (cx - 8, 56 + b)], ma)  # a great white beard
    lit_poly(c, [(cx - 14, 16 + b), (cx + 14, 16 + b), (cx + 16, 30 + b), (cx - 16, 30 + b)], ma) if False else None
    lit_ellipse(c, cx, 18 + b, 15, 8, ma)                                                                       # swept white hair
    lit_poly(c, [(cx - 14, 14 + b), (cx + 14, 14 + b), (cx + 12, 10 + b), (cx - 12, 10 + b)], gd)              # a gold fillet
    for sx in (-1, 1):
        lit_ellipse(c, cx + sx * 5, 27 + b, 2.4, 1.7, ramp("#101820")); c.set(cx + sx * 5, 27 + b, hexc("#80d0ff"))
    return finish(c)


def boss_head(kind, boss_fn):
    """A 24 by 24 head icon: the head of the boss, found from the top of its own drawing."""
    big = boss_fn(0)
    top = 0
    for y in range(big.h):
        if any(big.px[y * big.w + x] != CLEAR for x in range(big.w)):
            top = y
            break
    out = Canvas(24, 24)
    sy0, sx0 = top, 0
    span = int(big.h * 0.34)
    for y in range(24):
        for x in range(24):
            sx = int(x * big.w / 24)
            sy = sy0 + int(y * span / 24)
            out.px[y * 24 + x] = big.px[sy * big.w + sx] if sy < big.h else CLEAR
    outline_sel(out, 0.3)
    return out
