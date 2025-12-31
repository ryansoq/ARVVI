#!/usr/bin/env python3
"""
ARVVI Compare - Compare RVV instruction usage across multiple models
"""

import argparse
import json
import sys
from pathlib import Path


def load_stats(json_path):
    """Load statistics from JSON file"""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Error loading {json_path}: {e}", file=sys.stderr)
        return None


def print_comparison(stats_dict, markdown=False):
    """Print comparison table

    Args:
        stats_dict: Dictionary mapping model names to their statistics
        markdown: If True, output in markdown format for README.md
    """
    if markdown:
        print_comparison_markdown(stats_dict)
    else:
        print_comparison_text(stats_dict)


def print_comparison_text(stats_dict):
    """Print comparison table in text format"""
    print("\n" + "=" * 80)
    print("RVV Instruction Usage Comparison")
    print("=" * 80 + "\n")

    # Print summary statistics
    print(f"{'Model':<20} {'Total Instr':<15} {'RVV Instr':<15} {'RVV %':<10}")
    print(f"{'-'*80}")

    for model_name, data in stats_dict.items():
        stats = data.get('statistics', {})
        total = stats.get('total_instructions', 0)
        rvv = stats.get('rvv_instructions', 0)
        percentage = (rvv / total * 100) if total > 0 else 0

        print(f"{model_name:<20} {total:<15,} {rvv:<15,} {percentage:<10.2f}")

    # Collect all unique instructions
    all_instructions = set()
    for data in stats_dict.values():
        stats = data.get('statistics', {})
        all_instructions.update(stats.get('instruction_stats', {}).keys())

    # Calculate total usage for each instruction across all models
    instruction_totals = {}
    for instr in all_instructions:
        total = 0
        for data in stats_dict.values():
            stats = data.get('statistics', {})
            total += stats.get('instruction_stats', {}).get(instr, 0)
        instruction_totals[instr] = total

    # Sort by total usage
    sorted_instructions = sorted(instruction_totals.items(), key=lambda x: x[1], reverse=True)

    # Print top instructions
    print("\n" + "=" * 80)
    print("Top RVV Instructions Across All Models")
    print("=" * 80 + "\n")

    # Header
    model_names = list(stats_dict.keys())
    header = f"{'Instruction':<15} {'Total':<10}"
    for model_name in model_names:
        header += f"{model_name[:12]:<12}"
    print(header)
    print(f"{'-'*80}")

    # Print top 20 instructions
    for instr, total_count in sorted_instructions[:20]:
        row = f"{instr:<15} {total_count:<10}"
        for model_name in model_names:
            data = stats_dict[model_name]
            stats = data.get('statistics', {})
            count = stats.get('instruction_stats', {}).get(instr, 0)
            row += f"{count:<12}"
        print(row)


def print_comparison_markdown(stats_dict):
    """Print comparison table in markdown format for README.md"""

    print("\n## RVV Instruction Usage Comparison\n")

    # Summary table
    print("### Model Summary\n")
    print("| Model | Total Instructions | RVV Instructions | RVV % |")
    print("|-------|-------------------:|-----------------:|------:|")

    for model_name, data in stats_dict.items():
        stats = data.get('statistics', {})
        total = stats.get('total_instructions', 0)
        rvv = stats.get('rvv_instructions', 0)
        percentage = (rvv / total * 100) if total > 0 else 0

        print(f"| {model_name} | {total:,} | {rvv:,} | {percentage:.2f}% |")

    # Collect instruction statistics
    all_instructions = set()
    for data in stats_dict.values():
        stats = data.get('statistics', {})
        all_instructions.update(stats.get('instruction_stats', {}).keys())

    instruction_totals = {}
    for instr in all_instructions:
        total = 0
        for data in stats_dict.values():
            stats = data.get('statistics', {})
            total += stats.get('instruction_stats', {}).get(instr, 0)
        instruction_totals[instr] = total

    sorted_instructions = sorted(instruction_totals.items(), key=lambda x: x[1], reverse=True)

    # Top instructions table
    print("\n### Top 20 RVV Instructions Across All Models\n")

    model_names = list(stats_dict.keys())

    # Header
    header = "| Instruction | Total |"
    for model_name in model_names:
        header += f" {model_name} |"
    print(header)

    # Alignment row
    align = "|-------------|------:|"
    for _ in model_names:
        align += "------:|"
    print(align)

    # Data rows
    for instr, total_count in sorted_instructions[:20]:
        row = f"| **{instr}** | **{total_count:,}** |"
        for model_name in model_names:
            data = stats_dict[model_name]
            stats = data.get('statistics', {})
            count = stats.get('instruction_stats', {}).get(instr, 0)
            if count > 0:
                row += f" {count:,} |"
            else:
                row += " - |"
        print(row)


