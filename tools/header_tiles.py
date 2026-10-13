"""Header tiles of the Details view: twelve slots under the artwork card, each one a Theme Options list.

Every slot is a preset group ("Tile 1" to "Tile 12") whose choices set the Int32 constant
HeaderTileSlot<n> to the value of an information type. The view holds each type once, as a tile
in a Grid with twelve Auto columns; the tile looks at the twelve slot probes and moves to the
column of the slot that shows it (or stays collapsed). A type chosen in two slots shows in the
later one. Types keep the Playnite PART_ elements and the ThemeExtras controls, which must stay
unique in the template.

The types (id, value, labels, preview example) are listed in tools/options_spec.yaml under
header_tiles. The tile content comes from tools/header_tiles/<Id>.xaml when that file exists,
otherwise from SIMPLE below. build_options.py writes the view region and the preset groups.
"""
import re
from pathlib import Path

FRAGMENTS = Path(__file__).with_name("header_tiles")
SLOTS = 12
BEGIN = "<!-- BEGIN generated header tiles: edit tools/header_tiles.py, then run tools/build_options.py. -->"
END = "<!-- END generated header tiles -->"

LIST = "Converter={StaticResource ListToStringConverter}, ConverterParameter=', '"


def text_tile(label, text, hide=(), tag=None, wide=False):
    """A label over one line of text. `hide`: (binding, value) pairs that collapse the tile.

    With `tag`, the value is read into the panel Tag and the text shows the Tag, so the empty
    values of extensions ('' or '-') can hide the tile."""
    lines = ['<StackPanel VerticalAlignment="Center"' + (f'\n            Tag="{tag}">' if tag else ">")]
    triggers = list(hide)
    if tag:
        triggers = [("{Binding Tag, RelativeSource={RelativeSource Self}}", v) for v in ("", "-", "{x:Null}")] + triggers
    if triggers:
        lines += ["    <StackPanel.Style>", '        <Style TargetType="StackPanel">', "            <Style.Triggers>"]
        for binding, value in triggers:
            lines += [f'                <DataTrigger Binding="{binding}" Value="{value}">',
                      '                    <Setter Property="Visibility" Value="Collapsed" />',
                      "                </DataTrigger>"]
        lines += ["            </Style.Triggers>", "        </Style>", "    </StackPanel.Style>"]
    lines.append(f'    <Label Style="{{DynamicResource HeaderLabel}}" Content="{label}" />')
    if tag:
        text = "{Binding Tag, RelativeSource={RelativeSource AncestorType=StackPanel}}"
    trim = ' MaxWidth="320" TextTrimming="CharacterEllipsis"' if wide else ""
    if isinstance(text, list):
        lines.append('    <StackPanel Orientation="Horizontal">')
        for part in text:
            lines.append(f'        <TextBlock Style="{{DynamicResource HeaderTextBlock}}" Text="{part}" />')
        lines.append("    </StackPanel>")
    else:
        lines.append(f'    <TextBlock Style="{{DynamicResource HeaderTextBlock}}" Text="{text}"{trim} />')
    lines.append("</StackPanel>")
    return "\n".join(lines) + "\n"


def game_list(label, prop):
    return text_tile(label, f"{{Binding Game.{prop}, {LIST}}}",
                     hide=[(f"{{Binding Game.{prop}}}", "{x:Null}"), (f"{{Binding Game.{prop}.Count}}", "0")], wide=True)


def plugin(name, path, fallback="''"):
    return f"{{PluginSettings Plugin={name}, Path={path}, FallbackValue={fallback}}}"


PA_NONE = (plugin("PlayniteAchievements", "HasAchievements", "False"), "False")

