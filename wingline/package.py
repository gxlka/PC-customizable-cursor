from __future__ import annotations

import csv
import re
import shutil
import struct
import zipfile
from pathlib import Path, PureWindowsPath

from PIL import Image, ImageDraw, ImageFont

from .ani import encode_ani
from .artwork import ANIMATION_FRAMES, SUPPORTED_SIZES, render_cursor
from .cur import encode_cur
from .roles import ROLE_ORDER, THEMES, CursorRole, Theme


ANIMATED_ROLES = {"appstarting", "wait"}
INSTALL_TEXT = """Wingline Cursor Pack — Windows install

Extract this folder and double-click Install-Wingline.cmd. It copies the
cursor files into your user profile, reapplies the scheme even if Windows
already has an older registration, and reloads the active cursors. It does
not need administrator access.

The .inf remains available for manual import. If Windows reports that an INF
is already installed, run Install-Wingline.cmd to reapply and activate it.
Cursor files include sizes through 256 px.

The included preview.png shows the 48 px artwork on light and dark backgrounds.
"""


def cursor_filename(theme: Theme, role: CursorRole) -> str:
    extension = ".ani" if role.key in ANIMATED_ROLES else ".cur"
    return f"{theme.key}-{role.key}{extension}"


def _role_cursor_bytes(role: CursorRole, theme: Theme) -> bytes:
    if role.key in ANIMATED_ROLES:
        frames = []
        for frame_index in range(ANIMATION_FRAMES):
            image, hotspot = render_cursor(role, theme, max(SUPPORTED_SIZES), frame=frame_index)
            frames.append(encode_cur([(image, hotspot)]))
        return encode_ani(frames)

    images = [render_cursor(role, theme, size) for size in SUPPORTED_SIZES]
    return encode_cur(images)


def _installer_text(theme: Theme, filenames: list[str]) -> str:
    scheme_paths = [
        f"%10%\\Cursors\\{theme.key}\\{filename}" for filename in filenames
    ]
    scheme_value = ",".join(scheme_paths)
    active_cursor_values = [
        'HKCU,"Control Panel\\Cursors",,0x00000000,"%SchemeName%"',
        'HKCU,"Control Panel\\Cursors","Scheme Source",0x00010001,1',
    ]
    active_cursor_values.extend(
        f'HKCU,"Control Panel\\Cursors","{role.registry_value}",0x00000000,'
        f'"%10%\\Cursors\\{theme.key}\\{filename}"'
        for role, filename in zip(ROLE_ORDER, filenames)
    )
    source_files = "\n".join(f"{filename}=1" for filename in filenames)
    copy_files = "\n".join(filenames)
    return (
        "[Version]\n"
        'Signature="$Windows NT$"\n'
        "\n"
        "[DefaultInstall]\n"
        "CopyFiles=CursorFiles\n"
        "AddReg=CursorScheme,ActiveCursors\n"
        "\n"
        "[SourceDisksNames]\n"
        f"1=%DiskName%,,,.\n"
        "\n"
        "[SourceDisksFiles]\n"
        f"{source_files}\n"
        "\n"
        "[DestinationDirs]\n"
        f'CursorFiles=10,"Cursors\\{theme.key}"\n'
        "\n"
        "[CursorFiles]\n"
        f"{copy_files}\n"
        "\n"
        "[CursorScheme]\n"
        'HKCU,"Control Panel\\Cursors\\Schemes","%SchemeName%",'
        f'0x00000000,"{scheme_value}"\n'
        "\n"
        + "[ActiveCursors]\n"
        + "\n".join(active_cursor_values)
        + "\n\n"
        + "[Strings]\n"
        f'DiskName="{theme.label} Cursor Pack"\n'
        f'SchemeName="{theme.label}"\n'
    )


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        # Pillow added the size argument to load_default in version 10.1.
        return ImageFont.load_default()


