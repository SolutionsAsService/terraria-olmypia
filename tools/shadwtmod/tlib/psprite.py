"""psprite: a tiny pixel-art painter and the sprite recipes for tModLoader content (items, tiles, projectiles, enemies, bosses).

Everything is drawn from palettes and shapes in code, so a sprite is a recipe in a spec ("sprite": "khopesh", "palette": "gold"), not a file to paint.
Terraria textures are plain PNGs beside the class that uses them; sizes matter: a tile needs the 288 by 270 frame sheet, an enemy needs one
frame per animation step stacked vertically, a boss needs a `_Head_Boss` icon.
"""
import math
from .png import write_png

CLEAR = (0, 0, 0, 0)


def hexc(s, a=255):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def shade(c, d):
    return (max(0, min(255, c[0] + d)), max(0, min(255, c[1] + d)), max(0, min(255, c[2] + d)), c[3])


def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(4))


PALETTES = {
    "gold": {"base": "#e0b838", "dark": "#8a6a14", "light": "#fff0a0", "deep": "#4a3408"},
    "lapis": {"base": "#2a58b0", "dark": "#142c68", "light": "#6a98e8", "deep": "#0a1638"},
    "turquoise": {"base": "#2ab0a0", "dark": "#126058", "light": "#7ae8d8", "deep": "#08302c"},
    "sand": {"base": "#d4be84", "dark": "#8e7a48", "light": "#f0e2b0", "deep": "#4a3e20"},
    "basalt": {"base": "#3a3a46", "dark": "#1a1a22", "light": "#6a6a7c", "deep": "#08080c"},
    "linen": {"base": "#d8ceac", "dark": "#a09470", "light": "#f4ecd0", "deep": "#5a5238"},
    "flame": {"base": "#ff7a30", "dark": "#a02808", "light": "#ffd070", "deep": "#481004"},
    "sun": {"base": "#f0b020", "dark": "#a05a08", "light": "#fff4b0", "deep": "#502800"},
    "duat": {"base": "#40c8e8", "dark": "#1a6080", "light": "#c0f4ff", "deep": "#082838"},
    "scarab": {"base": "#1c6a78", "dark": "#0c3a48", "light": "#5ac8c0", "deep": "#041c24"},
    "blood": {"base": "#c02830", "dark": "#701018", "light": "#ff7a70", "deep": "#38080c"},
    "wood": {"base": "#8a6a3a", "dark": "#4a3418", "light": "#b08a52", "deep": "#241808"},
    "skin": {"base": "#c88a4a", "dark": "#8a5a28", "light": "#e8b078", "deep": "#4a2c10"},
    "bone": {"base": "#e6dfc8", "dark": "#a89c80", "light": "#fffaea", "deep": "#58503c"},
}


