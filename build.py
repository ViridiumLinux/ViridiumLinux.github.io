#!/usr/bin/env python3

from pathlib import Path
from html import escape
import re
import shutil
import sys


# ============================================================
# Configuration
# ============================================================

USERNAME = "ViridiumLinux"

WIKI_DIR = Path("/home/delta/Viridium-Linux.wiki")
SITE_DIR = Path("/home/delta/Viridium-Linux")

# Change this to https://viridiumlinux.github.io if that is
# the actual GitHub Pages URL for the repository.
BASE_URL = "https://github.io"

# Installation / ISO button target.
INSTALL_URL = "https://github.com"


# ============================================================
# Page definitions
# ============================================================

PAGES = [
    ("Home", "Home.md", ""),
    ("Installation", "Installation.md", "installation"),
    ("Configuration", "Configuration.md", "configuration"),
    ("vbuild", "vbuild.md", "vbuild"),
    ("viridium", "viridium.md", "viridium"),
    ("Architecture", ("Architecture.md", "archetecture.md"), "architecture"),
    ("Boot and UEFI", "Boot-and-UEFI.md", "boot-and-uefi"),
    ("Development", "Development.md", "development"),
    ("Networking", "Networking.md", "networking"),
    ("Package management", "Package-management.md", "package-management"),
    ("Troubleshooting", "Troubleshooting.md", "troubleshooting"),
    ("FAQ", "FAQ.md", "faq"),
]


# ============================================================
# Styling
# ============================================================

CSS = r"""
:root {
    --background: #141210;
    --sidebar: #1f1a16;
    --sidebar-hover: #2a211b;
    --border: #382414;
    --accent: #ff8838;
    --accent-hover: #ff9d59;
    --text: #e9e2dc;
    --muted: #a79c93;
    --code: #191512;
    --table-alt: #191512;
    --blockquote: #201913;
}

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    margin: 0;
    background: var(--background);
    color: var(--text);
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Helvetica,
        Arial,
        sans-serif;
    line-height: 1.7;
}

a {
    color: var(--accent);
    text-decoration: none;
}

a:hover {
    color: var(--accent-hover);
    text-decoration: underline;
}

.layout {
    display: flex;
    min-height: 100vh;
}

/* ------------------------------------------------------------
   Sidebar
   ------------------------------------------------------------ */

.sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 270px;
    height: 100vh;
    overflow-y: auto;

    background: var(--sidebar);
    border-right: 1px solid var(--border);

    padding: 28px 20px;
}

.logo {
    margin-bottom: 28px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border);
}

.logo-title {
    color: var(--accent);
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.5px;
}

.logo-subtitle {
    color: var(--muted);
    font-size: 13px;
    margin-top: 3px;
}

.nav-title {
    color: var(--muted);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 0 0 10px 4px;
}

.nav {
    display: flex;
    flex-direction: column;
    gap: 3px;
}

.nav a {
    display: block;
    padding: 9px 11px;
    border-radius: 6px;
    color: #cfc6bf;
    font-size: 14px;
    transition:
        background 0.12s ease,
        color 0.12s ease;
}

.nav a:hover {
    background: var(--sidebar-hover);
    color: var(--text);
    text-decoration: none;
}

.nav a.active {
    background: #2b211a;
    color: var(--accent);
    font-weight: 600;
}

.install-button {
    display: block;
    margin-top: 25px;
    padding: 11px 14px;

    background: var(--accent);
    color: #17110d;

    border-radius: 6px;
    text-align: center;

    font-size: 14px;
    font-weight: 800;

    transition:
        background 0.12s ease,
        transform 0.12s ease;
}

.install-button:hover {
    background: var(--accent-hover);
    color: #17110d;
    text-decoration: none;
    transform: translateY(-1px);
}

/* ------------------------------------------------------------
   Content
   ------------------------------------------------------------ */

.content {
    width: calc(100% - 270px);
    margin-left: 270px;
    padding: 55px 65px 80px;
}

.article {
    max-width: 950px;
    margin: 0 auto;
}

h1,
h2,
h3,
h4,
h5,
h6 {
    color: #f4eee9;
    line-height: 1.25;
    margin-top: 1.7em;
    margin-bottom: 0.65em;
}

h1 {
    margin-top: 0;
    font-size: 36px;
    letter-spacing: -1px;
}

h2 {
    font-size: 27px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}

h3 {
    font-size: 22px;
}

h4 {
    font-size: 18px;
}

p {
    margin: 0 0 16px;
}

strong {
    color: #fff5ed;
}

hr {
    border: 0;
    border-top: 1px solid var(--border);
    margin: 35px 0;
}

/* ------------------------------------------------------------
   Code
   ------------------------------------------------------------ */

code {
    background: var(--code);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 2px 6px;

    color: #f0d6c3;
    font-family:
        "JetBrains Mono",
        "Cascadia Code",
        "Fira Code",
        Consolas,
        monospace;

    font-size: 0.9em;
}

pre {
    margin: 22px 0;
    padding: 18px;

    overflow-x: auto;

    background: var(--code);
    border: 1px solid var(--border);
    border-radius: 7px;

    line-height: 1.55;
}

pre code {
    padding: 0;
    border: 0;
    background: transparent;

    color: #ddd3cb;
    font-size: 13px;
}

/* ------------------------------------------------------------
   Tables
   ------------------------------------------------------------ */

.table-wrapper {
    width: 100%;
    overflow-x: auto;
    margin: 22px 0;
}

table {
    width: 100%;
    border-collapse: collapse;

    border: 1px solid var(--border);
    background: var(--background);
}

th,
td {
    padding: 10px 13px;
    border: 1px solid var(--border);
    text-align: left;
}

th {
    background: #211a15;
    color: var(--accent);
    font-weight: 700;
}

tr:nth-child(even) td {
    background: var(--table-alt);
}

/* ------------------------------------------------------------
   Lists
   ------------------------------------------------------------ */

ul,
ol {
    margin-top: 8px;
    margin-bottom: 18px;
    padding-left: 28px;
}

li {
    margin: 4px 0;
}

/* ------------------------------------------------------------
   Blockquotes
   ------------------------------------------------------------ */

blockquote {
    margin: 20px 0;
    padding: 10px 18px;

    background: var(--blockquote);
    border-left: 3px solid var(--accent);

    color: #c5bbb3;
}

/* ------------------------------------------------------------
   Footer
   ------------------------------------------------------------ */

.footer {
    margin-top: 70px;
    padding-top: 20px;

    border-top: 1px solid var(--border);

    color: var(--muted);
    font-size: 12px;
}

/* ------------------------------------------------------------
   Mobile
   ------------------------------------------------------------ */

@media (max-width: 800px) {
    .sidebar {
        position: static;
        width: 100%;
        height: auto;
        border-right: 0;
        border-bottom: 1px solid var(--border);
    }

    .layout {
        display: block;
    }

    .content {
        width: 100%;
        margin-left: 0;
        padding: 35px 22px 60px;
    }

    .nav {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .install-button {
        margin-bottom: 5px;
    }
}
"""


