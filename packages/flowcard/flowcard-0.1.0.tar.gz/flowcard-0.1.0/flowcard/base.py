# Standard Library
from base64 import b64encode

# Third Party
import magic
from jinja2 import Template  # noqa

# Flowcard
from flowcard.component import Component

# Initialize magic for MIME type detection
m = magic.Magic(mime=True)


class Title(Component):
    name = "title"

    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text

    def to_html(self) -> dict[str, str]:
        return {"head": f"<title>{self.text}</title>", "body": f"<h1>{self.text}</h1>"}

    def to_markdown(self) -> str:
        return f"# {self.text}"


class Favicon(Component):
    name = "favicon"

    def __init__(self, image_data: bytes) -> None:
        super().__init__()
        self.base64 = b64encode(image_data).decode(encoding="ascii")
        self.mime = m.from_buffer(image_data)

    def to_html(self) -> dict[str, str]:
        return {
            "head": f"<link rel='icon' type='{self.mime}'  href='data:{self.mime};base64,{self.base64}'/>",
            "body": "",
        }

    def to_markdown(self) -> str:
        return ""


class Image(Component):
    name = "image"

    def __init__(self, image_data: bytes, width: int | None = None, height: int | None = None) -> None:
        super().__init__()
        self.base64 = b64encode(image_data).decode(encoding="ascii")
        self.mime = m.from_buffer(image_data)

    def to_html(self) -> dict[str, str]:
        return {
            "head": "",
            "body": f"<img type='{self.mime}'  src='data:{self.mime};base64,{self.base64}'/>",
        }

    def to_markdown(self) -> str:
        return f"<img type='{self.mime}'  src='data:{self.mime};base64,{self.base64}'/>"


class Header(Component):
    name = "header"

    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text

    def to_html(self) -> dict[str, str]:
        return {"head": "", "body": f"<h2>{self.text}</h2>"}

    def to_markdown(self) -> str:
        return f"## {self.text}"


class Code(Component):
    """Component for displaying code blocks with syntax highlighting."""
    name = "code"

    def __init__(self, code: str, language: str = "python") -> None:
        """Initializes the Code component.

        Args:
            code: The code content to display.
            language: The programming language for syntax highlighting. Defaults to "python".
        """
        super().__init__()
        self.code = code.strip() # Strip leading/trailing whitespace
        self.language = language

    def to_html(self) -> dict[str, str]:
        """Converts the code block to its HTML representation.

        Returns:
            A dictionary containing the HTML string for the code block.
            The HTML includes <pre> and <code> tags, with a language-specific
            class for syntax highlighting.
        """
        # Basic HTML structure for a code block.
        # In a real scenario, a JavaScript library like Prism.js or highlight.js
        # would be used on the client-side for actual syntax highlighting.
        # This HTML provides the necessary structure.
        return {
            "head": "",
            "body": f'<pre><code class="language-{self.language}">{self.code}</code></pre>',
        }

    def to_markdown(self) -> str:
        """Converts the code block to its Markdown representation.

        Returns:
            A string containing the Markdown for the code block,
            using triple backticks and specifying the language.
        """
        return f"```{self.language}\n{self.code}\n```"


class Paragraph(Component):
    """Component for displaying a paragraph of text."""
    name = "paragraph"

    def __init__(self, content: str, markdown: bool = True) -> None:
        """Initializes the Paragraph component.

        Args:
            content: The text content of the paragraph.
            markdown: Whether to process Markdown syntax within the content.
                      Defaults to True. (Currently, this flag is noted but
                      full Markdown processing within the paragraph itself
                      is a future enhancement).
        """
        super().__init__()
        self.content = content
        self.markdown = markdown # Stored for future use

    def to_html(self) -> dict[str, str]:
        """Converts the paragraph to its HTML representation.

        Returns:
            A dictionary with an empty "head" and the paragraph HTML in "body".
        """
        # For now, we directly use the content.
        # Markdown processing would happen here if implemented.
        return {"head": "", "body": f"<p>{self.content}</p>"}

    def to_markdown(self) -> str:
        """Converts the paragraph to its Markdown representation.

        Returns:
            The paragraph content as a string.
        """
        # For now, returns content directly.
        # If markdown=True, a library like mistune or markdown-it-py could be used.
        return f"{self.content}"
