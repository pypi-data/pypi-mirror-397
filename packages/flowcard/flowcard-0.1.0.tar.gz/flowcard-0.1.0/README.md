# FlowCard 🃏

**Programmatic Documentation Made Simple**

FlowCard is a Python package that enables you to create beautiful documentation, reports, and cards programmatically during code execution. Think of it as Streamlit for static content generation - you can build rich documents with components like titles, text, images, and data visualizations, then export them to Markdown, HTML, or PDF formats.

## ✨ Key Features

- **Streamlit-like API**: Familiar and intuitive component-based syntax
- **Multiple Export Formats**: Generate Markdown, HTML, and PDF outputs
- **Standalone Files**: Generate self-contained documents that work offline without external libraries or internet connection
- **Lightweight & Dependency-Free**: Minimal core dependencies, avoiding heavy wrappers or unnecessary layers
- **Rich Components**: Support for text, images, charts, code blocks, and more
- **Programmatic Content**: Build documentation dynamically during code execution
- **ML/Data Science Friendly**: Perfect for model cards, experiment reports, and data analysis documentation
- **Modern Python**: Built for Python 3.11+ with full type hints and modern features

## 🚀 Quick Start

### Installation

```bash
pip install flowcard
```

### Basic Usage

```python
import flowcard as fc
from sklearn.linear_model import LinearRegression
import numpy as np

# Create your model and train it
X = np.random.randn(100, 1)
y = 2 * X.ravel() + np.random.randn(100)
model = LinearRegression()
model.fit(X, y)

# Build your documentation programmatically
fc.title("My Machine Learning Model Card")
fc.text("This is an automatically generated model card created during training.")

fc.header("Model Performance")
score = model.score(X, y)
fc.paragraph(f"Model R² Score: **{score:.4f}**")

fc.header("Model Details")
fc.bullet_list([
    "Algorithm: Linear Regression",
    f"Training samples: {len(X)}",
    f"Features: {X.shape[1]}",
    f"Coefficient: {model.coef_[0]:.4f}",
    f"Intercept: {model.intercept_:.4f}"
])

# Export your documentation
fc.to_markdown("model_card.md")
fc.to_html("model_card.html")
fc.to_pdf("model_card.pdf")
```

## 📚 Components

FlowCard provides a rich set of components for building your documentation:

### Text Components
- `fc.title(text)` - Main title (H1)
- `fc.header(text)` - Section header (H2)
- `fc.subheader(text)` - Subsection header (H3)
- `fc.text(text)` - Regular text
- `fc.paragraph(text)` - Paragraph with Markdown support
- `fc.code(code, language="python")` - Code blocks with syntax highlighting

### Lists and Structure
- `fc.bullet_list(items)` - Bulleted list
- `fc.numbered_list(items)` - Numbered list
- `fc.table(data, headers)` - Data tables
- `fc.divider()` - Horizontal separator

### Media and Visuals
- `fc.image(path_or_bytes, caption=None)` - Images with optional captions
- `fc.chart(figure)` - Matplotlib/Plotly charts
- `fc.dataframe(df)` - Pandas DataFrame display

### Interactive Elements
- `fc.collapsible(title, content)` - Collapsible sections
- `fc.tabs(tab_dict)` - Tabbed content
- `fc.alert(message, type="info")` - Alert boxes (info, warning, error, success)

## 🎯 Use Cases

### Model Cards for ML Projects
```python
import flowcard as fc

fc.title("ResNet Image Classifier")
fc.text("Automatically generated model card")

fc.header("Model Overview")
fc.table({
    "Property": ["Architecture", "Dataset", "Accuracy", "Parameters"],
    "Value": ["ResNet-50", "ImageNet", "94.2%", "25.6M"]
})

fc.header("Training Metrics")
fc.chart(training_plot)  # Your matplotlib/plotly figure

fc.to_html("resnet_model_card.html")
```

### Experiment Reports
```python
import flowcard as fc

fc.title("A/B Test Results")
fc.paragraph("Experiment conducted from March 1-15, 2024")

for variant in ["Control", "Variant A", "Variant B"]:
    fc.subheader(f"{variant} Results")
    fc.bullet_list([
        f"Conversion Rate: {results[variant]['conversion']:.2%}",
        f"Sample Size: {results[variant]['samples']:,}",
        f"Confidence: {results[variant]['confidence']:.1%}"
    ])

fc.to_markdown("ab_test_report.md")
```

### Data Analysis Reports
```python
import flowcard as fc
import pandas as pd

fc.title("Sales Data Analysis")
fc.text(f"Report generated on {datetime.now().strftime('%Y-%m-%d')}")

fc.header("Dataset Overview")
fc.dataframe(df.describe())

fc.header("Key Insights")
fc.bullet_list([
    f"Total sales: ${df['sales'].sum():,.2f}",
    f"Average order value: ${df['sales'].mean():.2f}",
    f"Top product category: {df.groupby('category')['sales'].sum().idxmax()}"
])

fc.to_pdf("sales_analysis.pdf")
```

## 🔧 Advanced Features

### Standalone File Generation

FlowCard generates **completely self-contained documents** that work offline without any external dependencies:

```python
import flowcard as fc

# Generate standalone HTML with embedded assets
fc.title("Offline Report")
fc.image("chart.png")  # Image embedded as base64
fc.chart(matplotlib_figure)  # Chart embedded as base64

# Export with no external library dependencies
fc.to_html("standalone_report.html", standalone=True)
```

**Key Benefits:**
- **No Internet Required**: Documents work completely offline
- **No External Libraries**: No CDN dependencies (Bootstrap, jQuery, etc.)
- **Embedded Assets**: Images and charts embedded as base64 data
- **Single File Distribution**: Share one file that contains everything
- **Long-term Archival**: Documents remain viewable years later without dependency rot

**Perfect for:**
- Client deliverables that need to work on any system
- Archival documentation for compliance
- Reports shared in restricted environments
- Email attachments that must be self-contained

### Custom Templates
```python
# Use custom HTML/Markdown templates
fc.set_template("html", custom_html_template)
fc.set_template("markdown", custom_md_template)
```

### Conditional Content
```python
# Add content conditionally
if model_accuracy > 0.9:
    fc.alert("High accuracy model!", type="success")
else:
    fc.alert("Consider model improvements", type="warning")
```

### Batch Processing
```python
# Generate multiple reports
for experiment in experiments:
    fc.clear()  # Clear previous content
    fc.title(f"Experiment {experiment.id}")
    # ... add content ...
    fc.to_html(f"reports/experiment_{experiment.id}.html")
```

## 🎨 Export Formats

### Markdown
Perfect for README files, documentation sites, and version control.

### HTML
Rich, interactive documents with styling and JavaScript support.

### PDF
Professional reports ready for sharing and printing.

## 🚧 Roadmap & TODO

We are working on making FlowCard the ultimate tool for ML Model Cards, keeping it lightweight and dependency-free. Here is what's coming next:

- [ ] **Lightweight UI Components**
    - [ ] `metric` component (Display key metrics with deltas)
    - [ ] `badge` component (For licenses, status, tags)
    - [ ] `json` viewer (For configurations and hyperparameters)
    - [ ] `citation` block (BibTeX formatting)
- [ ] **Model Card Utilities**
    - [ ] Standard Model Card templates (Scaffolding for common sections)
    - [ ] Metadata helpers (Versioning, Author info)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [Streamlit](https://streamlit.io/) for the component-based API design
- Built for the Python data science and ML community

---

**FlowCard**: Because documentation should flow as smoothly as your code! 🚀

