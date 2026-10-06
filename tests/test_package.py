import csv
import re
import shutil
import struct
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path, PureWindowsPath
from unittest.mock import call, patch

import build
from PIL import ImageFont

from wingline.package import _font, build_pack, verify_pack
from wingline.roles import ROLE_ORDER, THEMES


def expected_cursor_files(theme):
    files = []
    for role in ROLE_ORDER:
        extension = ".ani" if role.key in {"appstarting", "wait"} else ".cur"
        files.append(f"{theme.key}-{role.key}{extension}")
    return files


def read_scheme_paths(inf_text):
    match = re.search(
        r'(?ms)^\[CursorScheme\]\s*\nHKCU,"Control Panel\\Cursors\\Schemes",'
        r'"%SchemeName%",0x00000000,"([^"]*)"\s*$',
        inf_text,
    )
    if match is None:
        raise AssertionError("INF must define a literal quoted cursor scheme value.")
    return match.group(1).split(",")


def read_active_settings(inf_text):
    match = re.search(r"(?ms)^\[ActiveCursors\]\s*\n(.*?)(?=^\[|\Z)", inf_text)
    if match is None:
        raise AssertionError("INF must define active cursor settings.")
    settings = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        row = next(csv.reader([line]))
        if len(row) != 5 or row[0] != "HKCU" or row[1] != "Control Panel\\Cursors":
            raise AssertionError(f"Invalid active cursor setting: {line}")
        settings[row[2]] = (row[3], row[4])
    return settings


