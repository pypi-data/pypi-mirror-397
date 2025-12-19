#!/usr/bin/env python3
"""
mdpres - Markdown to HTML Presentation Generator

CLI Usage:
    mdpres build input.md [-o output.html] [--theme dark|light]
    mdpres example                          # Generate example.md

Library Usage:
    from mdpres import build, build_file

    # Convert markdown string to HTML
    html = build("# Title\\n\\n---\\n\\n## Slide 2", theme="dark")

    # Convert file to file
    build_file("slides.md", "output.html", theme="nord")
"""

import argparse
import html
import re
import sys
from pathlib import Path
from typing import Any

__all__ = [
    "build",
    "build_file",
    "get_themes",
    "SlideParser",
    "HTMLRenderer",
    "THEMES",
    "EXAMPLE_MD",
]


# ============================================================================
# HTML Template
# ============================================================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --bg-primary: {bg_primary};
            --bg-secondary: {bg_secondary};
            --text-primary: {text_primary};
            --text-secondary: {text_secondary};
            --accent: {accent};
            --code-bg: {code_bg};
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            overflow: hidden;
            height: 100vh;
        }}
        
        .presentation {{
            height: 100vh;
            width: 100vw;
            position: relative;
        }}
        
        .slide {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            padding: 60px 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.4s ease, transform 0.4s ease;
            transform: translateX(30px);
            background: var(--bg-primary);
        }}
        
        .slide.active {{
            opacity: 1;
            visibility: visible;
            transform: translateX(0);
        }}
        
        .slide.prev {{
            transform: translateX(-30px);
        }}
        
        /* Typography */
        .slide h1 {{
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
            line-height: 1.2;
        }}
        
        .slide h2 {{
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: 1.2rem;
            color: var(--text-primary);
        }}
        
        .slide h3 {{
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--text-secondary);
        }}
        
        .slide p {{
            font-size: 1.4rem;
            line-height: 1.8;
            margin-bottom: 1rem;
            color: var(--text-secondary);
        }}
        
        .slide ul, .slide ol {{
            font-size: 1.3rem;
            line-height: 2;
            margin-left: 2rem;
            color: var(--text-secondary);
        }}
        
        .slide li {{
            margin-bottom: 0.5rem;
        }}
        
        .slide code {{
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            background: var(--code-bg);
            padding: 0.2em 0.5em;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        .slide pre {{
            background: var(--code-bg);
            padding: 1.5rem;
            border-radius: 12px;
            overflow-x: auto;
            margin: 1rem 0;
        }}
        
        .slide pre code {{
            background: none;
            padding: 0;
            font-size: 1rem;
            line-height: 1.6;
        }}
        
        .slide blockquote {{
            border-left: 4px solid var(--accent);
            padding-left: 1.5rem;
            margin: 1.5rem 0;
            font-style: italic;
            color: var(--text-secondary);
        }}
        
        .slide a {{
            color: var(--accent);
            text-decoration: none;
        }}
        
        .slide a:hover {{
            text-decoration: underline;
        }}
        
        /* Mermaid diagrams */
        .mermaid {{
            display: flex;
            justify-content: center;
            margin: 2rem 0;
        }}
        
        .mermaid svg {{
            max-width: 100%;
            height: auto;
        }}
        
        /* Title slide */
        .slide.title-slide {{
            text-align: center;
            justify-content: center;
            align-items: center;
        }}
        
        .slide.title-slide h1 {{
            font-size: 4.5rem;
            margin-bottom: 1rem;
        }}
        
        .slide.title-slide p {{
            font-size: 1.8rem;
        }}
        
        /* Navigation */
        .nav {{
            position: fixed;
            bottom: 30px;
            right: 40px;
            display: flex;
            gap: 10px;
            z-index: 100;
        }}
        
        .nav button {{
            width: 50px;
            height: 50px;
            border: none;
            border-radius: 50%;
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-size: 1.2rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .nav button:hover {{
            background: var(--accent);
            transform: scale(1.1);
        }}
        
        .nav button:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
            transform: none;
        }}
        
        /* Progress bar */
        .progress {{
            position: fixed;
            bottom: 0;
            left: 0;
            height: 4px;
            background: var(--accent);
            transition: width 0.3s ease;
            z-index: 100;
        }}
        
        /* Slide counter */
        .counter {{
            position: fixed;
            bottom: 40px;
            left: 40px;
            font-size: 1rem;
            color: var(--text-secondary);
            opacity: 0.7;
        }}
        
        /* Keyboard hint */
        .hint {{
            position: fixed;
            top: 20px;
            right: 20px;
            font-size: 0.8rem;
            color: var(--text-secondary);
            opacity: 0.5;
        }}
        
        /* Two column layout */
        .columns {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            width: 100%;
        }}
        
        .column {{
            display: flex;
            flex-direction: column;
        }}
        
        /* Image styling */
        .slide img {{
            max-width: 100%;
            max-height: 60vh;
            border-radius: 12px;
            margin: 1rem 0;
        }}
        
        /* Tables */
        .slide table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 1.1rem;
        }}
        
        .slide th, .slide td {{
            padding: 0.8rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--bg-secondary);
        }}
        
        .slide th {{
            background: var(--bg-secondary);
            font-weight: 600;
        }}
        
        /* Print styles */
        @media print {{
            .slide {{
                page-break-after: always;
                position: relative;
                opacity: 1;
                visibility: visible;
                transform: none;
                height: 100vh;
            }}
            .nav, .progress, .counter, .hint {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="presentation">
        {slides_html}
    </div>
    
    <div class="nav">
        <button id="prev" title="Previous (←)">←</button>
        <button id="next" title="Next (→)">→</button>
    </div>
    
    <div class="progress" id="progress"></div>
    <div class="counter" id="counter"></div>
    <div class="hint">← → to navigate | f for fullscreen</div>
    
    <script>
        // Initialize Mermaid
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: '{mermaid_theme}',
            flowchart: {{ 
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }}
        }});
        
        // Presentation logic
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;
        let currentSlide = 0;
        
        function showSlide(index) {{
            // Clamp index
            index = Math.max(0, Math.min(index, totalSlides - 1));
            
            // Update slides
            slides.forEach((slide, i) => {{
                slide.classList.remove('active', 'prev');
                if (i === index) {{
                    slide.classList.add('active');
                }} else if (i < index) {{
                    slide.classList.add('prev');
                }}
            }});
            
            currentSlide = index;
            
            // Update UI
            document.getElementById('prev').disabled = index === 0;
            document.getElementById('next').disabled = index === totalSlides - 1;
            document.getElementById('progress').style.width = ((index + 1) / totalSlides * 100) + '%';
            document.getElementById('counter').textContent = (index + 1) + ' / ' + totalSlides;
            
            // Update URL hash
            history.replaceState(null, null, '#' + (index + 1));
        }}
        
        function nextSlide() {{
            showSlide(currentSlide + 1);
        }}
        
        function prevSlide() {{
            showSlide(currentSlide - 1);
        }}
        
        // Event listeners
        document.getElementById('next').addEventListener('click', nextSlide);
        document.getElementById('prev').addEventListener('click', prevSlide);
        
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {{
                e.preventDefault();
                nextSlide();
            }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
                e.preventDefault();
                prevSlide();
            }} else if (e.key === 'Home') {{
                e.preventDefault();
                showSlide(0);
            }} else if (e.key === 'End') {{
                e.preventDefault();
                showSlide(totalSlides - 1);
            }} else if (e.key === 'f') {{
                if (document.fullscreenElement) {{
                    document.exitFullscreen();
                }} else {{
                    document.documentElement.requestFullscreen();
                }}
            }}
        }});
        
        // Touch support
        let touchStartX = 0;
        document.addEventListener('touchstart', (e) => {{
            touchStartX = e.touches[0].clientX;
        }});
        
        document.addEventListener('touchend', (e) => {{
            const touchEndX = e.changedTouches[0].clientX;
            const diff = touchStartX - touchEndX;
            if (Math.abs(diff) > 50) {{
                if (diff > 0) nextSlide();
                else prevSlide();
            }}
        }});
        
        // Initialize from URL hash
        const hash = parseInt(window.location.hash.slice(1));
        showSlide(hash ? hash - 1 : 0);
    </script>
