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
import yaml

import color_profiles

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


def vertical_mask(size, start, end, peak=255):
    """L mask: 0 above `start`, rising to `peak` at `end` (fractions of the height)."""
    w, h = size
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    for y in range(h):
        t = y / max(1, h - 1)
        if t <= start:
            v = 0
        elif t >= end:
            v = peak
        else:
            v = int(peak * (t - start) / max(1e-6, end - start))
        d.line([(0, y), (w, y)], fill=v)
    return mask


BLUR_LEVELS = {"off": None, "light": (1, 3), "medium": (2, 6), "strong": (3, 10), "extreme": (5, 16)}
BLUR_HEIGHTS = {"small": (0.6, 0.75, 0.92), "medium": (0.45, 0.65, 0.9), "large": (0.3, 0.5, 0.8), "full": (0.0, 0.35, 0.7)}
CARD_SHAPES = {"card": (10, 8, True), "wide": (18, 12, True), "tight": (4, 4, True), "full": (0, 0, False)}
CORNERS = {"rounded": dict(card=10, panel=7, tile=7, chip=5), "square": dict(card=0, panel=0, tile=0, chip=0),
           "subtle": dict(card=5, panel=4, tile=4, chip=3), "round": dict(card=14, panel=10, tile=9, chip=7)}
GLASS = {"glass": (16, 26, 24), "frosted": (30, 36, 34), "clear": (8, 18, 10), "borderless": (16, 0, 24)}
PAGES = {"glass": 0.55, "clear": 0.35, "dark": 0.75, "tinted": 0.55, "ambient": None, "solid": None}


def tile_row(d, x, y, style, corners, glass, actions_inside=False):
    """Row of information tiles (or the classic bar) under the card; returns the row height."""
    if style == "hidden":
        return 0
    labels = [("Time played", "1h 51"), ("Last played", "Thu"), ("Status", "Playing"), ("HowLongToBeat", "20h"),
              ("Achievements", "12/40"), ("Scores", "89 · 80"), ("Size", "2.3 GB")]
    if actions_inside:
        buttons(d, x, y + 5, "neon", 0.85)
        x += 130
    if style in ("bar", "solidbar"):
        d.rectangle((0, y, W, y + BAR_H), fill=(26, 31, 40, 255) if style == "solidbar" else (36, 44, 56, 200))
        for label, value in labels[:5]:
            if x > W - 40:
                break
            d.text((x, y + 4), label, font=font(6), fill=TEXT_DIM + (255,))
            d.text((x, y + 12), value, font=font(8, True), fill=TEXT + (255,))
            x += 52
        return BAR_H
    pad, gap, value_size = {"tiles": (5, 5, 9), "large": (7, 6, 11), "compact": (3, 3, 8), "text": (0, 12, 9)}[style]
    h = {"tiles": 28, "large": 34, "compact": 22, "text": 24}[style]
    fill_alpha, border_alpha, _ = glass
    for label, value in labels:
        f = font(value_size, True)
        w = max(int(d.textlength(value, font=f)), int(d.textlength(label, font=font(6)))) + pad * 2 + 2
        if x + w > W - 8:
            break
        if style != "text":
            rounded(d, (x, y + 4, x + w, y + 4 + h), corners["tile"], fill=TEXT + (fill_alpha,),
                    outline=(255, 255, 255, border_alpha) if border_alpha else None)
        d.text((x + pad, y + 4 + pad), label, font=font(6), fill=TEXT_DIM + (255,))
        d.text((x + pad, y + 4 + pad + 8), value, font=f, fill=(255, 255, 255, 255))
        x += w + gap
    return h + 8


def page_background(img, page, top):
    """Liquid glass: the artwork blurred behind the whole page, under a scrim."""
    scrim = PAGES[page]
    if scrim is None:
        return
    back = artwork(W, H - top).filter(ImageFilter.GaussianBlur(18)).convert("RGBA")
    if page == "tinted":
        layer = Image.new("RGBA", back.size, ACCENT + (46,))
        back.alpha_composite(layer)
    back.alpha_composite(Image.new("RGBA", back.size, (0, 0, 0, int(255 * scrim))))
    img.paste(back.convert("RGB"), (0, top))


