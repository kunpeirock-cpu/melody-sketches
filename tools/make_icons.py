"""Generate PWA icons for メロディ・スケッチ管理.

Produces icon-192.png, icon-512.png, icon-512-maskable.png, apple-touch-icon.png
in the repo root.
"""
from __future__ import annotations

import math
import os
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

BG_TOP = (18, 18, 22)
BG_BOTTOM = (8, 8, 10)
ACCENT = (255, 90, 95)
ACCENT_2 = (78, 163, 255)
INK = (240, 240, 245)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient_bg(size: int, radius_ratio: float = 0.22) -> Image.Image:
    img = Image.new("RGB", (size, size), BG_TOP)
    px = img.load()
    for y in range(size):
        t = y / (size - 1)
        c = lerp(BG_TOP, BG_BOTTOM, t)
        for x in range(size):
            px[x, y] = c
    # rounded corners via alpha mask
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    r = int(size * radius_ratio)
    md.rounded_rectangle((0, 0, size - 1, size - 1), radius=r, fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def draw_waveform(canvas: Image.Image, inset: float = 0.18) -> None:
    size = canvas.size[0]
    layer = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    s = size * 2
    pad = int(s * inset)
    width = s - pad * 2
    cy = s // 2
    amp = int(s * 0.18)

    pts = []
    n = 220
    for i in range(n + 1):
        t = i / n
        x = pad + int(width * t)
        # blended sine: gentle main wave with a smaller modulation
        y = cy - int(
            amp * math.sin(t * math.pi * 2.0)
            + (amp * 0.35) * math.sin(t * math.pi * 5.0 + 0.6)
        )
        pts.append((x, y))

    # glow pass
    glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line(pts, fill=(*ACCENT, 140), width=int(s * 0.055), joint="curve")
    glow = glow.filter(ImageFilter.GaussianBlur(radius=s * 0.025))
    layer.alpha_composite(glow)

    # main stroke with gradient (segment-wise)
    seg = 6
    for i in range(0, len(pts) - seg, max(1, seg // 2)):
        t = i / max(1, len(pts) - seg)
        c = lerp(ACCENT, ACCENT_2, t)
        d.line(pts[i : i + seg + 1], fill=(*c, 255), width=int(s * 0.035), joint="curve")

    # dots at the ends — like a recording cue
    r1 = int(s * 0.038)
    d.ellipse(
        (pts[0][0] - r1, pts[0][1] - r1, pts[0][0] + r1, pts[0][1] + r1),
        fill=(*ACCENT, 255),
    )
    r2 = int(s * 0.028)
    d.ellipse(
        (pts[-1][0] - r2, pts[-1][1] - r2, pts[-1][0] + r2, pts[-1][1] + r2),
        fill=(*ACCENT_2, 255),
    )

    layer = layer.resize((size, size), Image.LANCZOS)
    canvas.alpha_composite(layer)


def make_icon(size: int, maskable: bool = False) -> Image.Image:
    if maskable:
        # maskable icons need a safe zone — fill full canvas, keep art in inner 80%
        bg = Image.new("RGBA", (size, size), (0, 0, 0, 255))
        bgpx = bg.load()
        for y in range(size):
            t = y / (size - 1)
            c = lerp(BG_TOP, BG_BOTTOM, t)
            for x in range(size):
                bgpx[x, y] = (*c, 255)
        canvas = bg
        # draw waveform with larger inset (safe zone)
        draw_waveform(canvas, inset=0.22)
    else:
        canvas = gradient_bg(size)
        draw_waveform(canvas, inset=0.16)
    return canvas


def main() -> None:
    out = {
        "icon-192.png": make_icon(192),
        "icon-512.png": make_icon(512),
        "icon-512-maskable.png": make_icon(512, maskable=True),
        "apple-touch-icon.png": make_icon(180),
    }
    for name, img in out.items():
        path = os.path.join(ROOT, name)
        img.save(path, "PNG", optimize=True)
        print("wrote", path)


if __name__ == "__main__":
    main()
