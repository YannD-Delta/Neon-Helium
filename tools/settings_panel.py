"""Settings panel: one large popup with a page list on the left and setting cards on the right.

Generated from the "panel" section of tools/options_spec.yaml into two kinds of host:
  details  Views/DetailsViewGameOverview.xaml. Each section gear is a toggle bound to the
           radio button of its page, and the popup is open while any page is selected.
  top      Views/TopPanel.xaml and Presets/TopPanel/Dune.xaml. The workshop toggle opens it.
Every control is bound TwoWay to Theme Options Options[...], so the theme changes while you click.
"""
import re

THEME_OPTIONS_ADDON = "ThemeOptions_904cbf3b-573f-48f8-9642-0a09d05c64ef"
THEME_OPTIONS_GUID = "904cbf3b-573f-48f8-9642-0a09d05c64ef"
THEME_MODIFIER_GUID = "ec2f4013-17e6-428a-b8a9-5e34a3b80009"
EXTRAS = "felixkmh_Extras_Plugin"


def glyph(text):
    return "".join(f"&#x{ord(ch):X};" for ch in text)


def opt(key):
    return (f"{{PluginSettings Plugin=ThemeOptions, Path=Options[{key}], FallbackValue={{StaticResource {key}}}, "
            f"TargetNullValue={{StaticResource {key}}}}}")


def twoway(key, delay=False):
    extra = ", Delay=150" if delay else ""
    return f"{{PluginSettings Plugin=ThemeOptions, Path=Options[{key}], Mode=TwoWay{extra}, FallbackValue={{StaticResource {key}}}}}"


def indent(text, spaces):
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.split("\n"))