# ============================================================
# Utility functions
# ============================================================

def find_source(filename):
    """
    Resolve a normal filename or a tuple of fallback filenames.
    """

    if isinstance(filename, tuple):
        for candidate in filename:
            path = WIKI_DIR / candidate
            if path.is_file():
                return path

        return None

    path = WIKI_DIR / filename

    if path.is_file():
        return path

    return None


def page_url(slug):
    """
    Generate an absolute URL for a page.
    """

    if not slug:
        return BASE_URL + "/"

    return BASE_URL.rstrip("/") + "/" + slug.strip("/") + "/"


def html_inline(text):
    """
    Safely convert inline Markdown without touching block-level
    code or ASCII diagrams.
    """

    # Escape HTML first so raw HTML cannot break the generated page.
    text = escape(text, quote=False)

    # Inline code.
    text = re.sub(
        r"`([^`]+)`",
        lambda m: "<code>" + m.group(1) + "</code>",
        text,
    )

    # Images.
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: (
            '<img src="' + escape(m.group(2), quote=True) +
            '" alt="' + escape(m.group(1), quote=True) +
            '">'
        ),
        text,
    )

    # Links.
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: (
            '<a href="' + escape(m.group(2), quote=True) +
            '">' + m.group(1) + "</a>"
        ),
        text,
    )

    # Bold.
    text = re.sub(
        r"\*\*(.+?)\*\*",
        r"<strong>\1</strong>",
        text,
    )

    text = re.sub(
        r"__(.+?)__",
        r"<strong>\1</strong>",
        text,
    )

    # Italic.
    text = re.sub(
        r"(?<!\*)\*([^*]+)\*(?!\*)",
        r"<em>\1</em>",
        text,
    )

    text = re.sub(
        r"(?<!_)_([^_]+)_(?!_)",
        r"<em>\1</em>",
        text,
    )

    # Strikethrough.
    text = re.sub(
        r"~~(.+?)~~",
        r"<del>\1</del>",
        text,
    )

    return text


def is_table_separator(line):
    """
    Detect Markdown table separator rows such as:

    | --- | --- |
    """

    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]

    if not cells:
        return False

    return all(
        re.fullmatch(r":?-{3,}:?", cell)
        for cell in cells
    )


