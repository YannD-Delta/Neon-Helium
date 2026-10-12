"""Artwork info line: every chip has a free position (HeroChipPos<Id>, a Double) and the line is sorted live.

Playnite themes are loose XAML without code, so the order is built from stock WPF parts:
  * one FrameworkContentElement per chip (and per line break) holds the chip position in Tag,
    bound to Theme Options, and the template to show in ToolTip;
  * a CollectionViewSource sorts them by Tag (then Uid, the default order) with live sorting,
    so a new position moves the chip at once;
  * an ItemsControl shows the sorted items in a WrapPanel.

The arrows of the settings panel move a chip just before its predecessor or just after its successor:
MathConverter (shipped with Playnite) finds the neighbour positions, and two hidden sliders bound to the
chip position step by the computed distance (Slider.DecreaseSmall / IncreaseSmall). Only the moved chip
gets a new value, the midpoint between its two new neighbours, so no other setting is written.
"""

STEP = 10  # distance between the default positions, and the room taken at both ends of the line


def pos_key(chip):
    return "HeroChipPos" + chip["id"]


def opt(key):
    return (f"{{PluginSettings Plugin=ThemeOptions, Path=Options[{key}], FallbackValue={{StaticResource {key}}}, "
            f"TargetNullValue={{StaticResource {key}}}}}")


def twoway(key):
    return (f"{{PluginSettings Plugin=ThemeOptions, Path=Options[{key}], Mode=TwoWay, "
            f"FallbackValue={{StaticResource {key}}}, TargetNullValue={{StaticResource {key}}}}}")


def default_positions(chips):
    return {pos_key(chip): STEP * (index + 1) for index, chip in enumerate(chips)}


def indent(text, spaces):
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.split("\n"))


def sorted_view(prefix, entries, tag=lambda chip: opt(pos_key(chip))):
    """Keyed items, their array and the live sorted view (shown with the shared HndChipItem template).

    entries: (item key, sort Uid, template key, chip) in default order."""
    items = [f'<FrameworkContentElement x:Key="{key}" Uid="{uid}" ToolTip="{{StaticResource {template}}}"\n'
             f'                         Tag="{tag(chip)}" />'
             for key, uid, template, chip in entries]
    refs = "\n".join(f'    <StaticResource ResourceKey="{key}" />' for key, _, _, _ in entries)
    return "\n".join(items) + f'''
<x:Array x:Key="{prefix}Items" Type="{{x:Type FrameworkContentElement}}">
{refs}
</x:Array>
<CollectionViewSource x:Key="{prefix}View" Source="{{StaticResource {prefix}Items}}" IsLiveSortingRequested="True">
    <CollectionViewSource.SortDescriptions>
        <scm:SortDescription PropertyName="Tag" Direction="Ascending" />
        <scm:SortDescription PropertyName="Uid" Direction="Ascending" />
    </CollectionViewSource.SortDescriptions>
    <CollectionViewSource.LiveSortingProperties>
        <sys:String>Tag</sys:String>
    </CollectionViewSource.LiveSortingProperties>
</CollectionViewSource>'''


ITEM_TEMPLATE = '''<!-- each sorted item shows the template it carries, with the DataContext of the list (the game in the Details view) -->
<DataTemplate x:Key="HndChipItem">
    <ContentControl Focusable="False" ContentTemplate="{Binding ToolTip}"
                    Content="{Binding DataContext, RelativeSource={RelativeSource AncestorType=ItemsControl}}" />
</DataTemplate>'''


def break_template(key, chip, width):
    return (f'<DataTemplate x:Key="{key}">\n'
            f'    <Grid Style="{{DynamicResource SectionToggleGrid}}" Tag="{opt(chip["show"])}">\n'
            f'        <Grid Height="0" Width="{width}" Style="{{DynamicResource SectionToggleGrid}}" Tag="{opt(chip["break"])}" />\n'
            f'    </Grid>\n'
            f'</DataTemplate>')


def line_entries(prefix, chips, chip_template):
    """Break item then chip item for every chip; the break sorts first at the same position."""
    entries = []
    for index, chip in enumerate(chips):
        entries.append((f"{prefix}Break{chip['id']}Item", f"{index:02}a", f"{prefix}Break{chip['id']}", chip))
        entries.append((f"{prefix}Chip{chip['id']}Item", f"{index:02}b", chip_template(chip), chip))
    return entries


def hero_resources(chips):
    """Resources of the artwork line, in the Details view root Grid (the chip templates HndChip<Id> come first)."""
    width = opt("HeroInfoLineMaxWidth")
    breaks = "\n".join(break_template(f"HndHeroBreak{chip['id']}", chip, width) for chip in chips)
    return breaks + "\n" + sorted_view("HndHero", line_entries("HndHero", chips, lambda c: f"HndChip{c['id']}"))


