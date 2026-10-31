"""Validate external citation URLs.

URL validation does not replace DNS, redirect, or connection-level
SSRF protections when fetching external resources.
"""

import ipaddress
from urllib.parse import urlsplit

_BLOCKED = {"localhost", "localhost.localdomain"}


def validate_source_url(url: str) -> bool:
    """Return whether a URL has an acceptable public HTTP(S) host."""
    if not isinstance(url, str):
        return False

    try:
        parts = urlsplit(url)
        host = (parts.hostname or "").rstrip(".").lower()

        if (
            parts.scheme not in ("https", "http")
            or not host
            or parts.username is not None
            or parts.password is not None
        ):
            return False

        if host in _BLOCKED or host.endswith((".localhost", ".local")):
            return False

        # Reject malformed ports and URLs.
        port = parts.port
        if port is not None and port not in (80, 443):
            return False

        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            # A DNS hostname must have valid nonempty labels.
            labels = host.split(".")

            return (
                len(host) <= 253
                and len(labels) >= 2
                and all(
                    1 <= len(label) <= 63
                    and label[0].isalnum()
                    and label[-1].isalnum()
                    and all(char.isascii() and (char.isalnum() or char == "-") for char in label)
                    for label in labels
                )
            )

        return address.is_global

    except (ValueError, TypeError):
        return False


def unique_valid_sources(sources: list[str]) -> list[str]:
    """Deduplicate sources while retaining their original order."""
    result: list[str] = []
    seen: set[str] = set()

    for source in sources:
        if not isinstance(source, str):
            continue

        url = source.strip()
        canonical = url.rstrip("/")

        if validate_source_url(url) and canonical not in seen:
            seen.add(canonical)
            result.append(url)

    return result
