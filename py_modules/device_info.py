"""Device metadata sent with subscription requests on Steam Deck."""

from pathlib import Path
import platform
from typing import Dict


_DMI_DIR = Path("/sys/class/dmi/id")
_DECK_MODELS = {
    "jupiter": "Steam Deck LCD",
    "galileo": "Steam Deck OLED",
}


def _device_model() -> str:
    for field in ("product_name", "board_name"):
        try:
            product = (_DMI_DIR / field).read_text(encoding="utf-8").strip().casefold()
        except (OSError, UnicodeError):
            continue
        model = _DECK_MODELS.get(product)
        if model is not None:
            return model
    return "Steam Deck"


def _os_version() -> str:
    try:
        version = platform.freedesktop_os_release().get("VERSION_ID", "").strip()
    except (OSError, UnicodeError):
        return "unknown"
    # Keep malformed release metadata from breaking an otherwise valid request.
    if version and version.isascii() and all(32 <= ord(char) < 127 for char in version):
        return version
    return "unknown"


def get_subscription_headers() -> Dict[str, str]:
    return {
        "X-Device-Os": "Linux",
        "X-Ver-Os": _os_version(),
        "X-Device-Model": _device_model(),
    }
