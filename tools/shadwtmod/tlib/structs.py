"""structs: blueprints for the structures a mod can place in the world, and one entry point `build(spec)` that returns the blueprint dict.

Kinds: grand_pyramid (a stepped desert pyramid, see pyramid.py), greek_temple (a surface temple with a colonnade, a cella and a crypt),
labyrinth (an underground maze with a lair at its centre, a rope shaft to the surface and chests in the dead ends).

A blueprint dict has: width, height, ground_row (the row the surface sits on; 0 for an underground structure), rows (one string per row, one character per tile),
rooms {name: (x0, y0, x1, y1)}, chests [(x, y, role)], entrance (x, y), and kind-specific extras. Characters: ' ' untouched, '.' air with the back wall, 'w' air with the
column wall, 'B' 'G' 'H' 'L' the structure's four tiles (see its tile_map), 'p' platform, 'T' torch, 'K' spikes, 'C' + 'c' chest, 'R' rope.
"""
import random
from . import pyramid


def build(spec):
    kind = spec["kind"]
    if kind == "grand_pyramid":
        return pyramid.grand_pyramid(spec)
    if kind == "greek_temple":
        return greek_temple(spec)
    if kind == "labyrinth":
        return labyrinth(spec)
    raise ValueError(f"unknown structure kind {kind}")


