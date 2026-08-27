"""Dummy cut test for Banker IVF Rakshabandhan templates.

Verifies the circular photo hole is filled cleanly and the orange ring stays.
Run:  python tests/test_photo_cut.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
OUT = Path(__file__).resolve().parent / "output"

# Must match RAKHI_ELLIPSE in Indira_Creative_Studio.html
ELLIPSE = [422, 294, 761, 633]
PRESETS = {
    "doctor": {
        "path": TEMPLATES / "doctor-rakshabandhan.png",
        "name": (564, 702, "Dr. Asha Patel"),
        "desg": (564, 738, "Consultant, IVF"),
    },
    "employee": {
        "path": TEMPLATES / "employee-rakshabandhan.png",
        "name": (564, 708, "Asha Patel"),
        "desg": (564, 744, "Patient Coordinator"),
    },
}


def fail(msg: str) -> None:
    print("FAIL:", msg)
    sys.exit(1)


def ok(msg: str) -> None:
    print("OK  :", msg)


def make_dummy(w: int = 720, h: int = 900) -> Image.Image:
    im = Image.new("RGB", (w, h), (44, 74, 94))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, h // 2), fill=(122, 155, 179))
    d.ellipse((60, 620, 660, 1100), fill=(31, 77, 58))
    d.rectangle((318, 430, 402, 520), fill=(212, 160, 122))
    d.ellipse((212, 112, 508, 488), fill=(224, 176, 140))
    d.ellipse((208, 68, 512, 324), fill=(58, 36, 24))
    d.ellipse((184, 223, 260, 387), fill=(58, 36, 24))
    d.ellipse((460, 223, 536, 387), fill=(58, 36, 24))
    d.ellipse((293, 288, 323, 308), fill=(42, 28, 20))
    d.ellipse((397, 288, 427, 308), fill=(42, 28, 20))
    d.arc((308, 306, 412, 410), 20, 160, fill=(160, 90, 72), width=6)
    return im


def content_box(img: Image.Image) -> tuple[int, int, int, int]:
    w, h = img.size
    px = img.load()
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (0, h // 2)]
    cr = sum(px[x, y][0] for x, y in corners) / len(corners)
    cg = sum(px[x, y][1] for x, y in corners) / len(corners)
    cb = sum(px[x, y][2] for x, y in corners) / len(corners)
    x0, y0, x1, y1, n = w, h, 0, 0, 0
    step = max(1, min(w, h) // 400)
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b = px[x, y][:3]
            if abs(r - cr) + abs(g - cg) + abs(b - cb) < 36:
                continue
            n += 1
            x0 = min(x0, x)
            y0 = min(y0, y)
            x1 = max(x1, x)
            y1 = max(y1, y)
    if n < 80 or (x1 - x0) < w * 0.22 or (y1 - y0) < h * 0.22:
        return 0, 0, w, h
    pad_x = round((x1 - x0) * 0.06)
    pad_y = round((y1 - y0) * 0.04)
    x0 = max(0, x0 - pad_x)
    y0 = max(0, y0 - pad_y)
    x1 = min(w, x1 + pad_x + 1)
    y1 = min(h, y1 + pad_y + 1)
    usable_h = max(32, round((y1 - y0) * 0.88))
    return x0, y0, x1 - x0, min(usable_h, h - y0)


def cover_place(box: tuple[int, int, int, int], ellipse: list[int], zoom: float = 1.0):
    x0, y0, x1, y1 = ellipse
    pw, ph = x1 - x0, y1 - y0
    bw, bh = box[2], box[3]
    cover = max(pw / bw, ph / bh) * zoom
    dw, dh = bw * cover, bh * cover
    dx = x0 + pw / 2 - dw / 2
    dy = y0 + ph / 2 - dh / 2
    return dx, dy, dw, dh


def punch(tpl: Image.Image, ellipse: list[int]) -> Image.Image:
    out = tpl.convert("RGBA")
    mask = Image.new("L", out.size, 0)
    ImageDraw.Draw(mask).ellipse(ellipse, fill=255)
    clear = Image.new("RGBA", out.size, (0, 0, 0, 0))
    out = Image.composite(clear, out, mask)
    return out


def render(key: str, dummy: Image.Image) -> Image.Image:
    spec = PRESETS[key]
    tpl = Image.open(spec["path"]).convert("RGBA")
    box = (0, 0, dummy.width, dummy.height)
    dx, dy, dw, dh = cover_place(box, ELLIPSE)
    face = dummy.resize((max(1, int(dw)), max(1, int(dh))), Image.Resampling.LANCZOS)
    layer = Image.new("RGBA", tpl.size, (0, 0, 0, 0))
    layer.paste(face.convert("RGBA"), (int(dx), int(dy)))
    clip = Image.new("L", tpl.size, 0)
    x0, y0, x1, y1 = ELLIPSE
    ImageDraw.Draw(clip).ellipse([x0 - 3, y0 - 3, x1 + 3, y1 + 3], fill=255)
    layer.putalpha(clip)
    punched = punch(tpl, ELLIPSE)
    out = Image.alpha_composite(Image.new("RGBA", tpl.size, (255, 246, 238, 255)), layer)
    out = Image.alpha_composite(out, punched)
    draw = ImageDraw.Draw(out)
    font_paths = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "arialbd.ttf",
        "arial.ttf",
    ]
    font_b = font_r = ImageFont.load_default()
    for fp in font_paths:
        try:
            font_b = ImageFont.truetype(fp, 20)
            font_r = ImageFont.truetype(fp.replace("bd.ttf", ".ttf"), 15)
            break
        except OSError:
            continue

    def draw_centered(cx, baseline, text, font, fill):
        if hasattr(draw, "textbbox"):
            x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
            tw, th = x1 - x0, y1 - y0
        else:
            tw, th = draw.textsize(text, font=font)
        draw.text((cx - tw / 2, baseline - th + 2), text, fill=fill, font=font)

    nx, ny, ntxt = spec["name"]
    dx_, dy_, dtxt = spec["desg"]
    # paint over Gujarati placeholders first
    draw.rectangle((nx - 70, ny - 18, nx + 70, ny + 6), fill=(252, 242, 233))
    draw.rectangle((dx_ - 60, dy_ - 16, dx_ + 60, dy_ + 6), fill=(252, 242, 233))
    draw_centered(nx, ny, ntxt, font_b, (26, 26, 26))
    draw_centered(dx_, dy_, dtxt, font_r, (74, 74, 74))
    return out.convert("RGB")


def inside_circle(x: int, y: int, ellipse: list[int]) -> bool:
    x0, y0, x1, y1 = ellipse
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 0.82


def is_cream(rgb) -> bool:
    r, g, b = rgb[:3]
    return r >= 240 and g >= 228 and b >= 216 and (r - g) <= 22


def is_silhouette(rgb) -> bool:
    r, g, b = rgb[:3]
    return r >= 240 and 220 <= g <= 238 and 205 <= b <= 226 and (r - g) >= 12


def is_orange_ring(rgb) -> bool:
    r, g, b = rgb[:3]
    return r >= 145 and 30 <= g <= 170 and b <= 120 and (r - g) >= 35


def assert_cut(key: str, orig: Image.Image, out: Image.Image) -> None:
    x0, y0, x1, y1 = ELLIPSE
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    opx, npx = orig.load(), out.load()

    center = npx[cx, cy]
    if is_cream(center) or is_silhouette(center):
        fail(f"{key}: circle center still looks like the empty placeholder {center}")
    ok(f"{key}: circle center filled {center}")

    # several interior samples must be dummy (skin / hair / backdrop), not peach avatar
    misses = 0
    samples = [
        (cx, cy),
        (cx, cy - 40),
        (cx, cy + 50),
        (cx - 50, cy),
        (cx + 50, cy),
    ]
    for x, y in samples:
        if is_silhouette(npx[x, y]) or is_cream(npx[x, y]):
            misses += 1
    if misses:
        fail(f"{key}: {misses} interior sample(s) still show the placeholder")
    ok(f"{key}: interior samples are photo pixels")

    edge = npx[x0 + 12, cy]
    if is_cream(edge) or is_silhouette(edge):
        fail(f"{key}: cream gap remains just inside the orange ring {edge}")
    ok(f"{key}: fill reaches the orange ring")

    # just outside the circle, artwork must stay (Gujarati text / cream)
    left = (x0 - 28, cy)
    if inside_circle(*left, ELLIPSE):
        fail(f"{key}: outside probe landed inside the circle")
    if abs(opx[left][0] - npx[left][0]) + abs(opx[left][1] - npx[left][1]) + abs(opx[left][2] - npx[left][2]) > 18:
        fail(f"{key}: pixels left of the circle changed {opx[left]} -> {npx[left]}")
    ok(f"{key}: artwork outside the circle is unchanged")

    # orange ring should still exist near the hole edge
    ring_hits = 0
    for x in range(x0 - 6, x0 + 1):
        if is_orange_ring(npx[x, cy]) or is_orange_ring(opx[x, cy]):
            ring_hits += 1
    if ring_hits < 1:
        fail(f"{key}: orange photo ring is missing after the cut")
    ok(f"{key}: orange ring still present")

    nx, ny, _ = PRESETS[key]["name"]
    dark = 0
    for y in range(ny - 16, ny + 4):
        for x in range(nx - 50, nx + 50):
            r, g, b = npx[x, y][:3]
            if r + g + b < 360:
                dark += 1
    if dark < 20:
        fail(f"{key}: name was not drawn near ({nx},{ny}) dark_px={dark}")
    ok(f"{key}: name drawn at baseline")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dummy = make_dummy()
    dummy.save(OUT / "dummy-portrait.png")

    if not (TEMPLATES / "header-rakhi.png").exists():
        fail("missing templates/header-rakhi.png")

    for key, spec in PRESETS.items():
        if not spec["path"].exists():
            fail(f"missing template {spec['path']}")
        orig = Image.open(spec["path"]).convert("RGB")
        if orig.size != (768, 1024):
            fail(f"{key} template must be 768x1024, got {orig.size}")
        rendered = render(key, dummy)
        rendered.save(OUT / f"dummy-{key}.png")
        assert_cut(key, orig, rendered)
        ok(f"{key}: wrote {OUT / f'dummy-{key}.png'}")

    print("\nAll dummy photo-cut checks passed.")


if __name__ == "__main__":
    main()
