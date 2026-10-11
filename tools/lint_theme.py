#!/usr/bin/env python3
"""Static checks for the Neon theme sources.

Playnite loads theme dictionaries as loose XAML and fails the whole theme on
errors that a plain XML parser cannot see, so this script catches the classes
of mistakes that already happened or are easy to make:

  * XAML files that are not well-formed XML
  * `x:Shared`, which is rejected outside compiled dictionaries
  * ThemeModifier entries that point to a missing or unsupported resource
  * ThemeModifier entries whose resource is never read (dead options) or is
    only read through StaticResource (the override would not apply)
  * default values outside the declared (min,max) range
  * resource keys that are used but defined nowhere (compared to a baseline
    source tree, because Playnite itself provides many keys)

Usage:
    python tools/lint_theme.py [--source source] [--base path/to/old/source]
"""
import argparse
import re
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", default="source", help="theme source folder")
    parser.add_argument("--base", help="older source folder used as baseline for undefined keys")
    args = parser.parse_args()

    source = Path(args.source)
    files = sorted(source.rglob("*.xaml"))
    errors, warnings = [], []

    for path in files:
        text = read_text(path)
        try:
            ET.fromstring(text)
        except ET.ParseError as exc:
            errors.append(f"{path}: not well-formed XML ({exc})")
        if re.search(r"\bx:Shared\s*=", text):
            errors.append(f"{path}: x:Shared is rejected by Playnite's loose XAML loader")

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
    print(f"\n{len(files)} xaml files, {len(entries)} ThemeModifier options, {headers} groups, "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