</body>
</html>
"""


# ============================================================================
# Themes
# ============================================================================

THEMES = {
    "dark": {
        "bg_primary": "#0f0f0f",
        "bg_secondary": "#1a1a2e",
        "text_primary": "#ffffff",
        "text_secondary": "#a0a0a0",
        "accent": "#6366f1",
        "code_bg": "#1e1e2e",
        "mermaid_theme": "dark",
    },
    "light": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f5f5f5",
        "text_primary": "#1a1a1a",
        "text_secondary": "#666666",
        "accent": "#4f46e5",
        "code_bg": "#f8f8f8",
        "mermaid_theme": "default",
    },
    "nord": {
        "bg_primary": "#2e3440",
        "bg_secondary": "#3b4252",
        "text_primary": "#eceff4",
        "text_secondary": "#d8dee9",
        "accent": "#88c0d0",
        "code_bg": "#3b4252",
        "mermaid_theme": "dark",
    },
    "dracula": {
        "bg_primary": "#282a36",
        "bg_secondary": "#44475a",
        "text_primary": "#f8f8f2",
        "text_secondary": "#bd93f9",
        "accent": "#ff79c6",
        "code_bg": "#44475a",
        "mermaid_theme": "dark",
    },
}


# ============================================================================
# Markdown Parser
# ============================================================================


class SlideParser:
    """
    Parse markdown into slides with metadata.

    Attributes:
        content: Original markdown content
        metadata: Parsed YAML frontmatter (title, author, etc.)
        slides: List of parsed slide dictionaries

    Example:
        >>> parser = SlideParser("# Title\\n---\\n## Slide 2").parse()
        >>> print(len(parser.slides))
        2
    """

    def __init__(self, content: str):
        self.content = content
        self.metadata: dict[str, Any] = {}
        self.slides: list[dict[str, Any]] = []

    def parse(self) -> "SlideParser":
        """Parse the markdown content."""
        content = self.content

        # Extract YAML frontmatter if present
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                self._parse_frontmatter(parts[1])
                content = parts[2]

        # Split into slides by horizontal rule
        slide_contents = re.split(r"\n---\n", content)

        for i, slide_content in enumerate(slide_contents):
            slide_content = slide_content.strip()
            if slide_content:
                slide = self._parse_slide(slide_content, i)
                self.slides.append(slide)

        return self

    def _parse_frontmatter(self, yaml_content: str):
        """Parse YAML-like frontmatter."""
        for line in yaml_content.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                self.metadata[key.strip()] = value.strip()

    def _parse_slide(self, content: str, index: int) -> dict[str, Any]:
        """Parse a single slide."""
        slide = {
            "index": index,
            "content": content,
            "type": "normal",
            "classes": [],
        }

        # Check for slide directives (HTML comments)
        directives = re.findall(r"<!--\s*(\w+):\s*(.+?)\s*-->", content)
        for key, value in directives:
            if key == "class":
                slide["classes"].extend(value.split())
            elif key == "type":
                slide["type"] = value

        # Remove directives from content
        content = re.sub(r"<!--\s*\w+:\s*.+?\s*-->\n?", "", content)
        slide["content"] = content.strip()

        # Detect title slide (first slide with just h1 and maybe subtitle)
        if index == 0:
            lines = [line for line in content.split("\n") if line.strip()]
            if len(lines) <= 3 and lines[0].startswith("# "):
                slide["classes"].append("title-slide")

        return slide


# ============================================================================
# HTML Renderer
# ============================================================================


class HTMLRenderer:
    """
    Render parsed slides to HTML presentation.

    Args:
        parser: SlideParser instance with parsed slides
        theme: Color theme name (dark, light, nord, dracula)

    Example:
        >>> parser = SlideParser("# Title").parse()
        >>> renderer = HTMLRenderer(parser, theme="nord")
        >>> html = renderer.render()
    """

    def __init__(self, parser: SlideParser, theme: str = "dark"):
        self.parser = parser
        self.theme_name = theme
        self.theme = THEMES.get(theme, THEMES["dark"])

    def render(self) -> str:
        """Render the full presentation."""
        slides_html = "\n".join(
            self._render_slide(slide) for slide in self.parser.slides
        )

        title = self.parser.metadata.get("title", "Presentation")

        return HTML_TEMPLATE.format(
            title=html.escape(title), slides_html=slides_html, **self.theme
        )

    def _render_slide(self, slide: dict[str, Any]) -> str:
        """Render a single slide."""
        classes = ["slide"] + slide["classes"]
        if slide["index"] == 0:
            classes.append("active")

        content_html = self._render_markdown(slide["content"])

        return f'<div class="{" ".join(classes)}" data-index="{slide["index"]}">\n{content_html}\n</div>'

    def _render_markdown(self, content: str) -> str:
        """Convert markdown to HTML with mermaid support."""
        # Extract mermaid blocks first
        mermaid_blocks = []

        def save_mermaid(match):
            code = match.group(1)
            placeholder = f"__MERMAID_{len(mermaid_blocks)}__"
            mermaid_blocks.append(code)
            return placeholder

        content = re.sub(
            r"```mermaid\n(.*?)```", save_mermaid, content, flags=re.DOTALL
        )

        # Extract code blocks to protect them
        code_blocks = []

        def save_code(match):
            lang = match.group(1) or ""
            code = match.group(2)
            placeholder = f"__CODE_{len(code_blocks)}__"
            code_blocks.append((lang, code))
            return placeholder

        content = re.sub(r"```(\w*)\n(.*?)```", save_code, content, flags=re.DOTALL)

        # Simple markdown conversion
        lines = content.split("\n")
        html_lines: list[str] = []
        in_list = False
        list_type: str = ""

        for line in lines:
            stripped = line.strip()

            # Check for mermaid placeholder
            if stripped.startswith("__MERMAID_"):
                if in_list:
                    html_lines.append(f"</{list_type}>")
                    in_list = False
                match = re.search(r"__MERMAID_(\d+)__", stripped)
                if match:
                    idx = int(match.group(1))
                    html_lines.append(
                        f'<div class="mermaid">\n{mermaid_blocks[idx]}\n</div>'
                    )
                continue

            # Check for code placeholder
            if stripped.startswith("__CODE_"):
                if in_list:
                    html_lines.append(f"</{list_type}>")
                    in_list = False
                match = re.search(r"__CODE_(\d+)__", stripped)
                if not match:
                    continue
                idx = int(match.group(1))
                lang, code = code_blocks[idx]
                escaped_code = html.escape(code)
                html_lines.append(
                    f'<pre><code class="language-{lang}">{escaped_code}</code></pre>'
                )
                continue

            # Headers
            if stripped.startswith("# "):
                if in_list:
                    html_lines.append(f"</{list_type}>")
                    in_list = False
                html_lines.append(f"<h1>{self._inline_markdown(stripped[2:])}</h1>")
            elif stripped.startswith("## "):
                if in_list:
                    html_lines.append(f"</{list_type}>")
                    in_list = False
                html_lines.append(f"<h2>{self._inline_markdown(stripped[3:])}</h2>")
            elif stripped.startswith("### "):
                if in_list:
                    html_lines.append(f"</{list_type}>")
                    in_list = False
                html_lines.append(f"<h3>{self._inline_markdown(stripped[4:])}</h3>")

            # Lists
            elif stripped.startswith("- ") or stripped.startswith("* "):
                if not in_list or list_type != "ul":
                    if in_list:
                        html_lines.append(f"</{list_type}>")
                    html_lines.append("<ul>")
                    in_list = True
                    list_type = "ul"
                html_lines.append(f"<li>{self._inline_markdown(stripped[2:])}</li>")

            elif re.match(r"^\d+\.\s", stripped):
                if not in_list or list_type != "ol":
                    if in_list:
                        html_lines.append(f"</{list_type}>")
                    html_lines.append("<ol>")
                    in_list = True
                    list_type = "ol"
                text = re.sub(r"^\d+\.\s", "", stripped)
                html_lines.append(f"<li>{self._inline_markdown(text)}</li>")

            # Blockquote
            elif stripped.startswith("> "):
                if in_list:
                    html_lines.append(f"</{list_type}>")
                    in_list = False
                html_lines.append(
                    f"<blockquote>{self._inline_markdown(stripped[2:])}</blockquote>"
                )

            # Empty line
            elif not stripped:
                if in_list:
                    html_lines.append(f"</{list_type}>")
                    in_list = False

            # Regular paragraph
            elif stripped:
                if in_list:
                    html_lines.append(f"</{list_type}>")
                    in_list = False
                html_lines.append(f"<p>{self._inline_markdown(stripped)}</p>")

        if in_list:
            html_lines.append(f"</{list_type}>")

        return "\n".join(html_lines)

    def _inline_markdown(self, text: str) -> str:
        """Process inline markdown (bold, italic, code, links)."""
        # Code (must be first)
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        # Bold
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
        # Italic
        text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
        text = re.sub(r"_(.+?)_", r"<em>\1</em>", text)
        # Images (must be before links)
        text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', text)
        # Links
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)

        return text


# ============================================================================
# Example Content
# ============================================================================

EXAMPLE_MD = """---
title: My Presentation
author: Your Name
---

