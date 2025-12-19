"""Example demonstrating the Code component in FlowCard."""

# Flowcard
from flowcard import Flowcard

def create_code_example_report():
    """Creates a FlowCard report demonstrating the code component."""
    fc = Flowcard()

    fc.title(text="Code Component Demonstration")

    fc.paragraph(
        content="FlowCard allows you to easily embed code blocks into your reports. "
                "Here's an example of a Python code snippet:"
    )

    python_code = """
def greet(name: str) -> str:
    return f"Hello, {name}!"

print(greet(name="FlowCard User"))
"""
    fc.code(code=python_code, language="python")

    fc.paragraph(
        content="You can specify the language for syntax highlighting. "
                "The above block should be highlighted as Python code."
    )
    
    fc.header(text="Another Code Example: JavaScript")
    fc.paragraph(content="Here is a JavaScript example:")
    
    javascript_code = """
function welcome(message) {
  console.log(message);
}

welcome('Welcome to FlowCard code demos!');
"""
    fc.code(code=javascript_code, language="javascript")

    # Save the report
    output_path_html = "output/code_example.html"
    output_path_md = "output/code_example.md"
    
    fc.save(filepath=output_path_html)
    fc.save(filepath=output_path_md)
    
    print(f"Report saved to {output_path_html} and {output_path_md}")

if __name__ == "__main__":
    create_code_example_report()