def greek_temple(spec=None):
    spec = spec or {}
    W = spec.get("width", 65)
    A = 30                      # rows above the ground line
    D = 13                      # rows below it: the foundation and the crypt
    R = A + D
    cx = W // 2
    g = [[" "] * W for _ in range(R)]

    def fill(x0, x1, y0, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                g[y][x] = ch

    # the foundation and three steps (the widest step is at the bottom), all marble
    fill(0, W - 1, A, A + 2, "B")
    for k, hw in enumerate((cx, cx - 2, cx - 4)):
        fill(cx - hw, cx + hw, A - 1 - k, A - 1 - k, "B")
    floor = A - 3                 # the top step is the temple floor: its surface is row floor
    top_air = floor - 14          # the colonnade is 14 rows tall: rows floor-14 .. floor-1
    # the entablature (a plain band, a meander frieze and a cornice) over the full width, then the pediment
    fill(cx - 29, cx + 29, top_air - 1, top_air - 1, "B")
    fill(cx - 28, cx + 28, top_air - 3, top_air - 2, "H")
    fill(cx - 29, cx + 29, top_air - 4, top_air - 4, "B")
    for k, r in enumerate(range(top_air - 5, top_air - 14, -1)):
        hw = 29 - k * 3
        if hw < 1:
            break
        fill(cx - hw, cx + hw, r, r, "B")
        if hw > 4 and k > 0:
            fill(cx - hw + 3, cx + hw - 3, r, r, "L")     # the tympanum
    # the colonnade: column walls (background) between the end walls, so the peristyle can be walked through
    fill(cx - 27, cx + 27, top_air, floor - 1, ".")
    for x in range(cx - 26, cx + 27, 6):
        fill(x, x + 1, top_air, floor - 1, "w")
        g[top_air][x], g[top_air][x + 1] = "H", "H"          # the capitals are hard tiles
        g[floor - 1][x], g[floor - 1][x + 1] = "w", "w"
    # the cella: a walled room in the middle with a doorway on each side, an altar, braziers and chests
    fill(cx - 13, cx - 12, top_air, floor - 1, "B")
    fill(cx + 12, cx + 13, top_air, floor - 1, "B")
    fill(cx - 11, cx + 11, top_air, floor - 1, ".")
    fill(cx - 13, cx - 12, floor - 5, floor - 1, ".")                          # the doorways, five rows tall
    fill(cx + 12, cx + 13, floor - 5, floor - 1, ".")
    fill(cx - 2, cx + 2, floor - 3, floor - 1, "G")                            # the altar
    fill(cx - 1, cx + 1, floor - 4, floor - 4, "G")
    for x in (cx - 8, cx + 8):
        g[floor - 6][x] = "T"
    # the shaft and the crypt under the altar's side, reached by a hatch in the cella floor
    carve = lambda x0, x1, y0, y1: fill(x0, x1, y0, y1, ".")
    carve(cx - 9, cx - 7, floor, A + 4)                                     # the shaft (3 wide) down from the cella floor
    carve(cx - 14, cx + 14, A + 5, A + 10)                                  # the crypt
    rooms = {"entrance_steps": (0, floor - 3, cx - 28, floor - 1), "peristyle": (cx - 27, top_air, cx + 27, floor - 1), "cella": (cx - 11, top_air, cx + 11, floor - 1),
             "shaft": (cx - 9, floor, cx - 7, A + 4), "crypt": (cx - 14, A + 5, cx + 14, A + 10)}
    for x in range(cx - 12, cx + 13, 6):
        g[A + 6][x] = "T"
    # platforms to climb out of the crypt would be needed only above 5 rows: the shaft is 6 deep, so one platform halfway
    for x in range(cx - 9, cx - 6):
        g[A + 2][x] = "p"
    # the crypt floor: bronze under the chests
    for x in range(cx - 14, cx + 15):
        if g[A + 11][x] == " ":
            g[A + 11][x] = "B"
    for y in range(A + 11, R):
        for x in range(cx - 15, cx + 16):
            if g[y][x] == " ":
                g[y][x] = "B"
    chests = []

    def chest(x, floor_row, role):
        y = floor_row - 2
        if all(g[y + dy][x + dx] == "." for dy in (0, 1) for dx in (0, 1)) and g[floor_row][x] in "BLGp":
            g[y][x] = "C"
            g[y][x + 1] = g[y + 1][x] = g[y + 1][x + 1] = "c"
            chests.append((x, y, role))
    chest(cx - 6, floor, "cella")
    chest(cx + 6, floor, "cella")
    chest(cx - 12, A + 11, "crypt")
    chest(cx - 3, A + 11, "crypt")
    chest(cx + 6, A + 11, "crypt")
    entrance = (1, floor - 1)
    return {"width": W, "height": R, "ground_row": A, "rows": ["".join(r) for r in g], "rooms": rooms, "chests": chests, "entrance": entrance, "platforms": []}


def labyrinth(spec=None):
    spec = spec or {}
    CW, CH = spec.get("cells", [15, 7])
    pitch = 5
    W, H = CW * pitch + 1, CH * pitch + 1
    rnd = random.Random(spec.get("seed", 1))
    g = [["L"] * W for _ in range(H)]

    def open_cell(i, j):
        for y in range(1 + pitch * j, 5 + pitch * j):
            for x in range(1 + pitch * i, 5 + pitch * i):
                g[y][x] = "."

    def link(i, j, di, dj):
        if di:                                       # a door through the wall to the east or west
            x = 5 + pitch * i if di > 0 else pitch * i
            for y in range(1 + pitch * j, 5 + pitch * j):
                g[y][x] = "."
        else:                                        # a hole in the floor/ceiling, bridged by platforms so it can be climbed
            y = 5 + pitch * j if dj > 0 else pitch * j
            for x in range(1 + pitch * i, 5 + pitch * i):
                g[y][x] = "p"
    seen = {(0, 0)}
    stack = [(0, 0)]
    degree = {(i, j): 0 for i in range(CW) for j in range(CH)}
    for j in range(CH):
        for i in range(CW):
            open_cell(i, j)
    while stack:
        i, j = stack[-1]
        nbrs = [(i + di, j + dj, di, dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= i + di < CW and 0 <= j + dj < CH and (i + di, j + dj) not in seen]
        if not nbrs:
            stack.pop()
            continue
        ni, nj, di, dj = rnd.choice(nbrs)
        link(i, j, di, dj)
        degree[(i, j)] += 1
        degree[(ni, nj)] += 1
        seen.add((ni, nj))
        stack.append((ni, nj))
    # the lair: the 3 by 3 cells at the centre, opened into one great room (walls and floors between them removed)
    ci, cj = CW // 2, CH // 2
    lx0, lx1 = 1 + pitch * (ci - 1), 4 + pitch * (ci + 1)
    ly0, ly1 = 1 + pitch * (cj - 1), 4 + pitch * (cj + 1)
    for y in range(ly0, ly1 + 1):
        for x in range(lx0, lx1 + 1):
            g[y][x] = "."
    for x in range(lx0 + 2, lx1 - 1, 5):                               # pillars in the lair
        for y in range(ly1 - 3, ly1 + 1):
            g[y][x] = "L"
    # the entrance: the top-left cell opens through the ceiling; the generator digs a roped shaft from the surface to here
    for x in (2, 3):
        g[0][x] = "."
    entrance = (2, 1)
    # meander trim along the floor of the bottom row and the lintel of the top row
    for x in range(W):
        if g[H - 1][x] == "L":
            g[H - 1][x] = "H"
    # chests in dead ends (cells with one door), torches and spikes elsewhere
    chests = []
    dead = [(i, j) for (i, j), d in degree.items() if d == 1 and not (ci - 1 <= i <= ci + 1 and cj - 1 <= j <= cj + 1) and (i, j) != (0, 0)]
    rnd.shuffle(dead)
    for k, (i, j) in enumerate(dead[: spec.get("chests", 8)]):
        x, y = 1 + pitch * i + 1, 3 + pitch * j
        if all(g[y + dy][x + dx] == "." for dy in (0, 1) for dx in (0, 1)):
            g[y][x] = "C"
            g[y][x + 1] = g[y + 1][x] = g[y + 1][x + 1] = "c"
            chests.append((x, y, "dead_end" if k else "great"))
    others = [(i, j) for (i, j) in degree if (i, j) not in dead and not (ci - 1 <= i <= ci + 1 and cj - 1 <= j <= cj + 1)]
    rnd.shuffle(others)
    for (i, j) in others[:14]:
        g[1 + pitch * j][1 + pitch * i + 2] = "T" if g[1 + pitch * j][1 + pitch * i + 2] == "." else g[1 + pitch * j][1 + pitch * i + 2]
    for (i, j) in others[14:22]:
        y = 4 + pitch * j
        for x in (2 + pitch * i, 3 + pitch * i):
            if g[y][x] == ".":
                g[y][x] = "K"
    rooms = {"entrance_cell": (1, 1, 4, 4), "minotaur_lair": (lx0, ly0, lx1, ly1)}
    for k, (x, y, role) in enumerate(chests):
        rooms[f"chest_{k}"] = (x, y, x + 1, y + 1)
    return {"width": W, "height": H, "ground_row": 0, "rows": ["".join(r) for r in g], "rooms": rooms, "chests": chests, "entrance": entrance, "platforms": [], "arena": rooms["minotaur_lair"]}
