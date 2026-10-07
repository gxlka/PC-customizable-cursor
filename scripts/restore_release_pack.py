"""Reuse a published pack only when every cursor source still matches its tag."""
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image
from wingline.roles import THEMES
from wingline.package import _archive_theme, _draw_native_preview


def gh_json(*arguments):
    return json.loads(subprocess.check_output(["gh", *arguments], text=True))


def reusable(changed):
    # GitHub's comparison file list is limited to 300 entries. Fail closed.
    return len(changed) < 300 and all(
        path.startswith(".github/") or path in {"README.md", ".gitignore", "scripts/restore_release_pack.py"}
        for path in changed
    )


def main():
    restored = False
    try:
        repository = os.environ["GITHUB_REPOSITORY"]
        release = gh_json("api", f"repos/{repository}/releases/latest")
        tag = release["tag_name"]
        comparison = gh_json("api", f"repos/{repository}/compare/{tag}...{os.environ['GITHUB_SHA']}")
        if not reusable([file["filename"] for file in comparison["files"]]):
            print("Cursor sources changed; generate and test a new pack.")
            return
        archive_name = "curs0r-pack.zip"
        if not any(asset["name"] == archive_name for asset in release["assets"]):
            return
        output = Path("dist")
        if output.exists():
            shutil.rmtree(output)
        output.mkdir()
        subprocess.run(["gh", "release", "download", tag, "--repo", repository,
                        "--pattern", archive_name, "--dir", str(output)], check=True)
        with zipfile.ZipFile(output / archive_name) as archive:
            for entry in archive.infolist():
                path = PurePosixPath(entry.filename)
                if path.is_absolute() or ".." in path.parts or "\\" in entry.filename or not path.parts or path.parts[0] not in THEMES:
                    raise ValueError("Unexpected path in published cursor pack")
            archive.extractall(output)
        for theme in THEMES.values():
            with zipfile.ZipFile(output / f"{theme.key}.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
                _archive_theme(archive, theme, output / theme.key)
        previews = [Image.open(output / theme.key / "preview.png").convert("RGB") for theme in THEMES.values()]
        gutter = 18
        overview = Image.new("RGB", (sum(image.width for image in previews) + gutter * (len(previews) + 1), max(image.height for image in previews) + 2*gutter), "#DDE2EA")
        x = gutter
        for preview in previews:
            overview.paste(preview, (x, gutter))
            x += preview.width + gutter
        overview.save(output / "preview.png", optimize=True)
        _draw_native_preview(output / "preview-32px.png")
        restored = True
        print(f"Restored published {tag}; cursor sources are unchanged.")
    except (subprocess.CalledProcessError, KeyError, ValueError, OSError) as error:
        print(f"Published pack unavailable for reuse: {error}. Build from source.")
    finally:
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(f"restored={'true' if restored else 'false'}\n")


if __name__ == "__main__":
    main()
