"""Write a PNG file from a list of RGBA tuples, with the standard library only."""
import struct
import zlib
from pathlib import Path


def write_png(path, width, height, pixels):
    """pixels: width*height tuples of (r, g, b, a), row by row from the top."""
    raw = b"".join(b"\x00" + bytes(c for x in range(width) for c in pixels[y * width + x]) for y in range(height))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    data = (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def read_size(path):
    """(width, height) of a PNG, or None if it is not one."""
    head = Path(path).read_bytes()[:24]
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def has_transparency(path):
    """True if an 8-bit RGBA (or grey+alpha) PNG has any pixel with alpha below 255. Other formats: False."""
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return False
    pos, idat, w, h, depth, ctype, interlace = 8, b"", 0, 0, 0, 0, 0
    while pos < len(data):
        (n,) = struct.unpack(">I", data[pos:pos + 4])
        tag, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + n]
        if tag == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", body)
        elif tag == b"IDAT":
            idat += body
        elif tag == b"tRNS":
            return True
        pos += 12 + n
    if depth != 8 or interlace or ctype not in (4, 6):
        return False
    bpp = 4 if ctype == 6 else 2
    raw, stride, prev = zlib.decompress(idat), w * bpp, bytearray(w * bpp)
    for y in range(h):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + ((a + b) >> 1)) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else (b if pb <= pc else c))) & 255
        if any(line[i] < 255 for i in range(bpp - 1, stride, bpp)):
            return True
        prev = line
    return False