def card_scene(shape="card", blur="medium", blur_height="medium", tint=(0.3, 0.0), cover=0, tiles="tiles",
               actions=2, chips_style="pills", shade_level=0.35, art_blur=0, valign="center", halign="left",
               info_cover=False, page="glass", corners="rounded", glass="glass", reflection=0.0, outline=True):
    """The Details view: artwork card with its blurred band, cover, tiles and glass panels.

    Drawn on an RGB image so the translucent fills blend (Pillow replaces RGBA pixels instead)."""
    img = Image.new("RGB", (W, H), BG)
    page_background(img, page, HERO_TOP)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 0, W, HERO_TOP), fill=TOP + (255,))
    for i in range(5):
        d.ellipse((8 + i * 16, 5, 16 + i * 16, 13), fill=TEXT_DIM + (255,))
    rounded(d, (110, 4, 230, 14), 4, fill=(40, 46, 56, 255))

    radii = CORNERS[corners]
    glass_level = GLASS[glass]
    side, top, card_outline = CARD_SHAPES[shape]
    radius = 0 if shape == "full" else radii["card"]
    cx0, cy0, cx1, cy1 = side, HERO_TOP + top, W - side, 140
    cw, ch = cx1 - cx0, cy1 - cy0
    card = artwork(cw, ch, blur=art_blur, valign=valign, halign=halign).convert("RGBA")
    if BLUR_LEVELS[blur]:
        soft, strong = BLUR_LEVELS[blur]
        start, mid, full = BLUR_HEIGHTS[blur_height]
        card = Image.composite(card.filter(ImageFilter.GaussianBlur(soft)), card, vertical_mask(card.size, start, mid))
        card = Image.composite(card.filter(ImageFilter.GaussianBlur(strong)), card, vertical_mask(card.size, mid, full))
    start = BLUR_HEIGHTS[blur_height][0]
    for color, opacity in ((ACCENT, tint[0]), ((255, 255, 255), tint[1])):
        if opacity > 0:
            layer = Image.new("RGBA", card.size, color + (0,))
            layer.putalpha(vertical_mask(card.size, start, 1.0, int(255 * opacity)))
            card.alpha_composite(layer)
    shade(card, 0, ch, shade_level)
    if reflection:
        band = card.transpose(Image.FLIP_TOP_BOTTOM).resize((W, 70)).filter(ImageFilter.GaussianBlur(10))
        img.paste(Image.blend(Image.new("RGB", band.size, BG), band.convert("RGB"), reflection * 1.6), (0, cy1))
        d = ImageDraw.Draw(img, "RGBA")
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ch - 1), radius=radius, fill=255)
    if shape == "full":
        mask = Image.eval(vertical_mask(card.size, 0.75, 1.0), lambda v: 255 - v)
    img.paste(card, (cx0, cy0), mask)
    if card_outline and outline and glass != "borderless":
        rounded(d, (cx0, cy0, cx1 - 1, cy1 - 1), radius, outline=(255, 255, 255, 45))

    row_y = cy1 + 2
    cover_w, cover_h = 44, 66
    left = cx0 + 10
    tiles_x = (left + cover_w + 12) if (cover == 0 and tiles != "hidden") else left
    row_h = tile_row(d, tiles_x, row_y, tiles, radii, glass_level, actions_inside=(actions == 1))
    if cover != 2:
        bottom = row_y + 30 if (cover == 0 and tiles != "hidden") else cy1 - 8
        box = (left, bottom - cover_h, left + cover_w, bottom)
        cr = max(2, radii["chip"] + 1) if corners != "square" else 0
        rounded(d, (box[0] + 2, box[1] + 5, box[2] + 2, box[3] + 5), cr, fill=(0, 0, 0, 110))
        cov = Image.new("RGBA", (cover_w, cover_h))
        cd = ImageDraw.Draw(cov)
        for yy in range(cover_h):
            t = yy / cover_h
            cd.line([(0, yy), (cover_w, yy)], fill=(int(90 - 50 * t), int(61 - 30 * t), int(134 - 80 * t), 255))
        cd.text((5, 27), "COVER", font=font(7, True), fill=(220, 210, 240, 255))
        cmask = Image.new("L", cov.size, 0)
        ImageDraw.Draw(cmask).rounded_rectangle((0, 0, cover_w - 1, cover_h - 1), cr, fill=255)
        img.paste(cov, box[:2], cmask)
        rounded(d, box, cr, outline=(255, 255, 255, 120), width=1)
        band_x = box[2] + 10
    else:
        band_x = left + 4

    title_y = cy1 - (66 if chips_style != "hidden" else 50)
    if actions == 0:
        title_y -= 16
    d.text((band_x, title_y), "GAME TITLE", font=font(16, True), fill=(255, 255, 255, 255))
    y = title_y + 22
    d.text((band_x, y), "Studio · 2018 · PC · Steam", font=font(7), fill=(235, 235, 245, 230))
    y += 12
    if chips_style != "hidden":
        chips(d, band_x, y, chips_style, count=4 if actions == 2 else 6)
        y += 18
    if actions == 0:
        buttons(d, band_x, y + 1, "dune", 0.9)
    elif actions == 2:
        buttons(d, cx1 - 150, cy1 - 28, "dune", 1.0)

    info_y = row_y + max(row_h, 34 if cover == 0 and tiles != "hidden" else 0) + 4
    x = cx0 if shape != "full" else 10
    right = cx1 if shape != "full" else W - 10
    fill_alpha, border_alpha, _ = glass_level
    if info_cover:
        rounded(d, (x, info_y + 4, x + 32, info_y + 52), radii["chip"], fill=(60, 90, 140, 255))
        x += 40
    widths = (3, 3, 2)
    total = right - x - 16
    for part in widths:
        w = int(total * part / sum(widths))
        rounded(d, (x, info_y + 4, x + w, H - 8), radii["panel"], fill=TEXT + (fill_alpha,),
                outline=(255, 255, 255, border_alpha) if border_alpha else None)
        d.text((x + 8, info_y + 9), "SECTION", font=font(6, True), fill=TEXT_DIM + (255,))
        for j in range(3):
            d.rectangle((x + 8, info_y + 20 + j * 9, x + w - 12 - (j % 2) * 20, info_y + 23 + j * 9), fill=TEXT_DIM + (170,))
        cx = x + 8
        for k in range(3):
            rounded(d, (cx, H - 24, cx + 22, H - 14), radii["chip"], fill=TEXT + (glass_level[2],))
            cx += 26
        x += w + 8
    return img


