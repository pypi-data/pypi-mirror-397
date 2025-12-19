# FlowCard API Reference

This document provides detailed API reference for all FlowCard components and methods.

## 📦 Core Module

### `flowcard` - Main Module

The main module provides the primary interface for creating and managing FlowCard documents.

```python
import flowcard as fc
```

## 🏗️ Core Classes

### `Flowcard`

The main class for building and exporting documents.

```python
class Flowcard:
    def __init__(self, **kwargs) -> None
```

**Methods:**

#### `to_html(standalone: bool = True) -> str`
Export the document as HTML.

**Args:**
- `standalone`: Generate self-contained HTML without external dependencies (default: True)

**Returns:**
- `str`: Complete HTML document string

**Example:**
```python
fc = Flowcard()
fc.title("My Document")

# Generate standalone HTML (default - no external dependencies)
html_content = fc.to_html()

# Generate HTML with CDN dependencies (smaller file size)
html_content = fc.to_html(standalone=False)
```

**Standalone Mode Benefits:**
- **Offline Compatible**: Works without internet connection
- **No External Dependencies**: All CSS/JS embedded inline
- **Future-Proof**: No dependency rot over time
- **Single File**: Everything contained in one HTML file
- **Secure**: No external resource loading

#### `to_markdown() -> str`
Export the document as Markdown.

**Returns:**
- `str`: Markdown document string

**Example:**
```python
fc = Flowcard()
fc.title("My Document")
md_content = fc.to_markdown()
```

#### `save(filepath: Union[Path, str], extension: Optional[str] = None) -> None`
Save the document to a file.

**Args:**
- `filepath`: Path where to save the file
- `extension`: File format ("html", "md", "pdf"). If None, inferred from filepath

**Raises:**
- `ValueError`: If extension is not supported

**Example:**
```python
fc.save("report.html")
fc.save("report.md")
fc.save("report", extension="pdf")
```

## 📝 Text Components

### `title(text: str) -> None`
Add a main title (H1) to the document.

**Args:**
- `text`: The title text

**Example:**
```python
fc.title("My Machine Learning Model")
```

**Output:**
- HTML: `<h1>My Machine Learning Model</h1>`
- Markdown: `# My Machine Learning Model`

### `header(text: str) -> None`
Add a section header (H2) to the document.

**Args:**
- `text`: The header text

**Example:**
```python
fc.header("Model Performance")
```

### `subheader(text: str) -> None`
Add a subsection header (H3) to the document.

**Args:**
- `text`: The subheader text

**Example:**
```python
fc.subheader("Training Results")
```

### `text(content: str) -> None`
Add regular text to the document.

**Args:**
- `content`: The text content

**Example:**
```python
fc.text("This is a simple text paragraph.")
```

### `paragraph(content: str, markdown: bool = True) -> None`
Add a paragraph with optional Markdown formatting.

**Args:**
- `content`: The paragraph content
- `markdown`: Whether to process Markdown syntax (default: True)

**Example:**
```python
fc.paragraph("This text has **bold** and *italic* formatting.")
fc.paragraph("Raw text without formatting", markdown=False)
```

### `code(code: str, language: str = "python") -> None`
Add a code block with syntax highlighting.

**Args:**
- `code`: The code content
- `language`: Programming language for syntax highlighting

**Example:**
```python
fc.code('''
def hello_world():
    print("Hello, World!")
''', language="python")
```

## 📋 List Components

### `bullet_list(items: List[str]) -> None`
Add a bulleted list to the document.

**Args:**
- `items`: List of items to display

**Example:**
```python
fc.bullet_list([
    "First item",
    "Second item",
    "Third item"
])
```

### `numbered_list(items: List[str]) -> None`
Add a numbered list to the document.

**Args:**
- `items`: List of items to display

**Example:**
```python
fc.numbered_list([
    "Step one",
    "Step two", 
    "Step three"
])
```

### `table(data: Dict[str, List] | List[List], headers: Optional[List[str]] = None) -> None`
Add a data table to the document.

**Args:**
- `data`: Table data as dictionary of columns or list of rows
- `headers`: Column headers (optional, inferred from dict keys if data is dict)