def read_copy_files(inf_text):
    match = re.search(r"(?ms)^\[CursorFiles\]\s*\n(.*?)(?=^\[|\Z)", inf_text)
    if match is None:
        raise AssertionError("INF must define a CursorFiles section.")
    return [line.strip() for line in match.group(1).splitlines() if line.strip()]


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary_directory = tempfile.TemporaryDirectory()
        cls.output_root = Path(cls.temporary_directory.name)
        build_pack(cls.output_root)

    @classmethod
    def tearDownClass(cls):
        cls.temporary_directory.cleanup()

    def test_each_installer_maps_all_roles_in_windows_order(self):
        for theme in THEMES.values():
            with self.subTest(theme=theme.key):
                theme_dir = self.output_root / theme.key
                inf_path = theme_dir / f"{theme.key}.inf"
                inf_text = inf_path.read_text(encoding="utf-8")

                scheme_paths = read_scheme_paths(inf_text)
                filenames = [PureWindowsPath(path).name for path in scheme_paths]

                self.assertEqual(expected_cursor_files(theme), filenames)
                self.assertEqual(17, len(filenames))
                self.assertTrue(
                    all(
                        path.startswith(f"%10%\\Cursors\\{theme.key}\\")
                        for path in scheme_paths
                    )
                )
                for filename in filenames:
                    self.assertTrue((theme_dir / filename).is_file(), filename)

    def test_installers_select_the_scheme_and_set_every_active_cursor_role(self):
        registry_values = {
            "arrow": "Arrow",
            "help": "Help",
            "appstarting": "AppStarting",
            "wait": "Wait",
            "crosshair": "Crosshair",
            "ibeam": "IBeam",
            "nwpen": "NWPen",
            "no": "No",
            "sizens": "SizeNS",
            "sizewe": "SizeWE",
            "sizenwse": "SizeNWSE",
            "sizenesw": "SizeNESW",
            "sizeall": "SizeAll",
            "uparrow": "UpArrow",
            "hand": "Hand",
            "pin": "Pin",
            "person": "Person",
        }
        for theme in THEMES.values():
            with self.subTest(theme=theme.key):
                inf_text = (self.output_root / theme.key / f"{theme.key}.inf").read_text(
                    encoding="ascii"
                )
                settings = read_active_settings(inf_text)

                self.assertEqual(("0x00000000", "%SchemeName%"), settings[""])
                self.assertEqual(("0x00010001", "1"), settings["Scheme Source"])
                self.assertEqual(17, len(settings) - 2)
                for role in ROLE_ORDER:
                    extension = ".ani" if role.key in {"appstarting", "wait"} else ".cur"
                    filename = f"{theme.key}-{role.key}{extension}"
                    self.assertEqual(
                        (
                            "0x00000000",
                            f"%10%\\Cursors\\{theme.key}\\{filename}",
                        ),
                        settings[registry_values[role.key]],
                    )

    def test_one_click_installer_reapplies_registered_cursors_idempotently(self):
        installer = (Path(__file__).resolve().parents[1] / "installer" / "Install-Wingline.ps1").read_text(
            encoding="utf-8"
        )

        self.assertIn("Copy-Item -LiteralPath $matches.FullName -Destination $destination -Force", installer)
        self.assertIn("$cursorKey.SetValue($entry.Key, $destination", installer)
        self.assertIn("SystemParametersInfo(0x0057", installer)
        self.assertIn("was reapplied and is active", installer)

    def test_verifier_rejects_an_installer_with_unexpanded_dirid(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_root = Path(temporary_directory) / "dist"
            shutil.copytree(self.output_root, output_root)
            inf_path = output_root / "Wingline-White" / "Wingline-White.inf"
            inf_text = inf_path.read_text(encoding="ascii")
            inf_path.write_text(
                inf_text.replace(
                    "%10%\\Cursors\\Wingline-White\\Wingline-White-arrow.cur",
                    "%%10%%\\Cursors\\Wingline-White\\Wingline-White-arrow.cur",
                ),
                encoding="ascii",
            )

            with self.assertRaisesRegex(ValueError, "role mapping order"):
                verify_pack(output_root)

    def test_installer_copy_list_contains_every_mapped_file_once(self):
        for theme in THEMES.values():
            with self.subTest(theme=theme.key):
                inf_text = (self.output_root / theme.key / f"{theme.key}.inf").read_text(
                    encoding="utf-8"
                )
                copy_files = read_copy_files(inf_text)

                self.assertEqual(expected_cursor_files(theme), copy_files)
                self.assertEqual(len(copy_files), len(set(copy_files)))

    def test_all_archives_contain_their_assets_and_pass_integrity_checks(self):
        expected_combined = set()
        for theme in THEMES.values():
            archive_path = self.output_root / f"{theme.key}.zip"
            with zipfile.ZipFile(archive_path) as archive:
                self.assertIsNone(archive.testzip())
                names = set(archive.namelist())
                prefix = f"{theme.key}/"
                expected = {
                    prefix + f"{theme.key}.inf",
                    prefix + "INSTALL.txt",
                    prefix + "Install-Wingline.cmd",
                    prefix + "Install-Wingline.ps1",
                    prefix + "preview.png",
                    *(prefix + filename for filename in expected_cursor_files(theme)),
                }
                self.assertTrue(expected <= names)
                expected_combined.update(expected)

        combined_path = self.output_root / "Wingline-Cursor-Pack.zip"
        with zipfile.ZipFile(combined_path) as archive:
            self.assertIsNone(archive.testzip())
            self.assertTrue(expected_combined <= set(archive.namelist()))
        self.assertTrue((self.output_root / "preview.png").is_file())
        self.assertTrue(verify_pack(self.output_root))

    def test_build_check_command_verifies_the_existing_pack(self):
        previous_output_dir = build.OUTPUT_DIR
        output = StringIO()
        try:
            build.OUTPUT_DIR = self.output_root
            with redirect_stdout(output):
                result = build.main(["--check"])
        finally:
            build.OUTPUT_DIR = previous_output_dir

        self.assertEqual(0, result)
        self.assertIn("verified", output.getvalue())

    def test_verifier_rejects_archive_content_that_differs_from_built_files(self):
        cases = (
            ("Wingline-White.zip", "Wingline-White/Wingline-White.inf"),
            ("Wingline-Cursor-Pack.zip", "Wingline-White/Wingline-White-arrow.cur"),
        )
        for archive_name, member_name in cases:
            with self.subTest(archive=archive_name, member=member_name):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    output_root = Path(temporary_directory) / "dist"
                    shutil.copytree(self.output_root, output_root)
                    archive_path = output_root / archive_name
                    replacement_path = archive_path.with_suffix(".rewritten.zip")
                    with zipfile.ZipFile(archive_path) as source, zipfile.ZipFile(
                        replacement_path, "w", compression=zipfile.ZIP_DEFLATED
                    ) as replacement:
                        for info in source.infolist():
                            data = source.read(info.filename)
                            if info.filename == member_name:
                                data += b"\ncorrupted after packaging\n"
                            replacement.writestr(info, data)
                    replacement_path.replace(archive_path)

                    with self.assertRaisesRegex(ValueError, "differs from built files"):
                        verify_pack(output_root)

    def test_verifier_rejects_a_cursor_with_a_truncated_mask(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_root = Path(temporary_directory) / "dist"
            shutil.copytree(self.output_root, output_root)
            cursor_path = output_root / "Wingline-White" / "Wingline-White-arrow.cur"
            data = bytearray(cursor_path.read_bytes())
            image_count = struct.unpack_from("<H", data, 4)[0]
            last_entry = 6 + (image_count - 1) * 16
            data_length, data_offset = struct.unpack_from("<II", data, last_entry + 8)
            self.assertEqual(data_offset + data_length, len(data))
            struct.pack_into("<I", data, last_entry + 8, data_length - 1)
            cursor_path.write_bytes(data[:-1])

            with self.assertRaisesRegex(ValueError, "pixel and mask data"):
                verify_pack(output_root)

    def test_preview_font_supports_pillow_10_0_default_font_signature(self):
        fallback_font = ImageFont.load_default()
        with patch(
            "wingline.package.ImageFont.load_default",
            side_effect=[TypeError("size is not supported"), fallback_font],
        ) as load_default:
            font = _font(18)

        self.assertIs(fallback_font, font)
        self.assertEqual([call(size=18), call()], load_default.call_args_list)


if __name__ == "__main__":
    unittest.main()
