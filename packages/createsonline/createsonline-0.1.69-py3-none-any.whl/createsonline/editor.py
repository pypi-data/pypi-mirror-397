"""
CREATESONLINE Built-in Rich Text Editor
Advanced WYSIWYG editor with Wagtail/TinyMCE-level features

Pure Python - Zero external dependencies
Features: Full formatting, tables, images, code blocks, markdown support, auto-save
"""
from typing import Optional, Dict, Any, List


def rich_text_widget(
    name: str = "content",
    value: str = "",
    height: int = 400,
    placeholder: str = "Start writing...",
    autosave: bool = False,
    autosave_interval: int = 30000,
    upload_url: str = "/api/uploads",
    toolbar: str = "full",
    max_image_size: int = 5242880,  # 5MB in bytes
    theme: str = "light",
    **kwargs
) -> str:
    """
    Generate HTML for the advanced rich text editor widget.

    Args:
        name: Form field name for the textarea
        value: Initial HTML content
        height: Editor height in pixels (default: 400)
        placeholder: Placeholder text when empty
        autosave: Enable auto-save feature (default: False)
        autosave_interval: Auto-save interval in milliseconds (default: 30000 = 30s)
        upload_url: Endpoint for image uploads (default: /api/uploads)
        toolbar: Toolbar configuration ("full", "basic", "minimal", or custom)
        max_image_size: Maximum image upload size in bytes (default: 5MB)
        theme: Editor theme ("light" or "dark")
        **kwargs: Additional data attributes

    Returns:
        HTML string for the rich text editor

    Example:
        >>> from createsonline.editor import rich_text_widget
        >>>
        >>> # Basic usage
        >>> html = rich_text_widget(name="content", value="<p>Hello</p>")
        >>>
        >>> # Advanced usage with auto-save
        >>> html = rich_text_widget(
        ...     name="article_content",
        ...     value="",
        ...     height=600,
        ...     autosave=True,
        ...     toolbar="full",
        ...     upload_url="/admin/upload"
        ... )
        >>>
        >>> # In a template/view
        >>> return f'''
        ... <form method="POST">
        ...     <label>Article Content:</label>
        ...     {rich_text_widget(name="content")}
        ...     <button type="submit">Save</button>
        ... </form>
        ... '''
    """
    # Build data attributes
    data_attrs = {
        'autosave': 'true' if autosave else 'false',
        'autosave-interval': str(autosave_interval),
        'upload-url': upload_url,
        'max-image-size': str(max_image_size),
        **kwargs
    }

    data_attrs_str = ' '.join([f'data-{k}="{v}"' for k, v in data_attrs.items()])

    # Get toolbar HTML based on configuration
    toolbar_html = _get_toolbar_html(toolbar)

    # Escape value for HTML safety
    escaped_value = value.replace('"', '&quot;')

    return f"""
<link rel="stylesheet" href="/static/rte.css">
<div class="rte" {data_attrs_str}>
  {toolbar_html}
  <div class="rte-editor"
       contenteditable="true"
       data-target="{name}"
       style="min-height:{height}px"
       data-placeholder="{placeholder}">{value}</div>
  <textarea name="{name}" class="rte-output" hidden>{escaped_value}</textarea>
</div>
<script src="/static/rte.js"></script>
    """.strip()


def _get_toolbar_html(toolbar_type: str = "full") -> str:
    """Generate toolbar HTML based on configuration."""

    toolbars = {
        "full": _get_full_toolbar(),
        "basic": _get_basic_toolbar(),
        "minimal": _get_minimal_toolbar(),
        "blog": _get_blog_toolbar(),
        "document": _get_document_toolbar(),
    }

    return toolbars.get(toolbar_type, _get_full_toolbar())


