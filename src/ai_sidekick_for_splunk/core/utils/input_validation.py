"""
Secure input validation utilities for AI Sidekick for Splunk.

This module provides comprehensive input validation and sanitization
to protect against injection attacks and other security vulnerabilities.
"""

import logging
import re
import string
from pathlib import Path
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)


class InputValidationError(Exception):
    """Raised when input validation fails."""

    pass


class SecureInputValidator:
    """
    Secure input validation and sanitization utilities.

    This class provides methods to safely validate and sanitize user input
    to prevent injection attacks, path traversal, and other security issues.
    """

    # Safe characters for different input types
    SAFE_FILENAME_CHARS = string.ascii_letters + string.digits + "-_."
    SAFE_PATH_CHARS = string.ascii_letters + string.digits + "-_./"
    SAFE_IDENTIFIER_CHARS = string.ascii_letters + string.digits + "_"
    SAFE_URL_CHARS = string.ascii_letters + string.digits + "-._~:/?#[]@!$&'()*+,;="

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r"\.\./",  # Directory traversal
        r"\.\.\\",  # Windows directory traversal
        r"/etc/",  # System file access
        r"/proc/",  # Process information
        r"/sys/",  # System information
        r"C:\\Windows",  # Windows system directory
        r"C:\\System32",  # Windows system directory
        r"<script",  # XSS attempt
        r"javascript:",  # JavaScript injection
        r"data:",  # Data URI injection
        r"vbscript:",  # VBScript injection
        r"[;&|`$()]",  # Shell metacharacters
        r"eval\s*\(",  # Code evaluation
        r"exec\s*\(",  # Code execution
        r"import\s+os",  # OS module import
        r"import\s+subprocess",  # Subprocess import
        r"__import__",  # Dynamic import
    ]

    @classmethod
    def validate_filename(cls, filename: str, max_length: int = 255) -> str:
        """
        Validate and sanitize a filename.

        Args:
            filename: The filename to validate
            max_length: Maximum allowed length

        Returns:
            Sanitized filename

        Raises:
            InputValidationError: If validation fails
        """
        if not filename:
            raise InputValidationError("Filename cannot be empty")

        if len(filename) > max_length:
            raise InputValidationError(f"Filename too long (max {max_length} characters)")

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, filename, re.IGNORECASE):
                raise InputValidationError(f"Dangerous pattern detected in filename: {pattern}")

        # Remove unsafe characters
        safe_filename = "".join(c for c in filename if c in cls.SAFE_FILENAME_CHARS)

        if not safe_filename:
            raise InputValidationError("Filename contains no safe characters")

        # Prevent reserved names
        reserved_names = [
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        ]

        if safe_filename.upper() in reserved_names:
            raise InputValidationError(f"Reserved filename not allowed: {safe_filename}")

        logger.debug(f"Validated filename: {filename} -> {safe_filename}")
        return safe_filename

    @classmethod
    def validate_path(
        cls, path: Union[str, Path], must_exist: bool = False, must_be_relative: bool = True
    ) -> Path:
        """
        Validate and sanitize a file path.

        Args:
            path: The path to validate
            must_exist: Whether the path must exist
            must_be_relative: Whether the path must be relative

        Returns:
            Validated Path object

        Raises:
            InputValidationError: If validation fails
        """
        if not path:
            raise InputValidationError("Path cannot be empty")

        path_str = str(path)

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, path_str, re.IGNORECASE):
                raise InputValidationError(f"Dangerous pattern detected in path: {pattern}")

        # Convert to Path object
        try:
            path_obj = Path(path_str)
        except Exception as e:
            raise InputValidationError(f"Invalid path format: {e}")

        # Check if path is absolute when it shouldn't be
        if must_be_relative and path_obj.is_absolute():
            raise InputValidationError("Absolute paths not allowed")

        # Resolve path to check for traversal attempts
        try:
            resolved_path = path_obj.resolve()
        except Exception as e:
            raise InputValidationError(f"Cannot resolve path: {e}")

        # Check if path exists when required
        if must_exist and not resolved_path.exists():
            raise InputValidationError(f"Path does not exist: {path_str}")

        logger.debug(f"Validated path: {path_str}")
        return path_obj

    @classmethod
    def validate_identifier(cls, identifier: str, max_length: int = 100) -> str:
        """
        Validate a Python-style identifier (variable name, function name, etc.).

        Args:
            identifier: The identifier to validate
            max_length: Maximum allowed length

        Returns:
            Validated identifier

        Raises:
            InputValidationError: If validation fails
        """
        if not identifier:
            raise InputValidationError("Identifier cannot be empty")

        if len(identifier) > max_length:
            raise InputValidationError(f"Identifier too long (max {max_length} characters)")

        # Check if it's a valid Python identifier
        if not identifier.isidentifier():
            raise InputValidationError("Invalid identifier format")

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, identifier, re.IGNORECASE):
                raise InputValidationError(f"Dangerous pattern detected in identifier: {pattern}")

        # Check for Python keywords
        import keyword

        if keyword.iskeyword(identifier):
            raise InputValidationError(f"Python keyword not allowed as identifier: {identifier}")

        logger.debug(f"Validated identifier: {identifier}")
        return identifier

    @classmethod
    def validate_text_input(
        cls, text: str, max_length: int = 10000, allow_multiline: bool = True
    ) -> str:
        """
        Validate general text input.

        Args:
            text: The text to validate
            max_length: Maximum allowed length
            allow_multiline: Whether to allow newlines

        Returns:
            Validated text

        Raises:
            InputValidationError: If validation fails
        """
        if not isinstance(text, str):
            raise InputValidationError("Input must be a string")

        if len(text) > max_length:
            raise InputValidationError(f"Text too long (max {max_length} characters)")

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                raise InputValidationError(f"Dangerous pattern detected in text: {pattern}")

        # Check for newlines if not allowed
        if not allow_multiline and "\n" in text:
            raise InputValidationError("Multiline text not allowed")

        # Remove null bytes and other control characters (except newlines and tabs)
        cleaned_text = "".join(c for c in text if ord(c) >= 32 or c in "\n\t")

        logger.debug(f"Validated text input ({len(cleaned_text)} chars)")
        return cleaned_text

    @classmethod
    def validate_url(cls, url: str, allowed_schemes: Optional[list[str]] = None) -> str:
        """
        Validate a URL.

        Args:
            url: The URL to validate
            allowed_schemes: List of allowed URL schemes (default: ['http', 'https'])

        Returns:
            Validated URL

        Raises:
            InputValidationError: If validation fails
        """
        if not url:
            raise InputValidationError("URL cannot be empty")

        if allowed_schemes is None:
            allowed_schemes = ["http", "https"]

        # Basic URL format check
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if not url_pattern.match(url):
            raise InputValidationError("Invalid URL format")

        # Check scheme
        scheme = url.split("://")[0].lower()
        if scheme not in allowed_schemes:
            raise InputValidationError(f"URL scheme '{scheme}' not allowed")

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                raise InputValidationError(f"Dangerous pattern detected in URL: {pattern}")

        logger.debug(f"Validated URL: {url}")
        return url

    @classmethod
    def sanitize_for_logging(cls, data: Any) -> str:
        """
        Sanitize data for safe logging.

        Args:
            data: The data to sanitize

        Returns:
            Sanitized string representation
        """
        if isinstance(data, dict):
            # Mask sensitive keys
            sensitive_keys = ["password", "token", "key", "secret", "auth"]
            sanitized = {}
            for k, v in data.items():
                if any(sensitive in k.lower() for sensitive in sensitive_keys):
                    sanitized[k] = "***MASKED***"
                else:
                    sanitized[k] = cls.sanitize_for_logging(v)
            return str(sanitized)
        elif isinstance(data, list | tuple):
            return str([cls.sanitize_for_logging(item) for item in data])
        else:
            data_str = str(data)
            # Mask potential secrets in strings
            if any(
                keyword in data_str.lower() for keyword in ["password", "token", "key", "secret"]
            ):
                return "***POTENTIALLY_SENSITIVE***"
            return data_str[:1000]  # Limit length for logging


