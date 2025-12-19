"""FlowCard Example 01: Hello World

This is the simplest example showing basic FlowCard usage.
"""

# Standard Library
from pathlib import Path

# Flowcard
import flowcard as fc


def main() -> None:
    """Create a simple "Hello World" document."""
    # Create a new FlowCard document
    card = fc.Flowcard()
    
    # Add a title
    card.title("Hello FlowCard! 🃏")
    
    # Save the document in both formats
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    card.save(filepath="output/hello_world.html")
    card.save(filepath="output/hello_world.md")
    
    print("✅ Hello World example completed!")
    print("📁 Check the 'output' folder for generated files:")
    print("   - hello_world.html")
    print("   - hello_world.md")


if __name__ == "__main__":
    main()