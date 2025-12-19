"""Tests for mdpres - Markdown to HTML Presentation Generator."""

import tempfile
from pathlib import Path

import pytest

from mdpres import (
    THEMES,
    HTMLRenderer,
    SlideParser,
    build,
    build_file,
    get_themes,
)


class TestSlideParser:
    """Tests for SlideParser class."""

    def test_parse_simple_slides(self) -> None:
        """Test parsing markdown with multiple slides."""
        content = """# Slide 1

---

## Slide 2

---

## Slide 3"""
        parser = SlideParser(content).parse()

        assert len(parser.slides) == 3
        assert "# Slide 1" in parser.slides[0]["content"]
        assert "## Slide 2" in parser.slides[1]["content"]
        assert "## Slide 3" in parser.slides[2]["content"]

    def test_parse_frontmatter(self) -> None:
        """Test YAML frontmatter extraction."""
        content = """---
title: My Presentation
author: John Doe
---

# Welcome"""
        parser = SlideParser(content).parse()

        assert parser.metadata.get("title") == "My Presentation"
        assert parser.metadata.get("author") == "John Doe"
        assert len(parser.slides) == 1

    def test_parse_empty_frontmatter(self) -> None:
        """Test parsing without frontmatter."""
        content = "# Just a slide"
        parser = SlideParser(content).parse()

        assert parser.metadata == {}
        assert len(parser.slides) == 1

    def test_title_slide_detection(self) -> None:
        """Test that first slide with h1 gets title-slide class."""
        content = """# Main Title

Subtitle here

---

## Regular Slide"""
        parser = SlideParser(content).parse()

        assert "title-slide" in parser.slides[0]["classes"]
        assert "title-slide" not in parser.slides[1]["classes"]

    def test_slide_directives(self) -> None:
        """Test HTML comment directives parsing."""
        content = """<!-- class: special centered -->
<!-- type: custom -->

# Slide with directives"""
        parser = SlideParser(content).parse()

        assert "special" in parser.slides[0]["classes"]
        assert "centered" in parser.slides[0]["classes"]
        assert parser.slides[0]["type"] == "custom"

    def test_directives_removed_from_content(self) -> None:
        """Test that directives are removed from slide content."""
        content = """<!-- class: test -->

# Clean Content"""
        parser = SlideParser(content).parse()

        assert "<!--" not in parser.slides[0]["content"]
        assert "# Clean Content" in parser.slides[0]["content"]

    def test_empty_slides_ignored(self) -> None:
        """Test that empty slide sections are ignored."""
        content = """# Slide 1

---

---

## Slide 2"""
        parser = SlideParser(content).parse()

        assert len(parser.slides) == 2