def _get_full_toolbar() -> str:
    """Full-featured toolbar with all options."""
    return """
  <div class="rte-toolbar">
    <!-- History -->
    <button type="button" data-cmd="undo" title="Undo (Ctrl+Z)">↶</button>
    <button type="button" data-cmd="redo" title="Redo (Ctrl+Y)">↷</button>

    <span class="rte-toolbar-separator"></span>

    <!-- Text Formatting -->
    <button type="button" data-cmd="bold" title="Bold (Ctrl+B)"><b>B</b></button>
    <button type="button" data-cmd="italic" title="Italic (Ctrl+I)"><i>I</i></button>
    <button type="button" data-cmd="underline" title="Underline (Ctrl+U)"><u>U</u></button>
    <button type="button" data-cmd="strikeThrough" title="Strikethrough"><s>S</s></button>

    <span class="rte-toolbar-separator"></span>

    <!-- Headings -->
    <button type="button" data-cmd="formatBlock" data-value="h1" title="Heading 1">H1</button>
    <button type="button" data-cmd="formatBlock" data-value="h2" title="Heading 2">H2</button>
    <button type="button" data-cmd="formatBlock" data-value="h3" title="Heading 3">H3</button>
    <button type="button" data-cmd="formatBlock" data-value="p" title="Paragraph">P</button>

    <span class="rte-toolbar-separator"></span>

    <!-- Lists -->
    <button type="button" data-cmd="insertUnorderedList" title="Bulleted List">• List</button>
    <button type="button" data-cmd="insertOrderedList" title="Numbered List">1. List</button>
    <button type="button" data-cmd="indent" title="Indent (Tab)">→</button>
    <button type="button" data-cmd="outdent" title="Outdent (Shift+Tab)">←</button>

    <span class="rte-toolbar-separator"></span>

    <!-- Alignment -->
    <button type="button" data-cmd="justifyLeft" title="Align Left">⬅</button>
    <button type="button" data-cmd="justifyCenter" title="Align Center">⬌</button>
    <button type="button" data-cmd="justifyRight" title="Align Right">➡</button>
    <button type="button" data-cmd="justifyFull" title="Justify">⬍</button>

    <span class="rte-toolbar-separator"></span>

    <!-- Insert -->
    <button type="button" data-cmd="createLink" title="Insert Link (Ctrl+K)">🔗</button>
    <button type="button" data-cmd="insertImage" title="Upload Image">📷</button>
    <button type="button" data-cmd="insertImageUrl" title="Insert Image from URL">🖼️</button>
    <button type="button" data-cmd="insertTable" title="Insert Table">📊</button>
    <button type="button" data-cmd="insertCode" title="Code Block">&lt;/&gt;</button>
    <button type="button" data-cmd="insertHorizontalRule" title="Horizontal Line">—</button>
    <button type="button" data-cmd="formatBlock" data-value="blockquote" title="Quote">"</button>

    <span class="rte-toolbar-separator"></span>

    <!-- Formatting -->
    <button type="button" data-cmd="foreColor" title="Text Color">A</button>
    <button type="button" data-cmd="backColor" title="Background Color">🎨</button>
    <button type="button" data-cmd="fontName" title="Font Family">Font</button>
    <button type="button" data-cmd="fontSize" title="Font Size">Size</button>

    <span class="rte-toolbar-separator"></span>

    <!-- Special -->
    <button type="button" data-cmd="insertMarkdown" title="Convert Markdown">MD</button>
    <button type="button" data-cmd="findReplace" title="Find & Replace (Ctrl+F)">🔍</button>
    <button type="button" data-cmd="clearFormatting" title="Clear Formatting">✗</button>

    <span class="rte-toolbar-separator"></span>

    <!-- View -->
    <button type="button" data-cmd="toggleSource" title="View HTML Source">&lt;HTML&gt;</button>
    <button type="button" data-cmd="toggleFullscreen" title="Fullscreen">⛶</button>
  </div>
    """.strip()


def _get_basic_toolbar() -> str:
    """Basic toolbar with essential formatting."""
    return """
  <div class="rte-toolbar">
    <button type="button" data-cmd="undo" title="Undo">↶</button>
    <button type="button" data-cmd="redo" title="Redo">↷</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="bold" title="Bold"><b>B</b></button>
    <button type="button" data-cmd="italic" title="Italic"><i>I</i></button>
    <button type="button" data-cmd="underline" title="Underline"><u>U</u></button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="formatBlock" data-value="h2" title="Heading">H2</button>
    <button type="button" data-cmd="formatBlock" data-value="p" title="Paragraph">P</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="insertUnorderedList" title="Bulleted List">• List</button>
    <button type="button" data-cmd="insertOrderedList" title="Numbered List">1. List</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="createLink" title="Link">🔗</button>
    <button type="button" data-cmd="insertImage" title="Image">📷</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="clearFormatting" title="Clear">✗</button>
  </div>
    """.strip()


