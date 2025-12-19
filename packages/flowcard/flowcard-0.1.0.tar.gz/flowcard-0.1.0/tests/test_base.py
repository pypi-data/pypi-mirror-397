# Flowcard
from flowcard.base import Title


def test_title_component():
    title = Title("Hello World")
    
    # Test HTML output
    html = title.to_html()
    assert html["head"] == "<title>Hello World</title>"
    assert html["body"] == "<h1>Hello World</h1>"
    
    # Test Markdown output
    assert title.to_markdown() == "# Hello World"
