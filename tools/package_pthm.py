#!/usr/bin/env python3
"""Build the installable Playnite theme package (.pthm) from the theme sources.

A .pthm is a zip with the theme files at its root. Files that only exist to open
the theme in Visual Studio must not be shipped: Playnite would load them instead
of its own copies (stale App.xaml, GlobalResources.xaml, LocSource.xaml...), which
breaks the theme.

Usage:
    python tools/package_pthm.py [--source source] [--out dist] [--skip-lint]
"""
import argparse
import re
import subprocess
import sys
import zipfile
from pathlib import Path

EXCLUDED_FILES = {
    "App.xaml", "ControlGalleryView.xaml", "GlobalResources.xaml", "LocSource.xaml",
    "Neon.csproj", "Neon.sln",
}
EXCLUDED_DIRS = {"Fonts", "bin", "obj", ".vs"}


def read_manifest(path: Path):
    text = path.read_text(encoding="utf-8-sig")
    theme_id = re.search(r"^Id:\s*(\S+)", text, re.M).group(1)
    version = re.search(r"^Version:\s*(\S+)", text, re.M).group(1)
    return theme_id, version


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", default="source")
    parser.add_argument("--out", default="dist")
    parser.add_argument("--skip-lint", action="store_true")
    args = parser.parse_args()

    source, out = Path(args.source), Path(args.out)
    if not args.skip_lint:
        lint = Path(__file__).with_name("lint_theme.py")
        if subprocess.call([sys.executable, str(lint), "--source", str(source)]) != 0:
            print("Lint failed, package not built.")
            return 1

    theme_id, version = read_manifest(source / "theme.yaml")
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"{theme_id}_{version.replace('.', '_')}.pthm"

    count = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as package:
        for path in sorted(source.rglob("*")):
            relative = path.relative_to(source)
            if path.is_dir() or relative.parts[0] in EXCLUDED_DIRS:
                continue
            if len(relative.parts) == 1 and relative.name in EXCLUDED_FILES:
                continue
            package.write(path, relative.as_posix())
            count += 1
    print(f"{target} ({count} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