class TestHTMLRenderer:
    """Tests for HTMLRenderer class."""

    def test_render_basic_html(self) -> None:
        """Test basic HTML output structure."""
        content = "# Hello World"
        parser = SlideParser(content).parse()
        renderer = HTMLRenderer(parser, theme="dark")
        html = renderer.render()

        assert "<!DOCTYPE html>" in html
        assert "<title>Presentation</title>" in html
        assert "Hello World" in html

    def test_render_with_title_from_metadata(self) -> None:
        """Test that title comes from frontmatter."""
        content = """---
title: Custom Title
---

# Slide"""
        parser = SlideParser(content).parse()
        html = HTMLRenderer(parser).render()

        assert "<title>Custom Title</title>" in html

    def test_theme_application(self) -> None:
        """Test that theme colors are applied."""
        content = "# Test"
        parser = SlideParser(content).parse()

        dark_html = HTMLRenderer(parser, theme="dark").render()
        light_html = HTMLRenderer(parser, theme="light").render()

        assert THEMES["dark"]["bg_primary"] in dark_html
        assert THEMES["light"]["bg_primary"] in light_html

    def test_invalid_theme_falls_back_to_dark(self) -> None:
        """Test fallback to dark theme for invalid theme name."""
        content = "# Test"
        parser = SlideParser(content).parse()
        html = HTMLRenderer(parser, theme="nonexistent").render()

        assert THEMES["dark"]["bg_primary"] in html

    def test_first_slide_has_active_class(self) -> None:
        """Test that first slide is marked as active."""
        content = """# First

---

# Second"""
        parser = SlideParser(content).parse()
        html = HTMLRenderer(parser).render()

        assert 'class="slide title-slide active"' in html

    def test_inline_markdown_bold(self) -> None:
        """Test bold text rendering."""
        renderer = HTMLRenderer(SlideParser("").parse())

        assert renderer._inline_markdown("**bold**") == "<strong>bold</strong>"
        assert renderer._inline_markdown("__bold__") == "<strong>bold</strong>"

    def test_inline_markdown_italic(self) -> None:
        """Test italic text rendering."""
        renderer = HTMLRenderer(SlideParser("").parse())

        assert renderer._inline_markdown("*italic*") == "<em>italic</em>"
        assert renderer._inline_markdown("_italic_") == "<em>italic</em>"

    def test_inline_markdown_code(self) -> None:
        """Test inline code rendering."""
        renderer = HTMLRenderer(SlideParser("").parse())

        assert renderer._inline_markdown("`code`") == "<code>code</code>"

    def test_inline_markdown_links(self) -> None:
        """Test link rendering."""
        renderer = HTMLRenderer(SlideParser("").parse())
        result = renderer._inline_markdown("[text](https://example.com)")

        assert result == '<a href="https://example.com">text</a>'

    def test_inline_markdown_images(self) -> None:
        """Test image rendering."""
        renderer = HTMLRenderer(SlideParser("").parse())
        result = renderer._inline_markdown("![alt](image.png)")

        assert result == '<img src="image.png" alt="alt">'

    def test_render_headers(self) -> None:
        """Test header rendering."""
        content = """# H1

## H2

### H3"""
        parser = SlideParser(content).parse()
        html = HTMLRenderer(parser).render()

        assert "<h1>" in html
        assert "<h2>" in html
        assert "<h3>" in html

    def test_render_unordered_list(self) -> None:
        """Test unordered list rendering."""
        content = """- Item 1
- Item 2
- Item 3"""
        parser = SlideParser(content).parse()
        html = HTMLRenderer(parser).render()

        assert "<ul>" in html
        assert "<li>Item 1</li>" in html
        assert "</ul>" in html

    def test_render_ordered_list(self) -> None:
        """Test ordered list rendering."""
        content = """1. First
2. Second
3. Third"""
        parser = SlideParser(content).parse()
        html = HTMLRenderer(parser).render()

        assert "<ol>" in html
        assert "<li>First</li>" in html
        assert "</ol>" in html

    def test_render_blockquote(self) -> None:
        """Test blockquote rendering."""
        content = "> This is a quote"
        parser = SlideParser(content).parse()
        html = HTMLRenderer(parser).render()

        assert "<blockquote>This is a quote</blockquote>" in html

    def test_render_code_block(self) -> None:
        """Test code block rendering."""
        content = """```python
def hello():
    pass
```"""
        parser = SlideParser(content).parse()
        html = HTMLRenderer(parser).render()

        assert "<pre><code" in html
        assert "language-python" in html
        assert "def hello():" in html

    def test_render_mermaid_block(self) -> None:
        """Test mermaid diagram rendering."""
        content = """```mermaid
graph LR
    A --> B
```"""
        parser = SlideParser(content).parse()
        html = HTMLRenderer(parser).render()

        assert '<div class="mermaid">' in html
        assert "graph LR" in html
        assert "A --> B" in html

    def test_html_escaping_in_code(self) -> None:
        """Test that HTML in code blocks is escaped."""
        content = """```html
<div class="test">Content</div>
```"""
        parser = SlideParser(content).parse()
        html = HTMLRenderer(parser).render()

        assert "&lt;div" in html
        assert "&gt;" in html


class TestThemes:
    """Tests for theme configuration."""

    def test_all_themes_have_required_keys(self) -> None:
        """Test that all themes have required color keys."""
        required_keys = [
            "bg_primary",
            "bg_secondary",
            "text_primary",
            "text_secondary",
            "accent",
            "code_bg",
            "mermaid_theme",
        ]

        for theme_name, theme in THEMES.items():
            for key in required_keys:
                assert key in theme, f"Theme '{theme_name}' missing key '{key}'"

    def test_available_themes(self) -> None:
        """Test that expected themes are available."""
        expected_themes = ["dark", "light", "nord", "dracula"]

        for theme in expected_themes:
            assert theme in THEMES, f"Theme '{theme}' not found"


