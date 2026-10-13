"""Gear menus of the Details view sections.

Every section header has a gear (ToggleButton) that opens a popup with the settings of that section:
check boxes and sliders bound TwoWay to Theme Options Options[...], so a change applies at once and
Theme Options saves it. Settings that the views only read through DynamicResource (section order...)
are marked ↻: they apply after a Playnite restart. Buttons open the extension settings and Theme Options.

The menus are listed in tools/options_spec.yaml under section_menus; labels are the Theme Options
labels of the settings (LOCHNDOpt<key>). build_options.py writes each menu between its markers.
"""
import re

THEME_OPTIONS = "904cbf3b-573f-48f8-9642-0a09d05c64ef"
BEGIN = "<!-- BEGIN gear menu {id}: edit tools/options_spec.yaml (section_menus), then run tools/build_options.py. -->"
END = "<!-- END gear menu {id} -->"
MARKER = re.compile(r"<!-- BEGIN gear menu (\w+): .*?-->\n(.*?)<!-- END gear menu \1 -->", re.S)


def opt(key):
    return (f"{{PluginSettings Plugin=ThemeOptions, Path=Options[{key}], Mode=TwoWay, "
            f"FallbackValue={{StaticResource {key}}}, TargetNullValue={{StaticResource {key}}}}}")


def label(key, restart):
    runs = f'<Run Text="{{DynamicResource LOCHNDOpt{key}}}" />'
    if restart:
        runs += '<Run Text=" ↻" Foreground="{DynamicResource GlyphBrush}" />'
    return runs


def menu_xaml(gear_id, menu, ranges, kinds, live_keys):
    title = menu["title"]
    title_text = f"{{DynamicResource {title}}}" if title.startswith("LOC") else title
    rows = []
    restart_used = False
    slider = 0
    for entry in menu["keys"]:
        if isinstance(entry, dict):
            rows.append(f'<TextBlock Style="{{DynamicResource QuickSettingsHeading}}" Text="{{DynamicResource {entry["heading"]}}}" />')
            continue
        key = entry
        kind = kinds.get(key)
        restart = key not in live_keys
        restart_used |= restart
        if kind == "Boolean":
            rows += [f'<CheckBox Margin="0,3,0,3" IsChecked="{opt(key)}">',
                     f'    <TextBlock TextWrapping="Wrap">{label(key, restart)}</TextBlock>',
                     "</CheckBox>"]
        elif kind in ("Int32", "Double"):
            if key not in ranges:
                raise ValueError(f"section_menus {gear_id}: {key} has no range in the spec")
            low, high = ranges[key]
            slider += 1
            name = f"QuickSlider{gear_id}{slider}"
            step = 1 if high - low <= 1000 else 10
            rows += ['<DockPanel Margin="0,4,0,4">',
                     f'    <TextBlock DockPanel.Dock="Right" Style="{{DynamicResource BaseTextBlockStyle}}" Width="40" TextAlignment="Right" VerticalAlignment="Center"',
                     f'               Text="{{Binding Value, ElementName={name}, StringFormat={{}}{{0:0}}}}" />',
                     f'    <TextBlock DockPanel.Dock="Left" Style="{{DynamicResource BaseTextBlockStyle}}" Width="190" TextWrapping="Wrap" VerticalAlignment="Center">{label(key, restart)}</TextBlock>',
                     f'    <Slider x:Name="{name}" Minimum="{low}" Maximum="{high}" SmallChange="{step}" LargeChange="{step}" TickFrequency="{step}" IsSnapToTickEnabled="True"',
                     f'            VerticalAlignment="Center" Value="{opt(key)}" />',
                     "</DockPanel>"]
        else:
            raise ValueError(f"section_menus {gear_id}: {key} is not a Boolean, Int32 or Double setting")
    if restart_used:
        rows.append('<TextBlock Style="{DynamicResource QuickSettingsHeading}" Text="{DynamicResource LOCHNDQuickRestart}" Typography.Capitals="Normal" />')
    buttons = []
    if menu.get("plugin"):
        buttons += ['<Button Margin="0,4,8,0" Padding="10,5,10,5" Content="{DynamicResource LOCHNDQuickPluginSettings}"',
                    '        Visibility="{PluginStatus Plugin=felixkmh_Extras_Plugin, Status=Installed}"',
                    '        Command="{PluginSettings Plugin=ThemeExtras, Path=Commands.OpenPluginSettingsCommand, FallbackValue={x:Null}}"',
                    f'        CommandParameter="{menu["plugin"]}" />']
    buttons += ['<Button Margin="0,4,8,0" Padding="10,5,10,5" Content="{DynamicResource LOCHNDQuickThemeSettings}"',
                '        Visibility="{PluginStatus Plugin=felixkmh_Extras_Plugin, Status=Installed}"',
                '        Command="{PluginSettings Plugin=ThemeExtras, Path=Commands.OpenPluginSettingsCommand, FallbackValue={x:Null}}"',
                f'        CommandParameter="{THEME_OPTIONS}" />']
    toggle = f"QuickSettings{gear_id}"
    lines = [f'<ToggleButton x:Name="{toggle}" Style="{{DynamicResource SectionQuickSettingsToggle}}" VerticalAlignment="Center" />',
             f'<Popup IsOpen="{{Binding IsChecked, ElementName={toggle}, Mode=TwoWay}}" StaysOpen="False" AllowsTransparency="True"',
             f'       PlacementTarget="{{Binding ElementName={toggle}}}" Placement="Left">',
             '    <Border Style="{DynamicResource QuickSettingsPanel}">',
             '        <ScrollViewer VerticalScrollBarVisibility="Auto" MaxHeight="620">',
             "            <StackPanel>",
             f'                <TextBlock Style="{{DynamicResource QuickSettingsTitle}}" Text="{title_text}" />',
             '                <TextBlock Style="{DynamicResource QuickSettingsHint}" Text="{DynamicResource LOCHNDQuickNeedsThemeOptions}"',
             f'                           Visibility="{{PluginStatus Plugin=ThemeOptions_{THEME_OPTIONS}, Status=Installed, Converter={{StaticResource InvertedBooleanToVisibilityConverter}}}}" />',
             f'                <StackPanel IsEnabled="{{PluginStatus Plugin=ThemeOptions_{THEME_OPTIONS}, Status=Installed}}">']
    lines += ["                    " + row for row in rows]
    lines += ["                </StackPanel>", '                <WrapPanel Margin="0,12,0,0">']
    lines += ["                    " + row for row in buttons]
    lines += ["                </WrapPanel>", "            </StackPanel>", "        </ScrollViewer>", "    </Border>", "</Popup>"]
    return "\n".join(lines) + "\n"


