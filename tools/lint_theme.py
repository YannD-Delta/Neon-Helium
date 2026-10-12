#!/usr/bin/env python3
"""Static checks for the Neon theme sources.

Playnite loads theme dictionaries as loose XAML and fails the whole theme on
errors that a plain XML parser cannot see, so this script catches the classes
of mistakes that already happened or are easy to make:

  * XAML files that are not well-formed XML
  * `x:Shared`, which is rejected outside compiled dictionaries
  * Playnite binding markup extensions used as a Setter value (WPF rejects them)
  * StaticResource nested in another markup extension outside a template, for a
    key the same file does not define first: Playnite parses every theme file
    alone against the default theme before merging anything, so the key of
    the theme's Constants.xaml is not found and the whole theme is rejected
  * ThemeModifier entries that point to a missing or unsupported resource
  * ThemeModifier entries whose resource is never read (dead options) or is
    only read through StaticResource (the override would not apply)
  * default values outside the declared (min,max) range
  * resource keys that are used but defined nowhere (compared to a baseline
    source tree, because Playnite itself provides many keys)
  * ThemeOptions (options.yaml): variables and preset constants that are not
    defined, never read or only read through StaticResource, preset files that
    are missing or define keys the theme does not have, labels without a French
    translation, and generated files that are out of date

Usage:
    python tools/lint_theme.py [--source source] [--base path/to/old/source]
"""
import argparse
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

XAML_NS = "http://schemas.microsoft.com/winfx/2006/xaml"
KEY = "{%s}Key" % XAML_NS
SUPPORTED_TYPES = {
    "sys:Boolean", "sys:Double", "sys:Int32", "Visibility", "Color",
    "SolidColorBrush", "VerticalAlignment", "HorizontalAlignment",
}
NUMERIC_TYPES = {"sys:Double", "sys:Int32"}


def local_name(tag: str) -> str:
    return tag.split("}")[-1]


def prefixed_type(element: ET.Element) -> str:
    """Return the element type the way it is written in the file (sys:Double)."""
    tag = element.tag
    if tag.startswith("{"):
        namespace, name = tag[1:].split("}")
        if namespace == "clr-namespace:System;assembly=mscorlib":
            return "sys:" + name
        return name
    return tag


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def parse_modifier(path: Path):
    """Parse thememodifier.yaml lines into (key, range, label) entries."""
    entries, headers = [], 0
    pattern = re.compile(r"^\s*-\s*([A-Za-z0-9_]+)\s*(?:\(([^)]*)\))?\s*:\s*(.*)$")
    for number, line in enumerate(read_text(path).splitlines(), 1):
        if re.match(r'^\s*-\s*"', line):
            headers += 1
            continue
        match = pattern.match(line)
        if match:
            entries.append((number, match.group(1), match.group(2), match.group(3).strip()))
    return entries, headers


FRAMEWORK_TEMPLATES = {"ControlTemplate", "DataTemplate", "HierarchicalDataTemplate", "ItemsPanelTemplate"}
NESTED_STATIC = re.compile(r"\{\s*StaticResource\s+(?:ResourceKey=)?([A-Za-z0-9_.]+)\s*\}")


def read_default_keys() -> set:
    path = Path(__file__).with_name("playnite_default_keys.txt")
    if not path.exists():
        return set()
    return {line.strip() for line in read_text(path).splitlines() if line.strip() and not line.startswith("#")}


def nested_static_outside_templates(root: ET.Element, default_keys: set):
    """Yield (key, element name) for each StaticResource used as an argument of another markup extension
    (FallbackValue={StaticResource X} in a PluginSettings binding, ...) outside a template, when the key is
    not defined earlier in the same file nor by Playnite's default theme.

    Playnite's ThemeManager first parses every theme file on its own, with only the default theme in the
    application resources. Template content is deferred and a StaticResource set directly on a property can
    be resolved later, but an argument of another markup extension is resolved right away and throws."""
    defined = set()

    def walk(element, deferred):
        name = local_name(element.tag)
        deferred = deferred or name in FRAMEWORK_TEMPLATES
        if not deferred:
            for value in element.attrib.values():
                value = value.strip()
                if not value.startswith("{") or re.fullmatch(r"\{\s*StaticResource\s+[^{}]+\}", value):
                    continue
                for key in NESTED_STATIC.findall(value):
                    if key not in defined and key not in default_keys:
                        yield key, name
        for child in element:
            yield from walk(child, deferred)
        if element.get(KEY):
            defined.add(element.get(KEY))

    yield from walk(root, False)