SIMPLE = {
    "LastSession": text_tile("{DynamicResource LOCHNDChipLastSession}", None,
                             tag=plugin("GameActivity", "LastPlaytimeSession")),
    "RecentActivity": text_tile("{DynamicResource LOCHNDTileRecentActivity}", None,
                                tag=plugin("GameActivity", "RecentActivity")),
    "PlayCount": text_tile("{DynamicResource LOCPlayCountLabel}", "{Binding Game.PlayCount}",
                           hide=[("{Binding Game.PlayCount}", "0")]),
    "Added": text_tile("{DynamicResource LOCDateAddedLabel}",
                       "{Binding Game.Added, Converter={StaticResource NullableDateToStringConverter}}",
                       hide=[("{Binding Game.Added}", "{x:Null}")]),
    "ReleaseDate": text_tile("{DynamicResource LOCGameReleaseDateTitle}",
                             "{Binding Game.ReleaseDate, Converter={StaticResource ReleaseDateToStringConverter}}",
                             hide=[("{Binding Game.ReleaseDate}", "{x:Null}")]),
    "Source": text_tile("{DynamicResource LOCSourceLabel}", "{Binding Game.Source.Name}",
                        hide=[("{Binding Game.Source.Name}", ""), ("{Binding Game.Source.Name}", "{x:Null}")], wide=True),
    "Platforms": game_list("{DynamicResource LOCPlatformsTitle}", "Platforms"),
    "Developers": game_list("{DynamicResource LOCDevelopersLabel}", "Developers"),
    "Publishers": game_list("{DynamicResource LOCPublishersLabel}", "Publishers"),
    "Genres": game_list("{DynamicResource LOCGenresLabel}", "Genres"),
    "Series": game_list("{DynamicResource LOCSeriesLabel}", "Series"),
    "AgeRatings": game_list("{DynamicResource LOCAgeRatingsLabel}", "AgeRatings"),
    "Version": text_tile("{DynamicResource LOCVersionLabel}", "{Binding Game.Version}",
                         hide=[("{Binding Game.Version}", ""), ("{Binding Game.Version}", "{x:Null}")], wide=True),
    "UserScore": text_tile("{DynamicResource LOCUserScore}", "{Binding Game.UserScore}",
                           hide=[("{Binding Game.UserScore}", "{x:Null}")]),
    "CriticScore": text_tile("{DynamicResource LOCCriticScore}", "{Binding Game.CriticScore}",
                             hide=[("{Binding Game.CriticScore}", "{x:Null}")]),
    "CommunityScore": text_tile("{DynamicResource LOCCommunityScore}", "{Binding Game.CommunityScore}",
                                hide=[("{Binding Game.CommunityScore}", "{x:Null}")]),
    "HltbMainExtra": text_tile("{DynamicResource LOCHNDTileHltbExtra}", None,
                               tag=plugin("HowLongToBeat", "MainExtraFormat")),
    "HltbCompletionist": text_tile("{DynamicResource LOCHNDTileHltbCompletionist}", None,
                                   tag=plugin("HowLongToBeat", "CompletionistFormat")),
    "HltbAll": text_tile("HowLongToBeat",
                         [plugin("HowLongToBeat", "MainStoryFormat", "'-'"), " &#183; ",
                          plugin("HowLongToBeat", "MainExtraFormat", "'-'"), " &#183; ",
                          plugin("HowLongToBeat", "CompletionistFormat", "'-'")],
                         hide=[(plugin("HowLongToBeat", "MainStoryFormat"), ""),
                               (plugin("HowLongToBeat", "MainStoryFormat"), "-")]),
    "AchievementsPercent": text_tile("{DynamicResource LOCHNDChipAchievements}",
                                     [plugin("PlayniteAchievements", "ProgressPercentage", "'-'"), " %"],
                                     hide=[PA_NONE]),
    "LatestAchievement": text_tile("{DynamicResource LOCHNDChipLatestAchievement}",
                                   plugin("PlayniteAchievements", "LatestAchievementData.DisplayName"),
                                   hide=[(plugin("PlayniteAchievements", "HasLatestAchievementData", "False"), "False")],
                                   wide=True),
    "RareAchievements": text_tile("{DynamicResource LOCHNDTileRare}",
                                  [plugin("PlayniteAchievements", "Rare.Unlocked", "'-'"), "/",
                                   plugin("PlayniteAchievements", "Rare.Total", "'-'"), " &#183; ",
                                   plugin("PlayniteAchievements", "UltraRare.Unlocked", "'-'"), "/",
                                   plugin("PlayniteAchievements", "UltraRare.Total", "'-'")],
                                  hide=[PA_NONE]),
}


