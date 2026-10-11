![DownloadCountTotal](https://img.shields.io/github/downloads/YannD-Delta/Neon-Helium/total?label=total%20downloads&style=for-the-badge)
![LatestVersion](https://img.shields.io/github/v/tag/YannD-Delta/Neon-Helium?label=Latest%20version&style=for-the-badge)
![DownloadCountLatest](https://img.shields.io/github/downloads/YannD-Delta/Neon-Helium/latest/total?style=for-the-badge)
![License](https://img.shields.io/github/license/YannD-Delta/Neon-Helium?style=for-the-badge)

# Helium-Neon

Helium-Neon is a [Playnite](https://github.com/JosefNemec/Playnite) Desktop Mode theme. It is a fork of [Neon](https://github.com/XenorPLxx/Neon) by Xenor, itself based on [Helium](https://github.com/darklinkpower/Helium) by darklinkpower, with its own theme Id so it can be installed next to Neon. Some design ideas come from [Dune Rev](https://github.com/hugsyf/dune-rev) by hugsyf.

## Installation

Download the latest `.pthm` file from the [Releases page](https://github.com/YannD-Delta/Neon-Helium/releases/latest), then open it or drag it onto the Playnite Desktop window to install it.

## Optional integrations

Helium-Neon works without extensions. It includes integration hosts for the following optional extensions:

- **Achievements and duplicate management:** [PlayniteAchievements](https://github.com/justin-delano/PlayniteAchievements) native achievement progress, statistics, charts, icon lists, latest unlock and the full achievements grid; and [DuplicateHider](https://github.com/felixkmh/DuplicateHider) source selectors on grid covers and in the selected-game overview.
- **Game data and media:** [HowLongToBeat](https://github.com/Lacro59/playnite-howlongtobeat-plugin), [GameActivity](https://github.com/Lacro59/playnite-gameactivity-plugin), Extra Metadata Loader, Background Changer, Screenshots Visualizer, Steam Screenshots, Play Notes, and Steam Game Status Detector.
- **Library and game information:** CheckDLC, CheckLocalizations, SystemChecker, LibraryManagement, Game Relations, Review Viewer, News Viewer, VNDB Nexus, GOG Second Class Watcher, and Web Explorer.
- **Interface additions:** PlayState and ThemeExtras.

## ThemeModifier options

Helium-Neon exposes its settings through the [ThemeModifier](https://playnite.link/addons.html) extension (about 200 options, grouped):

- **Colors:** accent, text, controls, play button, details and grid views, game list, top panel, menus and inputs.
- **Sections:** show or hide each extension panel and each header item, in both the Grid and the Details views.
- **Order:** reorder the extension panels. Each panel needs its own number (0 to 18); two panels with the same number overlap. In the Details view the order applies within each column.
- **Sizes:** header buttons, section headers, logo limits, play button, top panel, sidebar, link icons, panel heights and text sizes.

## Development

`tools/lint_theme.py` checks the sources before packaging: well-formed XAML, no `x:Shared` (Playnite rejects it in loose XAML), valid ThemeModifier entries and no option that is never read.

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

Released under the MIT license. Helium-Neon builds on the work of [Xenor](https://github.com/XenorPLxx/Neon) (Neon), [darklinkpower](https://github.com/darklinkpower/Helium) (Helium) and [hugsyf and sakasakiking](https://github.com/hugsyf/dune-rev) (Dune Rev); see `THIRD_PARTY_NOTICES.md`.