# Welcome to mdpres

A simple markdown to presentation converter

---

## Features

- Write slides in **markdown**
- Support for `code` blocks
- **Mermaid** diagrams built-in
- Multiple themes
- Keyboard navigation

---

## Code Example

Here's some Python code:

```python
def hello(name):
    return f"Hello, {name}!"

print(hello("World"))
```

---

## Mermaid Diagrams

```mermaid
graph LR
    A[Markdown] --> B[Parser]
    B --> C[Renderer]
    C --> D[HTML]
    D --> E[Browser]
```

---

## Flowchart Example

```mermaid
flowchart TD
    Start([Start]) --> Input[/Input Data/]
    Input --> Process{Process}
    Process -->|Yes| Output[Output Result]
    Process -->|No| Error[Handle Error]
    Output --> End([End])
    Error --> End
```

---

## Lists and Formatting

### Ordered List

1. First item with **bold**
2. Second item with *italic*
3. Third item with `code`

### Unordered List

- Simple item
- Item with [link](https://example.com)
- Another item

---

## Blockquotes

> "The best way to predict the future is to invent it."
>
> — Alan Kay

---

# Thank You!

Questions?
"""


# ============================================================================
# Public API
# ============================================================================


def build(markdown: str, theme: str = "dark") -> str:
    """
    Convert markdown content to HTML presentation.

    Args:
        markdown: Markdown content with slides separated by '---'
        theme: Color theme name (dark, light, nord, dracula)

    Returns:
        Complete HTML document as string

    Example:
        >>> html = build("# Title\\n\\n---\\n\\n## Slide 2", theme="nord")
    """
    parser = SlideParser(markdown).parse()
    renderer = HTMLRenderer(parser, theme)
    return renderer.render()


def build_file(
    input_path: str | Path,
    output_path: str | Path | None = None,
    theme: str = "dark",
) -> Path:
    """
    Convert markdown file to HTML presentation file.

    Args:
        input_path: Path to input markdown file
        output_path: Path to output HTML file (default: input_name.html)
        theme: Color theme name (dark, light, nord, dracula)

    Returns:
        Path to the generated HTML file

    Raises:
        FileNotFoundError: If input file doesn't exist

    Example:
        >>> output = build_file("slides.md", theme="dracula")
        >>> print(f"Generated: {output}")
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path is None:
        output_path = input_path.with_suffix(".html")
    else:
        output_path = Path(output_path)

    content = input_path.read_text(encoding="utf-8")
    html_output = build(content, theme)
    output_path.write_text(html_output, encoding="utf-8")

    return output_path


def get_themes() -> list[str]:
    """
    Get list of available theme names.

    Returns:
        List of theme names
    """
    return list(THEMES.keys())


# ============================================================================
# CLI
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="mdpres - Markdown to HTML Presentation Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mdpres build presentation.md
  mdpres build slides.md -o output.html --theme nord
  mdpres example
  mdpres themes
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Build command
    build_parser = subparsers.add_parser(
        "build", help="Build presentation from markdown"
    )
    build_parser.add_argument("input", help="Input markdown file")
    build_parser.add_argument(
        "-o", "--output", help="Output HTML file (default: input_name.html)"
    )
    build_parser.add_argument(
        "--theme",
        choices=list(THEMES.keys()),
        default="dark",
        help="Color theme (default: dark)",
    )

    # Example command
    subparsers.add_parser("example", help="Generate example.md file")

    # Themes command
    subparsers.add_parser("themes", help="List available themes")

    args = parser.parse_args()

    if args.command == "build":
        input_path = Path(args.input)

        if not input_path.exists():
            print(f"Error: File not found: {input_path}", file=sys.stderr)
            sys.exit(1)

        output_path = (
            Path(args.output) if args.output else input_path.with_suffix(".html")
        )

        print(f"📖 Reading {input_path}...")
        content = input_path.read_text(encoding="utf-8")

        print("🔧 Parsing markdown...")
        slide_parser = SlideParser(content).parse()

        print(f"🎨 Rendering with theme '{args.theme}'...")
        renderer = HTMLRenderer(slide_parser, args.theme)
        html_output = renderer.render()

        print(f"💾 Writing {output_path}...")
        output_path.write_text(html_output, encoding="utf-8")

        print(f"✅ Done! {len(slide_parser.slides)} slides generated.")
        print(f"   Open in browser: file://{output_path.absolute()}")

    elif args.command == "example":
        example_path = Path("example.md")
        example_path.write_text(EXAMPLE_MD, encoding="utf-8")
        print(f"✅ Created {example_path}")
        print("   Build with: mdpres build example.md")

    elif args.command == "themes":
        print("Available themes:")
        for name, theme in THEMES.items():
            print(f"  • {name}")
            print(f"    Background: {theme['bg_primary']}")
            print(f"    Accent: {theme['accent']}")
            print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