class Panel:
    def __init__(self, spec, constants, loc_key, prefix):
        self.spec, self.constants, self.loc_key, self.prefix = spec, constants, loc_key, prefix
        self.ranges = {e["key"]: e.get("range") for e in spec["variables"] if "key" in e}
        self.tips = spec.get("tips") or {}
        self.panel = spec["panel"]

    def name(self, *parts):
        return self.prefix + "".join(parts)

    # ------------------------------------------------------------------ controls
    def control(self, key):
        if key not in self.ranges:
            raise ValueError(f"panel item {key} is not a variable")
        kind = self.constants[key][0]
        label = "{DynamicResource %s}" % self.loc_key("Opt", key)
        tip = ' ToolTip="{DynamicResource %s}"' % self.loc_key("Tip", key) if key in self.tips else ""
        info = ('\n    <TextBlock DockPanel.Dock="Right" Style="{DynamicResource HndPanelInfo}"%s />' % tip) if tip else ""
        if kind == "Boolean":
            return (f'<DockPanel Style="{{DynamicResource HndPanelRow}}">{info}\n'
                    f'    <CheckBox Style="{{DynamicResource HndPanelSwitch}}" Content="{label}" IsChecked="{twoway(key)}" />\n'
                    f'</DockPanel>')
        if kind == "Double" and self.ranges[key]:
            low, high = self.ranges[key]
            slider = self.name("Slider", key)
            step = 1 if high - low <= 12 else 10
            ticks = ' TickPlacement="BottomRight"' if high - low <= 12 else ""
            return (f'<DockPanel Style="{{DynamicResource HndPanelRow}}">{info}\n'
                    f'    <TextBlock DockPanel.Dock="Top" Style="{{DynamicResource HndPanelLabel}}" Text="{label}" />\n'
                    f'    <TextBlock DockPanel.Dock="Right" Style="{{DynamicResource HndPanelValue}}"\n'
                    f'               Text="{{Binding Value, ElementName={slider}, StringFormat={{}}{{0:0}}}}" />\n'
                    f'    <Slider x:Name="{slider}" Minimum="{low}" Maximum="{high}" SmallChange="1" LargeChange="{step}" TickFrequency="1"\n'
                    f'            IsSnapToTickEnabled="True"{ticks} VerticalAlignment="Center" Value="{twoway(key, True)}" />\n'
                    f'</DockPanel>')
        raise ValueError(f"panel item {key}: only Booleans and Doubles with a range are supported ({kind})")

    def card(self, title_key, items, extra=""):
        body = "\n".join(self.control(k) for k in items)
        return (f'<Border Style="{{DynamicResource HndPanelCard}}">\n    <StackPanel>\n'
                f'        <TextBlock Style="{{DynamicResource HndPanelCardTitle}}" Text="{{DynamicResource {title_key}}}" />\n'
                f'{indent(body, 8)}\n{indent(extra, 8) if extra else ""}    </StackPanel>\n</Border>')

    def plugin_button(self, guid, label_key="LOCHNDQuickPluginSettings"):
        return (f'<Button Style="{{DynamicResource HndPanelButton}}" Content="{{DynamicResource {label_key}}}"\n'
                f'        Visibility="{{PluginStatus Plugin={EXTRAS}, Status=Installed}}"\n'
                f'        Command="{{PluginSettings Plugin=ThemeExtras, Path=Commands.OpenPluginSettingsCommand, FallbackValue={{x:Null}}}}"\n'
                f'        CommandParameter="{guid}" />')

    # ------------------------------------------------------------------ pages
    def chips_page(self, page):
        groups = self.panel["chip_groups"]
        chips = self.panel["chips"]
        # live preview of the shown chips and line breaks, in the default group order
        # (the six order slots of the real line would make the panel several times larger)
        pills = []
        for group in groups:
            for chip in [c for c in chips if c["group"] == group["id"]]:
                pills.append(
                    f'<Grid Style="{{DynamicResource SectionToggleGrid}}" Tag="{opt(chip["show"])}">\n'
                    f'    <Grid Height="0" Width="560" Style="{{DynamicResource SectionToggleGrid}}" Tag="{opt(chip["break"])}" />\n'
                    f'</Grid>\n'
                    f'<Border Style="{{DynamicResource HndPanelPreviewPill}}" Tag="{opt(chip["show"])}"\n'
                    f'        Visibility="{{Binding Tag, RelativeSource={{RelativeSource Self}}, Converter={{StaticResource BooleanToVisibilityConverter}}}}">\n'
                    f'    <TextBlock Text="{{DynamicResource {self.loc_key("PanelChip", chip["id"])}}}" />\n'
                    f'</Border>')
        preview = (f'<Border Style="{{DynamicResource HndPanelPreview}}">\n    <StackPanel>\n'
                   f'        <TextBlock Style="{{DynamicResource HndPanelCardTitle}}" Text="{{DynamicResource LOCHNDPanelPreview}}" />\n'
                   f'        <WrapPanel Width="560" HorizontalAlignment="Left">\n{indent(chr(10).join(pills), 12)}\n        </WrapPanel>\n'
                   f'    </StackPanel>\n</Border>')
        # table: one card per group, a row per chip with show switch and line break toggle
        cards = []
        for group in groups:
            rows = []
            for chip in [c for c in chips if c["group"] == group["id"]]:
                rows.append(
                    f'<DockPanel Style="{{DynamicResource HndPanelRow}}">\n'
                    f'    <ToggleButton DockPanel.Dock="Right" Style="{{DynamicResource HndPanelBreakToggle}}" ToolTip="{{DynamicResource LOCHNDPanelBreakTip}}"\n'
                    f'                  IsChecked="{twoway(chip["break"])}" />\n'
                    f'    <CheckBox Style="{{DynamicResource HndPanelSwitch}}" IsChecked="{twoway(chip["show"])}"\n'
                    f'              Content="{{DynamicResource {self.loc_key("PanelChipName", chip["id"])}}}" />\n'
                    f'</DockPanel>')
            order = self.control(group["order"])
            cards.append(f'<Border Style="{{DynamicResource HndPanelCard}}">\n    <StackPanel>\n'
                         f'        <TextBlock Style="{{DynamicResource HndPanelCardTitle}}" Text="{{DynamicResource {self.loc_key("PanelGroup", group["id"])}}}" />\n'
                         f'{indent(chr(10).join(rows), 8)}\n{indent(order, 8)}\n    </StackPanel>\n</Border>')
        general = [self.card(self.loc_key("PanelCard", page["id"], str(i)), g["items"]) for i, g in enumerate(page.get("groups", []))]
        return "\n".join([preview] + general + cards)

    def colors_page(self):
        text = (f'<TextBlock Style="{{DynamicResource HndPanelText}}" Text="{{DynamicResource LOCHNDPanelColorsText}}" />\n'
                f'<WrapPanel Margin="0,8,0,0">\n'
                f'{indent(self.plugin_button(THEME_OPTIONS_GUID, "LOCHNDQuickThemeSettings"), 4)}\n'
                f'{indent(self.plugin_button(THEME_MODIFIER_GUID, "LOCHNDWorkshopColors"), 4)}\n</WrapPanel>')
        return f'<Border Style="{{DynamicResource HndPanelCard}}">\n    <StackPanel>\n{indent(text, 8)}\n    </StackPanel>\n</Border>'

    def section_page(self, section):
        cards = [self.card("LOCHNDQuickShowIn", section["show_in"]),
                 self.card("LOCHNDQuickSectionGroup", section["section"])]
        if section.get("plugin"):
            cards.append(f'<WrapPanel>\n{indent(self.plugin_button(section["plugin"]), 4)}\n</WrapPanel>')
        return "\n".join(cards)

    def pages(self):
        result = []
        for page in self.panel["pages"]:
            if page.get("kind") == "chips":
                body = self.chips_page(page)
            elif page.get("kind") == "colors":
                body = "\n".join([self.colors_page()] + [self.card(self.loc_key("PanelCard", page["id"], str(i)), g["items"])
                                                          for i, g in enumerate(page.get("groups", []))])
            else:
                body = "\n".join(self.card(self.loc_key("PanelCard", page["id"], str(i)), g["items"])
                                 for i, g in enumerate(page["groups"]))
            result.append((page["id"], self.loc_key("PanelPage", page["id"]), glyph(page["glyph"]), body))
        for section in self.panel["sections"]:
            result.append(("Section" + section["id"], self.loc_key("PanelSection", section["id"]), None,
                           self.section_page(section)))
        return result

    # ------------------------------------------------------------------ frame
    def frame(self, host, close_binding, first_checked):
        pages = self.pages()
        group = self.prefix + "Pages"
        nav, content = [], []
        for index, (pid, title, icon, body) in enumerate(pages):
            radio = self.name("Page", pid)
            if pid.startswith("Section") and not pages[index - 1][0].startswith("Section"):
                nav.append('<TextBlock Style="{DynamicResource HndPanelNavHeading}" Text="{DynamicResource LOCHNDPanelSections}" />')
            checked = ' IsChecked="True"' if first_checked and index == 0 else ""
            tag = f' Tag="{icon}"' if icon else ""
            nav.append(f'<RadioButton x:Name="{radio}" GroupName="{group}" Style="{{DynamicResource HndPanelNavButton}}"{checked}{tag}\n'
                       f'             Content="{{DynamicResource {title}}}" />')
            content.append(f'<StackPanel Visibility="{{Binding IsChecked, ElementName={radio}, Converter={{StaticResource BooleanToVisibilityConverter}}}}">\n'
                           f'    <TextBlock Style="{{DynamicResource HndPanelPageTitle}}" Text="{{DynamicResource {title}}}" />\n'
                           f'{indent(body, 4)}\n</StackPanel>')
        none_radio = ""
        if host == "details":
            none_radio = (f'\n<RadioButton x:Name="{self.name("PageNone")}" GroupName="{group}" Visibility="Collapsed" IsChecked="True" />')
        return f'''<Grid Width="{opt('SettingsPanelWidth')}" Height="{opt('SettingsPanelHeight')}">
<!-- look (Theme Options list "Settings panel"): profile popup colors under an optional dark or glass overlay -->
<Border Background="{{DynamicResource PopupBackgroundBrush}}" CornerRadius="{{DynamicResource SettingsPanelCornerRadius}}"
        Opacity="{{DynamicResource SettingsPanelProfileOpacity}}" />
<Border Style="{{DynamicResource HndPanelFrame}}">
    <DockPanel>
        <DockPanel DockPanel.Dock="Top" Margin="0,0,0,12">
            <ToggleButton DockPanel.Dock="Right" Style="{{DynamicResource HndPanelClose}}" ToolTip="{{DynamicResource LOCHNDPanelClose}}"
                          IsChecked="{close_binding}" />
            <TextBlock Style="{{DynamicResource HndPanelTitle}}" Text="{{DynamicResource LOCHNDWorkshopTitle}}" />
            <TextBlock Style="{{DynamicResource HndPanelHint}}" Text="{{DynamicResource LOCHNDQuickNeedsThemeOptions}}"
                       Visibility="{{PluginStatus Plugin={THEME_OPTIONS_ADDON}, Status=Installed, Converter={{StaticResource InvertedBooleanToVisibilityConverter}}}}" />
        </DockPanel>
        <ScrollViewer DockPanel.Dock="Left" Width="230" VerticalScrollBarVisibility="Auto" Margin="0,0,14,0">
            <StackPanel>
{indent(chr(10).join(nav), 16)}{indent(none_radio, 16)}
            </StackPanel>
        </ScrollViewer>
        <ScrollViewer VerticalScrollBarVisibility="Auto">
            <Grid Margin="0,0,10,0" IsEnabled="{{PluginStatus Plugin={THEME_OPTIONS_ADDON}, Status=Installed}}">
{indent(chr(10).join(content), 16)}
            </Grid>
        </ScrollViewer>
    </DockPanel>
</Border>
</Grid>''', [p[0] for p in pages]

    def details_host(self):
        frame, ids = self.frame("details", f"{{Binding IsChecked, ElementName={self.name('PageNone')}, Mode=TwoWay}}", False)
        triggers = "\n".join(
            f'<DataTrigger Binding="{{Binding IsChecked, ElementName={self.name("Page", pid)}}}" Value="True">\n'
            f'    <Setter Property="IsOpen" Value="True" />\n</DataTrigger>' for pid in ids)
        return f'''<!-- Settings panel: open while one of its pages is selected (the section gears select theirs) -->
<Popup x:Name="{self.name("Popup")}" StaysOpen="True" AllowsTransparency="True" Placement="Center"
       PlacementTarget="{{Binding ElementName=PART_ScrollViewHost}}">
    <Popup.Style>
        <Style TargetType="Popup">
            <Setter Property="IsOpen" Value="False" />
            <Style.Triggers>
{indent(triggers, 16)}
            </Style.Triggers>
        </Style>
    </Popup.Style>
{indent(frame, 4)}
</Popup>'''

    def top_host(self, toggle):
        frame, _ = self.frame("top", f"{{Binding IsChecked, ElementName={toggle}, Mode=TwoWay}}", True)
        return frame


def panel_labels(spec, loc_key):
    labels = {"en": {}, "fr": {}}
    panel = spec["panel"]

    def add(key, entry):
        labels["en"][key] = entry["en"]
        labels["fr"][key] = entry["fr"]
    for page in panel["pages"]:
        add(loc_key("PanelPage", page["id"]), page)
        for i, group in enumerate(page.get("groups", [])):
            add(loc_key("PanelCard", page["id"], str(i)), group)
    for section in panel["sections"]:
        add(loc_key("PanelSection", section["id"]), section)
    for chip in panel["chips"]:
        add(loc_key("PanelChip", chip["id"]), chip)
        add(loc_key("PanelChipName", chip["id"]), panel["chip_names"][chip["id"]])
    for group in panel["chip_groups"]:
        add(loc_key("PanelGroup", group["id"]), group)
    for key, entry in panel["strings"].items():
        add(key, entry)
    return labels
