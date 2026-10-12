"""Settings panel: one large popup with a page list on the left and setting cards on the right.

Generated from the "panel" section of tools/options_spec.yaml into two kinds of host:
  details  Views/DetailsViewGameOverview.xaml. Each section gear is a toggle bound to the
           radio button of its page, and the popup is open while any page is selected.
  top      Views/TopPanel.xaml and Presets/TopPanel/Dune.xaml. The workshop toggle opens it.
Every control is bound TwoWay to Theme Options Options[...], so the theme changes while you click.
"""
import re

import chips_line

THEME_OPTIONS_ADDON = "ThemeOptions_904cbf3b-573f-48f8-9642-0a09d05c64ef"
THEME_OPTIONS_GUID = "904cbf3b-573f-48f8-9642-0a09d05c64ef"
THEME_MODIFIER_GUID = "ec2f4013-17e6-428a-b8a9-5e34a3b80009"
EXTRAS = "felixkmh_Extras_Plugin"
# settings still read as {DynamicResource ...} somewhere (style setters, Playnite's own keys): Theme Options
# turns them into resources when Playnite starts, so the panel marks them "after a restart" (set by build_options)
RESTART_KEYS = set()


def glyph(text):
    return "".join(f"&#x{ord(ch):X};" for ch in text)


def opt(key):
    return (f"{{PluginSettings Plugin=ThemeOptions, Path=Options[{key}], FallbackValue={{StaticResource {key}}}, "
            f"TargetNullValue={{StaticResource {key}}}}}")


def twoway(key, delay=False):
    extra = ", Delay=150" if delay else ""
    return (f"{{PluginSettings Plugin=ThemeOptions, Path=Options[{key}], Mode=TwoWay{extra}, "
            f"FallbackValue={{StaticResource {key}}}, TargetNullValue={{StaticResource {key}}}}}")


def indent(text, spaces):
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.split("\n"))