def pal(name):
    p = PALETTES[name]
    return {k: hexc(v) for k, v in p.items()}


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [CLEAR] * (w * h)

    def set(self, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y * self.w + x] = c

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.px[y * self.w + x]
        return CLEAR

    def rect(self, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.set(x, y, c)

    def line(self, x0, y0, x1, y1, c, r=0):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            if r:
                self.disc(x0, y0, r, c)
            else:
                self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.3:
                    self.set(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c, fill=True, ring=0.0):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                d = ((x - cx) / max(rx, 0.5)) ** 2 + ((y - cy) / max(ry, 0.5)) ** 2
                if d <= 1.0 and (fill or d >= 1.0 - ring):
                    self.set(x, y, c)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            for i in range(len(pts)):
                (xa, ya), (xb, yb) = pts[i], pts[(i + 1) % len(pts)]
                if (ya <= y + 0.5 < yb) or (yb <= y + 0.5 < ya):
                    xs.append(xa + (y + 0.5 - ya) * (xb - xa) / (yb - ya))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(round(xs[i])), int(round(xs[i + 1]))):
                    self.set(x, y, c)

    def outline(self, c):
        """A one-pixel outline around everything opaque."""
        src = list(self.px)
        for y in range(self.h):
            for x in range(self.w):
                if src[y * self.w + x][3] == 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.w and 0 <= ny < self.h and src[ny * self.w + nx][3] > 0:
                            self.px[y * self.w + x] = c
                            break

    def bevel(self, light, dark):
        """Light on the top-left edge of every shape, shade on the bottom-right: the pixel-art edge Terraria sprites have."""
        src = list(self.px)
        for y in range(self.h):
            for x in range(self.w):
                c = src[y * self.w + x]
                if c[3] == 0:
                    continue
                up = src[(y - 1) * self.w + x][3] if y > 0 else 0
                left = src[y * self.w + x - 1][3] if x > 0 else 0
                down = src[(y + 1) * self.w + x][3] if y < self.h - 1 else 0
                right = src[y * self.w + x + 1][3] if x < self.w - 1 else 0
                if up == 0 or left == 0:
                    self.px[y * self.w + x] = mix(c, light, 0.35)
                elif down == 0 or right == 0:
                    self.px[y * self.w + x] = mix(c, dark, 0.35)

    def paste(self, other, ox, oy):
        for y in range(other.h):
            for x in range(other.w):
                c = other.px[y * other.w + x]
                if c[3]:
                    self.set(ox + x, oy + y, c)

    def scaled(self, k):
        out = Canvas(self.w * k, self.h * k)
        for y in range(out.h):
            for x in range(out.w):
                out.px[y * out.w + x] = self.px[(y // k) * self.w + x // k]
        return out

    def save(self, path):
        write_png(path, self.w, self.h, self.px)


def sheet(frames):
    """Stack frames vertically (an NPC animation sheet)."""
    out = Canvas(frames[0].w, sum(f.h for f in frames))
    y = 0
    for f in frames:
        out.paste(f, 0, y)
        y += f.h
    return out


# ---------------------------------------------------------------- items
def item_khopesh(p, w=44, h=44):
    c = Canvas(w, h)
    pts = []
    for i in range(0, 25):                      # the blade: a sickle (a quadratic curve from the guard up and over), thick at the belly and fine at the tip
        t = i / 24
        x = (1 - t) ** 2 * 16 + 2 * (1 - t) * t * 3 + t * t * 41
        y = (1 - t) ** 2 * 25 + 2 * (1 - t) * t * -4 + t * t * 9
        pts.append((x, y, 3.4 - 2.6 * t))
    for (x, y, r) in pts:
        c.disc(x, y, r, p["light"] if r > 2.4 else p["base"])
    for (x, y, r) in pts[::2]:
        c.set(x + 1, y + 2, p["dark"])
    c.line(7, 37, 17, 27, p["wood"] if "wood" in p else shade(p["dark"], 10), 1)
    c.rect(14, 24, 20, 28, p["base"])
    c.ellipse(6, 38, 2, 2, p["base"])
    c.outline(p["deep"])
    c.bevel(p["light"], p["dark"])
    return c


def item_staff(p, orb, w=40, h=40):
    c = Canvas(w, h)
    c.line(6, 36, 28, 12, shade(p["dark"], 6), 1)
    c.line(6, 36, 28, 12, p["base"], 0)
    c.ellipse(31, 9, 6, 6, orb["base"])
    c.ellipse(31, 9, 3.5, 3.5, orb["light"])
    c.ellipse(31, 9, 6, 6, p["base"], fill=False, ring=0.4)
    for a in range(0, 360, 45):                  # rays
        c.line(31 + 7 * math.cos(math.radians(a)), 9 + 7 * math.sin(math.radians(a)), 31 + 10 * math.cos(math.radians(a)), 9 + 10 * math.sin(math.radians(a)), orb["light"])
    c.rect(18, 20, 20, 22, p["light"])
    c.outline(p["deep"])
    return c


def item_ankh(p, w=32, h=32):
    c = Canvas(w, h)
    c.ellipse(16, 9, 6, 7, p["base"])
    c.ellipse(16, 9, 3, 4, CLEAR)
    c.rect(14, 15, 18, 29, p["base"])
    c.rect(7, 18, 25, 21, p["base"])
    c.outline(p["deep"])
    c.bevel(p["light"], p["dark"])
    c.set(16, 9, CLEAR)
    return c


def item_charm(p, accent, w=30, h=30):
    c = Canvas(w, h)
    c.ellipse(15, 17, 8, 10, p["base"])                         # the shell
    c.rect(14, 8, 15, 26, p["dark"])                            # the wing-case seam
    c.ellipse(15, 8, 4, 3, p["dark"])                           # the head
    for dy in (14, 18, 22):                                     # legs
        c.line(7, dy, 3, dy + 3, p["deep"])
        c.line(23, dy, 27, dy + 3, p["deep"])
    c.ellipse(15, 17, 8, 10, accent["base"], fill=False, ring=0.25)
    c.set(12, 13, accent["light"]); c.set(18, 13, accent["light"])
    c.outline(p["deep"])
    c.bevel(p["light"], p["dark"])
    return c


def item_shard(p, w=22, h=26):
    c = Canvas(w, h)
    c.poly([(11, 1), (19, 9), (16, 24), (6, 24), (3, 9)], p["base"])
    c.poly([(11, 1), (19, 9), (11, 12)], p["light"])
    c.poly([(11, 12), (19, 9), (16, 24)], p["dark"])
    c.outline(p["deep"])
    return c


def item_cartouche(p, accent, w=30, h=36):
    c = Canvas(w, h)
    c.ellipse(15, 18, 10, 15, p["base"])
    c.ellipse(15, 18, 7, 12, p["dark"])
    for y in range(8, 30, 5):
        c.rect(11, y, 19, y + 1, accent["base"])
        c.rect(13, y + 2, 17, y + 2, accent["light"])
    c.rect(5, 32, 25, 34, p["base"])
    c.outline(p["deep"])
    c.bevel(p["light"], p["dark"])
    return c


def item_bag(p, accent, w=30, h=32):
    c = Canvas(w, h)
    c.ellipse(15, 21, 11, 9, p["base"])
    c.poly([(9, 14), (21, 14), (19, 6), (11, 6)], p["base"])
    c.rect(9, 12, 21, 14, accent["base"])
    c.ellipse(15, 6, 5, 2, accent["light"])
    c.ellipse(15, 22, 4, 4, accent["base"])
    c.outline(p["deep"])
    c.bevel(p["light"], p["dark"])
    return c


def item_tile(tile_canvas):
    return tile_canvas


# ---------------------------------------------------------------- tiles
def tile16(pattern, p, accent=None):
    c = Canvas(16, 16)
    c.rect(0, 0, 15, 15, p["base"])
    if pattern in ("brick", "golden", "hieroglyph"):
        for row in range(4):
            y = row * 4
            c.rect(0, y, 15, y, p["light"])
            c.rect(0, y + 3, 15, y + 3, p["dark"])
            off = 0 if row % 2 == 0 else 8
            for x in range(off, 16, 16):
                c.rect(x, y, x, y + 3, p["dark"])
            if off:
                c.rect(0, y, 0, y + 3, p["dark"])
        for i in range(0, 16, 3):                      # grain
            c.set((i * 5 + 3) % 16, (i * 3 + 1) % 16, shade(p["base"], -10))
    if pattern == "golden":
        c.rect(0, 0, 15, 0, p["light"]); c.rect(0, 15, 15, 15, p["dark"])
    if pattern == "hieroglyph" and accent:
        for (x, y, w, h) in ((2, 1, 2, 2), (6, 5, 1, 2), (10, 1, 3, 1), (3, 9, 2, 2), (9, 9, 1, 3), (12, 12, 2, 1)):
            c.rect(x, y, x + w - 1, y + h - 1, accent["base"])
    if pattern == "lapis":
        for y in range(16):
            for x in range(16):
                if (x // 4 + y // 4) % 2 == 0:
                    c.set(x, y, p["dark"])
        for k in range(0, 16, 4):
            c.rect(k, 0, k, 15, p["light"]); c.rect(0, k, 15, k, p["light"])
        for (x, y) in ((2, 2), (10, 6), (6, 12), (13, 13)):
            if accent:
                c.set(x, y, accent["base"])
    return c


def tile_sheet(tile):
    """The 288 by 270 frame sheet tModLoader expects for a block (18-pixel cells, 16 by 15 of them): every cell is the same seamless tile."""
    out = Canvas(288, 270)
    for cy in range(15):
        for cx in range(16):
            out.paste(tile, cx * 18, cy * 18)
    return out


# ---------------------------------------------------------------- projectiles
def projectile_orb(p, w=18, h=18):
    c = Canvas(w, h)
    c.ellipse(w / 2, h / 2, w / 2 - 1, h / 2 - 1, mix(p["base"], CLEAR, 0.0))
    c.ellipse(w / 2, h / 2, w / 2 - 4, h / 2 - 4, p["light"])
    c.ellipse(w / 2, h / 2, w / 2 - 6.5, h / 2 - 6.5, (255, 255, 255, 255))
    c.ellipse(w / 2, h / 2, w / 2 - 1, h / 2 - 1, p["dark"], fill=False, ring=0.2)
    return c


def projectile_ray(p, w=14, h=34):
    c = Canvas(w, h)
    c.poly([(7, 0), (13, 20), (10, 33), (4, 33), (1, 20)], p["base"])
    c.poly([(7, 4), (10, 20), (7, 30), (4, 20)], p["light"])
    c.line(7, 8, 7, 28, (255, 255, 255, 255))
    return c


# ---------------------------------------------------------------- creatures
def enemy_cobra(frame, w=34, h=48):
    p, hood, belly = pal("sand"), pal("gold"), pal("bone")
    c = Canvas(w, h)
    sway = [0, 1, -1][frame % 3]
    for i in range(0, 38):                                    # the body: an S of overlapping discs from the coil up to the neck
        t = i / 37
        x = 17 + 5 * math.sin(t * 7 + frame * 0.9) * (1 - t * 0.5) + sway * t
        y = 47 - i
        c.disc(x, y, 4.2 - 1.5 * t if t < 0.8 else 3.2, p["base"] if i % 4 else p["dark"])
    hx, hy = 17 + sway, 12
    c.ellipse(hx, hy + 4, 9, 8, hood["base"])                 # the hood
    c.ellipse(hx, hy + 4, 9, 8, hood["dark"], fill=False, ring=0.2)
    c.ellipse(hx - 3, hy + 3, 1.6, 2, hood["deep"]); c.ellipse(hx + 3, hy + 3, 1.6, 2, hood["deep"])
    c.ellipse(hx, hy - 3, 5, 4, p["base"])                     # the head
    c.rect(hx - 3, hy - 4, hx - 2, hy - 3, pal("blood")["base"]); c.rect(hx + 2, hy - 4, hx + 3, hy - 3, pal("blood")["base"])
    c.rect(hx - 1, hy - 1, hx - 1, hy + 2, (255, 255, 240, 255)); c.rect(hx + 1, hy - 1, hx + 1, hy + 2, (255, 255, 240, 255))
    c.outline(p["deep"])
    return c


def enemy_guardian(frame, w=40, h=56):
    st, gold, bas = pal("sand"), pal("gold"), pal("basalt")
    c = Canvas(w, h)
    bob = [0, -1, 0][frame % 3]
    step = [0, 2, -2][frame % 3]
    c.rect(13, 34 + bob, 18 + step, 54, st["dark"]); c.rect(21 - step, 34 + bob, 27, 54, st["base"])         # legs
    c.rect(11 + step, 52, 19 + step, 55, gold["dark"]); c.rect(21 - step, 52, 29 - step, 55, gold["dark"])
    c.rect(10, 16 + bob, 30, 36 + bob, st["base"])                                                         # torso
    c.rect(8, 30 + bob, 32, 38 + bob, gold["base"]); c.rect(8, 30 + bob, 32, 31 + bob, gold["light"])      # kilt
    c.rect(7, 18 + bob, 11, 36 + bob, st["dark"]); c.rect(29, 18 + bob, 33, 36 + bob, st["dark"])          # arms
    c.rect(6, 34 + bob, 12, 38 + bob, bas["base"]); c.rect(28, 34 + bob, 34, 38 + bob, bas["base"])
    c.rect(18, 20 + bob, 21, 28 + bob, gold["base"]); c.rect(15, 23 + bob, 24, 24 + bob, gold["base"])      # an ankh on the chest
    c.rect(12, 14 + bob, 28, 18 + bob, gold["base"])                                                       # collar
    c.ellipse(20, 8 + bob, 7, 7, bas["base"])                                                              # the jackal head
    c.poly([(26, 7 + bob), (38, 10 + bob), (38, 13 + bob), (26, 13 + bob)], bas["base"])
    c.poly([(14, 3 + bob), (15, -2 + bob), (18, 3 + bob)], bas["base"]); c.poly([(22, 3 + bob), (24, -2 + bob), (26, 3 + bob)], bas["base"])
    c.rect(22, 6 + bob, 24, 7 + bob, pal("duat")["light"])
    c.outline(bas["deep"])
    return c


def enemy_scarab(frame, w=30, h=24):
    sc, gold = pal("scarab"), pal("gold")
    c = Canvas(w, h)
    flap = [0, 3, 5, 3][frame % 4]
    c.poly([(15, 12), (3, 6 - flap), (1, 12 - flap), (13, 15)], (*sc["light"][:3], 190)); c.poly([(15, 12), (27, 6 - flap), (29, 12 - flap), (17, 15)], (*sc["light"][:3], 190))
    c.ellipse(15, 15, 7, 6, sc["base"])
    c.rect(15, 10, 15, 20, gold["base"])
    c.ellipse(15, 9, 4, 3, sc["dark"])
    c.rect(12, 8, 12, 8, pal("blood")["base"]); c.rect(18, 8, 18, 8, pal("blood")["base"])
    for dy in (14, 17, 20):
        c.line(8, dy, 4, dy + 2, sc["deep"]); c.line(22, dy, 26, dy + 2, sc["deep"])
    c.outline(sc["deep"])
    return c


def boss_pharaoh(frame, kind, w, h):
    """A floating pharaoh: a bust over a wisp of linen, a mask face, a crown and a broad collar, with wings or a halo by kind. frame 0..3 bobs and beats."""
    kinds = {
        "forgotten": dict(skin="gold", cloth="linen", trim="lapis", crown="white_red", glow="sun", wings=True),
        "anubis": dict(skin="basalt", cloth="linen", trim="gold", crown="jackal", glow="duat", wings=False),
        "sun": dict(skin="skin", cloth="sun", trim="flame", crown="halo", glow="sun", wings=True),
    }
    k = kinds[kind]
    skin, cloth, trim, glow = pal(k["skin"]), pal(k["cloth"]), pal(k["trim"]), pal(k["glow"])
    gold = pal("gold")
    c = Canvas(w, h)
    cx = w // 2
    bob = [0, 2, 3, 1][frame % 4]
    flap = [0, 6, 10, 6][frame % 4]
    top = int(h * 0.14) + bob
    # wings or aura behind
    if k["wings"]:
        for side in (-1, 1):
            for i in range(7):
                ang = math.radians(200 - i * 14 - flap * 1.5) if side == 1 else math.radians(-20 + i * 14 + flap * 1.5)
                length = w * (0.46 - 0.035 * i)
                c.line(cx + side * 8, top + h * 0.35, cx + side * 8 + math.cos(ang) * length * (1 if side == 1 else -1) * (-1 if side == 1 else 1), top + h * 0.35 - math.sin(ang) * length * 0.55, trim["base"] if i % 2 else gold["base"], 2)
    # the linen wisp: a tapering shroud under the bust
    for yy in range(int(top + h * 0.38), h - 2):
        t = (yy - (top + h * 0.38)) / (h - 2 - (top + h * 0.38))
        half = (w * 0.2) * (1 - t * 0.85) + 2 * math.sin(yy * 0.5 + frame)
        c.rect(cx - half, yy, cx + half, yy, cloth["base"] if (yy // 3) % 2 else cloth["dark"])
    # the torso and collar
    c.ellipse(cx, top + h * 0.40, w * 0.22, h * 0.14, cloth["base"])
    c.ellipse(cx, top + h * 0.33, w * 0.26, h * 0.10, gold["base"])
    c.ellipse(cx, top + h * 0.33, w * 0.20, h * 0.07, trim["base"])
    c.ellipse(cx, top + h * 0.33, w * 0.14, h * 0.045, gold["light"])
    # arms crossed holding a crook and flail
    c.line(cx - w * 0.22, top + h * 0.46, cx + w * 0.10, top + h * 0.40, cloth["dark"], 2)
    c.line(cx + w * 0.22, top + h * 0.46, cx - w * 0.10, top + h * 0.40, cloth["dark"], 2)
    c.line(cx - w * 0.24, top + h * 0.20, cx - w * 0.20, top + h * 0.58, gold["base"], 1)
    c.line(cx + w * 0.24, top + h * 0.20, cx + w * 0.20, top + h * 0.58, gold["base"], 1)
    # the head
    hr = w * 0.15
    c.ellipse(cx, top + h * 0.17, hr, hr * 1.15, skin["base"])
    c.rect(cx - hr * 0.6, top + h * 0.15, cx - hr * 0.2, top + h * 0.15 + 1, glow["light"]); c.rect(cx + hr * 0.2, top + h * 0.15, cx + hr * 0.6, top + h * 0.15 + 1, glow["light"])
    c.rect(cx - hr * 0.7, top + h * 0.15 - 2, cx - hr * 0.1, top + h * 0.15 - 2, trim["base"]); c.rect(cx + hr * 0.1, top + h * 0.15 - 2, cx + hr * 0.7, top + h * 0.15 - 2, trim["base"])
    c.rect(cx - 1, top + h * 0.19, cx, top + h * 0.22, skin["dark"])
    c.rect(cx - hr * 0.4, top + h * 0.25, cx + hr * 0.4, top + h * 0.25, skin["dark"])
    c.rect(cx - 1, top + h * 0.27, cx, top + h * 0.34, trim["base"])                                       # the false beard
    # the crown
    if k["crown"] == "white_red":
        c.rect(cx - hr * 1.1, top + h * 0.05, cx + hr * 1.1, top + h * 0.08, trim["base"])                  # nemes band
        c.poly([(cx - hr * 1.1, top + h * 0.08), (cx - hr * 1.5, top + h * 0.30), (cx - hr * 0.8, top + h * 0.26)], trim["base"])
        c.poly([(cx + hr * 1.1, top + h * 0.08), (cx + hr * 1.5, top + h * 0.30), (cx + hr * 0.8, top + h * 0.26)], trim["base"])
        c.ellipse(cx, top + h * 0.03, hr * 0.9, h * 0.04, pal("blood")["base"])
        c.poly([(cx - hr * 0.45, top + h * 0.03), (cx + hr * 0.45, top + h * 0.03), (cx + hr * 0.3, top - h * 0.12), (cx - hr * 0.3, top - h * 0.12)], (240, 236, 224, 255))
    elif k["crown"] == "jackal":
        c.poly([(cx - hr * 0.9, top + h * 0.07), (cx - hr * 0.7, top - h * 0.12), (cx - hr * 0.35, top + h * 0.06)], skin["base"])
        c.poly([(cx + hr * 0.9, top + h * 0.07), (cx + hr * 0.7, top - h * 0.12), (cx + hr * 0.35, top + h * 0.06)], skin["base"])
        c.poly([(cx, top + h * 0.16), (cx + hr * 1.6, top + h * 0.20), (cx + hr * 1.6, top + h * 0.25), (cx, top + h * 0.25)], skin["base"])   # the snout, in profile
        c.rect(cx + hr * 0.2, top + h * 0.15, cx + hr * 0.4, top + h * 0.16, glow["light"])
    elif k["crown"] == "halo":
        c.ellipse(cx, top + h * 0.12, w * 0.34, w * 0.34, gold["base"], fill=False, ring=0.14)
        for a in range(0, 360, 30):
            r0, r1 = w * 0.36, w * 0.46
            c.line(cx + r0 * math.cos(math.radians(a + frame * 4)), top + h * 0.12 + r0 * math.sin(math.radians(a + frame * 4)), cx + r1 * math.cos(math.radians(a + frame * 4)), top + h * 0.12 + r1 * math.sin(math.radians(a + frame * 4)), glow["light"], 1)
        c.rect(cx - hr * 1.0, top + h * 0.05, cx + hr * 1.0, top + h * 0.08, gold["base"])
    c.outline(pal("basalt")["deep"])
    return c


def boss_head_icon(kind, size=24):
    c = boss_pharaoh(0, kind, 48, 52)
    out = Canvas(size, size)
    for y in range(size):
        for x in range(size):
            out.px[y * size + x] = c.px[int(y * 0.75) * c.w + int(x * 2 * 0.95)] if int(y * 0.75) < c.h and int(x * 2 * 0.95) < c.w else CLEAR
    return out


# ---------------------------------------------------------------- Greek (Olympian) palettes and sprites
PALETTES.update({
    "marble": {"base": "#e8e6ee", "dark": "#a8a6b6", "light": "#ffffff", "deep": "#4a4858"},
    "blackmarble": {"base": "#34323e", "dark": "#18161e", "light": "#6a687a", "deep": "#08060c"},
    "bronze": {"base": "#c88a40", "dark": "#7a4a1c", "light": "#f0c070", "deep": "#3a200a"},
    "olive": {"base": "#6a8a3a", "dark": "#3a5018", "light": "#a8c868", "deep": "#1c2c08"},
    "storm": {"base": "#8ab8f0", "dark": "#3a68b8", "light": "#f0faff", "deep": "#14284c"},
    "wine": {"base": "#7a2a58", "dark": "#40102c", "light": "#c868a0", "deep": "#200818"},
    "ambrosia": {"base": "#f0d890", "dark": "#b08838", "light": "#fffbe0", "deep": "#58400c"},
    "sea": {"base": "#2a88c8", "dark": "#104870", "light": "#80d0f8", "deep": "#08243c"},
    "stone": {"base": "#9a9a9a", "dark": "#585858", "light": "#d0d0d0", "deep": "#282828"},
    "green": {"base": "#4a9a4a", "dark": "#245024", "light": "#8ad88a", "deep": "#0c280c"},
})


def tile16_greek(pattern, p, accent=None):
    c = Canvas(16, 16)
    c.rect(0, 0, 15, 15, p["base"])
    if pattern in ("marble", "blackmarble"):
        c.rect(0, 0, 15, 0, p["light"]); c.rect(0, 15, 15, 15, p["dark"]); c.rect(0, 0, 0, 15, p["light"]); c.rect(15, 0, 15, 15, p["dark"])
        for (x0, y0, x1, y1) in ((2, 3, 7, 8), (6, 8, 11, 6), (9, 2, 13, 11), (3, 11, 5, 14)):          # veins
            c.line(x0, y0, x1, y1, p["dark"] if pattern == "marble" else p["light"])
        for i in range(0, 16, 3):
            c.set((i * 7 + 2) % 16, (i * 5 + 4) % 16, shade(p["base"], -8))
    elif pattern == "meander":
        c.rect(0, 0, 15, 15, p["base"])
        c.rect(0, 0, 15, 0, p["light"]); c.rect(0, 15, 15, 15, p["dark"])
        key = accent or p
        col = key["dark"] if accent else p["dark"]
        for (x0, y0, x1, y1) in ((2, 12, 2, 4), (2, 4, 12, 4), (12, 4, 12, 10), (12, 10, 6, 10), (6, 10, 6, 7)):     # the Greek key
            c.line(x0, y0, x1, y1, col)
    elif pattern == "bronze":
        c.rect(0, 0, 15, 15, p["base"])
        for (x, y) in ((1, 1), (14, 1), (1, 14), (14, 14)):
            c.set(x, y, p["light"]); c.set(x + (1 if x < 8 else -1), y, p["dark"])
        c.rect(0, 7, 15, 8, p["dark"]); c.rect(7, 0, 8, 15, p["dark"])
        c.rect(0, 0, 15, 0, p["light"]); c.rect(0, 0, 0, 15, p["light"]); c.rect(0, 15, 15, 15, p["deep"]); c.rect(15, 0, 15, 15, p["deep"])
        c.rect(5, 5, 10, 10, p["light"]); c.rect(6, 6, 9, 9, p["base"])
    return c


def item_xiphos(p, w=44, h=44):
    c = Canvas(w, h)
    c.poly([(40, 3), (43, 6), (22, 28), (18, 24)], p["light"])
    c.poly([(40, 3), (43, 6), (22, 28), (22, 24)], p["base"])
    c.line(18, 24, 12, 30, p["dark"], 1)
    c.rect(14, 22, 24, 26, shade(p["dark"], 12))
    c.line(10, 32, 4, 38, shade(p["deep"], 30), 1)
    c.ellipse(4, 39, 3, 3, p["base"])
    c.outline(p["deep"])
    return c


def item_labrys(p, haft, w=44, h=44):
    c = Canvas(w, h)
    c.line(5, 40, 32, 9, haft["base"], 1)
    dx, dy = 27 / 41.0, -31 / 41.0                      # along the haft
    nx, ny = 31 / 41.0, 27 / 41.0                       # across it
    tx, ty = 31, 10
    for sg in (-1, 1):
        pts = [(tx - dx * 5, ty - dy * 5), (tx - dx * 9 + nx * sg * 13, ty - dy * 9 + ny * sg * 13), (tx + dx * 9 + nx * sg * 13, ty + dy * 9 + ny * sg * 13), (tx + dx * 5, ty + dy * 5)]
        c.poly(pts, p["base"])
        c.poly([pts[0], pts[1], ((pts[0][0] + pts[1][0]) / 2 + dx * 2, (pts[0][1] + pts[1][1]) / 2 + dy * 2)], p["light"])
    c.disc(tx, ty, 3, p["dark"])
    c.outline(p["deep"])
    return c


def item_trident(p, w=40, h=44):
    c = Canvas(w, h)
    c.line(10, 42, 26, 12, shade(p["dark"], 20), 1)
    c.line(14, 8, 14, 18, p["base"], 0); c.line(26, 6, 26, 16, p["base"], 0); c.line(20, 2, 20, 14, p["light"], 0)
    c.line(14, 18, 26, 16, p["base"], 1)
    for x in (14, 20, 26):
        c.poly([(x - 2, 6 if x != 20 else 3), (x, 0 if x == 20 else 1), (x + 2, 6 if x != 20 else 3)], p["light"])
    c.outline(p["deep"])
    return c


def item_thunderbolt(p, w=36, h=44):
    c = Canvas(w, h)
    c.poly([(22, 1), (8, 22), (17, 22), (10, 42), (30, 17), (20, 17), (28, 1)], p["base"])
    c.poly([(22, 1), (8, 22), (13, 22), (22, 5)], p["light"])
    c.line(20, 4, 14, 20, (255, 255, 255, 255)); c.line(20, 22, 15, 34, (255, 255, 255, 255))
    c.outline(p["deep"])
    return c


def item_shield(p, accent, w=36, h=36):
    c = Canvas(w, h)
    c.ellipse(18, 18, 15, 15, p["base"])
    c.ellipse(18, 18, 15, 15, accent["dark"], fill=False, ring=0.18)
    c.ellipse(18, 18, 9, 9, p["light"], fill=False, ring=0.2)
    c.poly([(18, 10), (24, 16), (18, 26), (12, 16)], accent["base"])
    c.ellipse(18, 17, 3, 3, p["deep"])
    c.outline(p["deep"])
    c.bevel(p["light"], p["dark"])
    return c


def item_sandals(p, accent, w=36, h=30):
    c = Canvas(w, h)
    c.poly([(6, 18), (28, 18), (33, 24), (31, 27), (5, 27)], p["dark"])           # the sole
    c.poly([(7, 14), (24, 14), (29, 19), (7, 19)], p["base"])                      # the upper
    for x in (11, 16, 21):
        c.line(x, 14, x + 1, 19, p["light"])
    c.rect(6, 10, 10, 19, p["base"])                                               # the ankle strap
    for i in range(4):                                                             # a wing at the heel: four white feathers fanning up and back
        a = math.radians(200 + i * 22)
        c.line(6, 11, 6 + 11 * math.cos(a), 11 + 11 * math.sin(a), accent["light"] if i % 2 else accent["base"], 1)
    c.outline(p["deep"])
    return c


def item_laurel(p, w=34, h=30):
    c = Canvas(w, h)
    for k in range(9):
        for sx in (-1, 1):
            t = k / 8
            x = 17 + sx * (13 - 12 * t * t) if False else 17 + sx * (14 * math.cos(t * 2.2))
            y = 24 - 20 * math.sin(t * 2.2) * 0.9
            c.ellipse(x, y, 3.2, 1.8, p["base"] if k % 2 else p["light"])
    c.ellipse(17, 25, 3, 2, shade(p["dark"], 10))
    c.outline(p["deep"])
    return c


def item_bar(p, w=30, h=20):
    c = Canvas(w, h)
    c.poly([(4, 16), (8, 6), (26, 6), (24, 16)], p["base"])
    c.poly([(8, 6), (26, 6), (23, 9), (7, 9)], p["light"])
    c.poly([(24, 16), (26, 6), (23, 9), (21, 16)], p["dark"])
    c.outline(p["deep"])
    return c


def item_potion(p, w=22, h=30):
    c = Canvas(w, h)
    c.ellipse(11, 20, 8, 8, p["base"])
    c.rect(8, 6, 13, 13, p["base"])
    c.ellipse(11, 22, 5, 4, p["light"])
    c.rect(7, 3, 14, 5, (120, 90, 60, 255)); c.rect(8, 1, 13, 3, (170, 130, 80, 255))
    c.set(7, 17, (255, 255, 255, 255)); c.set(8, 16, (255, 255, 255, 255))
    c.outline(p["deep"])
    return c


def item_horn(p, w=36, h=34):
    c = Canvas(w, h)
    pts = []
    for i in range(0, 21):
        t = i / 20
        pts.append((6 + 26 * t, 26 - 22 * math.sin(t * 1.6) , 4.2 - 3.4 * t))
    for (x, y, r) in pts:
        c.disc(x, y, r, p["base"])
    for (x, y, r) in pts[::3]:
        c.disc(x, y + 1, max(0.5, r * 0.4), p["dark"])
    c.ellipse(6, 26, 5, 5, p["dark"])
    c.outline(p["deep"])
    c.bevel(p["light"], p["dark"])
    return c


def item_mirror(p, accent, w=30, h=38):
    c = Canvas(w, h)
    c.ellipse(15, 13, 11, 12, p["base"])
    c.ellipse(15, 13, 8, 9, accent["light"])
    c.line(10, 8, 14, 12, (255, 255, 255, 255))
    c.rect(13, 24, 17, 36, p["dark"])
    for a in range(0, 360, 40):                                # snakes around the rim
        c.disc(15 + 12 * math.cos(math.radians(a)), 13 + 13 * math.sin(math.radians(a)), 1.4, accent["base"])
    c.outline(p["deep"])
    return c


def item_flower(p, w=26, h=30):
    c = Canvas(w, h)
    c.line(13, 28, 13, 14, pal("olive")["base"], 0)
    c.ellipse(8, 22, 3, 1.5, pal("olive")["base"]); c.ellipse(18, 20, 3, 1.5, pal("olive")["base"])
    for a in range(0, 360, 60):
        c.ellipse(13 + 6 * math.cos(math.radians(a)), 9 + 6 * math.sin(math.radians(a)), 3.2, 3.2, p["base"])
    c.ellipse(13, 9, 3, 3, p["light"])
    c.outline(p["deep"])
    return c


def item_scale(p, w=24, h=26):
    c = Canvas(w, h)
    c.poly([(12, 1), (22, 9), (19, 24), (5, 24), (2, 9)], p["base"])
    for (x, y) in ((8, 8), (14, 8), (11, 13), (7, 18), (15, 18)):
        c.ellipse(x, y, 2.2, 2.2, p["light"])
    c.outline(p["deep"])
    return c


def item_bow(p, w=36, h=44):
    c = Canvas(w, h)
    for i in range(0, 31):
        t = i / 30
        x = 8 + 16 * math.sin(t * math.pi)
        y = 3 + 38 * t
        c.disc(x, y, 1.6, p["base"])
    c.line(8, 3, 8, 41, (235, 230, 215, 255))
    c.rect(22, 20, 26, 24, p["dark"])
    c.outline(p["deep"])
    return c


def item_spear_icon(p, w=44, h=44):
    return item_trident(p, w, h)


def projectile_bolt(p, w=14, h=40):
    c = Canvas(w, h)
    c.poly([(9, 0), (3, 18), (7, 18), (4, 39), (11, 16), (7, 16), (11, 0)], p["base"])
    c.line(8, 2, 5, 16, (255, 255, 255, 255)); c.line(7, 18, 6, 34, p["light"])
    return c


def projectile_rock(p, w=18, h=18):
    c = Canvas(w, h)
    c.poly([(3, 6), (9, 1), (15, 5), (16, 12), (9, 17), (2, 12)], p["base"])
    c.poly([(3, 6), (9, 1), (10, 8)], p["light"]); c.poly([(16, 12), (9, 17), (10, 8)], p["dark"])
    c.outline(p["deep"])
    return c


def buff_icon(p, glyph, w=32, h=32):
    c = Canvas(w, h)
    c.ellipse(16, 16, 14, 14, p["dark"])
    c.ellipse(16, 16, 12, 12, p["base"])
    if glyph == "heart":
        c.ellipse(12, 13, 4, 4, p["light"]); c.ellipse(20, 13, 4, 4, p["light"]); c.poly([(8, 15), (24, 15), (16, 25)], p["light"])
    elif glyph == "sun":
        c.ellipse(16, 16, 5, 5, p["light"])
        for a in range(0, 360, 45):
            c.line(16 + 7 * math.cos(math.radians(a)), 16 + 7 * math.sin(math.radians(a)), 16 + 10 * math.cos(math.radians(a)), 16 + 10 * math.sin(math.radians(a)), p["light"])
    elif glyph == "grape":
        for (x, y) in ((12, 11), (18, 11), (15, 16), (12, 21), (18, 21), (15, 26) if False else (15, 25)):
            c.ellipse(x, y, 3, 3, p["light"])
    elif glyph == "bolt":
        c.poly([(18, 6), (10, 18), (15, 18), (13, 27), (22, 14), (17, 14), (21, 6)], p["light"])
    c.outline(p["deep"])
    return c


# ---- Greek creatures
def enemy_humanoid(frame, kind, w=36, h=52):
    br, wh, sk, ol = pal("bronze"), pal("marble"), pal("skin"), pal("olive")
    c = Canvas(w, h)
    bob = [0, -1, 0][frame % 3]
    step = [0, 2, -2][frame % 3]
    cx = w // 2
    cloth = {"hoplite": pal("blood"), "satyr": pal("wood"), "cyclops": pal("wood")}[kind]
    c.rect(cx - 7, 34 + bob, cx - 2 + step, h - 4, sk["dark"] if kind != "satyr" else pal("wood")["dark"]); c.rect(cx + 1 - step, 34 + bob, cx + 7, h - 4, sk["base"] if kind != "satyr" else pal("wood")["base"])
    if kind == "satyr":
        c.poly([(cx - 7, h - 12), (cx - 3, h - 12), (cx - 1, h - 4), (cx - 9, h - 4)], pal("wood")["dark"]); c.poly([(cx + 3, h - 12), (cx + 7, h - 12), (cx + 9, h - 4), (cx + 1, h - 4)], pal("wood")["base"])
    c.rect(cx - 8 - (3 if kind == "cyclops" else 0), 18 + bob, cx + 8 + (3 if kind == "cyclops" else 0), 36 + bob, br["base"] if kind == "hoplite" else sk["base"])      # torso
    if kind == "hoplite":
        c.rect(cx - 8, 18 + bob, cx + 8, 22 + bob, br["light"]); c.rect(cx - 8, 34 + bob, cx + 8, 38 + bob, cloth["base"])
        c.ellipse(cx + 10, 28 + bob, 7, 9, br["base"]); c.ellipse(cx + 10, 28 + bob, 7, 9, br["dark"], fill=False, ring=0.22); c.ellipse(cx + 10, 28 + bob, 2, 2, br["light"])   # the shield
        c.line(cx - 12, 14 + bob, cx - 12, h - 2, shade(br["dark"], 20), 0); c.poly([(cx - 14, 14 + bob), (cx - 12, 8 + bob), (cx - 10, 14 + bob)], wh["light"])        # the spear
    if kind == "satyr":
        c.rect(cx - 8, 34 + bob, cx + 8, 38 + bob, ol["dark"])
    if kind == "cyclops":
        c.rect(cx - 11, 34 + bob, cx + 11, 40 + bob, cloth["base"])
        c.line(cx + 12, 8 + bob, cx + 14, 40 + bob, pal("wood")["base"], 1); c.ellipse(cx + 13, 10 + bob, 5, 6, pal("wood")["dark"])                        # a club
    c.ellipse(cx, 12 + bob, 7, 7, sk["base"] if kind != "satyr" else pal("skin")["light"])                                                                 # head
    if kind == "hoplite":
        c.ellipse(cx, 11 + bob, 8, 8, br["base"]); c.rect(cx - 2, 11 + bob, cx + 2, 16 + bob, sk["base"]); c.rect(cx - 7, 11 + bob, cx - 6, 17 + bob, br["dark"]); c.rect(cx + 6, 11 + bob, cx + 7, 17 + bob, br["dark"])
        c.poly([(cx - 3, 4 + bob), (cx, -1 + bob), (cx + 3, 4 + bob), (cx + 3, 9 + bob), (cx - 3, 9 + bob)], pal("blood")["base"])                       # the crest
    if kind == "satyr":
        c.poly([(cx - 6, 8 + bob), (cx - 10, 2 + bob), (cx - 4, 5 + bob)], wh["base"]); c.poly([(cx + 6, 8 + bob), (cx + 10, 2 + bob), (cx + 4, 5 + bob)], wh["base"])    # horns
        c.rect(cx - 2, 16 + bob, cx + 1, 19 + bob, pal("wood")["dark"])
    if kind == "cyclops":
        c.ellipse(cx, 12 + bob, 9, 9, sk["base"])
        c.ellipse(cx, 11 + bob, 3.2, 3.2, (245, 240, 225, 255)); c.ellipse(cx, 11 + bob, 1.6, 1.6, (30, 20, 10, 255)); c.rect(cx - 5, 7 + bob, cx + 5, 7 + bob, sk["dark"])
        c.rect(cx - 4, 17 + bob, cx - 3, 20 + bob, wh["base"]); c.rect(cx + 3, 17 + bob, cx + 4, 20 + bob, wh["base"])
    else:
        c.set(cx - 3, 11 + bob, (30, 20, 10, 255)); c.set(cx + 3, 11 + bob, (30, 20, 10, 255))
    c.outline(ol["deep"])
    return c


def enemy_bird(frame, w=34, h=28):
    br = pal("bronze")
    c = Canvas(w, h)
    flap = [0, 4, 7, 4][frame % 4]
    for sx in (-1, 1):
        for i in range(5):
            c.line(w // 2 + sx * 4, 12, w // 2 + sx * (8 + i * 4), 8 - flap + i * 2, br["base"] if i % 2 else br["light"], 1)
    c.ellipse(w // 2, 14, 6, 5, br["base"]); c.ellipse(w // 2 + 6, 11, 3, 3, br["light"])
    c.poly([(w // 2 + 8, 11), (w // 2 + 14, 13), (w // 2 + 8, 14)], pal("wood")["light"])
    c.set(w // 2 + 7, 10, (255, 60, 40, 255))
    c.poly([(w // 2 - 5, 16), (w // 2 - 12, 22), (w // 2 - 4, 19)], br["dark"])
    c.outline(br["deep"])
    return c


def enemy_snake(frame, w=34, h=48):
    g = pal("green")
    c = Canvas(w, h)
    for i in range(0, 34):
        t = i / 33
        x = 17 + 6 * math.sin(t * 8 + frame * 1.0) * (1 - t * 0.4)
        c.disc(x, 47 - i, 3.6 - 1.2 * t, g["base"] if i % 3 else g["dark"])
    hx, hy = 17 + [0, 1, -1][frame % 3], 10
    c.ellipse(hx, hy, 5, 4, g["base"])
    c.rect(hx - 3, hy - 1, hx - 2, hy, (255, 220, 60, 255)); c.rect(hx + 2, hy - 1, hx + 3, hy, (255, 220, 60, 255))
    c.rect(hx, hy + 3, hx, hy + 8, pal("blood")["base"])
    c.outline(g["deep"])
    return c


def boss_minotaur(frame, w, h):
    sk, br, bas = pal("skin"), pal("bronze"), pal("basalt")
    c = Canvas(w, h)
    step = [0, 4, 0, -4][frame % 4]
    bob = [0, -2, 0, -2][frame % 4]
    cx = w // 2
    c.rect(cx - 22, h * 0.62, cx - 6 + step, h - 4, sk["dark"]); c.rect(cx + 6 - step, h * 0.62, cx + 22, h - 4, sk["base"])
    c.rect(cx - 26 + step, h - 10, cx - 4 + step, h - 3, bas["base"]); c.rect(cx + 4 - step, h - 10, cx + 26 - step, h - 3, bas["base"])
    c.ellipse(cx, h * 0.46 + bob, w * 0.34, h * 0.24, sk["base"])                                      # a barrel chest
    c.rect(cx - w * 0.30, h * 0.6 + bob, cx + w * 0.30, h * 0.68 + bob, br["base"]); c.rect(cx - w * 0.30, h * 0.6 + bob, cx + w * 0.30, h * 0.61 + bob, br["light"])  # the belt
    c.line(cx - w * 0.32, h * 0.36 + bob, cx - w * 0.44, h * 0.62 + bob, sk["dark"], 5); c.line(cx + w * 0.32, h * 0.36 + bob, cx + w * 0.46, h * 0.56 + bob, sk["dark"], 5)
    c.line(cx + w * 0.46, h * 0.56 + bob, cx + w * 0.40, h * 0.10 + bob, pal("wood")["base"], 2)    # the labrys haft
    c.poly([(cx + w * 0.40, h * 0.05 + bob), (cx + w * 0.50, h * 0.00 + bob), (cx + w * 0.50, h * 0.20 + bob), (cx + w * 0.40, h * 0.16 + bob)], br["light"])
    c.poly([(cx + w * 0.40, h * 0.05 + bob), (cx + w * 0.30, h * 0.00 + bob), (cx + w * 0.30, h * 0.20 + bob), (cx + w * 0.40, h * 0.16 + bob)], br["base"])
    c.ellipse(cx, h * 0.17 + bob, w * 0.17, h * 0.13, pal("wood")["base"])                             # the bull head
    c.ellipse(cx, h * 0.24 + bob, w * 0.10, h * 0.07, sk["light"])
    c.poly([(cx - w * 0.15, h * 0.12 + bob), (cx - w * 0.34, h * 0.02 + bob), (cx - w * 0.30, h * 0.10 + bob), (cx - w * 0.14, h * 0.18 + bob)], pal("bone")["base"])
    c.poly([(cx + w * 0.15, h * 0.12 + bob), (cx + w * 0.34, h * 0.02 + bob), (cx + w * 0.30, h * 0.10 + bob), (cx + w * 0.14, h * 0.18 + bob)], pal("bone")["base"])
    c.ellipse(cx - w * 0.07, h * 0.16 + bob, 2.2, 2.2, (255, 60, 40, 255)); c.ellipse(cx + w * 0.07, h * 0.16 + bob, 2.2, 2.2, (255, 60, 40, 255))
    c.ellipse(cx, h * 0.27 + bob, 3, 2, br["light"])                                                   # a nose ring
    c.outline(bas["deep"])
    return c


def boss_olympian(frame, kind, w, h):
    """A hovering Olympian: Medusa (a bust with a mane of snakes) or Zeus (a bearded king over storm clouds)."""
    k = {"medusa": dict(skin="green", hair="olive", cloth="marble", trim="gold", glow="sun"), "zeus": dict(skin="skin", hair="marble", cloth="marble", trim="storm", glow="storm")}[kind]
    skin, hair, cloth, trim, glow = pal(k["skin"]), pal(k["hair"]), pal(k["cloth"]), pal(k["trim"]), pal(k["glow"])
    gold = pal("gold")
    c = Canvas(w, h)
    cx = w // 2
    bob = [0, 2, 3, 1][frame % 4]
    sway = [0, 1, 2, 1][frame % 4]
    top = int(h * 0.14) + bob
    if kind == "zeus":                                                                                   # storm clouds and lightning behind
        for (dx, dy, r) in ((-0.30, 0.30, 0.16), (0.30, 0.30, 0.16), (-0.18, 0.18, 0.18), (0.18, 0.18, 0.18), (0.0, 0.10, 0.2)):
            c.ellipse(cx + dx * w, top + dy * h, r * w, r * w * 0.7, (120, 130, 160, 255))
        for sx in (-1, 1):
            c.poly([(cx + sx * w * 0.38, top + h * 0.05), (cx + sx * w * 0.30, top + h * 0.28), (cx + sx * w * 0.35, top + h * 0.28), (cx + sx * w * 0.28, top + h * 0.5), (cx + sx * w * 0.42, top + h * 0.22), (cx + sx * w * 0.37, top + h * 0.22)], glow["light"])
    if kind == "medusa":                                                                                 # a mane of snakes
        for i in range(12):
            a = math.radians(200 + i * 15)
            for t in range(10):
                x = cx + math.cos(a) * (w * 0.14 + t * 2.4) + math.sin(t * 0.9 + i + frame) * 2
                y = top + h * 0.16 - math.sin(a) * (w * 0.14 + t * 2.4) * 1.0
                c.disc(x, y, 1.6 if t < 9 else 2.2, hair["base"] if i % 2 else hair["dark"])
            c.set(cx + math.cos(a) * (w * 0.14 + 9 * 2.4), top + h * 0.16 - math.sin(a) * (w * 0.14 + 9 * 2.4), (255, 220, 60, 255))
    for yy in range(int(top + h * 0.38), h - 2):                                                         # the robe: a tapering drape
        t = (yy - (top + h * 0.38)) / (h - 2 - (top + h * 0.38))
        half = (w * 0.24) * (1 - t * 0.7) + 2 * math.sin(yy * 0.4 + frame)
        c.rect(cx - half, yy, cx + half, yy, cloth["base"] if (yy // 3) % 2 else cloth["dark"])
    c.ellipse(cx, top + h * 0.40, w * 0.24, h * 0.13, cloth["base"])
    c.rect(cx - w * 0.24, top + h * 0.34, cx + w * 0.24, top + h * 0.37, trim["base"])
    c.line(cx - w * 0.26, top + h * 0.40, cx - w * 0.38, top + h * 0.56 + sway, skin["base"], 3); c.line(cx + w * 0.26, top + h * 0.40, cx + w * 0.38, top + h * 0.56 - sway, skin["base"], 3)
    hr = w * 0.15
    c.ellipse(cx, top + h * 0.17, hr, hr * 1.15, skin["base"])
    c.rect(cx - hr * 0.6, top + h * 0.15, cx - hr * 0.2, top + h * 0.15 + 1, glow["light"]); c.rect(cx + hr * 0.2, top + h * 0.15, cx + hr * 0.6, top + h * 0.15 + 1, glow["light"])
    c.rect(cx - hr * 0.4, top + h * 0.25, cx + hr * 0.4, top + h * 0.25, skin["dark"])
    if kind == "zeus":
        c.poly([(cx - hr * 0.9, top + h * 0.20), (cx + hr * 0.9, top + h * 0.20), (cx + hr * 0.6, top + h * 0.38), (cx, top + h * 0.44), (cx - hr * 0.6, top + h * 0.38)], hair["base"])     # a white beard
        c.ellipse(cx, top + h * 0.07, hr * 1.1, hr * 0.5, hair["base"])
        c.ellipse(cx, top + h * 0.15, hr * 0.5, 1.0, skin["base"])
        c.ellipse(cx, top + h * 0.02, hr * 1.1, 2, gold["base"], fill=False, ring=0.6)
    else:
        c.rect(cx - hr * 0.8, top + h * 0.06, cx + hr * 0.8, top + h * 0.08, gold["base"])
    c.outline(pal("basalt")["deep"])
    return c
