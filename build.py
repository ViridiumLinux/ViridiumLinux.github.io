#!/usr/bin/env python3
"""
build.py - Static site generator for the Viridium Linux GitHub Pages wiki.

Reads Markdown source files from the local wiki directory and compiles them
into a clean-URL static site (subfolder/index.html structure) inside the
static repository directory, ready to commit and push to GitHub Pages.

Run once:
    python3 build.py
"""

import os
import re
import html
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SITE_ROOT = "https://viridiumlinux.github.io"
ISO_RELEASES_URL = "https://github.com/ViridiumLinux/ViridiumLinux.github.io/releases"

WIKI_DIR = "/home/delta/Viridium-Linux.wiki"
OUT_DIR = "/home/delta/Viridium-Linux"

SITE_TITLE = "Viridium Linux"

# Ordered pages: (slug, page_title, list_of_candidate_filenames)
# slug == "" means this page compiles to the site root (index.html)
PAGES = [
    ("",                  "Home",                 ["Home.md"]),
    ("installation",      "Installation",         ["Installation.md"]),
    ("configuration",     "Configuration",        ["Configuration.md"]),
    ("vbuild",            "vbuild",               ["vbuild.md"]),
    ("viridium",          "viridium",             ["viridium.md"]),
    ("architecture",      "Architecture",         ["Architecture.md", "archetecture.md"]),
    ("boot-and-uefi",     "Boot and UEFI",        ["Boot-and-UEFI.md"]),
    ("development",       "Development",          ["Development.md"]),
    ("networking",        "Networking",           ["Networking.md"]),
    ("package-management","Package management",   ["Package-management.md"]),
    ("troubleshooting",   "Troubleshooting",       ["Troubleshooting.md"]),
    ("faq",               "FAQ",                  ["FAQ.md"]),
]


def page_url(slug: str) -> str:
    """Return the fully-qualified absolute URL for a page slug."""
    if slug == "":
        return f"{SITE_ROOT}/"
    return f"{SITE_ROOT}/{slug}/"


# ---------------------------------------------------------------------------
# Markdown -> HTML conversion
# ---------------------------------------------------------------------------