def tile_content(tile_id):
    """The tile content and the name of its root element (added when the root has none)."""
    path = FRAGMENTS / f"{tile_id}.xaml"
    if path.is_file():
        text = path.read_text(encoding="utf-8")
    elif tile_id in SIMPLE:
        text = SIMPLE[tile_id]
    else:
        raise ValueError(f"header tile {tile_id}: no tools/header_tiles/{tile_id}.xaml and no SIMPLE entry")
    head_end = text.index(">")
    head = text[:head_end]
    found = re.search(r'\b(?:x:)?Name="([^"]+)"', head)
    if found:
        return text, found.group(1)
    name = f"HeaderTileBody{tile_id}"
    root = re.match(r"<[\w.:]+", text).end()
    return text[:root] + f' x:Name="{name}"' + text[root:], name


def indent(text, pad):
    return "".join((pad + line if line.strip() else line) for line in text.splitlines(True))


def tile_xaml(entry):
    tile_id, value = entry["id"], entry["value"]
    content, body = tile_content(tile_id)
    lines = [f"<!-- {entry['en']} -->", f'<Border x:Name="HeaderTile{tile_id}">', "    <Border.Style>",
             '        <Style TargetType="Border">',
             '            <Setter Property="Background" Value="{DynamicResource HeaderTileBackground}" />',
             '            <Setter Property="CornerRadius" Value="{DynamicResource HeaderTileCornerRadius}" />',
             '            <Setter Property="Padding" Value="{DynamicResource HeaderTilePadding}" />',
             '            <Setter Property="Margin" Value="{DynamicResource HeaderTileMargin}" />',
             '            <Setter Property="Visibility" Value="Collapsed" />',
             "            <Style.Triggers>"]
    for slot in range(1, SLOTS + 1):
        lines += [f'                <DataTrigger Binding="{{Binding Tag, ElementName=HeaderTileSlotProbe{slot}}}" Value="{value}">',
                  f'                    <Setter Property="Grid.Column" Value="{slot - 1}" />',
                  '                    <Setter Property="Visibility" Value="Visible" />',
                  "                </DataTrigger>"]
    # last, so an empty tile (no data for this game) stays hidden whatever its slot. The content is
    # found by name: Border.Child is not a dependency property and is still empty when the style applies.
    lines += [f'                <DataTrigger Binding="{{Binding Visibility, ElementName={body}}}" Value="Collapsed">',
              '                    <Setter Property="Visibility" Value="Collapsed" />',
              "                </DataTrigger>",
              "            </Style.Triggers>", "        </Style>", "    </Border.Style>"]
    return "\n".join(lines) + "\n" + indent(content, "    ") + "</Border>\n"