def _get_minimal_toolbar() -> str:
    """Minimal toolbar for simple formatting."""
    return """
  <div class="rte-toolbar">
    <button type="button" data-cmd="bold" title="Bold"><b>B</b></button>
    <button type="button" data-cmd="italic" title="Italic"><i>I</i></button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="createLink" title="Link">🔗</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="clearFormatting" title="Clear">✗</button>
  </div>
    """.strip()


def _get_blog_toolbar() -> str:
    """Toolbar optimized for blog post writing."""
    return """
  <div class="rte-toolbar">
    <button type="button" data-cmd="undo" title="Undo">↶</button>
    <button type="button" data-cmd="redo" title="Redo">↷</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="bold" title="Bold"><b>B</b></button>
    <button type="button" data-cmd="italic" title="Italic"><i>I</i></button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="formatBlock" data-value="h2" title="Heading 2">H2</button>
    <button type="button" data-cmd="formatBlock" data-value="h3" title="Heading 3">H3</button>
    <button type="button" data-cmd="formatBlock" data-value="p" title="Paragraph">P</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="insertUnorderedList" title="Bulleted List">• List</button>
    <button type="button" data-cmd="insertOrderedList" title="Numbered List">1. List</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="createLink" title="Link">🔗</button>
    <button type="button" data-cmd="insertImage" title="Image">📷</button>
    <button type="button" data-cmd="insertCode" title="Code">&lt;/&gt;</button>
    <button type="button" data-cmd="formatBlock" data-value="blockquote" title="Quote">"</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="insertMarkdown" title="Markdown">MD</button>
    <button type="button" data-cmd="toggleFullscreen" title="Fullscreen">⛶</button>
  </div>
    """.strip()


def _get_document_toolbar() -> str:
    """Toolbar optimized for document editing."""
    return """
  <div class="rte-toolbar">
    <button type="button" data-cmd="undo" title="Undo">↶</button>
    <button type="button" data-cmd="redo" title="Redo">↷</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="bold" title="Bold"><b>B</b></button>
    <button type="button" data-cmd="italic" title="Italic"><i>I</i></button>
    <button type="button" data-cmd="underline" title="Underline"><u>U</u></button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="formatBlock" data-value="h1" title="Heading 1">H1</button>
    <button type="button" data-cmd="formatBlock" data-value="h2" title="Heading 2">H2</button>
    <button type="button" data-cmd="formatBlock" data-value="h3" title="Heading 3">H3</button>
    <button type="button" data-cmd="formatBlock" data-value="p" title="Paragraph">P</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="insertUnorderedList" title="Bulleted List">• List</button>
    <button type="button" data-cmd="insertOrderedList" title="Numbered List">1. List</button>
    <button type="button" data-cmd="indent" title="Indent">→</button>
    <button type="button" data-cmd="outdent" title="Outdent">←</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="justifyLeft" title="Align Left">⬅</button>
    <button type="button" data-cmd="justifyCenter" title="Align Center">⬌</button>
    <button type="button" data-cmd="justifyRight" title="Align Right">➡</button>
    <button type="button" data-cmd="justifyFull" title="Justify">⬍</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="insertTable" title="Table">📊</button>
    <button type="button" data-cmd="insertImage" title="Image">📷</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="fontName" title="Font">Font</button>
    <button type="button" data-cmd="fontSize" title="Size">Size</button>
    <span class="rte-toolbar-separator"></span>
    <button type="button" data-cmd="findReplace" title="Find">🔍</button>
    <button type="button" data-cmd="toggleFullscreen" title="Fullscreen">⛶</button>
  </div>
    """.strip()


def rich_text_field_class(**options):
    """
    Create a reusable rich text field class for form integration.

    Example:
        >>> from createsonline.editor import rich_text_field_class
        >>>
        >>> # Define custom field
        >>> ContentField = rich_text_field_class(
        ...     height=600,
        ...     autosave=True,
        ...     toolbar="blog"
        ... )
        >>>
        >>> # Use in forms
        >>> class ArticleForm:
        ...     def __init__(self):
        ...         self.content = ContentField
    """
    class RichTextField:
        def __init__(self, name: str, value: str = ""):
            self.name = name
            self.value = value
            self.options = options

        def render(self) -> str:
            return rich_text_widget(
                name=self.name,
                value=self.value,
                **self.options
            )

        def __str__(self) -> str:
            return self.render()

    return RichTextField


# Convenience aliases
rte_widget = rich_text_widget
RichTextWidget = rich_text_widget


__all__ = [
    "rich_text_widget",
    "rte_widget",
    "RichTextWidget",
    "rich_text_field_class",
]