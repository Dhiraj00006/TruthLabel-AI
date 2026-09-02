"""Fetches/parses e-commerce listing text from a URL, or accepts pasted text directly."""
import re
import urllib.request

TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def parse_listing_url(url: str) -> str:
    """Fetch a listing page and strip it down to plain text.

    v1: generic tag-stripping, no platform-specific selectors (see solution-design.md 3.7).
    """
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=10) as response:
        html = response.read().decode("utf-8", errors="ignore")
    return parse_listing_text(TAG_RE.sub(" ", html))


def parse_listing_text(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text).strip()