def split_table_row(line):
    """
    Split a Markdown table row while respecting the outer pipes.
    """

    line = line.strip()

    if line.startswith("|"):
        line = line[1:]

    if line.endswith("|"):
        line = line[:-1]

    return [cell.strip() for cell in line.split("|")]


# ============================================================
# Markdown compiler
# ============================================================

def markdown_to_html(markdown):
    """
    Convert the supported Markdown subset into HTML.

    Code blocks are handled before any inline Markdown processing,
    which means ASCII diagrams and path trees remain untouched.
    """

    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    output = []

    in_code = False
    code_lines = []

    in_ul = False
    in_ol = False
    in_blockquote = False

    def close_lists():
        nonlocal in_ul, in_ol

        if in_ul:
            output.append("</ul>")
            in_ul = False

        if in_ol:
            output.append("</ol>")
            in_ol = False

    def close_blockquote():
        nonlocal in_blockquote

        if in_blockquote:
            output.append("</blockquote>")
            in_blockquote = False

    i = 0

    while i < len(lines):
        line = lines[i]

        # ----------------------------------------------------
        # Fenced code block
        # ----------------------------------------------------

        if line.strip().startswith("```"):
            if in_code:
                code = "\n".join(code_lines)

                output.append(
                    "<pre><code>" +
                    escape(code, quote=False) +
                    "</code></pre>"
                )

                code_lines = []
                in_code = False

            else:
                close_lists()
                close_blockquote()

                in_code = True
                code_lines = []

            i += 1
            continue

        if in_code:
            # IMPORTANT:
            # No Markdown processing whatsoever happens here.
            # This preserves ASCII trees, diagrams, shell output,
            # paths, arrows, box drawing, etc.
            code_lines.append(line)
            i += 1
            continue

        # ----------------------------------------------------
        # Blank line
        # ----------------------------------------------------

        if not line.strip():
            close_lists()
            close_blockquote()
            i += 1
            continue

        # ----------------------------------------------------
        # Markdown table
        # ----------------------------------------------------

        if (
            "|" in line
            and i + 1 < len(lines)
            and is_table_separator(lines[i + 1])
        ):
            close_lists()
            close_blockquote()

            header_cells = split_table_row(line)

            output.append('<div class="table-wrapper">')
            output.append("<table>")
            output.append("<thead>")
            output.append("<tr>")

            for cell in header_cells:
                output.append(
                    "<th>" + html_inline(cell) + "</th>"
                )

            output.append("</tr>")
            output.append("</thead>")
            output.append("<tbody>")

            i += 2

            while i < len(lines):
                row = lines[i]

                if not row.strip() or "|" not in row:
                    break

                cells = split_table_row(row)

                output.append("<tr>")

                for cell in cells:
                    output.append(
                        "<td>" + html_inline(cell) + "</td>"
                    )

                output.append("</tr>")

                i += 1

            output.append("</tbody>")
            output.append("</table>")
            output.append("</div>")

            continue

        # ----------------------------------------------------
        # Headings
        # ----------------------------------------------------

        heading = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)

        if heading:
            close_lists()
            close_blockquote()

            level = len(heading.group(1))
            text = heading.group(2)

            output.append(
                f"<h{level}>{html_inline(text)}</h{level}>"
            )

            i += 1
            continue

        # ----------------------------------------------------
        # Horizontal rule
        # ----------------------------------------------------

        if re.fullmatch(r"\s*(-{3,}|\*{3,}|_{3,})\s*", line):
            close_lists()
            close_blockquote()

            output.append("<hr>")

            i += 1
            continue

        # ----------------------------------------------------
        # Blockquote
        # ----------------------------------------------------

        quote = re.match(r"^\s*>\s?(.*)$", line)

        if quote:
            close_lists()

            if not in_blockquote:
                output.append("<blockquote>")
                in_blockquote = True

            output.append(
                "<p>" + html_inline(quote.group(1)) + "</p>"
            )

            i += 1
            continue

        # ----------------------------------------------------
        # Unordered list
        # ----------------------------------------------------

        unordered = re.match(r"^\s*[-*+]\s+(.+)$", line)

        if unordered:
            close_blockquote()

            if not in_ul:
                close_lists()
                output.append("<ul>")
                in_ul = True

            output.append(
                "<li>" + html_inline(unordered.group(1)) + "</li>"
            )

            i += 1
            continue

        # ----------------------------------------------------
        # Ordered list
        # ----------------------------------------------------

        ordered = re.match(r"^\s*\d+\.\s+(.+)$", line)

        if ordered:
            close_blockquote()

            if not in_ol:
                close_lists()
                output.append("<ol>")
                in_ol = True

            output.append(
                "<li>" + html_inline(ordered.group(1)) + "</li>"
            )

            i += 1
            continue

        # ----------------------------------------------------
        # Normal paragraph
        # ----------------------------------------------------

        close_lists()
        close_blockquote()

        paragraph = [line]

        j = i + 1

        while j < len(lines):
            next_line = lines[j]

            if not next_line.strip():
                break

            if next_line.strip().startswith("```"):
                break

            if re.match(r"^#{1,6}\s+", next_line):
                break

            if re.match(r"^\s*>\s?", next_line):
                break

            if re.match(r"^\s*[-*+]\s+", next_line):
                break

            if re.match(r"^\s*\d+\.\s+", next_line):
                break

            paragraph.append(next_line)
            j += 1

        text = " ".join(part.strip() for part in paragraph)

        output.append(
            "<p>" + html_inline(text) + "</p>"
        )

        i = j

    # --------------------------------------------------------
    # Close anything still open
    # --------------------------------------------------------

    if in_code:
        code = "\n".join(code_lines)

        output.append(
            "<pre><code>" +
            escape(code, quote=False) +
            "</code></pre>"
        )

    close_lists()
    close_blockquote()

    return "\n".join(output)


