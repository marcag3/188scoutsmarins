#!/usr/bin/env python3
"""Convert WordPress WXR export to Astro markdown content files."""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_XML = ROOT / "188egroupedescoutismemarinmontral-nord.WordPress.2026-06-16.xml"
PAGES_DIR = ROOT / "src/content/pages"
ALBUMS_DIR = ROOT / "src/content/albums"
PHOTOS_DIR = ROOT / "public/images/photos"
PARTNERS_DIR = ROOT / "public/images/partners"
DOCUMENTS_DIR = ROOT / "public/documents"
PARTNERS_FILE = ROOT / "src/data/partners.ts"

TARGET_SLUGS = {
    "a-propos",
    "a-propos/calendrier",
    "a-propos/inscription-2",
    "a-propos/photos",
    "contact",
    "contact/simpliquer",
    "meute",
    "troupe",
    "partenaires",
}

LAYOUT_BY_SLUG = {
    "contact": "contact",
    "a-propos/calendrier": "calendar",
    "a-propos/photos": "photos",
    "partenaires": "partners",
}

WP_UPLOAD_RE = re.compile(
    r"https?://(?:www\.)?188scoutsmarins\.ca/wp-content/uploads/(.+?)(?:[?#\"'\s>]|$)",
    re.IGNORECASE,
)
ITEM_RE = re.compile(r"<item>(.*?)</item>", re.DOTALL)
CDATA_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)
FIELD_PATTERNS = {
    "title": re.compile(r"<title>(?:<!\[CDATA\[(.*?)\]\]>|([^<]*))</title>", re.DOTALL),
    "content": re.compile(
        r"<content:encoded>(?:<!\[CDATA\[(.*?)\]\]>|([^<]*))</content:encoded>", re.DOTALL
    ),
    "excerpt": re.compile(
        r"<excerpt:encoded>(?:<!\[CDATA\[(.*?)\]\]>|([^<]*))</excerpt:encoded>", re.DOTALL
    ),
    "post_id": re.compile(r"<wp:post_id>(\d+)</wp:post_id>"),
    "post_name": re.compile(
        r"<wp:post_name>(?:<!\[CDATA\[(.*?)\]\]>|([^<]*))</wp:post_name>", re.DOTALL
    ),
    "status": re.compile(
        r"<wp:status>(?:<!\[CDATA\[(.*?)\]\]>|([^<]*))</wp:status>", re.DOTALL
    ),
    "post_parent": re.compile(r"<wp:post_parent>(\d+)</wp:post_parent>"),
    "menu_order": re.compile(r"<wp:menu_order>(\d+)</wp:menu_order>"),
    "post_type": re.compile(
        r"<wp:post_type>(?:<!\[CDATA\[(.*?)\]\]>|([^<]*))</wp:post_type>", re.DOTALL
    ),
    "attachment_url": re.compile(
        r"<wp:attachment_url>(?:<!\[CDATA\[(.*?)\]\]>|([^<]*))</wp:attachment_url>", re.DOTALL
    ),
}
META_RE = re.compile(
    r"<wp:postmeta>\s*<wp:meta_key>(?:<!\[CDATA\[(.*?)\]\]>|([^<]*))</wp:meta_key>\s*"
    r"<wp:meta_value>(?:<!\[CDATA\[(.*?)\]\]>|([^<]*))</wp:meta_value>\s*</wp:postmeta>",
    re.DOTALL,
)
ML_SLIDER_CAT_RE = re.compile(
    r'<category domain="ml-slider" nicename="(\d+)"><!\[CDATA\[\1\]\]></category>'
)


def cdata_match(match: re.Match[str]) -> str:
    return (match.group(1) or match.group(2) or "").strip()


def read_export(path: Path) -> str:
    raw = path.read_bytes()
    # Strip invalid XML control chars that break strict parsers.
    cleaned = bytes(ch for ch in raw if ch in (9, 10, 13) or ch >= 32)
    return cleaned.decode("utf-8", errors="replace")


