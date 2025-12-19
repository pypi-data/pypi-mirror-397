"""
Lightweight SEO helpers for templates and JSON.
"""
from typing import Dict, Optional, Tuple
from html.parser import HTMLParser


def seo_context(
    title: str,
    description: str = "",
    canonical: Optional[str] = None,
    og_image: Optional[str] = None,
) -> Dict[str, str]:
    """Return a dict you can pass into templates or JSON responses."""
    ctx = {"title": title, "description": description}
    if canonical:
        ctx["canonical"] = canonical
    if og_image:
        ctx["og_image"] = og_image
    return ctx


def seo_meta_tags(ctx: Dict[str, str]) -> str:
    """Render basic SEO/meta tags as a string for inclusion in <head>."""
    title = ctx.get("title", "")
    desc = ctx.get("description", "")
    canonical = ctx.get("canonical")
    og_image = ctx.get("og_image")

    parts = [
        f"<title>{title}</title>",
        f'<meta name="description" content="{desc}">',
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{desc}">',
        '<meta property="og:type" content="website">',
    ]
    if canonical:
        parts.append(f'<link rel="canonical" href="{canonical}">')
        parts.append(f'<meta property="og:url" content="{canonical}">')
    if og_image:
        parts.append(f'<meta property="og:image" content="{og_image}">')
        parts.append(f'<meta name="twitter:card" content="summary_large_image">')
        parts.append(f'<meta name="twitter:image" content="{og_image}">')
    return "\n".join(parts)


class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_title = False
        self.title_text = ""
        self.in_title = False
        self.meta = {}
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() == "meta":
            if "name" in attrs_dict and "content" in attrs_dict:
                self.meta[attrs_dict["name"].lower()] = attrs_dict["content"]
            if "property" in attrs_dict and "content" in attrs_dict:
                self.meta[attrs_dict["property"].lower()] = attrs_dict["content"]
        if tag.lower() == "link":
            self.links.append(attrs_dict)

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False
            self.has_title = True

    def handle_data(self, data):
        if self.in_title:
            self.title_text += data.strip()


def audit_html_for_seo(html: str, defaults: Optional[Dict[str, str]] = None, inject: bool = False) -> Tuple[Dict[str, bool], str]:
    """
    Check an HTML string for basic SEO tags. Optionally inject defaults into <head>.

    Returns (report, html_out)
    report: dict of flags like {'has_title': True/False, 'has_description': True/False, ...}
    """
    parser = _MetaParser()
    parser.feed(html)
    report = {
        "has_title": parser.has_title and bool(parser.title_text),
        "has_description": "description" in parser.meta,
        "has_canonical": any(link.get("rel") == "canonical" for link in parser.links if isinstance(link.get("rel"), str)),
        "has_og_title": "og:title" in parser.meta,
        "has_og_description": "og:description" in parser.meta,
        "has_og_image": "og:image" in parser.meta,
    }

    if not inject:
        return report, html

    defaults = defaults or {}
    injections = []
    if not report["has_title"] and defaults.get("title"):
        injections.append(f"<title>{defaults['title']}</title>")
    if not report["has_description"] and defaults.get("description"):
        injections.append(f'<meta name="description" content="{defaults["description"]}">')
    if not report["has_canonical"] and defaults.get("canonical"):
        injections.append(f'<link rel="canonical" href="{defaults["canonical"]}">')
    if not report["has_og_title"] and defaults.get("title"):
        injections.append(f'<meta property="og:title" content="{defaults["title"]}">')
    if not report["has_og_description"] and defaults.get("description"):
        injections.append(f'<meta property="og:description" content="{defaults["description"]}">')
    if not report["has_og_image"] and defaults.get("og_image"):
        injections.append(f'<meta property="og:image" content="{defaults["og_image"]}">')

    if injections:
        if "<head>" in html:
            html = html.replace("<head>", "<head>\n" + "\n".join(injections), 1)
        else:
            html = "\n".join(injections) + "\n" + html

    return report, html


__all__ = ["seo_context", "seo_meta_tags", "audit_html_for_seo"]