# ============================================================
# HTML document
# ============================================================

def build_sidebar(current_slug):
    items = []

    for title, _, slug in PAGES:
        url = page_url(slug)

        active = slug == current_slug

        class_name = ' class="active"' if active else ""

        items.append(
            f'<a href="{escape(url, quote=True)}"{class_name}>'
            f'{escape(title)}'
            "</a>"
        )

    return "\n".join(items)


def build_page(title, slug, body):
    sidebar = build_sidebar(slug)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>{escape(title)} — Viridium Linux</title>

    <style>
{CSS}
    </style>
</head>

<body>

<div class="layout">

    <aside class="sidebar">

        <div class="logo">
            <div class="logo-title">Viridium Linux</div>
            <div class="logo-subtitle">Documentation</div>
        </div>

        <div class="nav-title">Documentation</div>

        <nav class="nav">
            {sidebar}
        </nav>

        <a
            class="install-button"
            href="{escape(INSTALL_URL, quote=True)}"
        >
            Install Viridium Linux
        </a>

    </aside>

    <main class="content">

        <article class="article">
            {body}

            <div class="footer">
                Viridium Linux · Documentation
            </div>
        </article>

    </main>

</div>

</body>
</html>
"""


# ============================================================
# Build
# ============================================================

def clean_generated_pages():
    """
    Remove only generated page directories/files.

    This intentionally does NOT wipe the entire repository because
    the repository may contain README files, .gitignore, assets,
    source files, etc.
    """

    root_index = SITE_DIR / "index.html"

    if root_index.exists():
        root_index.unlink()

    for _, _, slug in PAGES:
        if not slug:
            continue

        directory = SITE_DIR / slug

        if directory.exists():
            shutil.rmtree(directory)


def build():
    print("=" * 60)
    print("Viridium Linux Documentation Builder")
    print("=" * 60)

    if not WIKI_DIR.exists():
        print(f"ERROR: Wiki directory does not exist:")
        print(f"  {WIKI_DIR}")
        sys.exit(1)

    SITE_DIR.mkdir(parents=True, exist_ok=True)

    clean_generated_pages()

    built = 0
    missing = []

    for title, filename, slug in PAGES:
        source = find_source(filename)

        if source is None:
            missing.append(
                filename if isinstance(filename, str)
                else " / ".join(filename)
            )
            continue

        print(f"Building: {title}")

        markdown = source.read_text(encoding="utf-8")

        body = markdown_to_html(markdown)

        html = build_page(
            title=title,
            slug=slug,
            body=body,
        )

        if slug:
            output_dir = SITE_DIR / slug
            output_dir.mkdir(parents=True, exist_ok=True)

            output_file = output_dir / "index.html"

        else:
            output_file = SITE_DIR / "index.html"

        output_file.write_text(
            html,
            encoding="utf-8",
            newline="\n",
        )

        print(f"  -> {output_file}")

        built += 1

    print()
    print("=" * 60)
    print(f"Built {built}/{len(PAGES)} pages")
    print("=" * 60)

    if missing:
        print()
        print("WARNING: Missing wiki files:")

        for filename in missing:
            print(f"  - {filename}")

        print()

    if built == len(PAGES):
        print("Build completed successfully.")
    else:
        print("Build completed with missing pages.")


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    build()