def hero_line():
    return f'''<ItemsControl Focusable="False" Margin="0,0,0,6" MaxWidth="{opt("HeroInfoLineMaxWidth")}"
              ItemsSource="{{Binding Source={{StaticResource HndHeroView}}}}" ItemTemplate="{{StaticResource HndChipItem}}">
    <ItemsControl.ItemsPanel>
        <ItemsPanelTemplate>
            <WrapPanel Orientation="Horizontal" />
        </ItemsPanelTemplate>
    </ItemsControl.ItemsPanel>
</ItemsControl>'''


# ---------------------------------------------------------------------------------------------- panel
def neighbour_expressions(count, k):
    """MathConverter expressions on the positions [0]..[count-1] of every chip, for the chip k.

    The order matches the view: by position, then by default index (lower first on a tie)."""
    others = [i for i in range(count) if i != k]
    before = ",".join(f"([{i}]{'&lt;=' if i < k else '&lt;'}[{k}]?[{i}]:null)" for i in others)
    after = ",".join(f"([{i}]{'&gt;' if i < k else '&gt;='}[{k}]?[{i}]:null)" for i in others)
    # the chip before the predecessor / after the successor: [count] is that neighbour's position
    before2 = ",".join(f"([{i}]&lt;[{count}]?[{i}]:null)" for i in range(count))
    after2 = ",".join(f"([{i}]&gt;[{count}]?[{i}]:null)" for i in range(count))
    return f"Max({before})", f"Min({after})", f"Max({before2})", f"Min({after2})"


def multi(param, bindings, extra=""):
    inner = "    " + "".join(bindings)  # one line: the rows are repeated for every chip
    return (f'<MultiBinding Converter="{{StaticResource MathConverter}}" ConverterParameter="{param}"{extra}>\n'
            f'{inner}\n</MultiBinding>')


def row_template(chips, k, labels):
    """One row of the chips page: arrows, show switch with the chip name and an example, line break toggle."""
    chip = chips[k]
    cid = chip["id"]
    # positions in default order: the "Calc" grid below takes the source array of the sorted view the rows
    # are listed from as DataContext, so [i].Tag is the position of chip i
    positions = [f'<Binding Path="[{i}].Tag"/>' for i in range(len(chips))]
    prev, nxt, prev2, nxt2 = neighbour_expressions(len(chips), k)

    def probe(name, expr, extra_binding=None):
        binds = positions + ([extra_binding] if extra_binding else [])
        return (f'<FrameworkElement x:Name="{name}" Visibility="Collapsed">\n    <FrameworkElement.Tag>\n'
                f'{indent(multi(expr, binds), 8)}\n    </FrameworkElement.Tag>\n</FrameworkElement>')

    own = positions[k]

    def stepper(name, expr, first, second):
        change = multi(expr, [own, f'<Binding ElementName="{first}" Path="Tag" />', f'<Binding ElementName="{second}" Path="Tag" />'],
                       ' FallbackValue="0" TargetNullValue="0"')
        return (f'<Slider x:Name="{name}" Width="0" Height="0" Opacity="0" IsHitTestVisible="False" Focusable="False" IsTabStop="False"\n'
                f'        Minimum="-1000000" Maximum="1000000" Value="{twoway(pos_key(chip))}">\n'
                f'    <Slider.SmallChange>\n{indent(change, 8)}\n    </Slider.SmallChange>\n</Slider>')

    def arrow(glyph, command, target, probe_name, tip):
        return (f'<Button Content="{glyph}" Command="{command}" CommandTarget="{{Binding ElementName={target}}}"\n'
                f'        ToolTip="{{DynamicResource {tip}}}">\n'
                f'    <Button.Style>\n'
                f'        <Style TargetType="Button" BasedOn="{{StaticResource HndPanelArrow}}">\n'
                f'            <Style.Triggers>\n'
                f'                <DataTrigger Binding="{{Binding Tag, ElementName={probe_name}}}" Value="{{x:Null}}">\n'
                f'                    <Setter Property="Visibility" Value="Hidden" />\n'
                f'                </DataTrigger>\n'
                f'            </Style.Triggers>\n'
                f'        </Style>\n'
                f'    </Button.Style>\n'
                f'</Button>')

    # up: midpoint between the predecessor and the chip before it (or STEP before the first chip)
    up = stepper("Up", f"Max(0, x - (z == null ? y - {STEP} : (y + z) / 2))", "Prev", "Prev2")
    down = stepper("Down", f"Max(0, (z == null ? y + {STEP} : (y + z) / 2) - x)", "Next", "Next2")
    probes = "\n".join([probe("Prev", prev), probe("Next", nxt),
                        probe("Prev2", prev2, '<Binding ElementName="Prev" Path="Tag" />'),
                        probe("Next2", nxt2, '<Binding ElementName="Next" Path="Tag" />')])
    name_key, sample_key = labels("PanelChipName", cid), labels("PanelChip", cid)
    return f'''<DataTemplate x:Key="HndChipRow{cid}">
    <DockPanel Style="{{DynamicResource HndPanelRow}}">
        <Grid x:Name="Calc" DockPanel.Dock="Left" Width="0" Height="0"
              DataContext="{{Binding ItemsSource.SourceCollection, RelativeSource={{RelativeSource AncestorType=ItemsControl}}}}">
{indent(probes, 12)}
{indent(up, 12)}
{indent(down, 12)}
        </Grid>
        <StackPanel DockPanel.Dock="Left" Orientation="Horizontal" Margin="0,0,10,0" VerticalAlignment="Center">
{indent(arrow("&#xE70E;", "Slider.DecreaseSmall", "Up", "Prev", "LOCHNDPanelMoveUp"), 12)}
{indent(arrow("&#xE70D;", "Slider.IncreaseSmall", "Down", "Next", "LOCHNDPanelMoveDown"), 12)}
        </StackPanel>
        <ToggleButton DockPanel.Dock="Right" Style="{{DynamicResource HndPanelBreakToggle}}" ToolTip="{{DynamicResource LOCHNDPanelBreakTip}}"
                      IsChecked="{twoway(chip["break"])}" />
        <TextBlock DockPanel.Dock="Right" Style="{{DynamicResource HndPanelSample}}" Text="{{DynamicResource {sample_key}}}" />
        <CheckBox Style="{{DynamicResource HndPanelSwitch}}" IsChecked="{twoway(chip["show"])}"
                  Content="{{DynamicResource {name_key}}}" />
    </DockPanel>
</DataTemplate>'''