def view_with_menus(text, spec, kinds, other_sources):
    """The Details view with every gear menu regenerated between its markers (marker indentation kept)."""
    menus = spec.get("section_menus") or {}
    ranges = {e["key"]: e["range"] for e in spec["variables"] if "key" in e and "range" in e}
    known = {e["key"] for e in spec["variables"] if "key" in e}
    for gear_id, menu in menus.items():
        for entry in menu["keys"]:
            if not isinstance(entry, dict) and entry not in known:
                raise ValueError(f"section_menus {gear_id}: {entry} is not a Theme Options variable")
    # a setting is live when some view reads Options[key] outside the menus themselves
    stripped = MARKER.sub("", text) + other_sources
    live = set(re.findall(r"Options\[(\w+)\]", stripped))
    found = set()

    def replace(match):
        gear_id = match.group(1)
        base = gear_id[:-5] if gear_id.endswith("Right") and gear_id[:-5] in menus else gear_id
        if base not in menus:
            raise ValueError(f"gear menu {gear_id}: no section_menus entry {base}")
        found.add(base)
        start = match.start()
        pad = text[text.rindex("\n", 0, start) + 1:start]
        body = menu_xaml(gear_id, menus[base], ranges, kinds, live)
        body = "".join((pad + line if line.strip() else line) for line in body.splitlines(True))
        return BEGIN.format(id=gear_id) + "\n" + body + pad + END.format(id=gear_id)

    result = MARKER.sub(replace, text)
    unused = sorted(set(menus) - found)
    if unused:
        raise ValueError("section_menus without a gear in the view: " + ", ".join(unused))
    return result