def parse_items(xml_text: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for block in ITEM_RE.findall(xml_text):
        item: dict[str, Any] = {"meta": {}}
        for key, pattern in FIELD_PATTERNS.items():
            match = pattern.search(block)
            if not match:
                continue
            value = cdata_match(match)
            if key in {"post_id", "post_parent", "menu_order"}:
                item[key] = int(value) if value else 0
            else:
                item[key] = value
        for key_match in META_RE.finditer(block):
            meta_key = (key_match.group(1) or key_match.group(2) or "").strip()
            meta_val = (key_match.group(3) or key_match.group(4) or "").strip()
            if meta_key:
                item["meta"][meta_key] = meta_val
        slider_match = ML_SLIDER_CAT_RE.search(block)
        if slider_match:
            item["ml_slider_id"] = int(slider_match.group(1))
        items.append(item)
    return items


def build_page_paths(pages: dict[int, dict[str, Any]]) -> dict[int, str]:
    paths: dict[int, str] = {}

    def path_for(post_id: int, seen: set[int] | None = None) -> str:
        if post_id in paths:
            return paths[post_id]
        page = pages.get(post_id)
        if not page:
            return ""
        seen = seen or set()
        if post_id in seen:
            return page["post_name"]
        seen.add(post_id)
        parent_id = page.get("post_parent", 0)
        slug = page["post_name"]
        if parent_id and parent_id in pages:
            parent_path = path_for(parent_id, seen)
            full = f"{parent_path}/{slug}" if parent_path else slug
        else:
            full = slug
        paths[post_id] = full
        return full

    for pid in pages:
        path_for(pid)
    return paths


class AssetDownloader:
    def __init__(self) -> None:
        self.downloaded_images = 0
        self.downloaded_documents = 0
        self.failed: list[str] = []
        self._cache: dict[str, str] = {}

    def local_upload_path(self, url: str) -> str | None:
        match = WP_UPLOAD_RE.search(url)
        if not match:
            return None
        filename = Path(match.group(1).rstrip("/")).name
        if filename.startswith(("LogoSMGM", "JMU_Logo", "Logo_Montreal-Nord", "ste-colette")):
            return f"/images/partners/{filename}"
        return f"/images/photos/{filename}"

    def download_upload(self, url: str) -> str | None:
        local = self.local_upload_path(url)
        if not local:
            return url
        if local in self._cache:
            return self._cache[local]
        dest_dir = PARTNERS_DIR if "/images/partners/" in local else PHOTOS_DIR
        dest = dest_dir / Path(local).name
        if dest.exists():
            self._cache[local] = local
            return local
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "188scoutsmarins-migration/1.0"},
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                dest.write_bytes(response.read())
            self.downloaded_images += 1
            self._cache[local] = local
            return local
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            self.failed.append(f"image {url}: {exc}")
            return local

    def download_document(self, url: str, filename: str | None = None) -> str | None:
        match = WP_UPLOAD_RE.search(url)
        if not match:
            return None
        rel = match.group(1)
        name = filename or Path(rel).name
        dest = DOCUMENTS_DIR / name
        local = f"/documents/{name}"
        if dest.exists():
            return local
        try:
            DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "188scoutsmarins-migration/1.0"},
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                dest.write_bytes(response.read())
            self.downloaded_documents += 1
            return local
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            self.failed.append(f"document {url}: {exc}")
            return local


def rewrite_upload_urls(text: str) -> str:
    def replacer(match: re.Match[str]) -> str:
        filename = Path(match.group(1).rstrip("/")).name
        if filename.startswith(("LogoSMGM", "JMU_Logo", "Logo_Montreal-Nord", "ste-colette")):
            return f"/images/partners/{filename}"
        return f"/images/photos/{filename}"

    return re.sub(
        r"https?://(?:www\.)?188scoutsmarins\.ca/wp-content/uploads/([^\s\"'<>]+)",
        replacer,
        text,
        flags=re.IGNORECASE,
    )


