"""VIDAA remote text and mouse input helpers (MITM capture 2026-07-29)."""

from __future__ import annotations

import time
from typing import Any

# actions/input special tokens observed from the official VIDAA remote app.
_INPUT_SPECIAL: dict[str, str] = {
    " ": "Lit_SPACE",
    "\n": "Lit_ENTER",
    "\r": "Lit_ENTER",
    "\b": "Lit_BACKSPACE",
    "\x7f": "Lit_BACKSPACE",
}


def encode_mouse_rel(dx: int, dy: int) -> str:
    """Encode a relative pointer delta as ``REL_<dx>_<dy>`` (signed 16-bit hex)."""
    return f"REL_{dx & 0xFFFF:04x}_{dy & 0xFFFF:04x}"


def input_literal(char: str) -> str:
    """Map one character to an ``actions/input`` MQTT payload."""
    if not char:
        raise ValueError("empty character")
    if char in _INPUT_SPECIAL:
        return _INPUT_SPECIAL[char]
    if char == ".":
        return "Lit_."
    if char.isalpha():
        return f"Lit_{char.lower()}"
    if char.isdigit():
        return f"Lit_{char}"
    if len(char) == 1 and char.isprintable():
        return f"Lit_{char}"
    raise ValueError(f"unsupported input character {char!r}")


def build_changesource_payload(entry: dict[str, Any]) -> dict[str, Any]:
    """Build a ``changesource`` payload like the VIDAA mobile app."""
    source_id = str(entry.get("sourceid", ""))
    sourcename = str(entry.get("sourcename") or entry.get("displayname") or source_id)
    displayname = str(entry.get("displayname") or sourcename)
    return {
        "has_signal": int(entry.get("has_signal", 1)),
        "displayname2": str(entry.get("displayname2", "")),
        "httpIcon": str(entry.get("httpIcon", "")),
        "sourcename": sourcename,
        "is_signal": int(entry.get("is_signal", 0)),
        "sourceid": source_id,
        "displayname": displayname,
    }


def send_text_literals(
    publish: Any,
    topic: str,
    text: str,
    *,
    delay: float = 0.12,
) -> None:
    """Publish ``actions/input`` for each character in ``text``."""
    for char in text:
        publish(topic, input_literal(char))
        if delay:
            time.sleep(delay)
