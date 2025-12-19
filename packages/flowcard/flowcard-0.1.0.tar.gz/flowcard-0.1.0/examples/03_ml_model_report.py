"""FlowCard Example 03: Machine Learning Model Report

This example demonstrates how to create a comprehensive ML model report
using FlowCard with synthetic data to showcase real-world usage patterns.
"""

# Standard Library
import io
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Third Party
try:
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  Matplotlib/NumPy not installed. Install with: pip install matplotlib numpy")
    # Fallback for math functions
    import math

# Flowcard
import flowcard as fc


def generate_synthetic_training_data() -> Dict[str, List[float]]:
    """Generate synthetic training metrics for demonstration.
    
    Returns:
        Dictionary containing training metrics over epochs.
    """
    epochs = list(range(1, 21))  # 20 epochs
    
    # Simulate decreasing loss with some noise
    train_loss = []
    val_loss = []
    train_acc = []
    val_acc = []
    
    for epoch in epochs:
        # Training loss decreases with noise
        if MATPLOTLIB_AVAILABLE:
            t_loss = 2.0 * np.exp(-epoch * 0.15) + random.uniform(0, 0.1)
        else:
            t_loss = 2.0 * math.exp(-epoch * 0.15) + random.uniform(0, 0.1)
        train_loss.append(t_loss)
        
        # Validation loss similar but slightly higher
        v_loss = t_loss + random.uniform(0.05, 0.2)
        val_loss.append(v_loss)
        
        # Accuracy increases (inverse of loss pattern)
        t_acc = min(0.95, 0.5 + (1 - t_loss / 2.0) * 0.5)
        train_acc.append(t_acc)
        
        v_acc = t_acc - random.uniform(0.02, 0.08)
        val_acc.append(max(0.4, v_acc))
    
    return {
        "epochs": epochs,
        "train_loss": train_loss,
        "val_loss": val_loss,
        "train_accuracy": train_acc,
        "val_accuracy": val_acc
    }


def create_training_chart(metrics: Dict[str, List[float]]) -> bytes:
    """Create a training metrics visualization.
    
    Args:
        metrics: Dictionary containing training metrics.
        
    Returns:
        PNG image data as bytes.
    """
    if not MATPLOTLIB_AVAILABLE:
        return b"chart_placeholder_data"
    
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))
    
    # Loss plot
    ax1.plot(metrics["epochs"], metrics["train_loss"], 
             label="Training Loss", color='blue', linewidth=2)
    ax1.plot(metrics["epochs"], metrics["val_loss"], 
             label="Validation Loss", color='red', linewidth=2)
    ax1.set_title("Model Loss Over Time")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Accuracy plot
    ax2.plot(metrics["epochs"], metrics["train_accuracy"], 
             label="Training Accuracy", color='green', linewidth=2)
    ax2.plot(metrics["epochs"], metrics["val_accuracy"], 
             label="Validation Accuracy", color='orange', linewidth=2)
    ax2.set_title("Model Accuracy Over Time")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='PNG', dpi=150, bbox_inches='tight')
    plt.close()
    
    return img_buffer.getvalue()


def get_model_summary() -> Dict[str, str]:
    """Get synthetic model summary information.
    
    Returns:
        Dictionary containing model details.
    """
    return {
        "model_name": "ResNet-18 Image Classifier",
        "dataset": "Synthetic Dataset (10,000 samples)",
        "architecture": "ResNet-18 with custom head",
        "training_time": "2.5 hours",
        "final_train_accuracy": "94.2%",
        "final_val_accuracy": "91.8%",
        "parameters": "11.7M",
        "optimizer": "Adam (lr=0.001)",
        "batch_size": "32",
        "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def main() -> None:
    """Create a comprehensive ML model report."""
    print("🚀 Creating ML Model Report...")
    
    # Generate synthetic data
    metrics = generate_synthetic_training_data()
    model_info = get_model_summary()
    
    # Create FlowCard document
    card = fc.Flowcard()
    
    # Main title
    card.title("🤖 Machine Learning Model Report")
    
    # Add training metrics chart
    if MATPLOTLIB_AVAILABLE:
        chart_data = create_training_chart(metrics=metrics)
        card.image(image_data=chart_data)
        print("✅ Generated training metrics chart")
    else:
        print("⚠️  Skipping chart generation (matplotlib not available)")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Save the report
    card.save(filepath="output/ml_model_report.html")
    card.save(filepath="output/ml_model_report.md")
    
    print("✅ ML Model Report completed!")
    print("📁 Generated files:")
    print("   - output/ml_model_report.html")
    print("   - output/ml_model_report.md")
    
    # Print model summary
    print("\n📊 Model Summary:")
    for key, value in model_info.items():
        print(f"   - {key.replace('_', ' ').title()}: {value}")
    
    if MATPLOTLIB_AVAILABLE:
        final_train_acc = metrics["train_accuracy"][-1]
        final_val_acc = metrics["val_accuracy"][-1]
        print(f"\n🎯 Final Performance:")
        print(f"   - Training Accuracy: {final_train_acc:.3f}")
        print(f"   - Validation Accuracy: {final_val_acc:.3f}")


if __name__ == "__main__":
    main()