def pill_template(key, chip, labels):
    return (f'<DataTemplate x:Key="{key}">\n'
            f'    <Border Style="{{DynamicResource HndPanelPreviewPill}}" Tag="{opt(chip["show"])}"\n'
            f'            Visibility="{{Binding Tag, RelativeSource={{RelativeSource Self}}, Converter={{StaticResource BooleanToVisibilityConverter}}}}">\n'
            f'        <TextBlock Text="{{DynamicResource {labels("PanelChip", chip["id"])}}}" />\n'
            f'    </Border>\n'
            f'</DataTemplate>')


PREVIEW_WIDTH = 560


def shared_resources(chips, labels):
    """Common.xaml: the item template and the row templates of the chips page, loaded once for every host.
    The rows read the positions from the source array of the list they are in, so they need no key."""
    return "\n".join([ITEM_TEMPLATE] + [row_template(chips, k, labels) for k in range(len(chips))])


def rows_resources(prefix, chips):
    """Host resources of the chips page rows: one item per chip, sorted live."""
    return sorted_view(f"{prefix}Rows", [(f"{prefix}Row{c['id']}Item", f"{i:02}", f"HndChipRow{c['id']}", c)
                                          for i, c in enumerate(chips)])


def panel_resources(prefix, chips, labels, real_chips):
    """Resources of the chips page preview: the real chips of the selected game in the Details view,
    name pills in the top panel, where no game is at hand."""
    breaks = "\n".join(break_template(f"{prefix}PreviewBreak{c['id']}", c, PREVIEW_WIDTH) for c in chips)
    if real_chips:
        template = lambda c: f"HndChip{c['id']}"
        pills = ""
    else:
        template = lambda c: f"{prefix}Pill{c['id']}"
        pills = "\n".join(pill_template(f"{prefix}Pill{c['id']}", c, labels) for c in chips) + "\n"
    entries = []
    for index, chip in enumerate(chips):
        entries.append((f"{prefix}PreviewBreak{chip['id']}Item", f"{index:02}a", f"{prefix}PreviewBreak{chip['id']}", chip))
        entries.append((f"{prefix}PreviewChip{chip['id']}Item", f"{index:02}b", template(chip), chip))
    return breaks + "\n" + pills + sorted_view(f"{prefix}Preview", entries)


def preview_template(prefix, chips, labels, real_chips):
    """Host resource HndChipsPreview, shown by the chips page of Common.xaml."""
    return (f'<DataTemplate x:Key="HndChipsPreview">\n    <Grid>\n        <Grid.Resources>\n'
            f'{indent(panel_resources(prefix, chips, labels, real_chips), 12)}\n        </Grid.Resources>\n'
            f'{indent(panel_preview(prefix), 8)}\n    </Grid>\n</DataTemplate>')


def rows_list(prefix):
    return f'''<ItemsControl Focusable="False" ItemsSource="{{Binding Source={{StaticResource {prefix}RowsView}}}}"
              ItemTemplate="{{StaticResource HndChipItem}}" />'''


def panel_preview(prefix):
    return f'''<ItemsControl Focusable="False" Width="{PREVIEW_WIDTH}" HorizontalAlignment="Left" ClipToBounds="True"
              ItemsSource="{{Binding Source={{StaticResource {prefix}PreviewView}}}}" ItemTemplate="{{StaticResource HndChipItem}}">
    <ItemsControl.ItemsPanel>
        <ItemsPanelTemplate>
            <WrapPanel Orientation="Horizontal" />
        </ItemsPanelTemplate>
    </ItemsControl.ItemsPanel>
</ItemsControl>'''
