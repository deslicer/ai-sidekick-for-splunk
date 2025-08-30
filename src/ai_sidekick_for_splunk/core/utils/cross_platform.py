"""Cross-platform utilities for handling encoding and output."""

import sys
from typing import Any


def safe_print(*args: Any, **kwargs: Any) -> None:
    """Print function that handles Unicode characters safely across platforms.

    On Windows, this falls back to ASCII-safe alternatives for Unicode characters
    that can't be encoded in the default console encoding.
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback for Windows systems that can't handle Unicode
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # Replace common Unicode characters with ASCII alternatives
                safe_arg = (
                    arg.replace("✅", "[OK]")
                    .replace("❌", "[ERROR]")
                    .replace("🎉", "[SUCCESS]")
                    .replace("🚀", "[ROCKET]")
                    .replace("📁", "[FOLDER]")
                    .replace("📄", "[FILE]")
                    .replace("📖", "[DOC]")
                    .replace("🔍", "[SEARCH]")
                    .replace("💓", "[HEART]")
                    .replace("📊", "[CHART]")
                    .replace("📋", "[CLIPBOARD]")
                    .replace("🎯", "[TARGET]")
                    .replace("🔧", "[WRENCH]")
                    .replace("⚙️", "[GEAR]")
                    .replace("🌟", "[STAR]")
                    .replace("💡", "[BULB]")
                    .replace("🔒", "[LOCK]")
                    .replace("🎪", "[CIRCUS]")
                    .replace("🎓", "[GRADUATION]")
                    .replace("1️⃣", "1.")
                    .replace("2️⃣", "2.")
                    .replace("3️⃣", "3.")
                    .replace("4️⃣", "4.")
                    .replace("├──", "|-")
                    .replace("└──", "\\-")
                )
                safe_args.append(safe_arg)
            else:
                safe_args.append(str(arg))

        print(*safe_args, **kwargs)


def get_console_encoding() -> str:
    """Get the console encoding, with fallback for Windows."""
    if sys.platform == "win32":
        # Try to get Windows console encoding
        try:
            import locale

            return locale.getpreferredencoding()
        except Exception:
            return "cp1252"  # Common Windows encoding fallback
    return "utf-8"


def is_unicode_supported() -> bool:
    """Check if the current console supports Unicode characters."""
    try:
        # Test with a simple Unicode character
        sys.stdout.write("✅")
        sys.stdout.flush()
        return True
    except UnicodeEncodeError:
        return False
