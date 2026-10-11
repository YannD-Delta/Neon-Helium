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

- **Achievements:** [PlayniteAchievements](https://github.com/justin-delano/PlayniteAchievements): progress, statistics, charts, icon lists, latest unlock, rare and ultra rare counts and the full achievements grid, plus chips in the artwork header.
- **Play time and completion:** [HowLongToBeat](https://github.com/Lacro59/playnite-howlongtobeat-plugin) (section and header chips), [GameActivity](https://github.com/Lacro59/playnite-gameactivity-plugin) (charts, last session and recent activity chips), PlayState.
- **Media:** Extra Metadata Loader (logos and trailers), Background Changer, Screenshots Visualizer, Steam Screenshots, [Screenshot Utilities](https://knarzwerk.de/en/playnite-extensions/screenshot-utilities/) (new section).
- **Library and game information:** CheckDLC, CheckLocalizations, SystemChecker, LibraryManagement, Game Relations, Review Viewer, News Viewer, VNDB Nexus, GOG Second Class Watcher, Web Explorer, Play Notes, Steam Game Status Detector.
- **Buttons next to Play:** Steam Shortcuts (Steam client, store and community menu), [Game Update Status](https://github.com/FunkyKwak/playnite-get-update-status) (update available dot).
- **Interface:** ThemeExtras (favorite toggle, link icons, star rating, banners), DuplicateHider.

## Settings

The theme is fully usable with its defaults. Two optional extensions unlock the settings:

- **[Theme Options](https://codeberg.org/ashpynov/ThemeOptions)** (recommended): about 190 settings and 12 drop-down lists, with French labels when Playnite is in French. Open it from Playnite's add-on settings. Most changes apply when you close the settings window; the accent color needs a restart.
- **[ThemeModifier](https://github.com/Lacro59/playnite-thememodifier-plugin)**: free color pickers for about 75 theme colors.

Drop-down lists (Theme Options):

| List | Choices |
|---|---|
| Global style | Helium-Neon-Dune, Neon classic, Dune, Minimal |
| Play button style | Dune, Neon, Pill, Glass |
| Play, edit and favorite buttons | in the artwork (Dune) or in the header bar (Neon) |
| Information chips | pills, plain text (Dune), outline, hidden |
| Accent color | Neon blue, Dune amber, violet, emerald, crimson, pink, cyan, gold, Hybrid red |
| Animations | smooth, fast, off |
| Shade over the artwork | none, light, medium, strong |
| Artwork sharpness and position | sharp or blurred, vertical and horizontal alignment |
| Header bar | frosted glass, solid, transparent, hidden |
| Blurred background behind the information | off, light, normal, strong |

The global style sets a starting point; every list below it, and every individual setting, overrides it.

**Quick settings.** Every section of the Details view has a gear next to its fold arrow. It lists where that information shows (the section itself, chips on the artwork, the cover, the header bar), what the section contains and whether it opens by default; changes apply at once and are saved by Theme Options. Two buttons open the extension's own settings and all theme settings (both need ThemeExtras). The top panel also has buttons for the Theme Options and ThemeModifier settings.

**No repeated information.** When a section's information is already shown above (genres as chips, HowLongToBeat on the cover...), the section folds at the bottom of its column instead of disappearing, so its gear stays reachable. Turn this off with "Fold sections at the bottom when their information is shown above".

Individual settings cover: each information chip in the artwork (release date, platforms, source, genres, developers, completion status, community score, HowLongToBeat times, achievements, latest and rare achievements, last session and recent activity), sizes and corner rounding of the buttons and chips, each header bar item, every extension section in the Details and Grid views (shown, open by default, order), the achievements controls, covers, links and text sizes.

Section order: each section needs its own number (0 to 18); two sections with the same number overlap. In the Details view the order applies within each column.

If you used ThemeModifier with an earlier version, only its color settings still apply; reset the others in ThemeModifier if something looks wrong.

## Development

`tools/options_spec.yaml` is the single source of the settings. `tools/build_options.py` generates `options.yaml` (Theme Options), `Localization/fr_FR.xaml`, `thememodifier.yaml` (colors), the preset files in `Presets/` and the default hero styles in `DerivedStyles/PlayButton.xaml`. Types and defaults are read from `Constants.xaml`.

```
python tools/build_options.py
```

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

Released under the MIT license. Helium-Neon-Dune builds on the work of [Xenor](https://github.com/XenorPLxx/Neon) (Neon), [darklinkpower](https://github.com/darklinkpower/Helium) (Helium) and [hugsyf and sakasakiking](https://github.com/hugsyf/dune-rev) (Dune Rev); see `THIRD_PARTY_NOTICES.md`.
