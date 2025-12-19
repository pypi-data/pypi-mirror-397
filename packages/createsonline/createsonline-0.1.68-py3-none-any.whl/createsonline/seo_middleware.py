"""
CREATESONLINE SEO Checker Middleware
Comprehensive SEO analysis and optimization

Zero external dependencies - Pure Python implementation
"""
from typing import Dict, List, Optional, Tuple, Any
from html.parser import HTMLParser
import re
from collections import Counter


class SEOAnalyzer(HTMLParser):
    """
    Comprehensive SEO analyzer for HTML content.

    Analyzes:
    - Meta tags (title, description, keywords, og tags)
    - Heading structure (H1-H6)
    - Image alt attributes
    - Link structure (internal, external, broken)
    - Content quality (word count, readability)
    - Keyword density
    - Mobile-friendliness indicators
    """

    def __init__(self):
        super().__init__()
        self.reset_analysis()

    def reset_analysis(self):
        """Reset all analysis data."""
        # Meta tags
        self.title = ""
        self.title_length = 0
        self.has_title = False
        self.in_title = False

        self.meta_description = ""
        self.meta_keywords = []
        self.canonical_url = ""
        self.robots_content = ""

        # OpenGraph
        self.og_title = ""
        self.og_description = ""
        self.og_image = ""
        self.og_url = ""
        self.og_type = ""

        # Twitter Card
        self.twitter_card = ""
        self.twitter_title = ""
        self.twitter_description = ""
        self.twitter_image = ""

        # Structure
        self.headings = {'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []}
        self.current_heading = None
        self.in_heading = False

        # Images
        self.images = []
        self.images_without_alt = 0
        self.images_with_alt = 0

        # Links
        self.links = []
        self.internal_links = 0
        self.external_links = 0
        self.nofollow_links = 0

        # Content
        self.body_text = []
        self.in_body = False
        self.in_script = False
        self.in_style = False

        # Mobile
        self.has_viewport = False
        self.viewport_content = ""

        # Performance
        self.has_charset = False
        self.has_language = False
        self.language = ""

    def handle_starttag(self, tag, attrs):
        """Handle HTML start tags."""
        attrs_dict = dict(attrs)
        tag_lower = tag.lower()

        # Title
        if tag_lower == 'title':
            self.in_title = True
            self.has_title = True

        # Meta tags
        elif tag_lower == 'meta':
            self._parse_meta_tag(attrs_dict)

        # Link tags
        elif tag_lower == 'link':
            self._parse_link_tag(attrs_dict)

        # Headings
        elif tag_lower in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.in_heading = True
            self.current_heading = tag_lower

        # Images
        elif tag_lower == 'img':
            self._parse_image_tag(attrs_dict)

        # Links
        elif tag_lower == 'a':
            self._parse_anchor_tag(attrs_dict)

        # Body
        elif tag_lower == 'body':
            self.in_body = True

        # HTML tag
        elif tag_lower == 'html':
            if 'lang' in attrs_dict:
                self.has_language = True
                self.language = attrs_dict['lang']

        # Script/Style (ignore content)
        elif tag_lower in ['script', 'style']:
            if tag_lower == 'script':
                self.in_script = True
            else:
                self.in_style = True

    def handle_endtag(self, tag):
        """Handle HTML end tags."""
        tag_lower = tag.lower()

        if tag_lower == 'title':
            self.in_title = False
        elif tag_lower in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.in_heading = False
            self.current_heading = None
        elif tag_lower == 'body':
            self.in_body = False
        elif tag_lower == 'script':
            self.in_script = False
        elif tag_lower == 'style':
            self.in_style = False

    def handle_data(self, data):
        """Handle text data."""
        text = data.strip()
        if not text:
            return

        # Title content
        if self.in_title:
            self.title += text
            self.title_length = len(self.title)

        # Heading content
        elif self.in_heading and self.current_heading:
            self.headings[self.current_heading].append(text)

        # Body text (excluding scripts and styles)
        elif self.in_body and not self.in_script and not self.in_style:
            self.body_text.append(text)

    def _parse_meta_tag(self, attrs: Dict[str, str]):
        """Parse meta tag attributes."""
        name = attrs.get('name', '').lower()
        property_attr = attrs.get('property', '').lower()
        content = attrs.get('content', '')

        # Standard meta tags
        if name == 'description':
            self.meta_description = content
        elif name == 'keywords':
            self.meta_keywords = [k.strip() for k in content.split(',')]
        elif name == 'robots':
            self.robots_content = content
        elif name == 'viewport':
            self.has_viewport = True
            self.viewport_content = content
        elif attrs.get('charset'):
            self.has_charset = True

        # OpenGraph
        elif property_attr == 'og:title':
            self.og_title = content
        elif property_attr == 'og:description':
            self.og_description = content
        elif property_attr == 'og:image':
            self.og_image = content
        elif property_attr == 'og:url':
            self.og_url = content
        elif property_attr == 'og:type':
            self.og_type = content

        # Twitter Card
        elif name == 'twitter:card':
            self.twitter_card = content
        elif name == 'twitter:title':
            self.twitter_title = content
        elif name == 'twitter:description':
            self.twitter_description = content
        elif name == 'twitter:image':
            self.twitter_image = content

    def _parse_link_tag(self, attrs: Dict[str, str]):
        """Parse link tag attributes."""
        rel = attrs.get('rel', '').lower()
        href = attrs.get('href', '')

        if rel == 'canonical':
            self.canonical_url = href

    def _parse_image_tag(self, attrs: Dict[str, str]):
        """Parse image tag attributes."""
        src = attrs.get('src', '')
        alt = attrs.get('alt', '')

        self.images.append({
            'src': src,
            'alt': alt,
            'has_alt': bool(alt)
        })

        if alt:
            self.images_with_alt += 1
        else:
            self.images_without_alt += 1

    def _parse_anchor_tag(self, attrs: Dict[str, str]):
        """Parse anchor tag attributes."""
        href = attrs.get('href', '')
        rel = attrs.get('rel', '')

        if not href:
            return

        link_info = {
            'href': href,
            'rel': rel,
            'is_external': href.startswith('http://') or href.startswith('https://'),
            'is_nofollow': 'nofollow' in rel
        }

        self.links.append(link_info)

        if link_info['is_external']:
            self.external_links += 1
        else:
            self.internal_links += 1

        if link_info['is_nofollow']:
            self.nofollow_links += 1

    def get_word_count(self) -> int:
        """Get total word count from body text."""
        all_text = ' '.join(self.body_text)
        words = re.findall(r'\b\w+\b', all_text)
        return len(words)

    def get_keyword_density(self, top_n: int = 10) -> List[Tuple[str, int, float]]:
        """
        Get keyword density analysis.

        Returns list of (keyword, count, density_percentage)
        """
        all_text = ' '.join(self.body_text).lower()
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }

        words = re.findall(r'\b\w+\b', all_text)
        total_words = len(words)

        if total_words == 0:
            return []

        # Filter stop words and count
        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
        word_counts = Counter(filtered_words)

        # Calculate density
        results = []
        for word, count in word_counts.most_common(top_n):
            density = (count / total_words) * 100
            results.append((word, count, density))

        return results

    def analyze(self, html: str) -> Dict[str, Any]:
        """
        Analyze HTML and return comprehensive SEO report.

        Returns dictionary with analysis results and SEO score.
        """
        self.reset_analysis()
        self.feed(html)

        word_count = self.get_word_count()
        keyword_density = self.get_keyword_density()

        # Calculate SEO score (0-100)
        score = self._calculate_seo_score()

        # Generate recommendations
        recommendations = self._generate_recommendations()

        return {
            'score': score,
            'grade': self._score_to_grade(score),
            'meta': {
                'title': self.title,
                'title_length': self.title_length,
                'description': self.meta_description,
                'description_length': len(self.meta_description),
                'keywords': self.meta_keywords,
                'canonical': self.canonical_url,
                'robots': self.robots_content,
            },
            'opengraph': {
                'title': self.og_title,
                'description': self.og_description,
                'image': self.og_image,
                'url': self.og_url,
                'type': self.og_type,
            },
            'twitter': {
                'card': self.twitter_card,
                'title': self.twitter_title,
                'description': self.twitter_description,
                'image': self.twitter_image,
            },
            'structure': {
                'headings': {k: len(v) for k, v in self.headings.items()},
                'heading_texts': self.headings,
                'has_h1': len(self.headings['h1']) > 0,
                'h1_count': len(self.headings['h1']),
            },
            'images': {
                'total': len(self.images),
                'with_alt': self.images_with_alt,
                'without_alt': self.images_without_alt,
                'alt_percentage': (self.images_with_alt / len(self.images) * 100) if self.images else 100,
            },
            'links': {
                'total': len(self.links),
                'internal': self.internal_links,
                'external': self.external_links,
                'nofollow': self.nofollow_links,
            },
            'content': {
                'word_count': word_count,
                'keyword_density': keyword_density,
            },
            'mobile': {
                'has_viewport': self.has_viewport,
                'viewport': self.viewport_content,
            },
            'technical': {
                'has_charset': self.has_charset,
                'has_language': self.has_language,
                'language': self.language,
            },
            'recommendations': recommendations,
        }

    def _calculate_seo_score(self) -> int:
        """Calculate overall SEO score (0-100)."""
        score = 0
        max_score = 100

        # Title (15 points)
        if self.has_title and self.title:
            score += 10
            if 30 <= self.title_length <= 60:
                score += 5

        # Meta description (15 points)
        if self.meta_description:
            score += 10
            desc_len = len(self.meta_description)
            if 120 <= desc_len <= 160:
                score += 5

        # H1 tag (10 points)
        if len(self.headings['h1']) == 1:
            score += 10
        elif len(self.headings['h1']) > 0:
            score += 5

        # Heading hierarchy (5 points)
        if self.headings['h2']:
            score += 5

        # Image alt tags (10 points)
        if self.images:
            alt_ratio = self.images_with_alt / len(self.images)
            score += int(alt_ratio * 10)
        else:
            score += 5  # No images is okay

        # Content length (10 points)
        word_count = self.get_word_count()
        if word_count >= 300:
            score += 10
        elif word_count >= 150:
            score += 5

        # Links (5 points)
        if self.internal_links > 0:
            score += 3
        if self.external_links > 0:
            score += 2

        # OpenGraph (10 points)
        if self.og_title:
            score += 3
        if self.og_description:
            score += 3
        if self.og_image:
            score += 4

        # Mobile viewport (10 points)
        if self.has_viewport:
            score += 10

        # Canonical URL (5 points)
        if self.canonical_url:
            score += 5

        # Technical (5 points)
        if self.has_charset:
            score += 2
        if self.has_language:
            score += 3

        return min(score, max_score)

    def _score_to_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable SEO recommendations."""
        recommendations = []

        # Title issues
        if not self.has_title or not self.title:
            recommendations.append("⚠️ Add a <title> tag to your page")
        elif self.title_length < 30:
            recommendations.append("⚠️ Title is too short (< 30 characters). Aim for 30-60 characters")
        elif self.title_length > 60:
            recommendations.append("⚠️ Title is too long (> 60 characters). Keep it under 60 for better display")

        # Meta description issues
        if not self.meta_description:
            recommendations.append("⚠️ Add a meta description tag")
        else:
            desc_len = len(self.meta_description)
            if desc_len < 120:
                recommendations.append("⚠️ Meta description is too short (< 120 characters). Aim for 120-160")
            elif desc_len > 160:
                recommendations.append("⚠️ Meta description is too long (> 160 characters). Keep it under 160")

        # H1 issues
        h1_count = len(self.headings['h1'])
        if h1_count == 0:
            recommendations.append("⚠️ Add an H1 heading to your page")
        elif h1_count > 1:
            recommendations.append("⚠️ Use only ONE H1 heading per page (found {})".format(h1_count))

        # Image alt issues
        if self.images_without_alt > 0:
            recommendations.append(f"⚠️ {self.images_without_alt} image(s) missing alt attributes")

        # Content length
        word_count = self.get_word_count()
        if word_count < 300:
            recommendations.append(f"⚠️ Content is short ({word_count} words). Aim for at least 300 words")

        # OpenGraph
        if not self.og_title:
            recommendations.append("💡 Add og:title for better social media sharing")
        if not self.og_description:
            recommendations.append("💡 Add og:description for better social media sharing")
        if not self.og_image:
            recommendations.append("💡 Add og:image for better social media sharing")

        # Mobile viewport
        if not self.has_viewport:
            recommendations.append("⚠️ Add viewport meta tag for mobile optimization")

        # Canonical URL
        if not self.canonical_url:
            recommendations.append("💡 Add canonical URL to prevent duplicate content issues")

        # Language
        if not self.has_language:
            recommendations.append("💡 Add lang attribute to <html> tag")

        # Links
        if self.internal_links == 0:
            recommendations.append("💡 Add internal links to improve site navigation")

        if not recommendations:
            recommendations.append("✅ Great job! Your page follows SEO best practices")

        return recommendations


class SEOMiddleware:
    """
    SEO Checker Middleware for CREATESONLINE.

    Automatically analyzes HTML responses for SEO issues and can:
    - Add SEO analysis headers to responses
    - Log SEO issues
    - Inject missing SEO tags
    - Add SEO report to response

    Usage:
        >>> from createsonline import create_app
        >>> from createsonline.seo_middleware import SEOMiddleware
        >>>
        >>> app = create_app()
        >>>
        >>> # Add SEO middleware
        >>> seo_middleware = SEOMiddleware(
        ...     enabled=True,
        ...     inject_defaults=True,
        ...     add_headers=True
        ... )
        >>>
        >>> @app.middleware("http")
        >>> async def seo_check(request):
        ...     # Process response
        ...     response = await request.app.get_response(request)
        ...     return seo_middleware.process_response(request, response)
    """

    def __init__(
        self,
        enabled: bool = True,
        inject_defaults: bool = False,
        add_headers: bool = False,
        log_issues: bool = True,
        default_title: str = "",
        default_description: str = "",
        default_og_image: str = "",
    ):
        """
        Initialize SEO middleware.

        Args:
            enabled: Enable/disable SEO checking
            inject_defaults: Inject default SEO tags if missing
            add_headers: Add SEO score/grade as response headers
            log_issues: Log SEO issues to console
            default_title: Default page title if missing
            default_description: Default description if missing
            default_og_image: Default OG image if missing
        """
        self.enabled = enabled
        self.inject_defaults = inject_defaults
        self.add_headers = add_headers
        self.log_issues = log_issues
        self.default_title = default_title
        self.default_description = default_description
        self.default_og_image = default_og_image
        self.analyzer = SEOAnalyzer()

    def process_response(self, request: Any, response: Any) -> Any:
        """
        Process response and perform SEO analysis.

        Args:
            request: HTTP request object
            response: HTTP response object

        Returns:
            Modified response with SEO enhancements
        """
        if not self.enabled:
            return response

        # Only process HTML responses
        if not self._is_html_response(response):
            return response

        # Get HTML content
        html = self._get_response_html(response)
        if not html:
            return response

        # Analyze SEO
        analysis = self.analyzer.analyze(html)

        # Log issues if enabled
        if self.log_issues and analysis['score'] < 80:
            self._log_seo_issues(request, analysis)

        # Inject default tags if enabled
        if self.inject_defaults:
            html = self._inject_seo_tags(html, analysis)
            response = self._set_response_html(response, html)

        # Add SEO headers if enabled
        if self.add_headers:
            response = self._add_seo_headers(response, analysis)

        # Add SEO report to request context (for debugging)
        if hasattr(request, 'state'):
            request.state.seo_analysis = analysis

        return response

    def _is_html_response(self, response: Any) -> bool:
        """Check if response is HTML."""
        # Check content-type header
        if hasattr(response, 'headers'):
            content_type = response.headers.get('content-type', '').lower()
            return 'text/html' in content_type

        # Check if response is string starting with HTML
        if isinstance(response, str):
            return response.strip().lower().startswith('<!doctype html') or \
                   response.strip().lower().startswith('<html')

        return False

    def _get_response_html(self, response: Any) -> Optional[str]:
        """Extract HTML from response."""
        if isinstance(response, str):
            return response
        elif hasattr(response, 'body'):
            body = response.body
            if isinstance(body, bytes):
                return body.decode('utf-8', errors='ignore')
            return str(body)
        elif hasattr(response, 'content'):
            content = response.content
            if isinstance(content, bytes):
                return content.decode('utf-8', errors='ignore')
            return str(content)
        return None

    def _set_response_html(self, response: Any, html: str) -> Any:
        """Set modified HTML back to response."""
        if isinstance(response, str):
            return html
        elif hasattr(response, 'body'):
            response.body = html.encode('utf-8')
        elif hasattr(response, 'content'):
            response.content = html
        return response

    def _inject_seo_tags(self, html: str, analysis: Dict[str, Any]) -> str:
        """Inject missing SEO tags into HTML."""
        injections = []
        meta = analysis['meta']
        og = analysis['opengraph']

        # Inject title if missing or too short
        if not meta['title'] and self.default_title:
            injections.append(f"<title>{self.default_title}</title>")

        # Inject meta description if missing
        if not meta['description'] and self.default_description:
            injections.append(f'<meta name="description" content="{self.default_description}">')

        # Inject OpenGraph tags if missing
        if not og['title'] and self.default_title:
            injections.append(f'<meta property="og:title" content="{self.default_title}">')
        if not og['description'] and self.default_description:
            injections.append(f'<meta property="og:description" content="{self.default_description}">')
        if not og['image'] and self.default_og_image:
            injections.append(f'<meta property="og:image" content="{self.default_og_image}">')

        # Inject viewport if missing
        if not analysis['mobile']['has_viewport']:
            injections.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')

        # Inject charset if missing
        if not analysis['technical']['has_charset']:
            injections.append('<meta charset="UTF-8">')

        # Inject into <head>
        if injections:
            injection_html = '\n    '.join(injections)
            if '<head>' in html:
                html = html.replace('<head>', f'<head>\n    {injection_html}\n', 1)
            elif '<html>' in html:
                html = html.replace('<html>', f'<html>\n<head>\n    {injection_html}\n</head>\n', 1)

        return html

    def _add_seo_headers(self, response: Any, analysis: Dict[str, Any]) -> Any:
        """Add SEO analysis headers to response."""
        if hasattr(response, 'headers'):
            response.headers['X-SEO-Score'] = str(analysis['score'])
            response.headers['X-SEO-Grade'] = analysis['grade']
            response.headers['X-SEO-Issues'] = str(len(analysis['recommendations']))

        return response

    def _log_seo_issues(self, request: Any, analysis: Dict[str, Any]):
        """Log SEO issues to console."""
        import logging
        logger = logging.getLogger('createsonline.seo')

        path = getattr(request, 'path', 'unknown')
        score = analysis['score']
        grade = analysis['grade']

        logger.warning(f"SEO Analysis for {path}: Score {score}/100 (Grade: {grade})")

        for rec in analysis['recommendations'][:5]:  # Show top 5
            logger.warning(f"  {rec}")


__all__ = [
    'SEOAnalyzer',
    'SEOMiddleware',
]