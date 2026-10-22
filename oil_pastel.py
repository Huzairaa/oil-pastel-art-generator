
"""
Oil Pastel - Converts a photo into an oil-pastel-style painting.

Usage:
    python -m pip install numpy pillow
    python oil_pastel.py photo.jpg
        -> Creates natija.png

    python oil_pastel.py photo.jpg --video
        -> Creates painting-process frames in the frames/ folder

To create a video from the frames (FFmpeg required):
    ffmpeg -framerate 30 -i frames/%05d.png -pix_fmt yuv420p video.mp4
"""

import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

LAYERS = [36, 22, 13, 8, 5, 3]
MAX_SIDE = 1400
FRAMES_PER_LAYER = 40

random.seed(4)
np.random.seed(4)


def load(path):
    im = Image.open(path).convert("RGB")
    s = min(1.0, MAX_SIDE / max(im.size))
    return im.resize(
        (round(im.width * s), round(im.height * s)),
        Image.Resampling.LANCZOS,
    )


def make_layer(target, canvas, r):
    """Create brush strokes in areas that need more detail."""
    W, H = target.size

    blur = np.asarray(
        target.filter(ImageFilter.GaussianBlur(r * 0.5)),
        dtype=np.float32,
    )

    lum = blur @ np.array([0.299, 0.587, 0.114], np.float32)
    gy, gx = np.gradient(lum)

    err = np.abs(np.asarray(canvas, np.float32) - blur).sum(2)
    step = max(2, int(r * 0.9))
    strokes = []

    for y in range(0, H, step):
        for x in range(0, W, step):
            yy = min(H - 1, y + random.randint(0, step - 1))
            xx = min(W - 1, x + random.randint(0, step - 1))

            if r != LAYERS[0] and err[yy, xx] < 30:
                continue

            color = tuple(
                int(c)
                for c in np.clip(
                    blur[yy, xx] + np.random.normal(0, 7, 3),
                    0,
                    255,
                )
            )

            pts = [(xx, yy)]
            px, py = float(xx), float(yy)
            last = None

            for _ in range(random.randint(2, 4)):
                ix = int(min(W - 1, max(0, px)))
                iy = int(min(H - 1, max(0, py)))

                dx, dy = -gy[iy, ix], gx[iy, ix]
                m = math.hypot(dx, dy)

                if m < 0.5:
                    a = (
                        random.uniform(0, math.pi)
                        if last is None
                        else math.atan2(last[1], last[0])
                    )
                    dx, dy = math.cos(a), math.sin(a)
                else:
                    dx, dy = dx / m, dy / m

                if last and dx * last[0] + dy * last[1] < 0:
                    dx, dy = -dx, -dy

                px += dx * r * 0.9
                py += dy * r * 0.9
                pts.append((px, py))
                last = (dx, dy)

            strokes.append((r, color, pts))

    random.shuffle(strokes)
    return strokes


def draw_stroke(d, r, color, pts):
    w = max(2, int(r * 1.6))

    d.line(pts, fill=color, width=w, joint="curve")

    for p in (pts[0], pts[-1]):
        d.ellipse(
            (p[0] - w / 2, p[1] - w / 2,
             p[0] + w / 2, p[1] + w / 2),
            fill=color,
        )

    if r >= 5:
        for _ in range(3):
            off = random.uniform(-w / 3, w / 3)
            shade = random.choice((18, -18, 30))
            c2 = tuple(
                max(0, min(255, c + shade))
                for c in color
            )

            d.line(
                [(x + off * 0.7, y + off) for x, y in pts],
                fill=c2,
                width=max(1, w // 6),
            )


def main():
    if len(sys.argv) < 2:
        print("Usage: python oil_pastel.py photo.jpg [--video]")
        return

    image_path = sys.argv[1]

    if not os.path.isfile(image_path):
        print(f"Error: Image not found: {image_path}")
        print("Put the image in this folder or provide its full path.")
        return

    target = load(image_path)
    video = "--video" in sys.argv

    canvas = Image.new("RGB", target.size, (246, 242, 232))
    d = ImageDraw.Draw(canvas)

    if video:
        os.makedirs("frames", exist_ok=True)

    frame = 0

    for i, r in enumerate(LAYERS):
        strokes = make_layer(target, canvas, r)

        print(
            f"Layer {i + 1}/{len(LAYERS)} | "
            f"brush radius={r} | strokes={len(strokes)}"
        )

        chunk = max(1, len(strokes) // FRAMES_PER_LAYER)

        for k, stroke in enumerate(strokes):
            draw_stroke(d, *stroke)

            if video and k % chunk == 0:
                canvas.save(f"frames/{frame:05d}.png")
                frame += 1

    canvas.save("natija.png")

    if video:
        for _ in range(60):
            canvas.save(f"frames/{frame:05d}.png")
            frame += 1

        print(f"Frames saved: frames/ ({frame} frames)")

    print("Done! Result saved as natija.png")

    try:
        canvas.show()
    except Exception:
        pass


if __name__ == "__main__":
    main()
