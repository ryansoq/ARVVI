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


def print_comparison(stats_dict):
    """Print comparison table"""
    print(f"\n{'='*80}")
    print(f"RVV Instruction Usage Comparison")
    print(f"{'='*80}\n")

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
    print(f"\n{'='*80}")
    print(f"Top RVV Instructions Across All Models")
    print(f"{'='*80}\n")

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


def main():
    parser = argparse.ArgumentParser(
        description='ARVVI Compare - Compare RVV instruction usage across multiple models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s model1.json model2.json model3.json
  %(prog)s *.json --visualize
  %(prog)s bev.json mobilenet.json -o comparison.png
        """
    )

    parser.add_argument('json_files', nargs='+', help='JSON files containing statistics')
    parser.add_argument('-v', '--visualize', action='store_true',
                       help='Generate comparison visualization')
    parser.add_argument('-o', '--output', help='Output directory for visualizations (default: current directory)')

    args = parser.parse_args()

    # Load all statistics
    stats_dict = {}
    for json_file in args.json_files:
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
    print_comparison(stats_dict)

    # Generate visualization if requested
    if args.visualize:
        try:
            from arvvi_visualizer import compare_models

            # Convert data format for visualizer
            visualizer_stats = {}
            for model_name, data in stats_dict.items():
                visualizer_stats[model_name] = data.get('statistics', {})

            output_dir = args.output or '.'
            compare_models(visualizer_stats, output_dir)

        except ImportError:
            print("\nWarning: matplotlib not installed. Install with: pip install matplotlib")
            print("Skipping visualization.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