def animation_preview(mode):
    """Three frames of the hero fade-in, with the speed of each choice."""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    frames = {"smooth": (0.15, 0.6, 1.0), "fast": (0.6, 1.0, 1.0), "off": (1.0, 1.0, 1.0)}[mode]
    for i, opacity in enumerate(frames):
        x0 = 14 + i * 128
        card = artwork(116, 90).convert("RGB")
        dark = Image.new("RGB", card.size, BG)
        img.paste(Image.blend(dark, card, opacity), (x0, 40))
        d.text((x0 + 8, 100 - int(12 * (1 - opacity))), "TITLE", font=font(10, True), fill=(255, 255, 255, int(255 * opacity)))
        d.text((x0 + 40, 140), f"{i * (150 if mode == 'fast' else 300) if mode != 'off' else 0} ms", font=font(9), fill=TEXT_DIM + (255,))
    label = {"smooth": "Smooth: fade and slide, about 300 ms", "fast": "Fast: about 150 ms", "off": "Off: shows at once"}[mode]
    d.text((14, 190), label, font=font(12, True), fill=TEXT + (255,))
    for i in range(2):
        d.line([(132 + i * 128, 85), (140 + i * 128, 85)], fill=ACCENT + (255,), width=2)
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


def top_panel(layout):
    img = Image.new("RGBA", (W, 90), BG + (255,))
    img.paste(artwork(W, 90).convert("RGBA"), (0, 0))
    shade(img, 0, 90, 0.6)
    d = ImageDraw.Draw(img, "RGBA")
    if layout == "neon":
        d.rectangle((0, 0, W, 28), fill=TOP + (255,))
        x = 10
        d.ellipse((x, 7, x + 14, 21), fill=ACCENT + (255,))
        rounded(d, (x + 22, 7, x + 122, 21), 4, fill=(40, 46, 56, 255))
        x += 132
        for i in range(6):
            rounded(d, (x + i * 20, 7, x + i * 20 + 14, 21), 3, fill=TEXT_DIM + (255,))
    else:
        d.line([(0, 28), (W, 28)], fill=(255, 255, 255, 40))
        d.ellipse((10, 7, 24, 21), fill=ACCENT + (255,))
        rounded(d, (32, 7, 112, 21), 4, fill=(40, 46, 56, 200))
        cx = W // 2 - 60
        for i in range(6):
            rounded(d, (cx + i * 20, 7, cx + i * 20 + 14, 21), 3, fill=TEXT + (230,))
        d.line([(cx + 2, 25), (cx + 12, 25)], fill=ACCENT + (255,), width=2)
        for i in range(3):
            d.ellipse((W - 70 + i * 18, 8, W - 58 + i * 18, 20), fill=TEXT_DIM + (255,))
    d.text((14, 48), "GAME TITLE", font=font(16, True), fill=(255, 255, 255, 255))
    return img



