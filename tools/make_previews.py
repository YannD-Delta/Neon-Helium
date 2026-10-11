#!/usr/bin/env python3
"""Draw the schematic preview images shown by Theme Options next to its drop-down lists.

Theme Options shows a preset's Preview image while the mouse is over that choice. These are
simplified drawings of the Details view, one per choice, written to source/Presets/Previews/
as <Group>_<Option>.png. tools/build_options.py links every image that exists.

Usage:
    python tools/make_previews.py [--out source/Presets/Previews]

Needs Pillow. The images are committed, so this only runs when a preview changes.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 400, 250
HERO_TOP, HERO_BOTTOM = 18, 150
BAR_H = 24

BG = (15, 19, 24)
PANEL = (24, 29, 37)
TOP = (20, 24, 31)
TEXT = (223, 227, 230)
TEXT_DIM = (130, 138, 148)
GREEN = (43, 185, 67)
GREEN_LIGHT = (79, 200, 47)
BLUE = (42, 113, 216)
ACCENT = (26, 159, 255)


def font(size, bold=False):
    names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
             "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"]
    for name in names:
        for folder in ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation", "C:/Windows/Fonts"):
            path = Path(folder) / name
            if path.exists():
                return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def artwork(width, height, blur=0, valign="center", halign="left"):
    """A synthetic landscape, larger than the hero so the alignment choices show."""
    big = Image.new("RGB", (int(width * 1.5), int(height * 1.7)))
    d = ImageDraw.Draw(big)
    bw, bh = big.size
    for y in range(bh):
        t = y / bh
        d.line([(0, y), (bw, y)], fill=(int(58 + 120 * t), int(95 + 90 * t), int(122 + 60 * t)))
    d.ellipse([bw * 0.62, bh * 0.12, bw * 0.74, bh * 0.12 + bw * 0.12], fill=(255, 214, 120))
    d.polygon([(0, bh * 0.75), (bw * 0.25, bh * 0.35), (bw * 0.45, bh * 0.7), (bw * 0.7, bh * 0.3), (bw, bh * 0.68), (bw, bh), (0, bh)],
              fill=(38, 74, 52))
    d.polygon([(0, bh * 0.9), (bw * 0.3, bh * 0.62), (bw * 0.55, bh * 0.85), (bw * 0.85, bh * 0.6), (bw, bh * 0.8), (bw, bh), (0, bh)],
              fill=(24, 50, 34))
    if blur:
        big = big.filter(ImageFilter.GaussianBlur(blur))
    x = {"left": 0, "center": (bw - width) // 2, "right": bw - width}[halign]
    y = {"top": 0, "center": (bh - height) // 2, "bottom": bh - height}[valign]
    return big.crop((x, y, x + width, y + height))


def shade(img, top, bottom, strength):
    """Black gradient from the bottom of the hero, like the theme's shade."""
    if strength <= 0:
        return
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    span = bottom - top
    for y in range(top, bottom):
        t = (y - top) / span
        alpha = int(255 * strength * max(0.0, (t - 0.45) / 0.55))
        d.line([(0, y), (img.width, y)], fill=(0, 0, 0, alpha))
    img.alpha_composite(layer)