**Example:**
```python
# Dictionary format
fc.table({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["New York", "London", "Tokyo"]
})

# List format
fc.table([
    ["Alice", 25, "New York"],
    ["Bob", 30, "London"],
    ["Charlie", 35, "Tokyo"]
], headers=["Name", "Age", "City"])
```

## 🎨 Media Components

### `image(source: Union[str, bytes, Path], caption: Optional[str] = None, alt: Optional[str] = None) -> None`
Add an image to the document.

**Args:**
- `source`: Image file path, URL, or bytes data
- `caption`: Optional image caption
- `alt`: Alt text for accessibility

**Example:**
```python
# From file path
fc.image("chart.png", caption="Training Loss Over Time")

# From URL
fc.image("https://example.com/image.jpg", caption="Remote Image")

# From bytes
with open("image.png", "rb") as f:
    fc.image(f.read(), caption="Embedded Image")
```

### `chart(figure: Any, caption: Optional[str] = None, format: str = "png") -> None`
Add a chart or plot to the document.

**Args:**
- `figure`: Matplotlib figure, Plotly figure, or other supported chart object
- `caption`: Optional chart caption
- `format`: Image format for embedding ("png", "svg", "jpg")

**Example:**
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
fc.chart(fig, caption="Sample Line Chart")
```

### `dataframe(df: 'pandas.DataFrame', caption: Optional[str] = None, max_rows: int = 100) -> None`
Display a pandas DataFrame as a formatted table.

**Args:**
- `df`: Pandas DataFrame to display
- `caption`: Optional table caption
- `max_rows`: Maximum number of rows to display

**Example:**
```python
import pandas as pd

df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9]
})