def rewrite_site_urls(text: str) -> str:
    """Rewrite internal page links in markdown (not media URLs)."""
    replacements = [
        (r"https?://(?:www\.)?188scoutsmarins\.ca/simpliquer/?", "/contact/simpliquer/"),
        (r"https?://(?:www\.)?188scoutsmarins\.ca/contact/?", "/contact/"),
        (r"https?://(?:www\.)?188scoutsmarins\.ca/a-propos/?", "/a-propos/"),
        (
            r"https?://(?:www\.)?188scoutsmarins\.ca/([a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)?)/?",
            r"/\1/",
        ),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text


def strip_wp_comments(html_text: str) -> str:
    html_text = re.sub(r"<!--\s*/?wp:[^>]*-->", "", html_text)
    html_text = re.sub(r"<!--\s*wp:[^>]*-->", "", html_text)
    return html_text


def strip_tags(text: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def inline_markup(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<b[^>]*>(.*?)</b>", r"**\1**", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<i[^>]*>(.*?)</i>", r"*\1*", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(
        r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        r"[\2](\1)",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def convert_table(table_html: str, downloader: AssetDownloader) -> str:
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, flags=re.DOTALL | re.IGNORECASE)
    if not rows:
        return ""
    md_rows: list[list[str]] = []
    for row in rows:
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, flags=re.DOTALL | re.IGNORECASE)
        if cells:
            md_rows.append([inline_markup(cell) for cell in cells])
    if not md_rows:
        return ""
    cols = max(len(r) for r in md_rows)
    normalized = [r + [""] * (cols - len(r)) for r in md_rows]
    header = normalized[0]
    body = normalized[1:] if len(normalized) > 1 else []
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    caption_match = re.search(
        r"<figcaption[^>]*>(.*?)</figcaption>", table_html, flags=re.DOTALL | re.IGNORECASE
    )
    md = "\n".join(lines)
    if caption_match:
        md += f"\n\n*{strip_tags(caption_match.group(1))}*"
    return rewrite_site_urls(md)


def convert_html_to_markdown(html_text: str, downloader: AssetDownloader) -> str:
    html_text = strip_wp_comments(html_text)

    # Shortcodes and WP blocks without HTML representation.
    html_text = re.sub(r"\[wpforms[^\]]*\]", "", html_text)
    html_text = re.sub(r"\[calendar[^\]]*\]", "", html_text)
    html_text = re.sub(
        r"\[metaslider[^\]]*\]",
        "\n\n_Voir l'album photo « Camp d'été 2021 » ci-dessous._\n",
        html_text,
    )

    # File blocks (PDF etc.)
    def pdf_link(href: str, label: str) -> str:
        clean_label = strip_tags(label) or Path(href).stem
        local_doc = downloader.download_document(href, Path(href).name)
        if local_doc:
            return f"\n\n[{clean_label}]({local_doc})\n\n"
        local_img = downloader.download_upload(href)
        return f"\n\n[{clean_label}]({local_img or href})\n\n"

    def file_block_repl(match: re.Match[str]) -> str:
        block = match.group(0)
        if not re.search(r"\.pdf", block, re.IGNORECASE):
            return block
        href_match = re.search(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', block, re.IGNORECASE)
        label_match = re.search(
            r'href=["\'][^"\']+\.pdf[^"\']*["\'][^>]*>([^<]+)</a>', block, re.IGNORECASE
        )
        if not href_match:
            return block
        return pdf_link(href_match.group(1), label_match.group(1) if label_match else "")

    html_text = re.sub(
        r'<div class="wp-block-file">.*?</div>',
        file_block_repl,
        html_text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    html_text = re.sub(
        r'<a(?![^>]*wp-block-file__button)[^>]*href=["\']([^"\']+\.pdf[^"\']*)["\'][^>]*>(.*?)</a>',
        lambda m: pdf_link(m.group(1), m.group(2)),
        html_text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Buttons.
    html_text = re.sub(
        r'<a[^>]*class="[^"]*wp-block-button__link[^"]*"[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        lambda m: f"\n\n[{strip_tags(m.group(2))}]({rewrite_site_urls(m.group(1))})\n\n",
        html_text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Tables.
    def table_repl(match: re.Match[str]) -> str:
        return "\n\n" + convert_table(match.group(0), downloader) + "\n\n"

    html_text = re.sub(r"<figure[^>]*wp-block-table[^>]*>.*?</figure>", table_repl, html_text, flags=re.DOTALL | re.IGNORECASE)
    html_text = re.sub(r"<table[^>]*>.*?</table>", table_repl, html_text, flags=re.DOTALL | re.IGNORECASE)

    # Figures with images.
    def figure_repl(match: re.Match[str]) -> str:
        block = match.group(0)
        img_match = re.search(r'<img[^>]*src=["\']([^"\']+)["\']', block, flags=re.IGNORECASE)
        if not img_match:
            return ""
        src = img_match.group(1)
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', block, flags=re.IGNORECASE)
        alt = html.unescape(alt_match.group(1)) if alt_match else ""
        local = downloader.download_upload(src) or rewrite_site_urls(src)
        caption_match = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", block, flags=re.DOTALL | re.IGNORECASE)
        md = f"![{alt}]({local})"
        if caption_match:
            md += f"\n\n*{strip_tags(caption_match.group(1))}*"
        return f"\n\n{md}\n\n"

    html_text = re.sub(r"<figure[^>]*>.*?</figure>", figure_repl, html_text, flags=re.DOTALL | re.IGNORECASE)

    # Standalone images.
    def img_md(src: str, alt: str = "") -> str:
        local = downloader.download_upload(src) or rewrite_site_urls(src)
        return f"![{html.unescape(alt)}]({local})"

    html_text = re.sub(
        r'<img[^>]*src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']*)["\'][^>]*/?>',
        lambda m: img_md(m.group(1), m.group(2)),
        html_text,
        flags=re.IGNORECASE,
    )
    html_text = re.sub(
        r'<img[^>]*alt=["\']([^"\']*)["\'][^>]*src=["\']([^"\']+)["\'][^>]*/?>',
        lambda m: img_md(m.group(2), m.group(1)),
        html_text,
        flags=re.IGNORECASE,
    )
    html_text = re.sub(
        r'<img[^>]*src=["\']([^"\']+)["\'][^>]*/?>',
        lambda m: img_md(m.group(1)),
        html_text,
        flags=re.IGNORECASE,
    )

    # Headings.
    for level in range(6, 0, -1):
        html_text = re.sub(
            rf"<h{level}[^>]*>(.*?)</h{level}>",
            lambda m, lvl=level: f"\n\n{'#' * lvl} {strip_tags(m.group(1))}\n\n",
            html_text,
            flags=re.DOTALL | re.IGNORECASE,
        )

    # Lists.
    def list_repl(match: re.Match[str]) -> str:
        items = re.findall(r"<li[^>]*>(.*?)</li>", match.group(1), flags=re.DOTALL | re.IGNORECASE)
        lines = []
        for item in items:
            text = inline_markup(item)
            if text:
                lines.append(f"- {text}")
        return "\n\n" + "\n".join(lines) + "\n\n" if lines else ""

    html_text = re.sub(r"<ul[^>]*>(.*?)</ul>", list_repl, html_text, flags=re.DOTALL | re.IGNORECASE)
    html_text = re.sub(r"<ol[^>]*>(.*?)</ol>", list_repl, html_text, flags=re.DOTALL | re.IGNORECASE)

    # Paragraphs and breaks.
    html_text = re.sub(r"<hr[^>]*/?>", "\n\n---\n\n", html_text, flags=re.IGNORECASE)
    html_text = re.sub(
        r"<p[^>]*>(.*?)</p>",
        lambda m: f"\n\n{inline_markup(m.group(1))}\n\n" if strip_tags(m.group(1)) else "",
        html_text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Remove remaining wrappers.
    html_text = re.sub(r"</?(?:div|main|section|article|span)[^>]*>", "\n", html_text, flags=re.IGNORECASE)
    html_text = re.sub(r"<[^>]+>", "", html_text)
    html_text = html.unescape(html_text)
    html_text = re.sub(r"\n{3,}", "\n\n", html_text)
    html_text = re.sub(r"[ \t]+\n", "\n", html_text)
    html_text = rewrite_site_urls(html_text.strip())
    return html_text


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def extract_description(content_html: str, title: str) -> str:
    if not content_html:
        return title
    stripped = strip_wp_comments(content_html)
    para = re.search(r"<p[^>]*>(.*?)</p>", stripped, flags=re.DOTALL | re.IGNORECASE)
    if para:
        text = strip_tags(para.group(1))
        if text:
            return text[:200]
    return title


def extract_partners(html_text: str, downloader: AssetDownloader) -> list[dict[str, str]]:
    partners: list[dict[str, str]] = []
    groups = re.findall(
        r'<div class="wp-block-group"[^>]*>(.*?)</div>\s*<!-- /wp:group -->',
        html_text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for group in groups:
        href_match = re.search(r'<a[^>]*href=["\']([^"\']+)["\']', group, flags=re.IGNORECASE)
        img_match = re.search(r'<img[^>]*src=["\']([^"\']+)["\']', group, flags=re.IGNORECASE)
        name = ""
        link_match = re.search(
            r'<p[^>]*>\s*<a[^>]*>(.*?)</a>\s*</p>', group, flags=re.DOTALL | re.IGNORECASE
        )
        if link_match:
            name = strip_tags(link_match.group(1))
        if not name and img_match:
            name = Path(img_match.group(1)).stem.replace("-", " ").replace("_", " ")
        if not name:
            continue
        logo = ""
        if img_match:
            logo = downloader.download_upload(img_match.group(1)) or ""
        partner: dict[str, str] = {"name": name}
        if logo:
            partner["logo"] = logo
        if href_match:
            partner["href"] = href_match.group(1)
        partners.append(partner)
    return partners


def write_partners_ts(partners: list[dict[str, str]]) -> None:
    lines = [
        "export const partners = [",
    ]
    for partner in partners:
        fields: list[str] = [f"name: {json.dumps(partner['name'], ensure_ascii=False)}"]
        if partner.get("logo"):
            fields.append(f"logo: {json.dumps(partner['logo'], ensure_ascii=False)}")
        if partner.get("href"):
            fields.append(f"href: {json.dumps(partner['href'], ensure_ascii=False)}")
        lines.append("  { " + ", ".join(fields) + " },")
    lines.append("] as const;")
    lines.append("")
    lines.append("export type Partner = (typeof partners)[number];")
    lines.append("")
    PARTNERS_FILE.write_text("\n".join(lines), encoding="utf-8")


def get_attachment_url(attachment_id: int, attachments: dict[int, dict[str, Any]]) -> str:
    att = attachments.get(attachment_id)
    if not att:
        return ""
    return att.get("attachment_url") or att.get("guid", "")


def build_album_from_slider(
    slider_id: int,
    slides: list[dict[str, Any]],
    attachments: dict[int, dict[str, Any]],
    downloader: AssetDownloader,
    title: str,
    year: int,
    slug: str,
) -> tuple[str, list[str]]:
    slider_slides = [s for s in slides if s.get("ml_slider_id") == slider_id]
    slider_slides.sort(key=lambda s: s.get("menu_order", 0))
    image_paths: list[str] = []
    for slide in slider_slides:
        thumb_id = int(slide.get("meta", {}).get("_thumbnail_id", 0) or 0)
        url = get_attachment_url(thumb_id, attachments)
        if not url:
            continue
        local = downloader.download_upload(url)
        if local:
            image_paths.append(local)
    cover = image_paths[0] if image_paths else ""
    frontmatter = [
        "---",
        f"title: {yaml_quote(title)}",
        f"year: {year}",
        f"path: {yaml_quote(slug)}",
        f"cover: {yaml_quote(cover)}",
        "images:",
    ]
    for path in image_paths:
        frontmatter.append(f"  - {yaml_quote(path)}")
    frontmatter.append("---")
    frontmatter.append("")
    body = f"Album photo : **{title}** ({year})."
    album_filename = f"{slug}.md"
    (ALBUMS_DIR / album_filename).write_text("\n".join(frontmatter) + body + "\n", encoding="utf-8")
    return album_filename, image_paths


def slug_to_filename(slug: str) -> str:
    return slug.replace("/", "-") + ".md"


def main() -> int:
    xml_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_XML
    if not xml_path.exists():
        print(f"ERROR: export file not found: {xml_path}", file=sys.stderr)
        return 1

    print(f"Reading {xml_path}...")
    xml_text = read_export(xml_path)
    items = parse_items(xml_text)

    pages = {
        item["post_id"]: item
        for item in items
        if item.get("post_type") == "page" and item.get("status") == "publish"
    }
    attachments = {
        item["post_id"]: item
        for item in items
        if item.get("post_type") == "attachment"
    }
    slides = [item for item in items if item.get("post_type") == "ml-slide"]
    paths = build_page_paths(pages)

    slug_to_page: dict[str, dict[str, Any]] = {}
    for pid, full_slug in paths.items():
        if full_slug in slug_to_page:
            existing = slug_to_page[full_slug]
            if pages[pid].get("post_modified", "") > existing.get("post_modified", ""):
                slug_to_page[full_slug] = pages[pid]
        else:
            slug_to_page[full_slug] = pages[pid]

    downloader = AssetDownloader()
    created_files: list[str] = []
    issues: list[str] = []

    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    ALBUMS_DIR.mkdir(parents=True, exist_ok=True)

    # Album from metaslider 295.
    album_file, album_images = build_album_from_slider(
        slider_id=295,
        slides=slides,
        attachments=attachments,
        downloader=downloader,
        title="Camp d'été 2021",
        year=2021,
        slug="camp-ete-2021",
    )
    created_files.append(f"src/content/albums/{album_file}")
    if not album_images:
        issues.append("No images found for metaslider album id 295")

    partners: list[dict[str, str]] = []

    for slug in sorted(TARGET_SLUGS):
        page = slug_to_page.get(slug)
        if not page:
            issues.append(f"Page not found in export: {slug}")
            continue

        title = page.get("title") or slug.split("/")[-1]
        content_html = page.get("content", "")
        layout = LAYOUT_BY_SLUG.get(slug, "default")
        order = page.get("menu_order", 0)
        description = extract_description(content_html, title)

        if slug == "partenaires":
            partners = extract_partners(content_html, downloader)

        body = convert_html_to_markdown(content_html, downloader)

        if slug == "a-propos/photos":
            body = body.replace(
                "_Voir l'album photo « Camp d'été 2021 » ci-dessous._",
                "[Camp d'été 2021](/albums/camp-ete-2021/)",
            )
            if "[Camp d'été 2021" not in body:
                body += "\n\n## Albums\n\n- [Camp d'été 2021](/albums/camp-ete-2021/)\n"

        frontmatter = [
            "---",
            f"title: {yaml_quote(title)}",
            f"description: {yaml_quote(description)}",
            f"path: {yaml_quote(slug)}",
            f"layout: {layout}",
            f"order: {order}",
            "draft: false",
            "---",
            "",
        ]
        filename = slug_to_filename(slug)
        out_path = PAGES_DIR / filename
        out_path.write_text("\n".join(frontmatter) + body + "\n", encoding="utf-8")
        created_files.append(f"src/content/pages/{filename}")
        print(f"  wrote {out_path.relative_to(ROOT)}")

    if partners:
        write_partners_ts(partners)
        created_files.append("src/data/partners.ts")
        print(f"  wrote {PARTNERS_FILE.relative_to(ROOT)} ({len(partners)} partners)")
    else:
        issues.append("No partners extracted from partenaires page")

    print()
    print("=== Migration summary ===")
    print(f"Pages created: {len([f for f in created_files if f.startswith('src/content/pages')])}")
    print(f"Albums created: {len([f for f in created_files if f.startswith('src/content/albums')])}")
    print(f"Images downloaded: {downloader.downloaded_images}")
    print(f"Documents downloaded: {downloader.downloaded_documents}")
    print()
    print("Created files:")
    for path in created_files:
        print(f"  - {path}")
    if issues:
        print()
        print("Issues:")
        for issue in issues:
            print(f"  - {issue}")
    if downloader.failed:
        print()
        print(f"Download failures ({len(downloader.failed)}):")
        for fail in downloader.failed[:20]:
            print(f"  - {fail}")
        if len(downloader.failed) > 20:
            print(f"  ... and {len(downloader.failed) - 20} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