# live examples at the top of some pages, drawn with the theme's own styles and settings
PAGE_PREVIEWS = {
    "Header": f'''<StackPanel Orientation="Horizontal" IsHitTestVisible="False">
    <Button Style="{{DynamicResource HeroPlayButton}}" Content="{{DynamicResource LOCPlayGame}}" Margin="0,0,8,0"
            Width="{opt('HeroActionButtonWidth')}" Height="{opt('HeroActionButtonHeight')}" />
    <Button Style="{{DynamicResource HeroContextButton}}" Content="{{DynamicResource LOCInstallGame}}"
            Width="{opt('HeroActionButtonWidth')}" Height="{opt('HeroActionButtonHeight')}" />
</StackPanel>''',
    "Text": '''<StackPanel>
    <TextBlock Style="{DynamicResource BaseTextBlockStyle}" FontSize="{DynamicResource FontSizeLargest}" Text="Aa 2024" />
    <TextBlock Style="{DynamicResource BaseTextBlockStyle}" FontSize="{DynamicResource FontSizeLarger}" Text="{DynamicResource LOCHNDPanelTextSection}" />
    <TextBlock Style="{DynamicResource BaseTextBlockStyle}" FontSize="{DynamicResource FontSizeLarge}" Text="{DynamicResource LOCHNDPanelTextLarge}" />
    <TextBlock Style="{DynamicResource BaseTextBlockStyle}" FontSize="{DynamicResource FontSize}" Text="{DynamicResource LOCHNDPanelTextNormal}" />
    <TextBlock Style="{DynamicResource BaseTextBlockStyle}" FontSize="{DynamicResource FontSizeSmall}" Text="{DynamicResource LOCHNDPanelTextSmall}" />
</StackPanel>''',
}


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
        # the help text sits under the setting; settings that apply after a restart get a badge
        info = ""
        if key in RESTART_KEYS:
            info += ('\n    <TextBlock DockPanel.Dock="Right" Style="{DynamicResource HndPanelRestart}" '
                     'Text="{DynamicResource LOCHNDPanelRestart}" ToolTip="{DynamicResource LOCHNDPanelRestartTip}" />')
        if key in self.tips:
            info += ('\n    <TextBlock DockPanel.Dock="Bottom" Style="{DynamicResource HndPanelHelp}" Text="{DynamicResource %s}" />'
                     % self.loc_key("Tip", key))
        if kind == "Boolean":
            return (f'<DockPanel Style="{{DynamicResource HndPanelRow}}">{info}\n'
                    f'    <CheckBox Style="{{DynamicResource HndPanelSwitch}}" Content="{label}" IsChecked="{twoway(key)}" />\n'
                    f'</DockPanel>')
        if kind in ("Double", "Int32") and self.ranges[key]:
            # an Int32 setting gets the slider's Double: Theme Options keeps the declared type when it saves
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
        if kind == "Visibility":
            # two radio buttons: ObjectEqualityToBoolConverter writes its parameter back when one is checked
            def choice(value, text):
                return (f'<RadioButton Style="{{DynamicResource HndPanelSegment}}" GroupName="Hnd{key}" Content="{{DynamicResource {text}}}"\n'
                        f'             IsChecked="{{PluginSettings Plugin=ThemeOptions, Path=Options[{key}], Mode=TwoWay, '
                        f'Converter={{StaticResource ObjectEqualityToBoolConverter}}, ConverterParameter={{x:Static Visibility.{value}}}, '
                        f'FallbackValue=False}}" />')
            return (f'<DockPanel Style="{{DynamicResource HndPanelRow}}">{info}\n'
                    f'    <StackPanel DockPanel.Dock="Right" Orientation="Horizontal">\n'
                    f'{indent(choice("Visible", "LOCHNDPanelShow"), 8)}\n{indent(choice("Collapsed", "LOCHNDPanelHide"), 8)}\n'
                    f'    </StackPanel>\n'
                    f'    <TextBlock Style="{{DynamicResource HndPanelLabel}}" VerticalAlignment="Center" Text="{label}" />\n'
                    f'</DockPanel>')
        raise ValueError(f"panel item {key}: only Booleans, Visibility, and Doubles or Int32 with a range, are supported ({kind})")

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
        # live preview in the chip order (each host defines HndChipsPreview: the real chips of the selected game
        # in the Details view, name pills in the top panel), then one row per chip in that order: arrows on the
        # left move it (and the real line), the switch shows it, the toggle on the right starts a new line before it
        preview = (f'<Border Style="{{DynamicResource HndPanelPreview}}">\n    <StackPanel>\n'
                   f'        <TextBlock Style="{{DynamicResource HndPanelCardTitle}}" Text="{{DynamicResource LOCHNDPanelPreview}}" />\n'
                   f'        <ContentControl Focusable="False" Content="{{Binding}}" ContentTemplate="{{DynamicResource HndChipsPreview}}" />\n'
                   f'    </StackPanel>\n</Border>')
        rows = (f'<Border Style="{{DynamicResource HndPanelCard}}">\n    <StackPanel>\n'
                f'        <StackPanel.Resources>\n{indent(chips_line.rows_resources(self.prefix, self.panel["chips"]), 12)}\n'
                f'        </StackPanel.Resources>\n'
                f'        <TextBlock Style="{{DynamicResource HndPanelCardTitle}}" Text="{{DynamicResource LOCHNDPanelChipOrder}}" />\n'
                f'        <TextBlock Style="{{DynamicResource HndPanelText}}" Text="{{DynamicResource LOCHNDPanelChipOrderText}}" />\n'
                f'{indent(chips_line.rows_list(self.prefix), 8)}\n'
                f'    </StackPanel>\n</Border>')
        general = [self.card(self.loc_key("PanelCard", page["id"], str(i)), g["items"]) for i, g in enumerate(page.get("groups", []))]
        return "\n".join([preview, rows] + general)

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
            preview = PAGE_PREVIEWS.get(page["id"])
            if preview:
                body = (f'<Border Style="{{DynamicResource HndPanelPreview}}">\n    <StackPanel>\n'
                        f'        <TextBlock Style="{{DynamicResource HndPanelCardTitle}}" Text="{{DynamicResource LOCHNDPanelPreview}}" />\n'
                        f'{indent(preview, 8)}\n    </StackPanel>\n</Border>\n' + body)
            if page.get("desc"):
                body = (f'<TextBlock Style="{{DynamicResource HndPanelPageDesc}}" Text="{{DynamicResource {self.loc_key("PanelPageDesc", page["id"])}}}" />\n'
                        + body)
            result.append((page["id"], self.loc_key("PanelPage", page["id"]), glyph(page["glyph"]), body))
        for section in self.panel["sections"]:
            result.append(("Section" + section["id"], self.loc_key("PanelSection", section["id"]), None,
                           self.section_page(section)))
        return result

    def page_templates(self):
        """Common.xaml: one DataTemplate per page (HndPage<Id>), built only when a host shows that page."""
        templates = []
        for pid, title, _, body in self.pages():
            templates.append(f'<DataTemplate x:Key="HndPage{pid}">\n    <StackPanel>\n'
                             f'        <TextBlock Style="{{DynamicResource HndPanelPageTitle}}" Text="{{DynamicResource {title}}}" />\n'
                             f'{indent(body, 8)}\n    </StackPanel>\n</DataTemplate>')
        return "\n".join(templates)

    def page_ids(self):
        return ([(p["id"], self.loc_key("PanelPage", p["id"]), glyph(p["glyph"])) for p in self.panel["pages"]]
                + [("Section" + s["id"], self.loc_key("PanelSection", s["id"]), None) for s in self.panel["sections"]])

    # ------------------------------------------------------------------ frame
    def frame(self, host, close_binding, first_checked):
        pages = [(pid, title, icon, None) for pid, title, icon in self.page_ids()]
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
            # the page is built only while its radio button is checked: the trigger sets the page template,
            # kept once in Common.xaml, so a closed panel costs its page list only
            content.append(f'<ContentControl Focusable="False" Content="{{Binding}}">\n'
                           f'    <ContentControl.Style>\n'
                           f'        <Style TargetType="ContentControl">\n'
                           f'            <Setter Property="Visibility" Value="Collapsed" />\n'
                           f'            <Style.Triggers>\n'
                           f'                <DataTrigger Binding="{{Binding IsChecked, ElementName={radio}}}" Value="True">\n'
                           f'                    <Setter Property="Visibility" Value="Visible" />\n'
                           f'                    <Setter Property="ContentTemplate" Value="{{DynamicResource HndPage{pid}}}" />\n'
                           f'                </DataTrigger>\n'
                           f'            </Style.Triggers>\n'
                           f'        </Style>\n'
                           f'    </ContentControl.Style>\n'
                           f'</ContentControl>')
        none_radio = ""
        if host == "details":
            none_radio = (f'\n<RadioButton x:Name="{self.name("PageNone")}" GroupName="{group}" Visibility="Collapsed" IsChecked="True" />')
        resources = chips_line.preview_template(self.prefix, self.panel["chips"], self.loc_key, host == "details")
        return f'''<Grid Width="{opt('SettingsPanelWidth')}" Height="{opt('SettingsPanelHeight')}">
<Grid.Resources>
{indent(resources, 4)}
</Grid.Resources>
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
        if page.get("desc"):
            add(loc_key("PanelPageDesc", page["id"]), page["desc"])
        for i, group in enumerate(page.get("groups", [])):
            add(loc_key("PanelCard", page["id"], str(i)), group)
    for section in panel["sections"]:
        add(loc_key("PanelSection", section["id"]), section)
    for chip in panel["chips"]:
        add(loc_key("PanelChip", chip["id"]), chip)
        add(loc_key("PanelChipName", chip["id"]), panel["chip_names"][chip["id"]])
    for key, entry in panel["strings"].items():
        add(key, entry)
    return labels
