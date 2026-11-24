"""pyramid: the blueprint of a stepped pyramid with rooms, drawn as characters, checked for connectivity and rendered to a preview picture.

A blueprint is a list of rows (top row first) of one character per tile, in tile units:

    ' '  untouched (the world shows through)      '.'  carved air with the pyramid's back wall
    'B'  pharaoh brick     'G'  golden sandstone    'H'  hieroglyph brick     'L'  lapis tile
    'p'  platform          'T'  torch               'K'  spikes               'C'  chest (top-left of its 2 by 2; the 'c' cells are its body)

`grand_pyramid(spec)` builds the Grand Pyramid of Khemet; `connected(bp)` flood-fills from the entrance to prove every room can be reached;
`render(bp, path)` draws it. The game-side code (C#) places exactly these rows, so what the preview shows is what the world generator builds.
"""
from .png import write_png

COLORS = {" ": (88, 150, 214), ".": (62, 52, 40), "B": (196, 170, 112), "G": (232, 190, 60), "H": (150, 120, 70), "L": (42, 88, 176), "p": (142, 98, 52),
          "T": (255, 196, 80), "K": (200, 40, 40), "C": (255, 255, 255), "c": (255, 255, 255), "S": (214, 190, 132), "w": (104, 92, 116), "R": (170, 130, 70)}


