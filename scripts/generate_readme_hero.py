#!/usr/bin/env python3
"""Generate the animated SkillLint README hero without external image assets."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "readme" / "hero-animation.gif"
WIDTH, HEIGHT = 1280, 440
BG0 = (5, 13, 27)
CYAN = (53, 242, 203)
BLUE = (65, 145, 255)
PURPLE = (164, 124, 255)
WHITE = (241, 248, 255)
MUTED = (143, 169, 199)


def load_font(kind: str, size: int):
    files = {
        "bold": (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ),
        "regular": (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ),
        "mono": (
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
        ),
    }
    for filename in files[kind]:
        try:
            return ImageFont.truetype(filename, size)
        except OSError:
            continue
    return ImageFont.load_default()


F_HERO = load_font("bold", 59)
F_HEADING = load_font("bold", 19)
F_BODY = load_font("regular", 17)
F_SMALL = load_font("regular", 13)
F_MONO = load_font("mono", 13)
F_TINY = load_font("bold", 10)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def build_base() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    for y in range(HEIGHT):
        factor = y / HEIGHT
        row = (
            int(BG0[0] + 6 * factor),
            int(BG0[1] + 10 * factor),
            int(BG0[2] + 20 * factor),
        )
        for x in range(WIDTH):
            glow = max(0.0, 1.0 - math.sqrt(((x - 1000) / 480) ** 2 + ((y - 160) / 300) ** 2))
            pixels[x, y] = (
                min(255, int(row[0] + 1 * glow)),
                min(255, int(row[1] + 40 * glow)),
                min(255, int(row[2] + 60 * glow)),
            )

    grid = ImageDraw.Draw(image, "RGBA")
    for x in range(20, WIDTH, 32):
        grid.line((x, 0, x, HEIGHT), fill=(50, 103, 157, 22), width=1)
    for y in range(18, HEIGHT, 32):
        grid.line((0, y, WIDTH, y), fill=(50, 103, 157, 17), width=1)

    halo = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo)
    halo_draw.ellipse((830, 20, 1240, 390), fill=(30, 170, 210, 24))
    halo_draw.ellipse((935, 70, 1180, 320), fill=(42, 230, 194, 22))
    halo = halo.filter(ImageFilter.GaussianBlur(55))
    image = Image.alpha_composite(image.convert("RGBA"), halo)
    draw = ImageDraw.Draw(image, "RGBA")

    draw.ellipse((44, 42, 55, 53), fill=(*CYAN, 255))
    draw.text((68, 39), "VERITYAGENT  /  DEVELOPER TOOLING", font=F_SMALL, fill=(*MUTED, 255))
    draw.text((42, 88), "SKILLLINT", font=F_HERO, fill=(*WHITE, 255))
    draw.rounded_rectangle((46, 164, 344, 171), radius=3, fill=(*CYAN, 245))
    draw.text((46, 193), "TRUST YOUR AGENT SKILLS.", font=F_HEADING, fill=(*CYAN, 255))
    draw.text((46, 225), "Lint. Verify. Ship with confidence.", font=F_BODY, fill=(*WHITE, 242))
    draw.text((46, 266), "Metadata   ·   Links   ·   Conflicts   ·   Risk", font=F_SMALL, fill=(*MUTED, 255))

    chips = [("STATIC ONLY", 108), ("CI-READY", 94), ("SARIF 2.1", 94)]
    x = 46
    for label, width in chips:
        rounded(draw, (x, 323, x + width, 353), 10, (12, 30, 48, 245), outline=(48, 150, 153, 190))
        draw.ellipse((x + 10, 335, x + 17, 342), fill=(*CYAN, 255))
        draw.text((x + 25, 332), label, font=F_TINY, fill=(212, 231, 245, 255))
        x += width + 11

    # Terminal-like diagnostic report card.
    rounded(draw, (610, 47, 1234, 381), 22, (5, 17, 33, 244), outline=(62, 112, 158, 220), width=2)
    rounded(draw, (610, 47, 1234, 91), 22, (16, 38, 61, 255))
    draw.rectangle((610, 70, 1234, 91), fill=(16, 38, 61, 255))
    for index, color in enumerate(((255, 105, 111, 255), (255, 198, 75, 255), (*CYAN, 255))):
        draw.ellipse((634 + 19 * index, 65, 643 + 19 * index, 74), fill=color)
    draw.text((715, 61), "skilllint scan ./agent-skills", font=F_MONO, fill=(171, 199, 223, 255))
    rounded(draw, (1018, 103, 1207, 136), 12, (11, 48, 42, 255), outline=(45, 160, 131, 200))
    draw.ellipse((1033, 116, 1042, 125), fill=(*CYAN, 255))
    draw.text((1052, 112), "STATIC ANALYSIS", font=F_TINY, fill=(159, 255, 228, 255))

    rows = [
        ("SL001", "Metadata contract", CYAN, "PASS"),
        ("SLLINK001", "Local references", CYAN, "PASS"),
        ("SLCONF001", "Instruction conflicts", BLUE, "CHECK"),
        ("SLSEC001", "Risky shell patterns", PURPLE, "REVIEW"),
    ]
    for index, (rule, label, color, status) in enumerate(rows):
        y = 157 + index * 48
        rounded(draw, (636, y, 1208, y + 37), 9, (10, 28, 46, 255), outline=(42, 75, 107, 155))
        draw.text((653, y + 11), rule, font=F_MONO, fill=(*color, 255))
        draw.text((790, y + 10), label, font=F_SMALL, fill=(201, 219, 237, 255))
        tone = CYAN if status == "PASS" else BLUE if status == "CHECK" else PURPLE
        draw.text((1158, y + 11), status, font=F_TINY, fill=(*tone, 255))

    draw.text((642, 359), "Human review remains the final security boundary.", font=F_SMALL, fill=(120, 153, 183, 255))
    draw.line((42, 404, 1238, 404), fill=(45, 86, 122, 145), width=1)
    draw.text((45, 418), "SKILLLINT  ·  OPEN SOURCE  ·  PYTHON 3.10+", font=F_TINY, fill=(93, 133, 166, 255))
    draw.text((1235, 418), "VERITYAGENT", font=F_TINY, fill=(93, 133, 166, 255), anchor="ra")
    return image


def main() -> None:
    base = build_base()
    frames = []
    for index in range(12):
        phase = index / 12
        frame = base.copy()
        layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer, "RGBA")

        # Animated scanline across the diagnostic panel.
        scan_x = 625 + int(590 * phase)
        draw.line((scan_x, 96, scan_x, 375), fill=(*CYAN, 25), width=2)
        draw.line((scan_x - 2, 96, scan_x - 2, 375), fill=(*CYAN, 9), width=6)

        # Packet particles orbit the status/result connector.
        for particle in range(7):
            progress = (phase + particle / 7) % 1
            px = 885 + int(250 * progress)
            py = 147 + int(9 * math.sin(progress * math.tau))
            alpha = 230 if particle == 0 else 72
            draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill=(*CYAN, alpha))

        pulse = int(130 + 125 * (0.5 + 0.5 * math.sin(phase * math.tau)))
        draw.ellipse((1033, 116, 1042, 125), outline=(*CYAN, pulse), width=2)
        composed = Image.alpha_composite(frame, layer)
        frames.append(composed.convert("RGB"))

    # Share one palette across every frame to keep the GIF portable and small.
    previews = [frame.resize((256, 88), Image.Resampling.BILINEAR) for frame in frames]
    palette_source = Image.new("RGB", (1024, 264), (0, 0, 0))
    for idx, thumb in enumerate(previews):
        palette_source.paste(thumb, ((idx % 4) * 256, (idx // 4) * 88))
    palette = palette_source.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    quantized = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    quantized[0].save(
        OUTPUT, save_all=True, append_images=quantized[1:],
        duration=105, loop=0, optimize=True, disposal=1,
    )
    print(f"Generated {OUTPUT.relative_to(ROOT)}: {OUTPUT.stat().st_size:,} bytes / {len(quantized)} frames")


if __name__ == "__main__":
    main()