def color_profile(palette):
    """A small library window drawn with the colors a profile derives."""
    c = color_profiles.derive(palette)
    rgb = lambda value: color_profiles.parse(color_profiles.fmt(value))  # noqa: E731
    def col(key, index=None):
        value = c[key] if index is None else c[key][index]
        return tuple(int(round(v)) for v in rgb(value))
    img = Image.new("RGBA", (W, H), col("WindowBackgroundGradientColor2"))
    d = ImageDraw.Draw(img, "RGBA")
    top, bottom = col("WindowBackgroundGradientColor1"), col("WindowBackgroundGradientColor2")
    for y in range(26, H):
        t = (y - 26) / (H - 26)
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)) + (255,))
    # top panel
    d.rectangle((0, 0, W, 26), fill=col("TopPanelBackgroundBrush"))
    d.ellipse((10, 7, 22, 19), fill=col("GlyphColor"))
    rounded(d, (30, 6, 130, 20), 4, fill=col("TopPanelSearchBoxBackgroundBrush"))
    for i in range(5):
        rounded(d, (150 + i * 18, 8, 160 + i * 18, 18), 2, fill=col("TopPanelItemForegroundBrush"))
    rounded(d, (W - 76, 7, W - 16, 19), 3, fill=col("TopPanelItemForegroundBrush"))
    # game list
    d.rectangle((0, 26, 124, H), fill=col("LibraryDetailsViewBackgroundBrush"))
    for i in range(9):
        y = 36 + i * 22
        if i == 2:
            d.rectangle((0, y - 4, 124, y + 14), fill=col("DetailsViewItemIsSelectedBackgroundBrush"))
        if i == 4:
            d.rectangle((0, y - 4, 124, y + 14), fill=col("DetailsViewItemIsMouseOverBackgroundBrush"))
        key = "LibraryDetailsViewIsRunningForegroundBrush" if i == 6 else (
            "LibraryDetailsViewNotInstalledForegroundBrush" if i in (5, 8) else "TextColor")
        d.rectangle((10, y + 2, 10 + 60 + (i * 13) % 40, y + 8), fill=col(key))
    # header: title, chips, buttons
    d.text((140, 36), "GAME TITLE", font=font(17, True), fill=col("DetailsViewOverviewHeaderLabelBrush"))
    x = 140
    for width in (44, 58, 38, 50):
        rounded(d, (x, 62, x + width, 76), 7, fill=col("HeroSecondaryButtonBackgroundBrush"),
                outline=col("HeroSecondaryButtonBorderBrush"))
        d.rectangle((x + 8, 67, x + width - 8, 71), fill=col("TextColor"))
        x += width + 6
    play = Image.new("RGBA", (118, 30))
    pd = ImageDraw.Draw(play)
    stops = [col("PlayButtonBackgroundColor1"), col("PlayButtonBackgroundColor2"), col("PlayButtonBackgroundColor3")]
    for xx in range(118):
        t = xx / 117
        a, b, f = (stops[0], stops[1], t / 0.75) if t < 0.75 else (stops[1], stops[2], (t - 0.75) / 0.25)
        pd.line([(xx, 0), (xx, 30)], fill=tuple(int(a[i] * (1 - f) + b[i] * f) for i in range(3)) + (255,))
    mask = Image.new("L", (118, 30), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 117, 29), 6, fill=255)
    img.paste(play, (140, 88), mask)
    d.text((176, 95), "PLAY", font=font(11, True), fill=(255, 255, 255, 255))
    rounded(d, (264, 88, 294, 118), 6, fill=col("ContextButtonBackgroundColor2"))
    rounded(d, (300, 88, 330, 118), 6, fill=col("HeroSecondaryButtonBackgroundBrush"), outline=col("GlyphColor"), width=2)
    # section card with progress and ratings
    rounded(d, (140, 132, W - 14, H - 40), 8, fill=col("ControlBackgroundColor"))
    d.text((152, 140), "Achievements", font=font(10, True), fill=col("TextColor"))
    d.text((152, 156), "42 / 60", font=font(9), fill=col("TextColorDarker"))
    rounded(d, (152, 174, W - 28, 180), 3, fill=col("ProgressBarBackgroundBrush"))
    rounded(d, (152, 174, 152 + int((W - 180) * 0.7), 180), 3, fill=col("GlyphColor"))
    for i, key in enumerate(("PositiveRatingBrush", "MixedRatingBrush", "NegativeRatingBrush", "DataChangeNotifColor")):
        d.ellipse((152 + i * 22, 188, 164 + i * 22, 200), fill=col(key))
    rounded(d, (260, 186, W - 28, 202), 4, fill=col("MenusPopupsHoverBrush"))
    d.text((268, 188), "Menu item", font=font(9), fill=col("MenusPopupMouseOverForegroundBrush"))
    # base palette strip
    keys = ("bg_deep", "bg", "panel", "control", "text_dim", "text", "accent", "accent2", "play")
    for i, key in enumerate(keys):
        x0 = 140 + i * 27
        rounded(d, (x0, H - 30, x0 + 23, H - 12), 3, fill=color_profiles.parse(palette[key]), outline=(255, 255, 255, 60))
    return img