def grand_pyramid(spec=None):
    spec = spec or {}
    W = spec.get("width", 121)
    A = spec.get("height", 60)
    D = spec.get("depth", 34)
    R = A + D
    cx = W // 2
    g = [[" "] * W for _ in range(R)]

    def hw_above(r):
        return 2 + (r // 2) * 2

    def hw_below(r):
        return cx - (r - A) // 2

    # the solid: a stepped pyramid over an inverted foundation
    for r in range(R):
        hw = hw_above(r) if r < A else hw_below(r)
        hw = min(hw, cx)
        for x in range(cx - hw, cx + hw + 1):
            g[r][x] = "B"
    # gold courses: the cap and a band every 12 rows along the outer edge
    for r in range(A):
        hw = hw_above(r)
        edge = 3
        for x in range(cx - hw, cx + hw + 1):
            if r < 6 or (r % 12 < 2 and (x - (cx - hw) < edge or (cx + hw) - x < edge)):
                g[r][x] = "G"

    rooms = {}

    def carve(name, x0, y0, x1, y1):
        for r in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                g[r][x] = "."
        rooms[name] = (x0, y0, x1, y1)

    # the entrance gate on the left face at ground level, a corridor, the Hall of Gates, a corridor to the Great Gallery
    hwA = hw_above(A - 3)
    carve("entrance", cx - hwA - 1 + 0, A - 6, cx - hwA + 30, A - 1) if False else None
    ex0 = cx - hw_above(A - 1)
    carve("entrance", ex0, A - 6, ex0 + 9, A - 1)
    carve("hall_of_gates", ex0 + 10, A - 14, ex0 + 30, A - 1)
    carve("corridor_gate", ex0 + 31, A - 6, cx - 15, A - 1)
    # the Great Gallery: one tall room that follows the pyramid's slope, 14 to each side at most, 6 clear of the outer face
    gal = {}
    for r in range(16, A):
        half = min(14, hw_above(r) - 7)
        if half >= 3:
            gal[r] = half
    for r, half in gal.items():
        for x in range(cx - half, cx + half + 1):
            g[r][x] = "."
    rooms["great_gallery"] = (cx - 14, min(gal), cx + 14, A - 1)
    rooms["throne_room"] = (cx - gal[min(gal)], min(gal), cx + gal[min(gal)], min(gal) + 12)
    # the shaft from the gallery floor into the underworld, and the Hall of Judgement
    carve("shaft", cx - 1, A, cx + 1, A + 9)
    carve("hall_of_judgement", cx - 24, A + 10, cx + 24, A + 26)
    # side crypts and the treasure vault, each reached by a corridor from the hall
    carve("corridor_west", cx - 36, A + 22, cx - 25, A + 26)
    carve("crypt_west", cx - 52, A + 12, cx - 37, A + 26)
    carve("corridor_east", cx + 25, A + 22, cx + 36, A + 26)
    carve("treasure_vault", cx + 37, A + 12, cx + 52, A + 26)

    # pillars in the long halls, a lapis floor in the throne room and the judgement hall
    def pillar(x, y0, y1):
        for r in range(y0, y1 + 1):
            g[r][x] = "B"
    for x in range(ex0 + 14, ex0 + 30, 5):
        pillar(x, A - 14, A - 12)
    for x in range(cx - 20, cx + 21, 8):
        if x != cx:
            pillar(x, A + 10, A + 12)
            pillar(x, A + 24, A + 26)
    for x in range(cx - 24, cx + 25):
        if g[A + 27][x] == "B":
            g[A + 27][x] = "L"
    t0 = min(gal)
    for x in range(cx - gal[t0 + 13], cx + gal[t0 + 13] + 1):       # the throne room's floor: lapis across the gallery, with a gap in the middle
        if g[t0 + 13][x] == ".":
            g[t0 + 13][x] = "L"
    # platforms up the gallery, alternating sides, five rows apart (a jump is about six)
    plats = []
    side = 1
    for r in range(A - 6, t0 + 12, -5):
        half = gal.get(r, 6)
        x0 = cx + side * (half - 6) - 3 if side > 0 else cx + side * (half - 6) - 2
        for x in range(x0, x0 + 6):
            if g[r][x] == ".":
                g[r][x] = "p"
        plats.append((x0, r))
        side = -side
    # open the throne room floor so the platforms lead into it: a gap in the lapis floor at the centre
    for x in range(cx - 3, cx + 4):
        if g[t0 + 13][x] == "L":
            g[t0 + 13][x] = "p"
    # spikes: pits in the corridors and the vault entrance
    for (x0, x1, r) in ((cx - 33, cx - 28, A + 26), (cx + 28, cx + 33, A + 26), (ex0 + 33, ex0 + 40, A - 1)):
        for x in range(x0, x1 + 1):
            if g[r][x] == ".":
                g[r][x] = "K"
    # chests: two in the Hall of Gates, three in the vault, two in the west crypt, one beside the throne, two in the Hall of Judgement
    chests = []

    def chest(x, floor_row, role):
        y = floor_row - 2
        if all(g[y + dy][x + dx] == "." for dy in (0, 1) for dx in (0, 1)) and g[floor_row][x] in "BLG":
            g[y][x] = "C"
            g[y][x + 1] = g[y + 1][x] = g[y + 1][x + 1] = "c"
            chests.append((x, y, role))

    chest(ex0 + 12, A - 1 + 1, "gates")
    chest(ex0 + 28, A - 1 + 1, "gates")
    for k, x in enumerate((cx + 40, cx + 45, cx + 50)):
        chest(x, A + 27, "vault")
    for x in (cx - 50, cx - 43):
        chest(x, A + 27, "crypt")
    chest(cx - 10, A + 27, "judgement")
    chest(cx + 8, A + 27, "judgement")
    chest(cx + gal[t0] - 3, t0 + 13, "throne")
    chest(cx - gal[t0] + 2, t0 + 13, "throne")
    # torches on the back wall, every eight tiles along the halls
    def torches(name, step, dy):
        x0, y0, x1, y1 = rooms[name]
        for x in range(x0 + 3, x1 - 2, step):
            r = y0 + dy
            if g[r][x] == ".":
                g[r][x] = "T"
    torches("hall_of_gates", 5, 3)
    torches("hall_of_judgement", 8, 3)
    torches("crypt_west", 5, 3)
    torches("treasure_vault", 5, 3)
    torches("corridor_gate", 6, 1)
    for r in range(t0 + 4, A - 2, 7):
        half = gal.get(r, 0)
        if half > 8:
            for x in (cx - half + 1, cx + half - 1):
                if g[r][x] == ".":
                    g[r][x] = "T"
    # hieroglyph friezes over the doors
    for x in range(ex0, ex0 + 10):
        g[A - 7][x] = "H"
    for x in range(cx - 24, cx + 25):
        if g[A + 9][x] == "B":
            g[A + 9][x] = "H"
    entrance = (ex0, A - 2)
    return {"width": W, "height": R, "ground_row": A, "rows": ["".join(r) for r in g], "rooms": rooms, "chests": chests, "entrance": entrance,
            "platforms": plats, "arena": rooms["throne_room"]}


def connected(bp):
    """Flood-fill from the entrance over every passable tile (air, platform, torch, spike, chest cell). Returns {room: reached} and the reach count."""
    g = bp["rows"]
    passable = set(".pTKcCwR")
    ground = bp["ground_row"]
    ex, ey = bp["entrance"]
    seen = {(ex, ey)}
    stack = [(ex, ey)]
    while stack:
        x, y = stack.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= ny < len(g) and 0 <= nx < len(g[0]) and (nx, ny) not in seen and (g[ny][nx] in passable or (g[ny][nx] == " " and ny < ground)):
                seen.add((nx, ny))
                stack.append((nx, ny))
    reach = {}
    for name, (x0, y0, x1, y1) in bp["rooms"].items():
        reach[name] = ((x0 + x1) // 2, (y0 + y1) // 2) in seen or any((x, y) in seen for x in range(x0, x1 + 1) for y in range(y0, y1 + 1))
    return reach, len(seen)


def rle(row):
    out, i = [], 0
    while i < len(row):
        j = i
        while j < len(row) and row[j] == row[i]:
            j += 1
        out.append(row[i] + str(j - i))
        i = j
    return "".join(out)


def render(bp, path, k=5):
    W, H = bp["width"], bp["height"]
    px = []
    for y in range(H * k):
        for x in range(W * k):
            ch = bp["rows"][y // k][x // k]
            c = COLORS.get(ch, (255, 0, 255))
            if y // k == bp["ground_row"] and ch == " ":
                c = (150, 112, 60)
            if y // k > bp["ground_row"] and ch == " ":
                c = (150, 112, 60)
            if ch in "BGHL" and (y % k == 0 or x % k == 0):
                c = tuple(int(v * 0.85) for v in c)
            px.append((*c, 255))
    write_png(path, W * k, H * k, px)
