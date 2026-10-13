#!/usr/bin/env python3
"""Color profiles: full theme palettes built from a few base colors.

Each profile in the color_profiles section of tools/options_spec.yaml gives 13 base colors.
derive() turns them into a value for every color resource of Constants.xaml that holds a
literal color, and profile_file() writes them as a preset resource file
(Presets/Colors/<Id>.xaml) that Theme Options loads over Constants.xaml.

Brush geometry (gradient direction, stop offsets, radial centers, opacity) is copied from
Constants.xaml; only the colors change. Text on buttons is kept readable: button colors are
darkened until white text reaches a minimum contrast ratio.

Used by tools/build_options.py (files and preset list) and tools/make_previews.py (previews).
"""
import re

BASE_KEYS = ("bg_deep", "bg", "panel", "control", "text", "text_dim", "accent", "accent2",
             "play", "positive", "mixed", "negative", "orange")

WHITE = (255, 255, 255, 255)
NEUTRAL_KEYS = {"BlackColor", "WhiteColor", "TextColorDark"}


# ---------------------------------------------------------------------------- color helpers
def parse(value):
    """'#RGB', '#RRGGBB' or '#AARRGGBB' -> (r, g, b, a)."""
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) == 6:
        text = "FF" + text
    if len(text) != 8 or not re.fullmatch(r"[0-9A-Fa-f]{8}", text):
        raise ValueError(f"not a color: {value}")
    a, r, g, b = (int(text[i:i + 2], 16) for i in range(0, 8, 2))
    return (r, g, b, a)


def fmt(color):
    r, g, b, a = (max(0, min(255, round(v))) for v in color)
    return f"#{r:02X}{g:02X}{b:02X}" if a == 255 else f"#{a:02X}{r:02X}{g:02X}{b:02X}"


def mix(c1, c2, weight):
    """weight of c1 (0..1) blended with c2; alpha comes from c1."""
    return tuple(c1[i] * weight + c2[i] * (1 - weight) for i in range(3)) + (c1[3],)


def lighten(color, amount):
    return mix(WHITE, color, amount)[:3] + (color[3],)


def darken(color, amount):
    return tuple(v * (1 - amount) for v in color[:3]) + (color[3],)


def alpha(color, value):
    return color[:3] + (value,)