def collect_definitions(files):
    """Map resource key -> (type, text value, file) for every x:Key in the theme."""
    definitions = {}
    for path in files:
        try:
            root = ET.fromstring(read_text(path))
        except ET.ParseError:
            continue
        for element in root.iter():
            key = element.get(KEY)
            if key:
                definitions.setdefault(key, (prefixed_type(element), (element.text or "").strip(), path))
    return definitions


def collect_usages(files):
    """Count DynamicResource / StaticResource references per key."""
    dynamic, static = defaultdict(int), defaultdict(int)
    pattern = re.compile(r"\{\s*(DynamicResource|StaticResource)\s+(?:ResourceKey=)?([A-Za-z0-9_.]+)\s*\}")
    for path in files:
        for kind, key in pattern.findall(read_text(path)):
            (dynamic if kind == "DynamicResource" else static)[key] += 1
    return dynamic, static


def undefined_keys(source: Path):
    files = sorted(source.rglob("*.xaml"))
    definitions = collect_definitions(files)
    dynamic, static = collect_usages(files)
    used = set(dynamic) | set(static)
    return {key for key in used if key not in definitions}


def check_theme_options(source: Path, definitions, dynamic, static, errors):
    """Validate options.yaml (ThemeOptions) against the theme dictionaries."""
    path = source / "options.yaml"
    if not path.exists():
        return 0, 0
    try:
        import yaml
    except ImportError:
        errors.append("PyYAML is required to check options.yaml (pip install pyyaml)")
        return 0, 0
    options = yaml.safe_load(read_text(path)) or {}
    locale_path = source / "Localization" / "fr_FR.xaml"
    locale = set()
    if locale_path.exists():
        locale = {element.get(KEY) for element in ET.fromstring(read_text(locale_path)).iter() if element.get(KEY)}
    theme_files = [f for f in source.rglob("*.xaml") if "Presets" not in f.parts and "Localization" not in f.parts]
    theme_keys = set(collect_definitions(theme_files))

    def check_read(key, where):
        if key not in theme_keys:
            errors.append(f"{where}: {key} is not defined in the theme dictionaries")
        elif dynamic.get(key, 0) == 0 and not re.search(r"Options\[" + re.escape(key) + r"\]", "".join(
                read_text(f) for f in source.rglob("*.xaml"))):
            errors.append(f"{where}: {key} is never read through DynamicResource, the option would do nothing")

    def check_loc(key, where):
        if key and key not in locale:
            errors.append(f"{where}: no French label for {key}")

    groups = options.get("Presets") or {}
    for gid, group in groups.items():
        check_loc(group.get("LocKey"), f"{path} preset {gid}")
        for oid, option in (group.get("Presets") or {}).items():
            where = f"{path} preset {gid}.{oid}"
            check_loc(option.get("LocKey"), where)
            for file in option.get("Files") or []:
                file_path = source / file.replace("\\", "/")
                if not file_path.is_file():
                    errors.append(f"{where}: missing file {file}")
                    continue
                root = ET.fromstring(read_text(file_path))
                for element in root.iter():
                    key = element.get(KEY)
                    if key and key not in theme_keys:
                        errors.append(f"{where}: {file} defines {key}, which the theme itself does not define")
            for key in option.get("Constants") or {}:
                check_read(key, where)
    variables = options.get("Variables") or {}
    for key, variable in variables.items():
        where = f"{path} variable {key}"
        check_loc(variable.get("LocKey"), where)
        if variable.get("Type") != "Header":
            check_read(key, where)
    return len(groups), sum(1 for v in variables.values() if v.get("Type") != "Header")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", default="source", help="theme source folder")
    parser.add_argument("--base", help="older source folder used as baseline for undefined keys")
    args = parser.parse_args()

    source = Path(args.source)
    files = sorted(source.rglob("*.xaml"))
    errors, warnings = [], []
    default_keys = read_default_keys()

    for path in files:
        text = read_text(path)
        try:
            root = ET.fromstring(text)
        except ET.ParseError as exc:
            errors.append(f"{path}: not well-formed XML ({exc})")
        else:
            for key, element in sorted(set(nested_static_outside_templates(root, default_keys))):
                errors.append(f"{path}: {element} reads {{StaticResource {key}}} inside another markup extension "
                              "outside a template, Playnite cannot resolve it when it validates the file alone "
                              "(write the default value instead)")
        if re.search(r"\bx:Shared\s*=", text):
            errors.append(f"{path}: x:Shared is rejected by Playnite's loose XAML loader")
        # Playnite's binding markup extensions return themselves for a Setter value, and WPF only accepts
        # a Binding or a DynamicResource there: the style would throw when it is sealed.
        for match in re.finditer(r"<Setter\b[^>]*\bValue=\"\{(PluginSettings|PluginStatus|PluginConverter|Settings)\b", text):
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{path}:{line}: {match.group(1)} cannot be a Setter value, bind an element property and use {{Binding}} instead")

    definitions = collect_definitions(files)
    dynamic, static = collect_usages(files)

    modifier_path = source / "thememodifier.yaml"
    entries, headers = parse_modifier(modifier_path)
    seen = set()
    for number, key, value_range, label in entries:
        where = f"{modifier_path}:{number} ({key})"
        if key in seen:
            errors.append(f"{where}: duplicate entry")
        seen.add(key)
        if not label:
            errors.append(f"{where}: missing label")
        if key not in definitions:
            errors.append(f"{where}: resource is not defined in any theme dictionary")
            continue
        resource_type, text_value, _ = definitions[key]
        if resource_type not in SUPPORTED_TYPES:
            errors.append(f"{where}: type {resource_type} is not known to work with ThemeModifier")
        if resource_type in NUMERIC_TYPES and not value_range:
            errors.append(f"{where}: numeric option without a (min,max) range")
        if value_range and resource_type in NUMERIC_TYPES:
            try:
                low, high = (float(part) for part in value_range.split(","))
                value = float(text_value)
                if not low <= value <= high:
                    errors.append(f"{where}: default {value} is outside ({low},{high})")
            except ValueError:
                errors.append(f"{where}: cannot read range '{value_range}' / default '{text_value}'")
        if dynamic.get(key, 0) == 0 and static.get(key, 0) == 0:
            # Colors can be consumed by brushes that reference them dynamically.
            errors.append(f"{where}: dead option, the resource is never read")
        elif dynamic.get(key, 0) == 0:
            errors.append(f"{where}: only read through StaticResource, the override would not apply")
        elif static.get(key, 0) > 0:
            warnings.append(f"{where}: also read through StaticResource in {static[key]} place(s)")

    preset_groups, option_count = check_theme_options(source, definitions, dynamic, static, errors)

    builder = Path(__file__).with_name("build_options.py")
    if builder.exists() and (source / "options.yaml").exists():
        result = subprocess.run([sys.executable, str(builder), "--source", str(source), "--check"],
                                capture_output=True, text=True)
        if result.returncode != 0:
            errors.append("generated settings files: " + (result.stderr.strip() or result.stdout.strip()))

    missing_now = undefined_keys(source)
    if args.base:
        missing_now -= undefined_keys(Path(args.base))
        label = "new undefined resource key(s) compared to the baseline"
    else:
        label = "undefined resource key(s) (Playnite provides some of them)"
    for key in sorted(missing_now):
        (errors if args.base else warnings).append(f"{label}: {key}")

    for message in warnings:
        print("warning:", message)
    for message in errors:
        print("error:  ", message)
    print(f"\n{len(files)} xaml files, {len(entries)} ThemeModifier colors in {headers} groups, "
          f"{option_count} ThemeOptions variables, {preset_groups} preset lists, "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
