"""Generates the home-screen icon: a green square with a white check.

Hand-rolled so the repo carries no binary asset anyone has to trust or
re-source. Full-bleed square, which is what Android 'maskable' wants and what
iOS rounds off by itself. Re-run with: python3 make-icons.py
"""
import struct, zlib

BG    = (0x1F, 0x6F, 0x5C)
FG    = (0xFF, 0xFF, 0xFF)
CHECK = [((.295, .530), (.435, .668)), ((.435, .668), (.720, .352))]
HALF  = .058          # half stroke width, in units of the icon's side
SS    = 3             # supersampling per axis, for smooth edges


def dist_to_segment(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    cx, cy = ax + t * dx, ay + t * dy
    return ((px - cx) ** 2 + (py - cy) ** 2) ** .5


def coverage(u, v):
    """How much of this sub-pixel is inside the check stroke (0 or 1)."""
    return 1 if any(dist_to_segment(u, v, *a, *b) <= HALF for a, b in CHECK) else 0


def render(size):
    rows = bytearray()
    for y in range(size):
        rows.append(0)                       # PNG filter type: none
        for x in range(size):
            hits = 0
            for sy in range(SS):
                v = (y + (sy + .5) / SS) / size
                for sx in range(SS):
                    u = (x + (sx + .5) / SS) / size
                    hits += coverage(u, v)
            a = hits / (SS * SS)
            rows += bytes(round(BG[c] + (FG[c] - BG[c]) * a) for c in range(3))
    return bytes(rows)


def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def write_png(path, size):
    header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)   # 8-bit RGB
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", header)
           + chunk(b"IDAT", zlib.compress(render(size), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    print(f"{path}  {size}x{size}  {len(png):,} bytes")


for s in (180, 192, 512):
    write_png(f"icon-{s}.png", s)