fc.dataframe(df, caption="Sample Dataset")
```

## 🎯 Interactive Components

### `alert(message: str, type: str = "info") -> None`
Add an alert box to the document.

**Args:**
- `message`: Alert message
- `type`: Alert type ("info", "warning", "error", "success")

**Example:**
```python
fc.alert("Model training completed successfully!", type="success")
fc.alert("Low accuracy detected. Consider tuning hyperparameters.", type="warning")
```

### `collapsible(title: str, content: str) -> None`
Add a collapsible section to the document.

**Args:**
- `title`: Section title (always visible)
- `content`: Section content (collapsible)

**Example:**
```python
fc.collapsible("Model Details", """
This section contains detailed information about the model architecture,
hyperparameters, and training process.
""")
```

### `tabs(tab_dict: Dict[str, str]) -> None`
Add tabbed content to the document.

**Args:**
- `tab_dict`: Dictionary where keys are tab titles and values are tab content

**Example:**
```python
fc.tabs({
    "Overview": "General model information...",
    "Performance": "Detailed performance metrics...",
    "Code": "Implementation code and examples..."
})
```

## 🔧 Utility Components

### `divider() -> None`
Add a horizontal divider/separator.

**Example:**
```python
fc.title("Section 1")
fc.text("Some content...")
fc.divider()
fc.title("Section 2")
```

### `spacer(height: int = 1) -> None`
Add vertical spacing.

**Args:**
- `height`: Number of line breaks to add

**Example:**
```python
fc.text("First paragraph")
fc.spacer(3)
fc.text("Second paragraph with extra spacing")
```

### `raw_html(html: str) -> None`
Insert raw HTML content.

**Args:**
- `html`: Raw HTML string

**Example:**
```python
fc.raw_html('<div class="custom-styling">Custom HTML content</div>')
```

## ⚙️ Configuration Methods

### `set_template(format: str, template: str) -> None`
Set a custom template for export format.

**Args:**
- `format`: Export format ("html", "markdown", "pdf")
- `template`: Template string (Jinja2 format)

**Example:**
```python
custom_html = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>{{ custom_css }}</style>
</head>
<body>{{ body }}</body>
</html>
"""

fc.set_template("html", custom_html)
```

### `clear() -> None`
Clear all content from the document.

**Example:**
```python
fc.clear()  # Start fresh
```

### `set_style(css: str) -> None`
Add custom CSS styling for HTML export.

**Args:**
- `css`: CSS string

**Example:**
```python
fc.set_style("""
.title { color: blue; font-size: 2em; }
.highlight { background-color: yellow; }
""")
```

## 🚦 Component Context Managers

### `section(title: str)`
Create a logical section with automatic organization.

**Args:**
- `title`: Section title

**Example:**
```python
with fc.section("Model Training"):
    fc.text("Training configuration:")
    fc.bullet_list(["Epochs: 100", "Batch size: 32", "Learning rate: 0.001"])
    
    fc.subheader("Results")
    fc.text("Training completed successfully.")
```

### `columns(num_columns: int)`
Create a multi-column layout.

**Args:**
- `num_columns`: Number of columns

**Example:**
```python
with fc.columns(2):
    with fc.column():
        fc.header("Left Column")
        fc.text("Content for left column")
    
    with fc.column():
        fc.header("Right Column") 
        fc.text("Content for right column")
```

## 📊 Data Integration

### Matplotlib Integration
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(epochs, train_loss, label='Training Loss')
ax.plot(epochs, val_loss, label='Validation Loss')
ax.legend()

fc.chart(fig, caption="Training History")
```

### Plotly Integration
```python
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13]))
fc.chart(fig, caption="Interactive Plotly Chart")
```

### Pandas Integration
```python
import pandas as pd

# Display DataFrame
fc.dataframe(results_df, caption="Experiment Results")

# Display summary statistics
fc.dataframe(df.describe(), caption="Dataset Statistics")
```

## 🎨 Export Formats

### HTML Export
- Full CSS styling support
- Interactive elements (collapsible, tabs)
- Embedded images and charts
- Responsive design

#### Standalone HTML Generation

FlowCard's **standalone HTML mode** is a key differentiator that generates completely self-contained documents:

```python
# Generate standalone HTML (default behavior)
fc = Flowcard()
fc.title("Offline Report")
fc.image("chart.png")  # Automatically embedded as base64
fc.chart(matplotlib_fig)  # Chart converted to embedded image

# Standalone mode (default)
standalone_html = fc.to_html(standalone=True)

# Non-standalone mode (smaller files, requires internet)
regular_html = fc.to_html(standalone=False)
```

**Standalone Mode Features:**
- **Zero External Dependencies**: No CDN links to Bootstrap, jQuery, or other libraries
- **Embedded Assets**: All images, charts, and media converted to base64 and embedded inline
- **Offline Compatibility**: Documents work in air-gapped environments
- **Future-Proof**: No risk of external resources becoming unavailable
- **Single File Distribution**: Everything contained in one HTML file
- **Security**: No external resource loading that could be blocked by firewalls

**Technical Implementation:**
- CSS frameworks embedded inline instead of CDN links
- JavaScript libraries included in `<script>` tags
- Images converted to `data:image/png;base64,` format
- Charts rendered as embedded SVG or PNG data
- Fonts embedded as base64 or web-safe fallbacks

**Use Cases for Standalone Files:**
- **Client Deliverables**: Reports that must work on any client system
- **Compliance Documentation**: Long-term archival without dependency concerns  
- **Restricted Environments**: Air-gapped networks, secure facilities
- **Email Attachments**: Self-contained reports via email
- **Offline Presentations**: Documents that work without internet

### Markdown Export
- GitHub Flavored Markdown
- Code syntax highlighting
- Tables and lists
- Image references

### PDF Export
- Professional formatting
- Vector graphics support
- Page breaks and headers
- Print-optimized layout

## 🔍 Error Handling

All FlowCard methods include proper error handling:

```python
try:
    fc.image("nonexistent.jpg")
except FileNotFoundError:
    fc.alert("Image not found", type="error")

try:
    fc.table(invalid_data)
except ValueError as e:
    fc.text(f"Data error: {e}")
```

## 💡 Best Practices

1. **Use descriptive titles and headers** for better document structure
2. **Add captions to images and charts** for context
3. **Use appropriate alert types** to highlight important information
4. **Organize content with sections** for readability
5. **Test exports in multiple formats** to ensure compatibility
6. **Handle errors gracefully** when dealing with external data

---

For more examples and tutorials, see the main [README](README.md) and [examples directory](examples/).