def convert_inline(text: str) -> str:
    """Handle inline markdown: bold, italic, inline code, links."""
    # Inline code `code`
    text = re.sub(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>", text)
    # Bold **text**
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic *text* (avoid already-processed strong tags by requiring non-* chars)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    # Links [text](url)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )
    return text


def parse_table(lines):
    """Parse a block of markdown table lines into an HTML <table>."""
    rows = []
    for line in lines:
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        cells = [c.strip() for c in line.split("|")]
        rows.append(cells)

    # Second row is the separator (---|---|---)
    header = rows[0]
    body_rows = rows[2:] if len(rows) > 1 and re.match(r"^:?-+:?$", rows[1][0].replace(" ", "")) else rows[1:]

    out = ['<div class="table-wrap"><table>']
    out.append("<thead><tr>")
    for cell in header:
        out.append(f"<th>{convert_inline(html.escape(cell))}</th>")
    out.append("</tr></thead>")

    out.append("<tbody>")
    for i, row in enumerate(body_rows):
        row_class = "row-even" if i % 2 == 0 else "row-odd"
        out.append(f'<tr class="{row_class}">')
        for cell in row:
            out.append(f"<td>{convert_inline(html.escape(cell))}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def markdown_to_html(md_text: str) -> str:
    lines = md_text.replace("\r\n", "\n").split("\n")
    html_parts = []
    i = 0
    n = len(lines)
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            html_parts.append("</ul>")
            in_list = False

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Fenced code block
        if stripped.startswith("```"):
            close_list()
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            code_escaped = html.escape("\n".join(code_lines))
            # ASCII trees / flowcharts preserved verbatim, no link/underline styling
            html_parts.append(f'<pre class="ascii-block"><code>{code_escaped}</code></pre>')
            continue

        # Table block: a line with pipes followed by a separator line
        if "|" in stripped and i + 1 < n and re.match(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$", lines[i + 1]):
            close_list()
            table_lines = [line]
            i += 1
            while i < n and "|" in lines[i]:
                table_lines.append(lines[i])
                i += 1
            html_parts.append(parse_table(table_lines))
            continue

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            close_list()
            level = len(m.group(1))
            content = convert_inline(html.escape(m.group(2)))
            html_parts.append(f"<h{level}>{content}</h{level}>")
            i += 1
            continue

        # Unordered list items
        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            content = convert_inline(html.escape(m.group(1)))
            html_parts.append(f"<li>{content}</li>")
            i += 1
            continue

        # Blank line
        if stripped == "":
            close_list()
            i += 1
            continue

        # Paragraph
        close_list()
        para_lines = [stripped]
        i += 1
        while i < n and lines[i].strip() != "" and not lines[i].strip().startswith("```") \
                and not re.match(r"^#{1,6}\s", lines[i].strip()) \
                and not re.match(r"^[-*]\s+", lines[i].strip()):
            para_lines.append(lines[i].strip())
            i += 1
        content = convert_inline(html.escape(" ".join(para_lines)))
        html_parts.append(f"<p>{content}</p>")

    close_list()
    return "\n".join(html_parts)


# ---------------------------------------------------------------------------
# HTML templating
# ---------------------------------------------------------------------------

CSS = """
:root {
    --bg-main: #141210;
    --bg-sidebar: #1f1a16;
    --border-color: #382414;
    --accent: #ff8838;
    --text-main: #e8e0d8;
    --text-dim: #a89a8c;
}

* { box-sizing: border-box; }

html, body {
    margin: 0;
    padding: 0;
    background: var(--bg-main);
    color: var(--text-main);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
}

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

.layout {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: 250px;
    flex-shrink: 0;
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border-color);
    padding: 24px 16px;
}

.sidebar h1 {
    font-size: 1.2rem;
    color: var(--text-main);
    margin: 0 0 20px 4px;
}

.sidebar nav ul {
    list-style: none;
    margin: 0;
    padding: 0;
}

.sidebar nav li { margin-bottom: 2px; }

.sidebar nav a {
    display: block;
    padding: 8px 10px;
    border-radius: 6px;
    color: var(--text-dim);
    font-size: 0.95rem;
}

.sidebar nav a:hover {
    background: rgba(255, 136, 56, 0.1);
    color: var(--text-main);
    text-decoration: none;
}

.sidebar nav a.active {
    background: rgba(255, 136, 56, 0.15);
    color: var(--accent);
    font-weight: 600;
}

.install-btn {
    display: block;
    margin: 8px 4px 24px 4px;
    padding: 12px 14px;
    background: var(--accent);
    color: #141210;
    font-weight: 700;
    text-align: center;
    border-radius: 8px;
    letter-spacing: 0.3px;
}

.install-btn:hover {
    background: #ff9a55;
    text-decoration: none;
}

.content {
    flex: 1;
    padding: 40px 56px;
    max-width: 900px;
}

.content h1, .content h2, .content h3 {
    color: var(--text-main);
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 8px;
}

.content pre.ascii-block {
    background: #100e0c;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 16px;
    overflow-x: auto;
    color: var(--text-main);
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 0.9rem;
}

.content pre.ascii-block a { text-decoration: none !important; color: inherit !important; }

.content code {
    background: #100e0c;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 0.9em;
}

.content pre code {
    background: none;
    padding: 0;
}

.table-wrap {
    overflow-x: auto;
    margin: 20px 0;
}

table {
    border-collapse: collapse;
    width: 100%;
}

th, td {
    border: 1px solid var(--border-color);
    padding: 10px 14px;
    text-align: left;
}

th {
    background: var(--bg-sidebar);
    color: var(--accent);
}

tr.row-even { background: #1a1613; }
tr.row-odd { background: #141210; }

footer.site-footer {
    margin-top: 48px;
    padding-top: 16px;
    border-top: 1px solid var(--border-color);
    color: var(--text-dim);
    font-size: 0.85rem;
}
"""


def render_sidebar(current_slug: str) -> str:
    items = []
    for slug, title, _ in PAGES:
        active = " active" if slug == current_slug else ""
        items.append(f'<li><a class="link{active}" href="{page_url(slug)}">{html.escape(title)}</a></li>')
    return "\n".join(items)


def render_page(slug: str, title: str, body_html: str) -> str:
    sidebar_items = render_sidebar(slug)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} - {html.escape(SITE_TITLE)}</title>
<style>
{CSS}
</style>
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <h1>{html.escape(SITE_TITLE)}</h1>
    <a class="install-btn" href="{ISO_RELEASES_URL}">Download ISO</a>
    <nav>
      <ul>
        {sidebar_items}
      </ul>
    </nav>
  </aside>
  <main class="content">
    {body_html}
    <footer class="site-footer">
      <p>{html.escape(SITE_TITLE)} documentation.</p>
    </footer>
  </main>
</div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Build process
# ---------------------------------------------------------------------------

def find_source_file(candidates):
    for name in candidates:
        path = os.path.join(WIKI_DIR, name)
        if os.path.isfile(path):
            return path
    return None


def build():
    if not os.path.isdir(WIKI_DIR):
        print(f"ERROR: wiki directory not found: {WIKI_DIR}")
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)

    built = 0
    missing = []

    for slug, title, candidates in PAGES:
        src_path = find_source_file(candidates)
        if src_path is None:
            missing.append(candidates[0])
            continue

        with open(src_path, "r", encoding="utf-8") as f:
            md_text = f.read()

        body_html = markdown_to_html(md_text)
        page_html = render_page(slug, title, body_html)

        if slug == "":
            out_path = os.path.join(OUT_DIR, "index.html")
        else:
            out_dir = os.path.join(OUT_DIR, slug)
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, "index.html")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page_html)

        print(f"Built: {src_path} -> {out_path}")
        built += 1

    print(f"\nDone. {built}/{len(PAGES)} pages built.")
    if missing:
        print("WARNING: could not find source files for:")
        for m in missing:
            print(f"  - {m}")


if __name__ == "__main__":
    build()