def _draw_theme_preview(theme: Theme, output_path: Path) -> Image.Image:
    width = 354
    row_height = 58
    header_height = 94
    image = Image.new("RGB", (width, header_height + len(ROLE_ORDER) * row_height + 18), "#EEF1F6")
    draw = ImageDraw.Draw(image)
    title_font = _font(19)
    label_font = _font(12)
    small_font = _font(10)
    draw.text((18, 16), theme.label, fill="#151922", font=title_font)
    draw.text((18, 48), "48 px cursor previews on light and dark surfaces", fill="#4A5362", font=small_font)
    draw.text((225, 72), "LIGHT", fill="#394252", font=small_font)
    draw.text((282, 72), "DARK", fill="#394252", font=small_font)

    for index, role in enumerate(ROLE_ORDER):
        top = header_height + index * row_height
        draw.rounded_rectangle((12, top, width - 12, top + row_height - 4), radius=8, fill="#FFFFFF")
        draw.text((22, top + 21), role.label, fill="#202633", font=label_font)
        for x, background in ((222, "#F8FAFC"), (278, "#171A20")):
            draw.rounded_rectangle((x, top + 5, x + 48, top + 53), radius=6, fill=background)
            cursor, _ = render_cursor(role, theme, 48, frame=0)
            image.alpha_composite(cursor, (x, top + 5)) if image.mode == "RGBA" else image.paste(
                cursor, (x, top + 5), cursor
            )

    image.save(output_path, format="PNG", optimize=True)
    return image


def _draw_native_preview(output_path: Path) -> None:
    """Render exports at their actual 32px size on both background colors."""
    width, header, row = 750, 82, 42
    image = Image.new("RGB", (width, header + len(ROLE_ORDER)*row + 10), "#EEF1F6")
    draw = ImageDraw.Draw(image)
    draw.text((16, 12), "Actual 32 px cursor exports", fill="#151922", font=_font(17))
    draw.text((16, 37), "Each role fitted to a 24 px visible extent; light and dark surfaces", fill="#4A5362", font=_font(11))
    for column, theme in enumerate(THEMES.values()):
        x = 190 + column*138
        draw.text((x, 62), theme.label, fill="#151922", font=_font(10))
        for index, role in enumerate(ROLE_ORDER):
            y = header + index*row
            if column == 0:
                draw.text((16,y+13), role.label, fill="#202633", font=_font(11))
            for offset, background in ((0,"#F8FAFC"),(48,"#171A20")):
                draw.rounded_rectangle((x+offset,y,x+offset+40,y+38),radius=4,fill=background)
                cursor, _ = render_cursor(role,theme,32,frame=0)
                image.paste(cursor,(x+offset+4,y+3),cursor)
    image.save(output_path, optimize=True)


