![DownloadCountTotal](https://img.shields.io/github/downloads/YannD-Delta/Neon-Helium/total?label=total%20downloads&style=for-the-badge)
![LatestVersion](https://img.shields.io/github/v/tag/YannD-Delta/Neon-Helium?label=Latest%20version&style=for-the-badge)
![DownloadCountLatest](https://img.shields.io/github/downloads/YannD-Delta/Neon-Helium/latest/total?style=for-the-badge)
![License](https://img.shields.io/github/license/YannD-Delta/Neon-Helium?style=for-the-badge)

# Helium-Neon-Dune

Helium-Neon-Dune is a [Playnite](https://github.com/JosefNemec/Playnite) Desktop Mode theme that merges three themes: the game information layout of [Neon](https://github.com/XenorPLxx/Neon) by Xenor and [Helium](https://github.com/darklinkpower/Helium) by darklinkpower, and the artwork header and buttons of [Dune Rev](https://github.com/hugsyf/dune-rev) by hugsyf. Almost every part can be switched between the Neon and the Dune look from the theme settings. It has its own theme Id, so it can be installed next to Neon.

## Installation

Download the latest `.pthm` file from the [Releases page](https://github.com/YannD-Delta/Neon-Helium/releases/latest), then open it or drag it onto the Playnite Desktop window to install it.

## Optional integrations

Helium-Neon-Dune works without extensions. It includes integration hosts for these optional extensions (each one has its own setting):

- **Achievements:** [PlayniteAchievements](https://github.com/justin-delano/PlayniteAchievements): progress, statistics, charts, icon lists, latest unlock, rare and ultra rare counts and the full achievements grid, plus chips in the artwork header, a collection level badge in the top panel and an unlock notification in the theme colors (used when "Use my theme's design when available" is on in its Notifications settings).
- **Play time and completion:** [HowLongToBeat](https://github.com/Lacro59/playnite-howlongtobeat-plugin) (section and header chips), [GameActivity](https://github.com/Lacro59/playnite-gameactivity-plugin) (charts, last session, recent activity and average FPS chips), PlayState.
- **Media:** Extra Metadata Loader (logos and trailers), Background Changer, Screenshots Visualizer, Steam Screenshots, [Screenshot Utilities](https://knarzwerk.de/en/playnite-extensions/screenshot-utilities/) (section and viewer button).
- **Library and game information:** [Metadata Utilities](https://knarzwerk.de/en/playnite-extensions/metadata-utilities/) (genres, categories, features and tags grouped by prefix, optional), CheckDLC, CheckLocalizations, SystemChecker, LibraryManagement, Game Relations, Review Viewer, News Viewer, VNDB Nexus, GOG Second Class Watcher, Web Explorer, Play Notes, Steam Game Status Detector.
- **Per-game badges:** HowLongToBeat and PlayniteAchievements times and counts at the end of each game in the list and on Grid view covers (HowLongToBeat needs its "view item" integration turned on).
- **Buttons next to Play:** Steam Shortcuts (Steam client, store and community menu), [Game Update Status](https://github.com/FunkyKwak/playnite-get-update-status) (update available dot).
- **Interface:** ThemeExtras (favorite and hide toggles, link icons, star rating, banners), DuplicateHider.

## Settings

The theme is fully usable with its defaults. Two optional extensions unlock the settings:

- **[Theme Options](https://codeberg.org/ashpynov/ThemeOptions)** (recommended): about 260 settings and 31 drop-down lists with a preview image for each choice, and French labels when Playnite is in French. Open it from Playnite's add-on settings, from the gear button of the top panel or from the gear of any section (both need ThemeExtras). Most changes apply when you close the settings window; the color profile and the accent color need a restart.
- **[ThemeModifier](https://github.com/Lacro59/playnite-thememodifier-plugin)**: free color pickers for 80 theme colors. Colors saved in ThemeModifier win over the color profile: reset them in ThemeModifier to see a profile as designed.

Drop-down lists (Theme Options):

| List | Choices |
|---|---|
| Global style | Liquid Glass, Dune, Neon (full width, buttons in a bar), Minimal |
| Corner rounding | rounded, square, subtle, very round (card, panels, tiles, chips, buttons and cover together) |
| Page background | liquid glass, clear glass, smoked glass, tinted glass, ambient reflection, solid |
| Glass of the panels, tiles and chips | glass, frosted, clear, without outlines |
| Artwork card size | spaced, wide spacing, close to the edges, full width |
| Blur at the bottom of the artwork | medium, none, light, strong, very strong |
| Height of the blurred band | bottom half, bottom quarter, two thirds, whole artwork |
| Color over the blurred band | light accent, none, strong accent, white frost, accent and frost |
| Dark shade at the bottom of the artwork | light, none, medium, strong |
| Cover in the artwork card | over the card edge and the tiles, inside the card (with or without the information panel cover), information panel only |
| Play button style | Dune, Neon, Pill, Glass |
| Play, edit and favorite buttons | at the right of the information, under the chips, or in the header bar |
| Information chips | pills, plain text, outline, hidden |
| Tiles under the card (look) | glass tiles, large, compact, text only, frosted bar, solid bar, hidden |
| Tile 1 to Tile 12 | the information shown in each tile under the card, from 30 choices (see below) |
| Color profile | theme colors, Liquid, Midnight, Graphite, OLED black, Dune sand, Ember, Forest, Aurora, Rose, Violet, Nord, Catppuccin Mocha, Tokyo Night |
| Accent color | color of the profile, Dune amber, violet, emerald, crimson, pink, cyan, gold, Hybrid red |
| Animations | smooth, fast, off |
| Artwork sharpness and position | sharp or blurred, vertical and horizontal alignment |
| Top panel | Neon, Dune (view buttons centered, transparent) |

Every choice of every list shows a preview while the mouse is over it.

The global style sets a starting point; every list below it, and every individual setting, overrides it.

**Color profiles.** Each profile recolors the whole theme: window and panel backgrounds, text, accent, buttons, game list, menus, popups, inputs, ratings and section cards (109 colors, derived from 13 base colors per profile, with white text kept readable on buttons; backgrounds use steps of one hue and accents sit next to each other on the color wheel). All profiles are dark, because the theme draws white text over the artwork. The Accent list can still replace the accent of any profile.

**Liquid glass.** The artwork of the selected game, blurred and dimmed, stays behind the whole page while it scrolls. The information panel, the links, the sections, the tiles and the chips are glass panels in the colors of the profile, with one corner rounding for everything (Corner rounding list) and the same side margins as the artwork card.

**Help in Theme Options.** Settings with an explanation have a "?" row under them: the mouse over it shows the full text and, for some, a schema.

**Sections in the right column.** Genres, categories, features and tags can each move to the narrow right column (Theme Options, "Details view - sections moved to the right column"), with their own order there. In the right column they show the Playnite list, without the Metadata Utilities grouping.

**Artwork card.** The top of the Details view is a rounded card: the artwork gets sharper towards the top and blurs progressively towards the bottom, under a light accent tint instead of a dark shade, and the bottom band holds the logo or name, the information line, the chips and the buttons. The cover sits in the bottom-left corner, over the edge of the card and the row of tiles below it. Shape, blur strength, blur height, tint, cover place and tile look each have a list with previews; cover size and rounding have their own settings.

**Tiles.** The row under the card has twelve slots, "Tile 1" to "Tile 12" in Theme Options, from left to right. Each slot is a list of every information the theme can show there, with a preview of the tile: time played, last played, completion status (editable with ThemeExtras), play count, date added, release date, source, platforms, developers, publishers, genres, series, age rating, version, your score, critic score, community score, both scores, install size, achievements (count and bar, percentage, latest, rare and ultra rare), HowLongToBeat (main story, main + extra, 100%, all three), GameActivity (average FPS, last session, recent activity), or empty. A tile without a value for the selected game hides itself and the next tiles move left; an information chosen in two slots shows in the later one. The Neon global style and the full-width card size bring back the full-width artwork.

**Theme settings.** The gear button of the top panel and the gear of each section open Theme Options (needs ThemeExtras).

**No repeated information.** When a section's information is already shown above (genres as chips, HowLongToBeat on the cover...), the section folds at the bottom of its column instead of disappearing, so its gear stays reachable. Each foldable section has its own setting in Theme Options (PlayniteAchievements and GameActivity stay in place by default, their sections show much more than the chips), and "Fold sections at the bottom when their information is shown above" turns folding off everywhere.

**Tabs.** Optionally, the Details view sections go into tabs: All, About, Media, Stats and Community. Each section gear sets the tab of that section (0 shows it in every tab).

**Auto-hide.** The top panel and a left or right sidebar can shrink to a thin strip and come back when the mouse is over them (off by default).

**Chips.** A click on a chip opens or folds the matching section (HowLongToBeat, achievements, activity, genres, categories, features, tags). The chips on the artwork are grouped: game (release date, platforms, source), classification (genres, categories, features, tags), studio and status (developers, completion status, score), HowLongToBeat, achievements and activity. A line break can be added before any chip, and the groups can be reordered, in Theme Options (Details view - information chips).

Individual settings cover: each information chip in the artwork (release date, platforms, source, genres, developers, completion status, community score, HowLongToBeat times, achievements, latest and rare achievements, last session, recent activity and average FPS), sizes and corner rounding of the buttons, chips and header cover, each header bar item, every extension section in the Details and Grid views (shown, open by default, order), the achievements controls, covers, links and text sizes.

Section order: each section needs its own number (0 to 18); two sections with the same number overlap. In the Details view the order applies within each column.

If you used ThemeModifier with an earlier version, only its color settings still apply; reset the others in ThemeModifier if something looks wrong.

## Development

`tools/options_spec.yaml` is the single source of the settings. `tools/build_options.py` generates `options.yaml` (Theme Options), `Localization/fr_FR.xaml`, `thememodifier.yaml` (colors), the preset files in `Presets/` and the default hero styles in `DerivedStyles/PlayButton.xaml`. Types and defaults are read from `Constants.xaml`.

```
python tools/build_options.py
```

`tools/color_profiles.py` turns the 13 base colors of each profile (`color_profiles` in the spec) into every color of `Constants.xaml`; the build writes `Presets/Colors/<Id>.xaml` and stops if a profile misses a color.

`tools/make_previews.py` draws the preview images shown next to the drop-down choices, color profiles included (needs Pillow and PyYAML).

`tools/lint_theme.py` checks the sources before packaging: well-formed XAML, no `x:Shared` (Playnite rejects it in loose XAML), valid ThemeModifier and Theme Options entries, no option that is never read, preset files that only override existing keys, French labels, and generated files that are up to date. It needs PyYAML.

```
python tools/lint_theme.py --source source
```

`tools/package_pthm.py` builds the installable package from `source/`, without the files that only exist for Visual Studio (`App.xaml`, `GlobalResources.xaml`, `LocSource.xaml`, `ControlGalleryView.xaml`, the project files and `Fonts`). It runs the linter first.

```
python tools/package_pthm.py
```

The package is written to `dist/<Id>_<version>.pthm`.

## Relevant settings

Keep in mind that a similar effect can be achieved by using original [Helium](https://playnite.link/addons.html#8b15c46a-90c2-4fe5-9ebb-1ab25ba7fcb1) with the [Details to Grid View Converter](https://playnite.link/addons.html#ThemesDetailsViewToGridViewConverter_ef8a7226-eedc-478d-a506-92ee6c088aa3) add-on, which is a recommended way for most users.

Settings used to take the preview screenshots:

![settings-1](https://github.com/YannD-Delta/Neon-Helium/raw/master/screenshots/settings-1.png)

![settings-2](https://github.com/YannD-Delta/Neon-Helium/raw/master/screenshots/settings-2.png)

![settings-3](https://github.com/YannD-Delta/Neon-Helium/raw/master/screenshots/settings-3.png)

![settings-4](https://github.com/YannD-Delta/Neon-Helium/raw/master/screenshots/settings-4.png)

## Screenshots

![Screenshot](https://github.com/YannD-Delta/Neon-Helium/raw/master/screenshots/screenshot_01.jpg)

## Credits and license

Released under the MIT license. Helium-Neon-Dune builds on the work of [Xenor](https://github.com/XenorPLxx/Neon) (Neon), [darklinkpower](https://github.com/darklinkpower/Helium) (Helium) and [hugsyf and sakasakiking](https://github.com/hugsyf/dune-rev) (Dune Rev); see `THIRD_PARTY_NOTICES.md`. Several color profiles reuse the published palettes of Nord, Dracula, Catppuccin, Tokyo Night, Gruvbox, Rosé Pine, Everforest, Solarized and One Dark, credited to their authors.