def scan_json_files(models_dir):
    """
    Scan directory recursively for all *_rvv_stats.json files

    Args:
        models_dir: Root directory to scan

    Returns:
        List of JSON file paths found
    """
    models_path = Path(models_dir)
    if not models_path.exists():
        print(f"Error: Directory not found: {models_dir}", file=sys.stderr)
        return []

    # Find all *_rvv_stats.json files recursively
    json_files = list(models_path.rglob('*_rvv_stats.json'))

    if not json_files:
        print(f"No *_rvv_stats.json files found in {models_dir}", file=sys.stderr)
        return []

    print(f"Found {len(json_files)} JSON file(s) to compare\n")
    for json_file in json_files:
        print(f"  - {json_file}")

    return [str(f) for f in json_files]


def main():
    parser = argparse.ArgumentParser(
        description='ARVVI Compare - Compare RVV instruction usage across multiple models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Compare specific files:
    %(prog)s model1.json model2.json model3.json
    %(prog)s *.json --visualize
    %(prog)s bev.json mobilenet.json -o comparison.png

  Scan directory for all JSON files:
    %(prog)s --scan models/
    %(prog)s --scan ../AutoIREE_zoo/models/ --visualize
    %(prog)s --scan models/ --markdown > results.md
        """
    )

    parser.add_argument('json_files', nargs='*', help='JSON files containing statistics (not used with --scan)')
    parser.add_argument('--scan', dest='scan_dir', metavar='DIR',
                        help='Scan directory recursively for all *_rvv_stats.json files')
    parser.add_argument('-v', '--visualize', action='store_true',
                        help='Generate comparison visualization')
    parser.add_argument('-o', '--output', help='Output directory for visualizations (default: current directory)')
    parser.add_argument('--markdown', action='store_true',
                        help='Output in markdown format for README.md')

    args = parser.parse_args()

    # Check if using scan mode
    if args.scan_dir:
        json_files = scan_json_files(args.scan_dir)
        if not json_files:
            sys.exit(1)
    else:
        if not args.json_files:
            parser.error("Either provide JSON files or use --scan <directory>")
        json_files = args.json_files

    # Load all statistics
    stats_dict = {}
    for json_file in json_files:
        path = Path(json_file)
        if not path.exists():
            print(f"Warning: File not found: {json_file}", file=sys.stderr)
            continue

        data = load_stats(json_file)
        if data:
            model_name = data.get('model', path.stem)
            stats_dict[model_name] = data

    if not stats_dict:
        print("Error: No valid statistics files found", file=sys.stderr)
        sys.exit(1)

    if len(stats_dict) < 2:
        print("Warning: Only one model loaded. Need at least 2 models for comparison.")

    # Print comparison
    print_comparison(stats_dict, markdown=args.markdown)

    # Generate visualization if requested
    if args.visualize:
        try:
            from arvvi_visualizer import compare_models, visualize_instruction_breakdown_by_model

            # Convert data format for visualizer
            visualizer_stats = {}
            for model_name, data in stats_dict.items():
                visualizer_stats[model_name] = data.get('statistics', {})

            output_dir = args.output or '.'

            # Generate grouped comparison chart
            compare_models(visualizer_stats, output_dir)

            # Generate stacked breakdown chart
            visualize_instruction_breakdown_by_model(visualizer_stats, output_dir)

        except ImportError:
            print("\nWarning: matplotlib not installed. Install with: pip install matplotlib")
            print("Skipping visualization.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
