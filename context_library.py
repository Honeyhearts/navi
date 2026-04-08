import random
import re
from pathlib import Path

LIBRARY_DIR = Path(__file__).parent / "library"
_CACHE: list[dict] | None = None


def _parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter fields as a dict."""
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip().strip('"')
    return fields


def load_all() -> list[dict]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not LIBRARY_DIR.exists():
        _CACHE = []
        return _CACHE
    entries = []
    for f in sorted(LIBRARY_DIR.glob("*.md")):
        text = f.read_text()
        meta = _parse_frontmatter(text)
        if meta:
            entries.append(meta)
    _CACHE = entries
    return _CACHE


def sample_context(n: int = 2) -> str:
    """Return a compact context block of n random personas for system prompt injection."""
    entries = load_all()
    if not entries:
        return ""
    sample = random.sample(entries, min(n, len(entries)))
    lines = ["EXAMPLE PEOPLE NAVI IS BUILT FOR (use for intuition, not as scripts):"]
    for e in sample:
        name = e.get("name", "Someone")
        role = e.get("role", "")
        pain = e.get("pain", "")
        navi_role = e.get("navi_role", "")
        lines.append(f"- {name} ({role}): {pain} → {navi_role}")
    return "\n".join(lines)