def rounded(d, box, radius, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def chips(d, x, y, style="pills", count=6):
    labels = ["2015", "PC", "Steam", "Racing", "Sim", "4,5h"][:count]
    f = font(8)
    for label in labels:
        w = int(d.textlength(label, font=f)) + (12 if style != "text" else 4)
        if style == "pills":
            rounded(d, (x, y, x + w, y + 13), 6, fill=(16, 20, 24, 170), outline=(255, 255, 255, 60))
        elif style == "outline":
            rounded(d, (x, y, x + w, y + 13), 6, outline=(255, 255, 255, 140))
        tx = x + (6 if style != "text" else 2)
        d.text((tx, y + 1), label, font=f if style != "text" else font(8, True), fill=(255, 255, 255, 255))
        x += w + (5 if style != "text" else 10)
    return x


def buttons(d, x, y, style="dune", scale=1.0):
    h = int(20 * scale)
    w = int(80 * scale)
    r = {"dune": 4, "neon": 1, "pill": h // 2, "glass": 4}[style]
    if style == "glass":
        rounded(d, (x, y, x + w, y + h), r, fill=(0, 0, 0, 90), outline=ACCENT + (255,), width=max(1, int(1.5 * scale)))
        play = ACCENT
    else:
        top_col, bottom_col = (GREEN_LIGHT, GREEN) if style != "neon" else ((95, 210, 60), (24, 177, 78))
        rounded(d, (x, y, x + w, y + h), r, fill=bottom_col + (255,))
        rounded(d, (x, y, x + w * 0.6, y + h), r, fill=top_col + (255,))
        d.rectangle((x + w * 0.4, y, x + w * 0.62, y + h), fill=tuple((a + b) // 2 for a, b in zip(top_col, bottom_col)) + (255,))
        play = (255, 255, 255)
    cx, cy = x + 12 * scale, y + h / 2
    d.polygon([(cx, cy - 5 * scale), (cx, cy + 5 * scale), (cx + 8 * scale, cy)], fill=play + (255,))
    label = "PLAY" if style == "neon" else "Play"
    d.text((x + 26 * scale, y + 4 * scale), label, font=font(int(9 * scale), style != "neon"), fill=(255, 255, 255, 255))
    d.line([(x + w - h, y + 3), (x + w - h, y + h - 3)], fill=(255, 255, 255, 110), width=1)
    d.text((x + w - h + 6 * scale, y + 3 * scale), "v", font=font(int(9 * scale)), fill=(255, 255, 255, 255))
    for i in range(2):
        bx = x + w + 6 * scale + i * (h + 6 * scale)
        if style == "glass":
            rounded(d, (bx, y, bx + h, y + h), r, fill=(0, 0, 0, 90), outline=ACCENT + (255,))
        else:
            rounded(d, (bx, y, bx + h, y + h), r if style != "pill" else h // 2, fill=(16, 20, 24, 170), outline=(255, 255, 255, 60))
        d.ellipse((bx + h * 0.35, y + h * 0.35, bx + h * 0.65, y + h * 0.65), fill=(255, 255, 255, 220))


def header_bar(img, d, y, style="glass", buttons_inside=False):
    if style == "hidden":
        return y
    if style == "glass":
        band = img.crop((0, y - BAR_H, W, y)).filter(ImageFilter.GaussianBlur(6))
        img.paste(band, (0, y))
        d.rectangle((0, y, W, y + BAR_H), fill=(20, 26, 34, 150))
    elif style == "solid":
        d.rectangle((0, y, W, y + BAR_H), fill=(26, 31, 40, 255))
    x = 12
    if buttons_inside:
        buttons(d, 10, y + 2, "neon", 1.0)
        x = 150
    for label in ("LAST PLAYED", "TIME PLAYED", "STATUS"):
        d.text((x, y + 4), label, font=font(6), fill=TEXT_DIM + (255,))
        d.rectangle((x, y + 14, x + 34, y + 17), fill=TEXT + (200,))
        x += 62
    return y + BAR_H


def info_area(img, d, y, blur_strength=0.25):
    if blur_strength > 0:
        band = img.crop((0, HERO_TOP, W, HERO_BOTTOM)).resize((W, H - y)).filter(ImageFilter.GaussianBlur(14))
        band = Image.blend(Image.new("RGBA", band.size, BG + (255,)), band.convert("RGBA"), min(1.0, blur_strength * 1.6))
        img.alpha_composite(band, (0, y))
    d.rectangle((12, y + 10, 62, y + 80), fill=(60, 90, 140, 255))
    for i in range(5):
        d.rectangle((76, y + 12 + i * 11, 76 + (170 if i < 4 else 90), y + 16 + i * 11), fill=TEXT_DIM + (200,))
    for i in range(4):
        d.rectangle((270, y + 12 + i * 11, 300, y + 16 + i * 11), fill=TEXT_DIM + (160,))
        d.rectangle((308, y + 12 + i * 11, 360, y + 16 + i * 11), fill=TEXT + (200,))


def scene(chips_style="pills", buttons_style="dune", actions="hero", bar="glass", shade_level=0.65,
          blur=0, valign="center", halign="left", info_blur=0.25, hero_bottom=HERO_BOTTOM):
    img = Image.new("RGBA", (W, H), BG + (255,))
    art = artwork(W, hero_bottom - HERO_TOP, blur=blur, valign=valign, halign=halign).convert("RGBA")
    img.paste(art, (0, HERO_TOP))
    shade(img, HERO_TOP, hero_bottom, shade_level)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 0, W, HERO_TOP), fill=TOP + (255,))
    for i in range(5):
        d.ellipse((8 + i * 16, 5, 16 + i * 16, 13), fill=TEXT_DIM + (255,))
    rounded(d, (110, 4, 230, 14), 4, fill=(40, 46, 56, 255))
    title_y = hero_bottom - 80 if chips_style != "hidden" else hero_bottom - 66
    d.text((14, title_y), "GAME TITLE", font=font(18, True), fill=(255, 255, 255, 255))
    y = title_y + 28
    if chips_style != "hidden":
        chips(d, 14, y, chips_style)
        y += 18
    if actions == "hero":
        buttons(d, 14, hero_bottom - 26, buttons_style)
    y = header_bar(img, d, hero_bottom, bar, buttons_inside=(actions == "bar"))
    info_area(img, d, y, info_blur)
    return img


def closeup(draw_fn, background="art"):
    img = Image.new("RGBA", (W, 110), BG + (255,))
    if background == "art":
        img.paste(artwork(W, 110).convert("RGBA"), (0, 0))
        shade(img, 0, 110, 0.85)
    d = ImageDraw.Draw(img, "RGBA")
    draw_fn(d)
    return img


def accent(color):
    img = Image.new("RGBA", (W, 140), BG + (255,))
    d = ImageDraw.Draw(img, "RGBA")
    rounded(d, (16, 16, 384, 124), 8, fill=PANEL + (255,))
    d.text((32, 28), "Links", font=font(10, True), fill=TEXT + (255,))
    for i, name in enumerate(("Steam", "PCGamingWiki", "Metacritic")):
        x = 32 + i * 112
        d.ellipse((x, 50, x + 12, 62), fill=color + (255,))
        d.text((x + 18, 49), name, font=font(9), fill=TEXT + (255,))
    rounded(d, (32, 78, 232, 84), 3, fill=(40, 46, 56, 255))
    rounded(d, (32, 78, 162, 84), 3, fill=color + (255,))
    rounded(d, (260, 72, 360, 108), 6, outline=color + (255,), width=2)
    d.text((282, 82), "Selected", font=font(9, True), fill=color + (255,))
    rounded(d, (32, 96, 120, 112), 4, fill=color + (60,), outline=color + (255,))
    return img


PRESETS = {
    "Style_Default": lambda: scene(),
    "Style_Neon": lambda: scene(chips_style="hidden", buttons_style="neon", actions="bar", shade_level=0.25),
    "Style_Dune": lambda: scene(chips_style="text", bar="transparent", shade_level=0.85, hero_bottom=165),
    "Style_Minimal": lambda: scene(chips_style="hidden", bar="hidden", shade_level=0.5),
    "Buttons_Dune": lambda: closeup(lambda d: buttons(d, 40, 30, "dune", 2.2)),
    "Buttons_Neon": lambda: closeup(lambda d: buttons(d, 40, 30, "neon", 2.2)),
    "Buttons_Pill": lambda: closeup(lambda d: buttons(d, 40, 30, "pill", 2.2)),
    "Buttons_Glass": lambda: closeup(lambda d: buttons(d, 40, 30, "glass", 2.2)),
    "ActionsLocation_Hero": lambda: scene(),
    "ActionsLocation_HeaderBar": lambda: scene(actions="bar"),
    "Chips_Pills": lambda: closeup(lambda d: chips(d, 20, 48, "pills")),
    "Chips_Text": lambda: closeup(lambda d: chips(d, 20, 48, "text")),
    "Chips_Outline": lambda: closeup(lambda d: chips(d, 20, 48, "outline")),
    "Chips_Hidden": lambda: scene(chips_style="hidden"),
    "Accent_Default": lambda: accent((26, 159, 255)),
    "Accent_Amber": lambda: accent((255, 181, 71)),
    "Accent_Violet": lambda: accent((167, 139, 250)),
    "Accent_Emerald": lambda: accent((52, 211, 153)),
    "Accent_Crimson": lambda: accent((248, 113, 113)),
    "Accent_Pink": lambda: accent((244, 114, 182)),
    "Accent_Cyan": lambda: accent((34, 211, 238)),
    "Accent_Gold": lambda: accent((250, 204, 21)),
    "Accent_Linkin": lambda: accent((230, 57, 70)),
    "HeroShade_None": lambda: scene(shade_level=0),
    "HeroShade_Light": lambda: scene(shade_level=0.35),
    "HeroShade_Medium": lambda: scene(shade_level=0.65),
    "HeroShade_Strong": lambda: scene(shade_level=0.85),
    "HeroBackground_Default": lambda: scene(),
    "HeroBackground_Soft": lambda: scene(blur=4),
    "HeroBackground_Strong": lambda: scene(blur=10),
    "BackgroundVertical_Default": lambda: scene(valign="center"),
    "BackgroundVertical_Top": lambda: scene(valign="top"),
    "BackgroundVertical_Bottom": lambda: scene(valign="bottom"),
    "BackgroundHorizontal_Default": lambda: scene(halign="left"),
    "BackgroundHorizontal_Center": lambda: scene(halign="center"),
    "BackgroundHorizontal_Right": lambda: scene(halign="right"),
    "HeaderBar_Glass": lambda: scene(bar="glass"),
    "HeaderBar_Solid": lambda: scene(bar="solid"),
    "HeaderBar_Transparent": lambda: scene(bar="transparent"),
    "HeaderBar_Hidden": lambda: scene(bar="hidden"),
    "BackgroundBlur_Default": lambda: scene(info_blur=0.25),
    "BackgroundBlur_Off": lambda: scene(info_blur=0),
    "BackgroundBlur_Light": lambda: scene(info_blur=0.15),
    "BackgroundBlur_Strong": lambda: scene(info_blur=0.5),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default="source/Presets/Previews")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, draw in PRESETS.items():
        image = draw().convert("RGB")
        image = image.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        image.save(out / f"{name}.png", optimize=True)
    print(f"{len(PRESETS)} previews written to {out}")


if __name__ == "__main__":
    main()