def tile_preview(entry):
    """Preview of one header tile type: the card edge, the tiles row with the slot outlined and a close-up."""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    cx0, cy0, cx1, cy1 = 10, 8, W - 10, 104
    card = artwork(cx1 - cx0, cy1 - cy0, valign="bottom").convert("RGBA")
    soft, strong = BLUR_LEVELS["medium"]
    card = Image.composite(card.filter(ImageFilter.GaussianBlur(soft)), card, vertical_mask(card.size, 0.2, 0.5))
    card = Image.composite(card.filter(ImageFilter.GaussianBlur(strong)), card, vertical_mask(card.size, 0.5, 0.85))
    layer = Image.new("RGBA", card.size, ACCENT + (0,))
    layer.putalpha(vertical_mask(card.size, 0.2, 1.0, 70))
    card.alpha_composite(layer)
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=10, fill=255)
    img.paste(card, (cx0, cy0), mask)
    rounded(d, (cx0, cy0, cx1 - 1, cy1 - 1), 10, outline=(255, 255, 255, 45))
    d.text((80, 50), "GAME TITLE", font=font(15, True), fill=(255, 255, 255, 255))
    rounded(d, (20, 72, 66, 141), 6, fill=(74, 50, 112, 255), outline=(255, 255, 255, 120))
    d.text((27, 100), "COVER", font=font(7, True), fill=(220, 210, 240, 255))

    empty = entry["value"] == 0
    label = entry["en"].split(" (")[0].upper()
    value = entry.get("example", "")
    x, y = 78, 110
    neighbours = [("TIME", "1h 51"), ("LAST", "Thu"), (None, None), ("STATUS", "Playing"), ("SIZE", "2.3 GB")]
    for small_label, small_value in neighbours:
        if small_label is None:
            w = 64
            if empty:
                for i in range(0, w, 6):
                    d.line([(x + i, y + 4), (x + min(i + 3, w), y + 4)], fill=ACCENT + (255,), width=1)
                    d.line([(x + i, y + 30), (x + min(i + 3, w), y + 30)], fill=ACCENT + (255,), width=1)
            else:
                rounded(d, (x, y + 4, x + w, y + 30), 5, fill=TEXT + (40,), outline=ACCENT + (255,), width=2)
                d.text((x + 5, y + 7), label[:12], font=font(6), fill=TEXT_DIM + (255,))
                d.text((x + 5, y + 16), value[:10], font=font(8, True), fill=TEXT + (255,))
        else:
            # the other slots stay neutral, so the preview never shows the same information twice
            w = 44
            rounded(d, (x, y + 4, x + w, y + 30), 5, fill=TEXT + (18,))
            d.rectangle((x + 5, y + 9, x + 22, y + 11), fill=TEXT_DIM + (120,))
            d.rectangle((x + 5, y + 18, x + 34, y + 22), fill=TEXT + (90,))
        x += w + 6
        if x > W - 40:
            break

    # close-up of the tile
    bx0, by0, bx1, by1 = 70, 158, W - 70, 228
    if empty:
        for i in range(bx0, bx1, 8):
            d.line([(i, by0), (min(i + 4, bx1), by0)], fill=ACCENT + (255,), width=2)
            d.line([(i, by1), (min(i + 4, bx1), by1)], fill=ACCENT + (255,), width=2)
        d.text((bx0 + 18, by0 + 24), "Empty slot: the next tiles move left", font=font(10), fill=TEXT_DIM + (255,))
    else:
        rounded(d, (bx0, by0, bx1, by1), 10, fill=TEXT + (26,), outline=ACCENT + (255,), width=2)
        d.text((bx0 + 14, by0 + 10), label, font=font(9), fill=TEXT_DIM + (255,))
        d.text((bx0 + 14, by0 + 26), value, font=font(20, True), fill=(255, 255, 255, 255))
        if entry["id"] in ("Achievements", "AchievementsPercent"):
            rounded(d, (bx0 + 14, by1 - 12, bx1 - 14, by1 - 7), 2, fill=(255, 255, 255, 40))
            rounded(d, (bx0 + 14, by1 - 12, bx0 + 14 + int((bx1 - bx0 - 28) * 0.3), by1 - 7), 2, fill=(242, 184, 75, 255))
        elif entry["id"] == "HltbAll":
            span = bx1 - bx0 - 28
            for start, part, color in ((0, 0.35, (74, 168, 255)), (0.35, 0.12, (122, 108, 255)), (0.47, 0.53, (63, 191, 79))):
                d.rectangle((bx0 + 14 + int(span * start), by1 - 12, bx0 + 14 + int(span * (start + part)), by1 - 7),
                            fill=color + (255,))
    note = f"Needs {entry['needs']}" if entry.get("needs") else ("" if empty else "Hidden when the game has no value")
    d.text((bx0, by1 + 6), note, font=font(8), fill=TEXT_DIM + (255,))
    return img