def build_theme(theme: Theme, output_dir: Path) -> list[Path]:
    """Write one complete scheme, its installer, install notes, and preview."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    filenames: list[str] = []
    for role in ROLE_ORDER:
        filename = cursor_filename(theme, role)
        path = output_dir / filename
        path.write_bytes(_role_cursor_bytes(role, theme))
        generated.append(path)
        filenames.append(filename)

    inf_path = output_dir / f"{theme.key}.inf"
    inf_path.write_text(_installer_text(theme, filenames), encoding="ascii", newline="\n")
    generated.append(inf_path)
    install_path = output_dir / "INSTALL.txt"
    install_path.write_text(INSTALL_TEXT, encoding="utf-8", newline="\n")
    generated.append(install_path)
    installer_dir = Path(__file__).resolve().parents[1] / "installer"
    for installer_name in ("Install-Wingline.cmd", "Install-Wingline.ps1"):
        installer_path = output_dir / installer_name
        shutil.copy2(installer_dir / installer_name, installer_path)
        generated.append(installer_path)
    preview_path = output_dir / "preview.png"
    _draw_theme_preview(theme, preview_path)
    generated.append(preview_path)
    return generated


def _archive_theme(archive: zipfile.ZipFile, theme: Theme, theme_dir: Path) -> None:
    for path in sorted(theme_dir.iterdir(), key=lambda item: item.name):
        if path.is_file():
            archive.write(path, f"{theme.key}/{path.name}")


def build_pack(output_root: Path) -> list[Path]:
    """Build both cursor schemes, their previews, and three ZIP archives."""
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    theme_dirs: dict[str, Path] = {}
    for theme in THEMES.values():
        theme_dir = output_root / theme.key
        if theme_dir.exists():
            shutil.rmtree(theme_dir)
        theme_dirs[theme.key] = theme_dir
        generated.extend(build_theme(theme, theme_dir))

    for theme in THEMES.values():
        archive_path = output_root / f"{theme.key}.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            _archive_theme(archive, theme, theme_dirs[theme.key])
        generated.append(archive_path)

    combined_path = output_root / "Wingline-Cursor-Pack.zip"
    with zipfile.ZipFile(combined_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for theme in THEMES.values():
            _archive_theme(archive, theme, theme_dirs[theme.key])
    generated.append(combined_path)

    previews = [Image.open(theme_dirs[theme.key] / "preview.png").convert("RGB") for theme in THEMES.values()]
    gutter = 18
    overview = Image.new(
        "RGB",
        (sum(preview.width for preview in previews) + gutter * (len(previews) + 1), max(p.height for p in previews) + 2 * gutter),
        "#DDE2EA",
    )
    x = gutter
    for preview in previews:
        overview.paste(preview, (x, gutter))
        x += preview.width + gutter
    preview_path = output_root / "preview.png"
    overview.save(preview_path, format="PNG", optimize=True)
    _draw_native_preview(output_root / "preview-32px.png")
    generated.append(preview_path)
    return generated


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _check_cur(data: bytes, expected_sizes: set[int]) -> None:
    _require(len(data) >= 6, "CUR is shorter than its directory header.")
    reserved, file_type, count = struct.unpack_from("<HHH", data, 0)
    _require((reserved, file_type) == (0, 2), "CUR header has an invalid type.")
    _require(count == len(expected_sizes), "CUR has the wrong number of images.")
    found_sizes: set[int] = set()
    for index in range(count):
        entry_offset = 6 + index * 16
        _require(entry_offset + 16 <= len(data), "CUR directory entry is truncated.")
        width, height, _, _, hot_x, hot_y, length, offset = struct.unpack_from(
            "<BBBBHHII", data, entry_offset
        )
        width = width or 256
        height = height or 256
        _require(width == height and width in expected_sizes, "CUR entry has an unexpected size.")
        _require(width not in found_sizes, "CUR contains duplicate image sizes.")
        _require(hot_x < width and hot_y < height, "CUR hotspot lies outside its image.")
        _require(offset >= 6 + 16 * count, "CUR image data overlaps the directory.")
        _require(length > 40 and offset + length <= len(data), "CUR image data is truncated.")
        dib_size, dib_width, doubled_height, planes, bit_count = struct.unpack_from(
            "<IiiHH", data, offset
        )
        _require(
            (dib_size, dib_width, doubled_height, planes, bit_count)
            == (40, width, height * 2, 1, 32),
            "CUR DIB header is invalid.",
        )
        xor_stride = ((width * bit_count + 31) // 32) * 4
        mask_stride = ((width + 31) // 32) * 4
        expected_length = dib_size + (xor_stride + mask_stride) * height
        _require(length == expected_length, "CUR pixel and mask data is truncated.")
        found_sizes.add(width)
    _require(found_sizes == expected_sizes, "CUR does not include every expected size.")


def _read_riff_chunks(data: bytes, start: int, end: int) -> list[tuple[bytes, bytes]]:
    chunks = []
    offset = start
    while offset < end:
        _require(offset + 8 <= end, "RIFF chunk header is truncated.")
        chunk_id = data[offset : offset + 4]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        payload_start = offset + 8
        payload_end = payload_start + size
        _require(payload_end <= end, "RIFF chunk data is truncated.")
        chunks.append((chunk_id, data[payload_start:payload_end]))
        offset = payload_end + (size & 1)
        _require(offset <= end, "RIFF chunk padding is truncated.")
    return chunks


def _check_ani(data: bytes) -> None:
    _require(len(data) >= 12 and data[:4] == b"RIFF", "ANI RIFF header is invalid.")
    _require(struct.unpack_from("<I", data, 4)[0] == len(data) - 8, "ANI RIFF length is invalid.")
    _require(data[8:12] == b"ACON", "ANI form type is not ACON.")
    chunks = _read_riff_chunks(data, 12, len(data))
    headers = [payload for chunk_id, payload in chunks if chunk_id == b"anih"]
    rates = [payload for chunk_id, payload in chunks if chunk_id == b"rate"]
    sequences = [payload for chunk_id, payload in chunks if chunk_id == b"seq "]
    frame_lists = [payload for chunk_id, payload in chunks if chunk_id == b"LIST"]
    _require(len(headers) == len(rates) == len(sequences) == len(frame_lists) == 1, "ANI chunks are incomplete.")
    _require(len(headers[0]) == 36, "ANI header size is invalid.")
    _, frame_count, step_count, width, height, bit_count, planes, _, flags = struct.unpack(
        "<9I", headers[0]
    )
    _require((frame_count, step_count, width, height, bit_count, planes, flags) == (8, 8, max(SUPPORTED_SIZES), max(SUPPORTED_SIZES), 32, 1, 3), "ANI header values are invalid.")
    _require(len(rates[0]) == 32 and len(sequences[0]) == 32, "ANI timing chunks have invalid lengths.")
    _require(struct.unpack("<8I", rates[0]) == (7,) * 8, "ANI frame rates are invalid.")
    _require(struct.unpack("<8I", sequences[0]) == tuple(range(8)), "ANI sequence is invalid.")
    frame_list = frame_lists[0]
    _require(frame_list[:4] == b"fram", "ANI frame list has an invalid type.")
    frames = _read_riff_chunks(frame_list, 4, len(frame_list))
    _require(len(frames) == 8 and all(chunk_id == b"icon" for chunk_id, _ in frames), "ANI frame list is invalid.")
    for _, frame in frames:
        _check_cur(frame, {max(SUPPORTED_SIZES)})


def _scheme_paths(inf_text: str) -> list[str]:
    section = re.search(r"(?ms)^\[CursorScheme\]\s*\n(.*?)(?=^\[|\Z)", inf_text)
    _require(section is not None, "INF is missing its CursorScheme section.")
    lines = [line.strip() for line in section.group(1).splitlines() if line.strip()]
    _require(len(lines) == 1, "INF must define exactly one CursorScheme value.")
    match = re.fullmatch(
        r'HKCU,"Control Panel\\Cursors\\Schemes","%SchemeName%",0x00000000,"(.*)"',
        lines[0],
    )
    _require(match is not None, "INF CursorScheme must be a quoted registry value.")
    return match.group(1).split(",")


def _active_cursor_settings(inf_text: str) -> dict[str, tuple[str, str]]:
    section = re.search(r"(?ms)^\[ActiveCursors\]\s*\n(.*?)(?=^\[|\Z)", inf_text)
    _require(section is not None, "INF is missing its ActiveCursors section.")
    settings: dict[str, tuple[str, str]] = {}
    for line in section.group(1).splitlines():
        if not line.strip():
            continue
        try:
            fields = next(csv.reader([line]))
        except csv.Error as error:
            raise ValueError("INF ActiveCursors entry is invalid.") from error
        _require(
            len(fields) == 5
            and fields[0] == "HKCU"
            and fields[1] == "Control Panel\\Cursors",
            "INF ActiveCursors entry is invalid.",
        )
        _require(fields[2] not in settings, "INF has duplicate active cursor values.")
        settings[fields[2]] = (fields[3], fields[4])
    return settings


def _copy_files(inf_text: str) -> list[str]:
    match = re.search(r"(?ms)^\[CursorFiles\]\s*\n(.*?)(?=^\[|\Z)", inf_text)
    _require(match is not None, "INF is missing its CursorFiles section.")
    return [line.strip() for line in match.group(1).splitlines() if line.strip()]


def _default_install_addreg_sections(inf_text: str) -> list[str]:
    section = re.search(r"(?ms)^\[DefaultInstall\]\s*\n(.*?)(?=^\[|\Z)", inf_text)
    _require(section is not None, "INF is missing its DefaultInstall section.")
    directives = [
        line.partition("=")[2]
        for line in section.group(1).splitlines()
        if line.partition("=")[0].strip().casefold() == "addreg"
    ]
    _require(len(directives) == 1, "INF must have one AddReg directive.")
    return [name.strip() for name in directives[0].split(",")]


def _expected_archive_entries(theme: Theme) -> set[str]:
    prefix = f"{theme.key}/"
    names = {
        prefix + f"{theme.key}.inf",
        prefix + "INSTALL.txt",
        prefix + "Install-Wingline.cmd",
        prefix + "Install-Wingline.ps1",
        prefix + "preview.png",
    }
    names.update(prefix + cursor_filename(theme, role) for role in ROLE_ORDER)
    return names


def _expected_archive_files(theme: Theme, theme_dir: Path) -> dict[str, Path]:
    prefix = f"{theme.key}/"
    return {
        archive_name: theme_dir / archive_name.removeprefix(prefix)
        for archive_name in _expected_archive_entries(theme)
    }


def _check_archive(archive_path: Path, expected_files: dict[str, Path]) -> None:
    _require(archive_path.is_file(), f"Archive is missing: {archive_path.name}.")
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        _require(archive.testzip() is None, f"Archive is corrupt: {archive_path.name}.")
        _require(
            len(names) == len(expected_files) and set(names) == set(expected_files),
            f"Archive has missing or unexpected files: {archive_path.name}.",
        )
        for name, source_path in expected_files.items():
            _require(
                archive.read(name) == source_path.read_bytes(),
                f"Archive member differs from built files: {name}.",
            )


def verify_pack(output_root: Path) -> bool:
    """Check role mappings, cursor binaries, previews, and ZIP integrity."""
    output_root = Path(output_root)
    _require((output_root / "preview.png").is_file(), "Combined preview is missing.")
    for theme in THEMES.values():
        theme_dir = output_root / theme.key
        _require(theme_dir.is_dir(), f"Theme output is missing: {theme.key}.")
        filenames = [cursor_filename(theme, role) for role in ROLE_ORDER]
        inf_path = theme_dir / f"{theme.key}.inf"
        _require(inf_path.is_file(), f"Installer is missing: {inf_path.name}.")
        inf_text = inf_path.read_text(encoding="ascii")
        _require(
            _default_install_addreg_sections(inf_text) == ["CursorScheme", "ActiveCursors"],
            f"{theme.key} installer does not apply its active cursor settings.",
        )
        expected_scheme_paths = [f"%10%\\Cursors\\{theme.key}\\{filename}" for filename in filenames]
        _require(
            _scheme_paths(inf_text) == expected_scheme_paths,
            f"{theme.key} role mapping order is wrong.",
        )
        expected_active_settings = {
            "": ("0x00000000", "%SchemeName%"),
            "Scheme Source": ("0x00010001", "1"),
        }
        expected_active_settings.update(
            {
                role.registry_value: (
                    "0x00000000",
                    f"%10%\\Cursors\\{theme.key}\\{filename}",
                )
                for role, filename in zip(ROLE_ORDER, filenames)
            }
        )
        _require(
            _active_cursor_settings(inf_text) == expected_active_settings,
            f"{theme.key} active cursor settings are incomplete.",
        )
        _require(_copy_files(inf_text) == filenames, f"{theme.key} copy list is wrong.")
        role_payloads: set[bytes] = set()
        for role, filename in zip(ROLE_ORDER, filenames):
            asset = theme_dir / filename
            _require(asset.is_file(), f"Installer references a missing cursor: {filename}.")
            payload = asset.read_bytes()
            _require(
                payload not in role_payloads,
                f"{theme.key} assigns identical cursor artwork to more than one role.",
            )
            role_payloads.add(payload)
            if role.key in ANIMATED_ROLES:
                _check_ani(payload)
            else:
                _check_cur(payload, set(SUPPORTED_SIZES))
        _require((theme_dir / "INSTALL.txt").is_file(), f"{theme.key} install notes are missing.")
        preview = theme_dir / "preview.png"
        _require(preview.is_file(), f"{theme.key} preview is missing.")
        with Image.open(preview) as image:
            image.verify()

        archive_path = output_root / f"{theme.key}.zip"
        _check_archive(archive_path, _expected_archive_files(theme, theme_dir))

    combined_path = output_root / "Wingline-Cursor-Pack.zip"
    combined_files = {}
    for theme in THEMES.values():
        combined_files.update(
            _expected_archive_files(theme, output_root / theme.key)
        )
    _check_archive(combined_path, combined_files)
    return True


def build(output_root: Path) -> list[Path]:
    """Build and validate all downloadable pack files."""
    generated = build_pack(output_root)
    verify_pack(output_root)
    return generated
