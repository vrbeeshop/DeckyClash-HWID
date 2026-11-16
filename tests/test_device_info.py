"""Exercise device discovery using temporary DMI files and mocked os-release."""

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "py_modules" / "device_info.py"


class DeviceInfoTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("device_info_under_test", MODULE_PATH)
        self.device_info = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.device_info)
        self.tmp = tempfile.TemporaryDirectory(prefix="deckyclash-dmi-test-")
        self.addCleanup(self.tmp.cleanup)
        self.dmi_dir = Path(self.tmp.name)
        self.device_info._DMI_DIR = self.dmi_dir
        release_patch = mock.patch.object(
            self.device_info.platform,
            "freedesktop_os_release",
            return_value={"NAME": "SteamOS", "VERSION_ID": "3.7.0"},
        )
        self.os_release = release_patch.start()
        self.addCleanup(release_patch.stop)

    def test_jupiter_reports_lcd_and_steamos_version(self):
        (self.dmi_dir / "product_name").write_text("Jupiter\n", encoding="utf-8")
        self.assertEqual(self.device_info.get_subscription_headers(), {
            "X-Device-Os": "Linux",
            "X-Ver-Os": "3.7.0",
            "X-Device-Model": "Steam Deck LCD",
        })

    def test_galileo_reports_oled_case_insensitively(self):
        (self.dmi_dir / "product_name").write_text("gAlIlEo\n", encoding="utf-8")
        self.assertEqual(
            self.device_info.get_subscription_headers()["X-Device-Model"],
            "Steam Deck OLED",
        )

    def test_board_name_is_used_when_product_name_is_unrecognized(self):
        (self.dmi_dir / "product_name").write_text("Unknown product", encoding="utf-8")
        (self.dmi_dir / "board_name").write_text("Jupiter", encoding="utf-8")
        self.assertEqual(
            self.device_info.get_subscription_headers()["X-Device-Model"],
            "Steam Deck LCD",
        )

    def test_missing_dmi_files_fall_back_to_steam_deck(self):
        self.assertEqual(
            self.device_info.get_subscription_headers()["X-Device-Model"],
            "Steam Deck",
        )

    def test_unrecognized_hardware_falls_back_to_steam_deck(self):
        (self.dmi_dir / "product_name").write_text("Other computer", encoding="utf-8")
        (self.dmi_dir / "board_name").write_text("Other board", encoding="utf-8")
        self.assertEqual(
            self.device_info.get_subscription_headers()["X-Device-Model"],
            "Steam Deck",
        )

    def test_oserror_reading_product_does_not_prevent_board_detection(self):
        # Reading a directory as a file raises an OSError on Linux, without
        # depending on test runner privileges or real sysfs permissions.
        (self.dmi_dir / "product_name").mkdir()
        (self.dmi_dir / "board_name").write_text("Galileo", encoding="utf-8")
        self.assertEqual(
            self.device_info.get_subscription_headers()["X-Device-Model"],
            "Steam Deck OLED",
        )

    def test_invalid_utf8_product_does_not_prevent_board_detection(self):
        (self.dmi_dir / "product_name").write_bytes(b"\xff\xfe")
        (self.dmi_dir / "board_name").write_text("Galileo", encoding="utf-8")
        self.assertEqual(
            self.device_info.get_subscription_headers()["X-Device-Model"],
            "Steam Deck OLED",
        )

    def test_missing_version_id_reports_unknown(self):
        self.os_release.return_value = {"NAME": "SteamOS"}
        self.assertEqual(
            self.device_info.get_subscription_headers()["X-Ver-Os"], "unknown",
        )

    def test_unavailable_os_release_reports_unknown(self):
        self.os_release.side_effect = OSError("os-release is unavailable")
        self.assertEqual(
            self.device_info.get_subscription_headers()["X-Ver-Os"], "unknown",
        )

    def test_version_id_whitespace_is_trimmed(self):
        self.os_release.return_value = {"VERSION_ID": " 3.7.0 \n"}
        self.assertEqual(
            self.device_info.get_subscription_headers()["X-Ver-Os"], "3.7.0",
        )

    def test_empty_non_ascii_and_control_versions_report_unknown(self):
        for version in ("", "  ", "3.7.0\nInjected: value", "3.7\r0", "3.7\x000", "3.7\t0", "3.7\x7f", "версия3.7"):
            with self.subTest(version=repr(version)):
                self.os_release.return_value = {"VERSION_ID": version}
                self.assertEqual(
                    self.device_info.get_subscription_headers()["X-Ver-Os"], "unknown",
                )


if __name__ == "__main__":
    unittest.main()