class TestEdgeCases:
    """Tests for edge cases and potential bugs."""

    def test_empty_content(self) -> None:
        """Test handling of empty content."""
        parser = SlideParser("").parse()

        assert len(parser.slides) == 0

    def test_whitespace_only_content(self) -> None:
        """Test handling of whitespace-only content."""
        parser = SlideParser("   \n\n   ").parse()

        assert len(parser.slides) == 0

    def test_single_slide_no_separator(self) -> None:
        """Test single slide without separators."""
        content = "# Just one slide\n\nWith some content"
        parser = SlideParser(content).parse()

        assert len(parser.slides) == 1

    def test_special_characters_in_content(self) -> None:
        """Test handling of special characters."""
        content = '# Title with <special> & "characters"'
        parser = SlideParser(content).parse()
        html = HTMLRenderer(parser).render()

        assert "&lt;special&gt;" in html or "<special>" in html

    def test_nested_formatting(self) -> None:
        """Test nested inline formatting."""
        renderer = HTMLRenderer(SlideParser("").parse())
        result = renderer._inline_markdown("**bold with `code` inside**")

        assert "<strong>" in result
        assert "<code>code</code>" in result

    def test_multiple_code_blocks(self) -> None:
        """Test multiple code blocks in one slide."""
        content = """```python
code1
```

Some text

```javascript
code2
```"""
        parser = SlideParser(content).parse()
        html = HTMLRenderer(parser).render()

        assert "code1" in html
        assert "code2" in html
        assert "language-python" in html
        assert "language-javascript" in html


class TestPublicAPI:
    """Tests for public API functions."""

    def test_build_simple(self) -> None:
        """Test build function with simple markdown."""
        html = build("# Hello World")

        assert "<!DOCTYPE html>" in html
        assert "Hello World" in html

    def test_build_with_theme(self) -> None:
        """Test build function with theme parameter."""
        html = build("# Test", theme="nord")

        assert THEMES["nord"]["bg_primary"] in html

    def test_build_multiple_slides(self) -> None:
        """Test build function with multiple slides."""
        markdown = """# Slide 1

---

## Slide 2

---

## Slide 3"""
        html = build(markdown)

        assert "Slide 1" in html
        assert "Slide 2" in html
        assert "Slide 3" in html

    def test_build_file_creates_output(self) -> None:
        """Test build_file creates HTML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "test.md"
            input_path.write_text("# Test Slide")

            output = build_file(input_path)

            assert output.exists()
            assert output.suffix == ".html"
            assert "Test Slide" in output.read_text()

    def test_build_file_custom_output(self) -> None:
        """Test build_file with custom output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.md"
            output_path = Path(tmpdir) / "custom.html"
            input_path.write_text("# Custom")

            result = build_file(input_path, output_path)

            assert result == output_path
            assert output_path.exists()

    def test_build_file_with_theme(self) -> None:
        """Test build_file with theme parameter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "test.md"
            input_path.write_text("# Themed")

            output = build_file(input_path, theme="dracula")
            html = output.read_text()

            assert THEMES["dracula"]["bg_primary"] in html

    def test_build_file_not_found(self) -> None:
        """Test build_file raises error for missing file."""
        with pytest.raises(FileNotFoundError):
            build_file("nonexistent.md")

    def test_build_file_accepts_string_paths(self) -> None:
        """Test build_file accepts string paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = f"{tmpdir}/test.md"
            Path(input_path).write_text("# String Path")

            output = build_file(input_path)

            assert output.exists()

    def test_get_themes(self) -> None:
        """Test get_themes returns available themes."""
        themes = get_themes()

        assert isinstance(themes, list)
        assert "dark" in themes
        assert "light" in themes
        assert "nord" in themes
        assert "dracula" in themes

    def test_get_themes_matches_themes_dict(self) -> None:
        """Test get_themes matches THEMES dictionary."""
        themes = get_themes()

        assert set(themes) == set(THEMES.keys())