def region_xaml(section):
    types = [t for t in section["types"] if t["value"] != 0]
    lines = ['<Grid x:Name="HeaderTilesGrid" DockPanel.Dock="Left">',
             "    <Grid.Resources>",
             "        <!-- Tile text: a small label over a larger, brighter value (overrides the header bar styles inside the tiles) -->",
             '        <Style TargetType="Label" x:Key="HeaderLabel">',
             '            <Setter Property="FontSize" Value="{DynamicResource FontSizeSmall}" />',
             '            <Setter Property="FontFamily" Value="{DynamicResource FontFamily}" />',
             '            <Setter Property="Foreground" Value="{DynamicResource TextBrushDarker}" />',
             '            <Setter Property="Padding" Value="0" />',
             '            <Setter Property="Margin" Value="0,0,0,3" />',
             "        </Style>",
             '        <Style TargetType="TextBlock" x:Key="HeaderTextBlock">',
             '            <Setter Property="FontSize" Value="{DynamicResource HeaderTileValueFontSize}" />',
             '            <Setter Property="FontWeight" Value="SemiBold" />',
             '            <Setter Property="Foreground" Value="{DynamicResource TextBrush}" />',
             "        </Style>",
             "    </Grid.Resources>",
             "    <Grid.ColumnDefinitions>"]
    lines += ['        <ColumnDefinition Width="Auto" />'] * SLOTS
    lines += ["    </Grid.ColumnDefinitions>",
              '    <!-- Slot probes: Tag is the information type of each slot (Theme Options lists "Tile 1" to "Tile 12") -->']
    lines += [f'    <FrameworkElement x:Name="HeaderTileSlotProbe{slot}" Visibility="Collapsed" Tag="{{DynamicResource HeaderTileSlot{slot}}}" />'
              for slot in range(1, SLOTS + 1)]
    body = "\n".join(lines) + "\n"
    for entry in types:
        body += indent(tile_xaml(entry), "    ")
    return body + "</Grid>\n"


def view_with_region(text, section):
    """The Details view with the generated tiles between the markers (marker indentation kept)."""
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError("Views/DetailsViewGameOverview.xaml must contain the generated header tiles markers once")
    head, rest = text.split(BEGIN)
    _, tail = rest.split(END)
    pad = head[head.rindex("\n") + 1:]
    return head + BEGIN + "\n" + indent(region_xaml(section), pad) + pad + END + tail


def check_types(section, constants):
    values = [t["value"] for t in section["types"]]
    ids = [t["id"] for t in section["types"]]
    if len(set(values)) != len(values) or len(set(ids)) != len(ids):
        raise ValueError("header_tiles: type ids and values must be unique")
    if len(section["slots"]) != SLOTS:
        raise ValueError(f"header_tiles: {SLOTS} slots expected")
    by_id = {t["id"]: t for t in section["types"]}
    for n, tile_id in enumerate(section["slots"], 1):
        key = f"HeaderTileSlot{n}"
        kind, default = constants.get(key, (None, None))
        if kind != "Int32":
            raise ValueError(f"header_tiles: {key} must be a sys:Int32 in Constants.xaml")
        if int(default) != by_id[tile_id]["value"]:
            raise ValueError(f"header_tiles: {key} is {default} in Constants.xaml, slot {n} default is {tile_id}")


def slot_groups(section):
    """Preset groups "Tile 1" to "Tile 12"; every choice of every slot shares its label and preview."""
    by_id = {t["id"]: t for t in section["types"]}
    groups = []
    for n, default_id in enumerate(section["slots"], 1):
        default = by_id[default_id]
        options = [{"id": "Default",
                    "en": section["default"]["en"].format(type=default["en"]),
                    "fr": section["default"]["fr"].format(type=default["fr"]),
                    "preview": f"Presets/Previews/Tile_{default_id}.png"}]
        for entry in section["types"]:
            options.append({"id": entry["id"], "en": entry["en"], "fr": entry["fr"],
                            "lockey": f"LOCHNDTileType{entry['id']}",
                            "preview": f"Presets/Previews/Tile_{entry['id']}.png",
                            "constants": {f"HeaderTileSlot{n}": entry["value"]}})
        groups.append({"group": f"TileSlot{n}", "en": section["group"]["en"].format(n=n),
                       "fr": section["group"]["fr"].format(n=n), "options": options})
    return groups


def add_slot_groups(spec):
    section = spec.get("header_tiles")
    if not section:
        return
    names = [g["group"] for g in spec["presets"]]
    where = names.index(section["insert_after"]) + 1 if section.get("insert_after") in names else len(names)
    spec["presets"][where:where] = slot_groups(section)
