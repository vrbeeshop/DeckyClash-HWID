"""Run with: python3 -m unittest discover -s tests -v.

The HTTP requests and subscription file handling are real. Only the Decky runtime
and Mihomo executable are replaced so these regressions can run on ordinary WSL.
"""

import asyncio
import importlib.util
import logging
from pathlib import Path
import ssl
import sys
import tempfile
import threading
import types
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock


MODULES_DIR = Path(__file__).resolve().parents[1] / "py_modules"
HWID = "a618df94-a771-48c7-a2ae-d21104081e8a"
WORKING_CONFIG = (
    b"proxies:\n"
    b"  - name: Working proxy\n"
    b"    type: socks5\n"
    b"    server: 127.0.0.1\n"
    b"    port: 1080\n"
)
# A syntactically valid fallback must be rejected by its response headers, before
# Mihomo validation can accept it as an ordinary profile.
FALLBACK_CONFIG = (
    b"proxies:\n"
    b"  - name: Maximum device limit reached\n"
    b"    type: vless\n"
    b"    server: 0.0.0.0\n"
    b"    port: 1\n"
    b"    uuid: 00000000-0000-0000-0000-000000000000\n"
    b"    network: tcp\n"
)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class SubscriptionHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.requests.append(dict(self.headers.items()))
        status, headers, body = self.server.response
        self.send_response(status)
        self.send_header("Content-Type", "application/yaml")
        self.send_header("Content-Disposition", 'attachment; filename="profile.yaml"')
        self.send_header("Content-Length", str(len(body)))
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class SubscriptionHwidTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), SubscriptionHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="deckyclash-hwid-test-")
        self.addCleanup(self.tmp.cleanup)

        decky = types.ModuleType("decky")
        decky.DECKY_PLUGIN_SETTINGS_DIR = self.tmp.name
        decky.DECKY_PLUGIN_VERSION = "test"
        decky.logger = mock.Mock(spec=logging.Logger)
        core = types.ModuleType("core")
        core.LAST_CORE_VERSION = "test"
        self.check_config = mock.Mock(return_value=True)
        core.CoreController = types.SimpleNamespace(check_config=self.check_config)
        # aiohttp belongs to unrelated helpers in utils; the code under test uses
        # urllib against the local server and does not require an aiohttp install.
        modules = mock.patch.dict(sys.modules, {
            "decky": decky,
            "core": core,
            "aiohttp": types.ModuleType("aiohttp"),
        })
        modules.start()
        self.addCleanup(modules.stop)
        load_module("metadata", MODULES_DIR / "metadata.py")
        utils = load_module("utils", MODULES_DIR / "utils.py")
        utils._ssl_context = ssl.create_default_context()
        self.subscription = load_module("subscription", MODULES_DIR / "subscription.py")

        self.subscriptions_dir = Path(self.subscription.SUBSCRIPTIONS_DIR)
        self.subscriptions_dir.mkdir()
        self.existing = Path(self.subscription.get_path("existing"))
        self.existing.write_bytes(WORKING_CONFIG)
        self.server.requests = []
        self.server.response = (200, {}, FALLBACK_CONFIG)
        self.url = f"http://127.0.0.1:{self.server.server_port}/subscription"

    def assert_rejected(self, operation, header, expected_code):
        for status in (200, 404):
            with self.subTest(operation=operation, status=status, header=header):
                self.check_config.reset_mock()
                self.server.response = (
                    status,
                    {header: "  TrUe  "},
                    FALLBACK_CONFIG,
                )
                if operation == "download":
                    result = self.subscription.download_sub(self.url, {}, 3, hwid=HWID)
                    self.assertEqual(result, (False, expected_code))
                else:
                    result = asyncio.run(self.subscription.update_sub(
                        "existing", self.url, 3, hwid=HWID,
                    ))
                    self.assertEqual(result, expected_code)

                self.check_config.assert_not_called()
                self.assertEqual(self.existing.read_bytes(), WORKING_CONFIG)
                self.assertEqual(
                    sorted(path.name for path in self.subscriptions_dir.iterdir()),
                    ["existing.yaml"],
                    "Rejected responses must not leave a profile or temporary file",
                )

    def test_download_reports_device_limit_on_success_and_error_status(self):
        self.assert_rejected(
            "download", "X-HwId-Max-Devices-Reached", "HWID_MAX_DEVICES_REACHED",
        )

    def test_update_reports_device_limit_and_preserves_profile(self):
        self.assert_rejected(
            "update", "X-HwId-Max-Devices-Reached", "HWID_MAX_DEVICES_REACHED",
        )

    def test_download_hides_unsupported_hwid_details(self):
        self.assert_rejected(
            "download", "X-HwId-Not-Supported", "SUBSCRIPTION_REQUEST_FAILED",
        )

    def test_update_hides_unsupported_hwid_details_and_preserves_profile(self):
        self.assert_rejected(
            "update", "X-HwId-Not-Supported", "SUBSCRIPTION_REQUEST_FAILED",
        )

    def test_download_handles_generic_hwid_limit(self):
        self.assert_rejected(
            "download", "X-HwId-Limit", "SUBSCRIPTION_REQUEST_FAILED",
        )

    def test_update_handles_generic_hwid_limit_and_preserves_profile(self):
        self.assert_rejected(
            "update", "X-HwId-Limit", "SUBSCRIPTION_REQUEST_FAILED",
        )

    def test_specific_device_limit_takes_precedence_over_generic_flags(self):
        self.server.response = (200, {
            "x-hwid-not-supported": "true",
            "x-hwid-max-devices-reached": "true",
            "x-hwid-limit": "true",
        }, FALLBACK_CONFIG)
        self.assertEqual(
            self.subscription.download_sub(self.url, {}, 3, hwid=HWID),
            (False, "HWID_MAX_DEVICES_REACHED"),
        )
        self.check_config.assert_not_called()

    def test_normal_download_and_update_send_same_hwid(self):
        user_agent = "DeckyClash-test/1.0"
        result = self.subscription.download_sub(
            self.url, {}, 3, user_agent=user_agent, hwid=HWID,
        )
        self.assertEqual(result, (True, ("profile", self.url)))
        self.assertEqual(
            Path(self.subscription.get_path("profile")).read_bytes(), FALLBACK_CONFIG,
        )
        self.assertIsNone(asyncio.run(self.subscription.update_sub(
            "existing", self.url, 3, user_agent=user_agent, hwid=HWID,
        )))
        self.assertEqual(self.existing.read_bytes(), FALLBACK_CONFIG)
        self.assertEqual(self.check_config.call_count, 2)
        self.assertEqual(len(self.server.requests), 2)
        for headers in self.server.requests:
            normalized = {name.lower(): value for name, value in headers.items()}
            self.assertEqual(normalized["x-hwid"], HWID)
            self.assertEqual(normalized["user-agent"], user_agent)
        self.assertEqual(
            sorted(path.name for path in self.subscriptions_dir.iterdir()),
            ["existing.yaml", "profile.yaml"],
        )

    def test_optional_hwid_does_not_break_existing_callers(self):
        self.assertTrue(self.subscription.download_sub(self.url, {}, 3)[0])
        self.assertIsNone(asyncio.run(self.subscription.update_sub(
            "existing", self.url, 3,
        )))
        for headers in self.server.requests:
            self.assertNotIn("x-hwid", {name.lower() for name in headers})

    def test_false_error_flags_do_not_reject_a_profile(self):
        self.server.response = (200, {
            "x-hwid-active": "true",
            "x-hwid-not-supported": "false",
            "x-hwid-max-devices-reached": "false",
            "x-hwid-limit": "false",
        }, FALLBACK_CONFIG)
        self.assertTrue(self.subscription.download_sub(self.url, {}, 3, hwid=HWID)[0])

    def test_empty_update_preserves_existing_profile_and_cleans_temp_file(self):
        self.server.response = (200, {}, b"")
        self.check_config.return_value = False
        result = asyncio.run(self.subscription.update_sub(
            "existing", self.url, 3, hwid=HWID,
        ))
        self.assertEqual(result, "Invalid config")
        self.assertEqual(self.existing.read_bytes(), WORKING_CONFIG)
        self.assertEqual(list(self.subscriptions_dir.iterdir()), [self.existing])


if __name__ == "__main__":
    unittest.main()
