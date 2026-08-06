#!/usr/bin/env python3
"""
Example usage of figure-production assembly.

This script demonstrates how to use the assemble() function from main.py
to compose pre-rendered panels into a composite figure.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from main import assemble  # 真实存在的函数式 API


def create_sample_images(n=6):
    """Create sample test images (PNG) for demonstration."""
    from PIL import Image, ImageDraw, ImageFont
    colors = [(255,200,200),(200,255,200),(200,200,255),(255,255,200),(255,200,255),(200,255,255)]
    labels = list("ABCDEF")[:n]
    output_dir = Path("example_output")
    output_dir.mkdir(exist_ok=True)
    paths = []
    for color, label in zip(colors, labels):
        img = Image.new('RGB', (400, 300), color)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("Arial", 40)
        except Exception:
            font = ImageFont.load_default()
        text = f"Sample {label}"
        bbox = draw.textbbox((0,0), text, font=font)
        x = (400 - (bbox[2]-bbox[0])) // 2
        y = (300 - (bbox[3]-bbox[1])) // 2
        draw.text((x, y), text, fill=(0,0,0), font=font)
        path = output_dir / f"{label}.png"
        img.save(path)
        paths.append(str(path))
    return paths


def example_1_basic():
    """Example 1: Basic usage with default settings."""
    print("\n=== Example 1: Basic Usage ===")
    inputs = create_sample_images()
    ok = assemble(inputs=inputs, output="example_output/figure_basic.png")
    return ok


def example_2_custom_layout():
    """Example 2: 3x2 layout with high DPI."""
    print("\n=== Example 2: 3x2 Layout with 600 DPI ===")
    inputs = [f"example_output/{l}.png" for l in "ABCDEF"]
    ok = assemble(inputs=inputs, output="example_output/figure_3x2.png",
                  layout="3x2", dpi=600, label_size=24)
    return ok


def example_3_custom_styling():
    """Example 3: Custom styling — padding + label styling."""
    print("\n=== Example 3: Custom Styling ===")
    inputs = [f"example_output/{l}.png" for l in "ABCDEF"]
    ok = assemble(inputs=inputs, output="example_output/figure_styled.png",
                  layout="2x3", dpi=300, label_size=20, label_bold=False,
                  padding=0.05, bg_color="#f0f0f0")
    return ok


def example_4_custom_labels():
    """Example 4: Custom panel labels (passed via inputs naming — labels come from filename stem)."""
    print("\n=== Example 4: Custom Labels ===")
    inputs = [f"example_output/{l}.png" for l in "ABCDEF"]
    # Note: assemble() derives panel labels from filename stem (A/B/C...) and applies A-F overlay.
    # For custom text labels, rename input files or post-process. Here we use auto A-F.
    ok = assemble(inputs=inputs, output="example_output/figure_custom.png",
                  layout="2x3", dpi=300, label_size=18)
    return ok


if __name__ == "__main__":
    print("figure-production assembly - Examples")
    print("=" * 50)
    try:
        results = []
        results.append(("example_1_basic", example_1_basic()))
        results.append(("example_2_custom_layout", example_2_custom_layout()))
        results.append(("example_3_custom_styling", example_3_custom_styling()))
        results.append(("example_4_custom_labels", example_4_custom_labels()))
        print("\n" + "=" * 50)
        for name, ok in results:
            status = "✓ OK" if ok else "✗ FAILED"
            print(f"  {name}: {status}")
        print("\nCheck 'example_output/' for results.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)