# Convenience functions for common validation tasks
def safe_input(prompt: str, max_length: int = 1000, allow_empty: bool = False) -> str:
    """
    Get safe user input with validation.

    Args:
        prompt: The input prompt
        max_length: Maximum input length
        allow_empty: Whether to allow empty input

    Returns:
        Validated user input
    """
    while True:
        try:
            user_input = input(prompt).strip()

            if not user_input and not allow_empty:
                print("Input cannot be empty. Please try again.")
                continue

            if not user_input and allow_empty:
                return ""

            validated_input = SecureInputValidator.validate_text_input(
                user_input, max_length=max_length, allow_multiline=False
            )
            return validated_input

        except InputValidationError as e:
            print(f"Invalid input: {e}. Please try again.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            raise
        except EOFError:
            print("\nEnd of input reached.")
            return ""


def safe_filename_input(prompt: str, max_length: int = 255) -> str:
    """
    Get safe filename input with validation.

    Args:
        prompt: The input prompt
        max_length: Maximum filename length

    Returns:
        Validated filename
    """
    while True:
        try:
            filename = input(prompt).strip()

            if not filename:
                print("Filename cannot be empty. Please try again.")
                continue

            validated_filename = SecureInputValidator.validate_filename(filename, max_length)
            return validated_filename

        except InputValidationError as e:
            print(f"Invalid filename: {e}. Please try again.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            raise
        except EOFError:
            print("\nEnd of input reached.")
            return ""


def safe_path_input(prompt: str, must_exist: bool = False, must_be_relative: bool = True) -> Path:
    """
    Get safe path input with validation.

    Args:
        prompt: The input prompt
        must_exist: Whether the path must exist
        must_be_relative: Whether the path must be relative

    Returns:
        Validated Path object
    """
    while True:
        try:
            path_str = input(prompt).strip()

            if not path_str:
                print("Path cannot be empty. Please try again.")
                continue

            validated_path = SecureInputValidator.validate_path(
                path_str, must_exist=must_exist, must_be_relative=must_be_relative
            )
            return validated_path

        except InputValidationError as e:
            print(f"Invalid path: {e}. Please try again.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            raise
        except EOFError:
            print("\nEnd of input reached.")
            return Path(".")
