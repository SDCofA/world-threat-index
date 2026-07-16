import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = "\n".join(
    (ROOT / "css" / name).read_text(encoding="utf-8")
    for name in ("variables.css", "layout.css", "components.css", "wti.css")
)

REQUIRED_RUNTIME_IDS = (
    "status-pill",
    "last-update",
    "coverage-text",
    "main-index",
    "status-text",
    "countries-active",
    "groups-grid",
    "top-threats",
    "world-map",
    "country-detail",
    "country-search",
    "rankings-table",
)


def _declaration(selector: str, css: str = CSS) -> str:
    selector_pattern = r"\s*".join(re.escape(part) for part in selector.split())
    match = re.search(rf"{selector_pattern}\s*\{{([^}}]+)\}}", css, re.DOTALL)
    assert match, f"Missing CSS rule for {selector}"
    return re.sub(r"\s+", " ", match.group(1)).lower()


def test_information_architecture_is_semantic_and_ordered():
    assert re.search(
        r"<h1\b[^>]*>\s*World Threat Index\s*</h1>", HTML, re.IGNORECASE
    )

    section_ids = (
        "global-overview",
        "world-intelligence",
        "geopolitical-groups",
        "country-rankings",
        "methodology",
    )
    positions = [HTML.index(f'id="{section_id}"') for section_id in section_ids]
    assert positions == sorted(positions)

    for section_id in section_ids:
        assert re.search(
            rf"<section\b[^>]*\bid=\"{section_id}\"[^>]*>", HTML, re.IGNORECASE
        )


def test_endorsed_masterbrand_and_existing_logo_are_visible():
    assert "Part of Monarch Castle Technologies" in HTML
    assert "SDCofA" in HTML
    assert re.search(
        r'<header\b[\s\S]*?<img\b[^>]*src="logo\.png"[^>]*'
        r'alt="[^"]*Monarch Castle Technologies[^"]*"',
        HTML,
        re.IGNORECASE,
    )
    assert "most accurate" not in HTML.lower()


def test_runtime_hooks_and_script_order_are_preserved():
    for runtime_id in REQUIRED_RUNTIME_IDS:
        assert len(re.findall(rf'\bid="{runtime_id}"', HTML)) == 1

    required_scripts = (
        "wti_data.js",
        "js/core.js",
        "js/map.js",
        "js/groups.js",
        "js/rankings.js",
    )
    loaded_scripts = re.findall(r'<script\b[^>]*\bsrc="([^"]+)"', HTML)
    positions = [loaded_scripts.index(script) for script in required_scripts]
    assert positions == sorted(positions)


def test_editorial_type_and_warm_palette_replace_terminal_tokens():
    assert "family=Spectral" in HTML
    assert "IBM+Plex+Sans" in HTML
    assert "IBM+Plex+Mono" in HTML

    compact_css = re.sub(r"\s+", "", CSS).lower()
    for token in ("--bg:#15130f", "--bg-panel:#191711", "--text-primary:#ece6d8", "--accent:#c9a24b"):
        assert token in compact_css

    for old_terminal_token in (
        "#ff6600",
        "#00d4ff",
        "jetbrains mono",
        "bloomberg",
        "scanline",
    ):
        assert old_terminal_token not in CSS.lower()


def test_phone_layout_prevents_document_overflow_and_stacks_opening():
    phone = re.search(r"@media\s*\(max-width:\s*720px\)", CSS, re.IGNORECASE)
    assert phone, "A 720px phone breakpoint is required"
    phone_css = CSS[phone.start() :]

    document_rule = _declaration("html,\nbody", phone_css)
    assert "max-width: 100%" in document_rule
    assert "overflow-x: clip" in document_rule

    opening_rule = _declaration(".opening-grid", phone_css)
    assert re.search(r"grid-template-columns:\s*minmax\(0,\s*1fr\)", opening_rule)

    shell_rule = _declaration(".app-shell", phone_css)
    assert "min-width: 0" in shell_rule
    assert "max-width: 100%" in shell_rule


def test_map_and_rankings_bound_their_own_overflow():
    map_rule = _declaration(".wti-map-wrap svg")
    assert "width: 100%" in map_rule
    assert "max-width: 100%" in map_rule
    assert "height: auto" in map_rule

    rankings_rule = _declaration(".rankings-table")
    assert "max-width: 100%" in rankings_rule
    assert "overflow-x: auto" in rankings_rule