def luminance(color):
    def channel(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(v) for v in color[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(c1, c2):
    l1, l2 = sorted((luminance(c1), luminance(c2)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def readable(color, foreground=WHITE, ratio=3.0):
    """Darken color until foreground text on it reaches the contrast ratio."""
    for _ in range(40):
        if contrast(color, foreground) >= ratio:
            break
        color = darken(color, 0.04)
    return color


# ---------------------------------------------------------------------------- derivation
def derive(palette):
    """Base palette -> {resource key: color or list of gradient stop colors}."""
    missing = [k for k in BASE_KEYS if k not in palette]
    if missing:
        raise ValueError("palette misses " + ", ".join(missing))
    p = {k: parse(palette[k]) for k in BASE_KEYS}
    bg_deep, bg, panel, control = p["bg_deep"], p["bg"], p["panel"], p["control"]
    text, text_dim, accent, accent2 = p["text"], p["text_dim"], p["accent"], p["accent2"]

    play = readable(p["play"], WHITE, 3.0)          # play button, white text
    act = readable(accent2, WHITE, 3.2)             # install and context buttons, white text
    bright = mix(text, WHITE, 0.4)                  # text over artwork and hovered icons
    selected = mix(accent, control, 0.28)           # selected rows and hovered expanders
    menu_hover = mix(text, accent, 0.88)            # light menu highlight...
    menu_text = mix(bg_deep, control, 0.6)          # ...with dark text on it

    colors = {
        # Color resources
        "TextColor": text,
        "TextColorDarker": text_dim,
        "MainColor": mix(accent, bg, 0.30),
        "MainColorDark": mix(accent, bg_deep, 0.12),
        "HoverColor": readable(darken(accent, 0.25), text, 3.0),
        "GlyphColor": accent,
        "GlyphSubColor": accent2,
        "HighlightGlyphColor": alpha(lighten(accent, 0.25), 0x88),
        "PopupBackgroundColor": panel,
        "PopupBorderColor": mix(accent, control, 0.45),
        "BackgroundToneColor": mix(accent, panel, 0.22),
        "GridItemBackgroundColor": lighten(control, 0.04),
        "PanelSeparatorColor": bg_deep,
        "DataChangeNotifColor": p["orange"],
        "ControlBackgroundColor": control,
        "ControlBackgroundColorDarker": mix(control, bg_deep, 0.5),
        "ControlBackgroundColorDark": alpha(mix(control, bg_deep, 0.45), 0x99),
        "ControlBackgroundColorDarkHover": lighten(control, 0.05),
        "ToggleButtonNotCheckedBorderColor": mix(text_dim, control, 0.55),
        "DetailsViewContainerLabelColor": mix(text_dim, bg, 0.75),
        "PopupBackgroundGradientColor1": control,
        "PopupBackgroundGradientColor2": mix(control, panel, 0.75),
        "WindowBackgroundGradientColor1": bg,
        "WindowBackgroundGradientColor2": bg_deep,
        "PlayButtonBackgroundColor1": lighten(play, 0.14),
        "PlayButtonBackgroundColor2": play,
        "PlayButtonBackgroundColor3": darken(play, 0.07),
        "PlayButtonIsMouseOverBackgroundColor1": lighten(play, 0.26),
        "PlayButtonIsMouseOverBackgroundColor2": lighten(play, 0.14),
        "PlayButtonIsMouseOverBackgroundColor3": lighten(play, 0.05),
        "ContextButtonBackgroundColor1": lighten(act, 0.14),
        "ContextButtonBackgroundColor2": act,
        "ContextButtonBackgroundColor3": darken(act, 0.08),
        "ContextButtonIsMouseOverBackgroundColor1": lighten(act, 0.28),
        "ContextButtonIsMouseOverBackgroundColor2": lighten(act, 0.16),
        "ContextButtonIsMouseOverBackgroundColor3": lighten(act, 0.08),

        # solid brushes
        "LibraryDetailsViewNotInstalledForegroundBrush": mix(text_dim, accent, 0.9),
        "LibraryDetailsViewIsLaunchingForegroundBrush": accent,
        "LibraryDetailsViewIsRunningForegroundBrush": p["positive"],
        "PlayersCountDetailsViewForegroundBrush": alpha(text, 0x99),
        "PlayersCountGridViewForegroundBrush": p["positive"],
        "HeroSecondaryButtonBackgroundBrush": alpha(bg_deep, 0x66),
        "HeroSecondaryButtonHoverBackgroundBrush": alpha(lighten(control, 0.04), 0x99),
        "HeroSecondaryButtonBorderBrush": alpha(mix(text, accent, 0.8), 0x33),
        "DetailsViewBannerPanelBorderBrush": alpha(text, 0x4D),
        "DetailsViewBannerPanelBackgroundBrush": alpha(bg_deep, 0x4D),
        "GridViewItemMaskBackgroundBrush": mix(bg_deep, control, 0.7),
        "ProgressBarBackgroundBrush": mix(control, bg_deep, 0.45),
        "TabControlSeparatorBrush": alpha(lighten(accent, 0.2), 0x55),
        "ThumbBackgroundBrush": mix(text_dim, control, 0.45),
        "ThumbIsMouseOverBackgroundBrush": mix(text_dim, control, 0.65),
        "TreeViewBackgroundBrush": mix(control, panel, 0.45),
        "TreeViewItemMouseOverBackgroundBrush": menu_hover,
        "TreeViewItemForegroundBrush": mix(text, text_dim, 0.5),
        "TreeViewItemMouseOverForegroundBrush": menu_text,
        "TreeViewItemSelectedForegroundBrush": bright,
        "ExpanderExIsMouseOverBackgroundBrush": selected,
        "DetailsViewOverviewHeaderLabelBrush": bright,
        "DetailsViewOverviewHeaderTextBlockBrush": bright,
        "DetailsViewContainerTextBrush": mix(text, text_dim, 0.75),
        "DetailsViewLinksTextBrush": alpha(text, 0x52),
        "DetailsViewOverviewHeaderButtonsBrush": alpha(text, 0xDB),
        "DetailsViewHeaderIconsFillBrush": mix(text_dim, bg, 0.9),
        "DetailsViewItemIsSelectedBackgroundBrush": selected,
        "DetailsViewItemIsMouseOverBackgroundBrush": mix(accent, mix(control, bg, 0.5), 0.14),
        "DetailsViewItemIsMouseOverInstalledBackgroundBrush": mix(accent, control, 0.45),
        "TopPanelBackgroundBrush": panel,
        "TopPanelSearchBoxBackgroundBrush": mix(control, panel, 0.6),
        "TopPanelItemForegroundBrush": mix(text_dim, panel, 0.85),
        "TopPanelItemIsMouseOverForegroundBrush": bright,
        "NormalBrush": alpha(lighten(accent, 0.25), 0x55),
        "MenusPopupsHoverBrush": menu_hover,
        "MenusPopupMouseOverForegroundBrush": menu_text,
        "GroupCountBackgroundBrush": mix(control, bg, 0.75),
        "PositiveRatingBrush": p["positive"],
        "NegativeRatingBrush": p["negative"],
        "MixedRatingBrush": p["mixed"],
        "WarningBrush": p["negative"],
        "WindowBarButtonForegroundBrush": mix(text_dim, panel, 0.8),
        "MoreButtonInstalledBackgroundBrush": darken(play, 0.07),
        "MoreButtonNotInstalledBackgroundBrush": darken(act, 0.08),
        "LibraryDetailsViewBackgroundBrush": mix(bg, bg_deep, 0.8),
        "FilterPanelViewBackgroundBrush": lighten(control, 0.08),
        "GameInfoContainerBackgroundBrush": alpha(bg_deep, 0x33),
        "OpaqueGrayHighlightBrush": alpha(text_dim, 0x4C),
        "GridViewCoverSubtitleBrush": mix(text, text_dim, 0.5),
        "GridViewCoverSubtitleBackgroundBrush": lighten(control, 0.03),

        # gradient brushes: one color per GradientStop, in the order of Constants.xaml
        "ButtonBackgroundBrush": [lighten(act, 0.14), act, darken(act, 0.08)],
        "ButtonIsMouseOverBackgroundBrush": [lighten(act, 0.28), lighten(act, 0.16), lighten(act, 0.08)],
        "ExpanderExBackgroundBrush": [mix(control, bg, 0.3), mix(control, bg, 0.18), mix(control, bg, 0.08)],
        "TrayContextMenuBackgroundBrush1": [panel, panel, panel],
        "HoverBrush": [lighten(control, 0.12), lighten(control, 0.08), lighten(control, 0.08)],
        "MenusHoverBrush": [mix(accent, control, 0.32), mix(accent, control, 0.29), mix(accent, control, 0.26)],
        "GridItemBackgroundBrush": [readable(accent, WHITE, 2.5), readable(mix(accent, accent2, 0.5), WHITE, 2.5),
                                    readable(accent2, WHITE, 2.5)],
        "WindowBackgourndBrush1": [mix(bg, control, 0.85), mix(bg, control, 0.85)],
        "StandardWindowBackgroundBrush": [mix(control, bg, 0.5), bg],
        "StandardWindowBorderBrush": [lighten(accent, 0.1), accent2],
        "ProgressBarBrush": [accent2, mix(accent, accent2, 0.5), accent],
        "ControlsIconsGlyphBrush": [lighten(accent, 0.15), accent2],
        "MoreButtonInstalledIsMouseOverBackgroundBrush": [lighten(play, 0.26), lighten(play, 0.16), lighten(play, 0.05)],
        "MoreButtonNotInstalledIsMouseOverBackgroundBrush": [lighten(act, 0.28), lighten(act, 0.18), lighten(act, 0.1)],
        "MenuBackgroundBrush": [lighten(control, 0.14), lighten(control, 0.14), lighten(control, 0.2)],
        "DetailsSectionBackgroundBrush": [alpha(bg, 0), alpha(bg, 0), alpha(mix(bg, accent, 0.85), 0x33),
                                          alpha(text, 0x1A), alpha(bg_deep, 0x4D)],
        "BackdropGlass1": [alpha(bg, 0x1A), alpha(bg, 0xB3)],
        "BackdropGlass2": [alpha(bg, 0xB3), alpha(bg, 0x4D), alpha(bg, 0x00)],
        "LinksContainerBackgroundBrush": [alpha(mix(text_dim, accent, 0.85), 0x1A), alpha(mix(text_dim, bg, 0.5), 0x1A)],
        "SectionContainerBackgroundBrush": [alpha(mix(text, accent, 0.7), 0x4D), alpha(mix(text_dim, accent, 0.75), 0x21),
                                            alpha(mix(text_dim, bg, 0.5), 0x1A)],
        "SectionContainerMainBackgroundBrush": [alpha(mix(text_dim, control, 0.4), 0x4D), alpha(control, 0x80),
                                                alpha(bg, 0x80)],
        "SectionContainerBorderBrush": [alpha(mix(control, accent, 0.7), 0x26), alpha(text, 0x14), alpha(text, 0x26),
                                        alpha(mix(control, accent, 0.6), 0x1A)],
    }
    return colors


# ---------------------------------------------------------------------------- resource file
ELEMENT = re.compile(r'<(?P<kind>Color|SolidColorBrush|LinearGradientBrush|RadialGradientBrush) x:Key="(?P<key>[^"]+)"'
                     r'(?:[^>]*/>|.*?</(?P=kind)>)', re.S)


def constants_elements(constants_text):
    return {m.group("key"): m for m in ELEMENT.finditer(constants_text)}


def resource_xaml(key, value, element):
    """Copy of the Constants.xaml element with the colors replaced."""
    kind = element.group("kind")
    source = element.group(0)
    if kind == "Color":
        if isinstance(value, list):
            raise ValueError(f"{key} is a Color, not a gradient")
        return f'    <Color x:Key="{key}">{fmt(value)}</Color>'
    if kind == "SolidColorBrush":
        if isinstance(value, list) or "DynamicResource" in source:
            raise ValueError(f"{key}: a solid brush with a literal color is expected")
        return "    " + re.sub(r'Color="[^"]*"', f'Color="{fmt(value)}"', source, count=1)
    stops = re.findall(r'<GradientStop Color="[^"]*"', source)
    if not isinstance(value, list) or len(value) != len(stops):
        raise ValueError(f"{key}: {len(stops)} gradient stops in Constants.xaml, "
                         f"{len(value) if isinstance(value, list) else 1} colors given")
    if "DynamicResource" in source:
        raise ValueError(f"{key}: gradient reads Color keys, change those instead")
    colors = iter(value)
    return "    " + re.sub(r'<GradientStop Color="[^"]*"', lambda m: f'<GradientStop Color="{fmt(next(colors))}"', source)


def profile_file(profile, constants_text, generated_note):
    elements = constants_elements(constants_text)
    values = derive(profile["palette"])
    lines = []
    for key, value in values.items():
        if key not in elements:
            raise ValueError(f"color profile {profile['id']}: {key} is not in Constants.xaml")
        lines.append(resource_xaml(key, value, elements[key]))
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            f"<!-- {generated_note} Color profile: {profile['en']}. -->\n"
            '<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"\n'
            '                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">\n\n'
            + "\n".join(lines) + "\n\n</ResourceDictionary>\n")


def literal_color_keys(constants_text):
    """Keys of Constants.xaml that hold literal colors (what a complete profile must cover)."""
    keys = []
    for key, m in constants_elements(constants_text).items():
        body = m.group(0)
        if "DynamicResource" in body:
            continue
        if m.group("kind") == "Color":
            colors = re.findall(r">([^<]*)</Color>", body)
        else:
            colors = re.findall(r'Color="([^"]*)"', body)
        if all(c.strip() in ("Transparent", "Red", "Green") for c in colors) or key in NEUTRAL_KEYS:
            continue  # transparent on purpose, never used (red and green debug brushes), or plain black and white
        keys.append(key)
    return keys