def tile_previews():
    spec = yaml.safe_load(Path(__file__).with_name("options_spec.yaml").read_text(encoding="utf-8"))
    section = spec.get("header_tiles") or {}
    return {f"Tile_{entry['id']}": (lambda e: lambda: tile_preview(e))(entry) for entry in section.get("types", [])}


def color_profile_previews():
    spec = yaml.safe_load(Path(__file__).with_name("options_spec.yaml").read_text(encoding="utf-8"))
    section = spec.get("color_profiles") or {}
    previews = {"ColorProfile_Default": lambda: color_profile(section["default_palette"])} if section else {}
    for profile in section.get("profiles", []):
        previews[f"ColorProfile_{profile['id']}"] = (lambda palette: lambda: color_profile(palette))(profile["palette"])
    return previews

PRESETS = {
    "Style_Default": lambda: card_scene(),
    "Style_Dune": lambda: card_scene(blur="strong", blur_height="large", chips_style="text", shade_level=0.5),
    "Style_Neon": lambda: card_scene(shape="full", blur="off", tint=(0, 0), cover=2, tiles="bar", actions=1, chips_style="hidden",
                                     shade_level=0.25, page="ambient", reflection=0.25, info_cover=True),
    "Style_Minimal": lambda: card_scene(chips_style="hidden", tiles="hidden", shade_level=0.5),
    "Corners_Default": lambda: card_scene(corners="rounded"),
    "Corners_Square": lambda: card_scene(corners="square"),
    "Corners_Subtle": lambda: card_scene(corners="subtle"),
    "Corners_Round": lambda: card_scene(corners="round"),
    "PageBackground_Default": lambda: card_scene(page="glass"),
    "PageBackground_Clear": lambda: card_scene(page="clear"),
    "PageBackground_Dark": lambda: card_scene(page="dark"),
    "PageBackground_Tinted": lambda: card_scene(page="tinted"),
    "PageBackground_Ambient": lambda: card_scene(page="ambient", reflection=0.25),
    "PageBackground_Solid": lambda: card_scene(page="solid"),
    "Glass_Default": lambda: card_scene(glass="glass"),
    "Glass_Frosted": lambda: card_scene(glass="frosted"),
    "Glass_Clear": lambda: card_scene(glass="clear"),
    "Glass_Borderless": lambda: card_scene(glass="borderless"),
    "HeroCard_Default": lambda: card_scene(shape="card"),
    "HeroCard_Wide": lambda: card_scene(shape="wide"),
    "HeroCard_Tight": lambda: card_scene(shape="tight"),
    "HeroCard_FullWidth": lambda: card_scene(shape="full"),
    "HeroBlur_Default": lambda: card_scene(blur="medium"),
    "HeroBlur_Off": lambda: card_scene(blur="off"),
    "HeroBlur_Light": lambda: card_scene(blur="light"),
    "HeroBlur_Strong": lambda: card_scene(blur="strong"),
    "HeroBlur_Extreme": lambda: card_scene(blur="extreme"),
    "HeroBlurHeight_Default": lambda: card_scene(blur="strong", blur_height="medium"),
    "HeroBlurHeight_Small": lambda: card_scene(blur="strong", blur_height="small"),
    "HeroBlurHeight_Large": lambda: card_scene(blur="strong", blur_height="large"),
    "HeroBlurHeight_Full": lambda: card_scene(blur="strong", blur_height="full"),
    "HeroTint_Default": lambda: card_scene(tint=(0.3, 0)),
    "HeroTint_None": lambda: card_scene(tint=(0, 0)),
    "HeroTint_AccentStrong": lambda: card_scene(tint=(0.55, 0)),
    "HeroTint_Frost": lambda: card_scene(tint=(0, 0.12)),
    "HeroTint_AccentFrost": lambda: card_scene(tint=(0.25, 0.08)),
    "HeroShade_Default": lambda: card_scene(shade_level=0.35),
    "HeroShade_None": lambda: card_scene(shade_level=0),
    "HeroShade_Medium": lambda: card_scene(shade_level=0.65),
    "HeroShade_Strong": lambda: card_scene(shade_level=0.85),
    "HeroCover_Default": lambda: card_scene(cover=0),
    "HeroCover_Inside": lambda: card_scene(cover=1),
    "HeroCover_InsideKeepPanel": lambda: card_scene(cover=1, info_cover=True),
    "HeroCover_Hidden": lambda: card_scene(cover=2, info_cover=True),
    "Buttons_Default": lambda: closeup(lambda d: buttons(d, 40, 30, "dune", 2.2)),
    "Buttons_Dune": lambda: closeup(lambda d: buttons(d, 40, 30, "dune", 2.2)),
    "Buttons_Neon": lambda: closeup(lambda d: buttons(d, 40, 30, "neon", 2.2)),
    "Buttons_Pill": lambda: closeup(lambda d: buttons(d, 40, 30, "pill", 2.2)),
    "Buttons_Glass": lambda: closeup(lambda d: buttons(d, 40, 30, "glass", 2.2)),
    "ActionsLocation_Default": lambda: card_scene(actions=2),
    "ActionsLocation_HeroRight": lambda: card_scene(actions=2),
    "ActionsLocation_Hero": lambda: card_scene(actions=0),
    "ActionsLocation_HeaderBar": lambda: card_scene(actions=1),
    "Chips_Default": lambda: closeup(lambda d: chips(d, 20, 48, "pills")),
    "Chips_Pills": lambda: closeup(lambda d: chips(d, 20, 48, "pills")),
    "Chips_Text": lambda: closeup(lambda d: chips(d, 20, 48, "text")),
    "Chips_Outline": lambda: closeup(lambda d: chips(d, 20, 48, "outline")),
    "Chips_Hidden": lambda: card_scene(chips_style="hidden"),
    "TopPanel_Default": lambda: top_panel("neon"),
    "TopPanel_Dune": lambda: top_panel("dune"),
    "Accent_Default": lambda: accent((26, 159, 255)),
    "Accent_Amber": lambda: accent((255, 181, 71)),
    "Accent_Violet": lambda: accent((167, 139, 250)),
    "Accent_Emerald": lambda: accent((52, 211, 153)),
    "Accent_Crimson": lambda: accent((248, 113, 113)),
    "Accent_Pink": lambda: accent((244, 114, 182)),
    "Accent_Cyan": lambda: accent((34, 211, 238)),
    "Accent_Gold": lambda: accent((250, 204, 21)),
    "Accent_Linkin": lambda: accent((230, 57, 70)),
    "Animations_Default": lambda: animation_preview("smooth"),
    "Animations_Fast": lambda: animation_preview("fast"),
    "Animations_Off": lambda: animation_preview("off"),
    "HeroBackground_Default": lambda: card_scene(),
    "HeroBackground_Soft": lambda: card_scene(art_blur=4),
    "HeroBackground_Strong": lambda: card_scene(art_blur=10),
    "BackgroundVertical_Default": lambda: card_scene(valign="center"),
    "BackgroundVertical_Top": lambda: card_scene(valign="top"),
    "BackgroundVertical_Bottom": lambda: card_scene(valign="bottom"),
    "BackgroundHorizontal_Default": lambda: card_scene(halign="left"),
    "BackgroundHorizontal_Center": lambda: card_scene(halign="center"),
    "BackgroundHorizontal_Right": lambda: card_scene(halign="right"),
    "HeaderBar_Default": lambda: card_scene(tiles="tiles"),
    "HeaderBar_Large": lambda: card_scene(tiles="large"),
    "HeaderBar_Compact": lambda: card_scene(tiles="compact"),
    "HeaderBar_TextOnly": lambda: card_scene(tiles="text"),
    "HeaderBar_Bar": lambda: card_scene(tiles="bar"),
    "HeaderBar_SolidBar": lambda: card_scene(tiles="solidbar"),
    "HeaderBar_Hidden": lambda: card_scene(tiles="hidden"),
}


def missing_previews(names):
    """Spec choices that have no preview (the generated tile slots use the Tile_<type> images)."""
    spec = yaml.safe_load(Path(__file__).with_name("options_spec.yaml").read_text(encoding="utf-8"))
    missing = []
    for group in spec["presets"]:
        for option in group["options"]:
            name = f"{group['group']}_{option['id']}"
            if name not in names:
                missing.append(name)
    return missing


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default="source/Presets/Previews")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    extra = {**color_profile_previews(), **tile_previews()}
    for name, draw in {**PRESETS, **extra}.items():
        image = draw().convert("RGB")
        image = image.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        image.save(out / f"{name}.png", optimize=True)
    print(f"{len(PRESETS) + len(extra)} previews written to {out}")
    missing = missing_previews(set(PRESETS) | set(extra))
    if missing:
        print("no preview for: " + ", ".join(missing))


if __name__ == "__main__":
    main()
