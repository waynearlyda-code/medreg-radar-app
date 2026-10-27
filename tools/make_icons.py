"""用纯 Python 画 App 图标（雷达），输出 PNG。不依赖第三方库。
用法：python3 tools/make_icons.py"""
import math
import os
import struct
import zlib

BG = (14, 17, 16)        # 深色底
RING = (58, 65, 61)
ACCENT = (57, 135, 229)  # 蓝
DOT = (217, 89, 38)      # 橙
HERE = os.path.dirname(os.path.abspath(__file__))


def png(path, w, h, px):
    raw = b"".join(b"\x00" + bytes(px[y * w * 3:(y + 1) * w * 3]) for y in range(h))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw(size, safe=0.8):
    """safe：图标主体占画面的比例（maskable 图标要留安全边距）。"""
    px = bytearray(size * size * 3)
    c = size / 2
    R = size / 2 * safe
    dot = (c + R * 0.42, c - R * 0.45)
    for y in range(size):
        for x in range(size):
            col = BG
            dx, dy = x + 0.5 - c, y + 0.5 - c
            d = math.hypot(dx, dy)
            ang = (math.degrees(math.atan2(dx, -dy)) + 360) % 360   # 0° 朝上，顺时针
            if d <= R:
                # 扫描扇形：从 320° 到 360°，越靠前沿越亮
                if ang >= 300:
                    col = mix(BG, ACCENT, ((ang - 300) / 60) ** 2 * 0.55)
                for rr in (R, R * 0.66, R * 0.33):
                    if abs(d - rr) < max(1.0, size / 160):
                        col = RING
                if ang > 359 or ang < 1.2 and d < R:
                    col = ACCENT
            if math.hypot(x + 0.5 - dot[0], y + 0.5 - dot[1]) < size * 0.045:
                col = DOT
            if d < size * 0.03:
                col = (238, 240, 236)
            i = (y * size + x) * 3
            px[i:i + 3] = bytes(col)
    return px


def main():
    out = os.path.join(HERE, "..", "www", "icons")
    os.makedirs(out, exist_ok=True)
    for s in (192, 512):
        png(os.path.join(out, "icon-%d.png" % s), s, s, draw(s, 0.84))
        png(os.path.join(out, "maskable-%d.png" % s), s, s, draw(s, 0.62))
    png(os.path.join(out, "apple-touch-icon.png"), 180, 180, draw(180, 0.8))
    png(os.path.join(HERE, "..", "assets", "logo.png"), 1024, 1024, draw(1024, 0.62))  # 安卓打包用
    print("done")


if __name__ == "__main__":
    main()
