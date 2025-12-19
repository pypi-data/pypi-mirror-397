"""FlowCard Example 02: Basic Components

This example demonstrates the core components available in FlowCard:
- Title
- Images (with embedded data)
- Multiple output formats
"""

# Standard Library
import io
from pathlib import Path

# Third Party
try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  Pillow not installed. Install with: pip install Pillow")

# Flowcard
import flowcard as fc


def create_sample_image() -> bytes:
    """Create a simple sample image for demonstration.
    
    Returns:
        Image data as bytes.
    """
    if not PIL_AVAILABLE:
        # Return a placeholder if PIL is not available
        return b"placeholder_image_data"
    
    # Create a simple colored rectangle
    img = Image.new(mode='RGB', size=(400, 200), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Add some text
    draw.text(xy=(50, 80), text="Sample FlowCard Image", fill='darkblue')
    draw.rectangle(xy=[20, 20, 380, 180], outline='navy', width=3)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


def main() -> None:
    """Create a document demonstrating basic FlowCard components."""
    # Create a new FlowCard document
    card = fc.Flowcard()
    
    # Add title
    card.title(text="FlowCard Basic Components Demo")

    # Add a header
    card.header(text="This is a Section Header (H2)")

    # Add an image from bytes data
    if PIL_AVAILABLE:
        sample_image_data = create_sample_image()
        card.image(image_data=sample_image_data)
        print("✅ Generated sample image")
    else:
        print("⚠️  Skipping image generation (Pillow not available)")
    
    # Create favicon (small icon for HTML)
    if PIL_AVAILABLE:
        # Create a small favicon
        favicon_img = Image.new(mode='RGB', size=(32, 32), color='blue')
        favicon_bytes = io.BytesIO()
        favicon_img.save(favicon_bytes, format='ICO')
        card.favicon(image_data=favicon_bytes.getvalue())
        print("✅ Generated favicon")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Save in multiple formats
    card.save(filepath="output/basic_components.html")
    card.save(filepath="output/basic_components.md")
    
    print("✅ Basic components example completed!")
    print("📁 Generated files:")
    print("   - output/basic_components.html")
    print("   - output/basic_components.md")
    
    # Display some info about the generated content
    print("\n📊 Content summary:")
    html_content = card.to_html()
    md_content = card.to_markdown()
    print(f"   - HTML: {len(html_content)} characters")
    print(f"   - Markdown: {len(md_content)} characters")


if __name__ == "__main__":
    main()