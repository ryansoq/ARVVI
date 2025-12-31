#!/usr/bin/env python3
"""
ARVVI Visualizer - Generate charts for RVV instruction statistics
"""

import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path

# Use non-interactive backend if no display available
matplotlib.use('Agg')


def visualize_statistics(stats, model_name='Unknown', output_dir='.'):
    """
    Generate visualization charts for RVV instruction statistics

    Args:
        stats: Dictionary containing statistics from RVVAnalyzer
        model_name: Name of the model being analyzed
        output_dir: Directory to save the charts
    """
    instruction_stats = stats.get('instruction_stats', {})

    if not instruction_stats:
        print("No RVV instructions found to visualize")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Sort instructions by count
    sorted_instructions = sorted(instruction_stats.items(), key=lambda x: x[1], reverse=True)

    # Limit to top 20 for readability
    top_n = min(20, len(sorted_instructions))
    top_instructions = sorted_instructions[:top_n]

    instructions, counts = zip(*top_instructions)

    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(f'RVV Instruction Analysis - {model_name}', fontsize=16, fontweight='bold')

    # 1. Bar chart
    colors = plt.cm.viridis(range(len(instructions)))
    bars = ax1.barh(range(len(instructions)), counts, color=colors)
    ax1.set_yticks(range(len(instructions)))
    ax1.set_yticklabels(instructions)
    ax1.set_xlabel('Count', fontweight='bold')
    ax1.set_title('Top RVV Instructions by Usage Count')
    ax1.invert_yaxis()

    # Add count labels on bars
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax1.text(count, i, f' {count}', va='center', fontweight='bold')

    # 2. Pie chart for top 10
    top_10 = min(10, len(sorted_instructions))
    top_10_instructions = sorted_instructions[:top_10]
    top_10_names, top_10_counts = zip(*top_10_instructions)

    # Calculate "others" if there are more than 10 instructions
    if len(sorted_instructions) > top_10:
        others_count = sum(count for _, count in sorted_instructions[top_10:])
        top_10_names = list(top_10_names) + ['Others']
        top_10_counts = list(top_10_counts) + [others_count]

    colors_pie = plt.cm.Set3(range(len(top_10_names)))
    wedges, texts, autotexts = ax2.pie(top_10_counts, labels=top_10_names, autopct='%1.1f%%',
                                       colors=colors_pie, startangle=90)

    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    ax2.set_title('Distribution of Top RVV Instructions')

    # Add statistics text
    total_instr = stats.get('total_instructions', 0)
    rvv_instr = stats.get('rvv_instructions', 0)
    rvv_percentage = (rvv_instr / total_instr * 100) if total_instr > 0 else 0

    stats_text = f'Total Instructions: {total_instr:,}\n'
    stats_text += f'RVV Instructions: {rvv_instr:,}\n'
    stats_text += f'RVV Usage: {rvv_percentage:.2f}%'

    fig.text(0.5, 0.02, stats_text, ha='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout(rect=[0, 0.05, 1, 0.96])

    # Save the figure
    output_file = output_path / f'{model_name}_rvv_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved to: {output_file}")

    # Also create a detailed bar chart with all instructions if there are many
    if len(sorted_instructions) > top_n:
        create_detailed_chart(sorted_instructions, model_name, output_path)


def create_detailed_chart(sorted_instructions, model_name, output_path):
    """Create a detailed chart with all instructions"""
    instructions, counts = zip(*sorted_instructions)

    # Calculate figure height based on number of instructions
    fig_height = max(10, len(instructions) * 0.3)

    fig, ax = plt.subplots(figsize=(12, fig_height))
    fig.suptitle(f'Complete RVV Instruction Analysis - {model_name}', fontsize=14, fontweight='bold')

    colors = plt.cm.viridis(range(len(instructions)))
    bars = ax.barh(range(len(instructions)), counts, color=colors)
    ax.set_yticks(range(len(instructions)))
    ax.set_yticklabels(instructions, fontsize=8)
    ax.set_xlabel('Count', fontweight='bold')
    ax.set_title('All RVV Instructions by Usage Count')
    ax.invert_yaxis()

    # Add count labels on bars
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax.text(count, i, f' {count}', va='center', fontsize=7)

    plt.tight_layout()

    output_file = output_path / f'{model_name}_rvv_analysis_detailed.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Detailed visualization saved to: {output_file}")


def compare_models(stats_dict, output_dir='.'):
    """
    Compare RVV instruction usage across multiple models

    Args:
        stats_dict: Dictionary mapping model names to their statistics
        output_dir: Directory to save the comparison chart
    """
    if len(stats_dict) < 2:
        print("Need at least 2 models for comparison")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Collect all unique instructions across all models
    all_instructions = set()
    for stats in stats_dict.values():
        all_instructions.update(stats.get('instruction_stats', {}).keys())

    # Get top instructions across all models
    instruction_totals = {}
    for instr in all_instructions:
        total = sum(stats.get('instruction_stats', {}).get(instr, 0)
                    for stats in stats_dict.values())
        instruction_totals[instr] = total

    # Sort and take top 15
    top_instructions = sorted(instruction_totals.items(), key=lambda x: x[1], reverse=True)[:15]
    top_instr_names = [instr for instr, _ in top_instructions]

    # Prepare data for grouped bar chart
    model_names = list(stats_dict.keys())
    x = range(len(top_instr_names))
    width = 0.8 / len(model_names)

    fig, ax = plt.subplots(figsize=(14, 8))

    for i, model_name in enumerate(model_names):
        stats = stats_dict[model_name]
        instruction_stats = stats.get('instruction_stats', {})
        counts = [instruction_stats.get(instr, 0) for instr in top_instr_names]

        offset = (i - len(model_names) / 2) * width + width / 2
        ax.bar([pos + offset for pos in x], counts, width, label=model_name)

    ax.set_xlabel('RVV Instructions', fontweight='bold')
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_title('RVV Instruction Usage Comparison Across Models', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(top_instr_names, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    output_file = output_path / 'model_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nModel comparison chart saved to: {output_file}")


def visualize_instruction_breakdown_by_model(stats_dict, output_dir='.', top_n=20):
    """
    Create stacked horizontal bar chart showing instruction usage breakdown by model

    Args:
        stats_dict: Dictionary mapping model names to their statistics
        output_dir: Directory to save the chart
        top_n: Number of top instructions to show (default: 20)
    """
    if len(stats_dict) < 1:
        print("Need at least 1 model for breakdown visualization")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Collect all unique instructions and calculate totals
    instruction_totals = {}
    instruction_by_model = {}  # {instruction: {model: count}}

    for model_name, stats in stats_dict.items():
        instruction_stats = stats.get('instruction_stats', {})
        for instr, count in instruction_stats.items():
            if instr not in instruction_totals:
                instruction_totals[instr] = 0
                instruction_by_model[instr] = {}
            instruction_totals[instr] += count
            instruction_by_model[instr][model_name] = count

    # Sort by total count and take top N
    sorted_instructions = sorted(instruction_totals.items(), key=lambda x: x[1], reverse=True)
    top_instructions = sorted_instructions[:top_n]
    top_instr_names = [instr for instr, _ in top_instructions]
    top_instr_totals = [total for _, total in top_instructions]

    # Prepare data for stacked bar chart
    model_names = list(stats_dict.keys())
    colors = plt.cm.tab20(range(len(model_names)))

    # Create figure
    fig, ax = plt.subplots(figsize=(14, max(10, top_n * 0.4)))

    # Build stacked bars
    left_positions = [0] * len(top_instr_names)

    for model_idx, model_name in enumerate(model_names):
        model_counts = []
        for instr in top_instr_names:
            count = instruction_by_model[instr].get(model_name, 0)
            model_counts.append(count)

        # Only show in legend if this model has non-zero contribution
        if sum(model_counts) > 0:
            label = model_name[:20]  # Truncate long names
        else:
            label = None

        ax.barh(range(len(top_instr_names)), model_counts,
                left=left_positions, color=colors[model_idx],
                label=label, edgecolor='white', linewidth=0.5)

        # Update left positions for next stack
        left_positions = [left + count for left, count in zip(left_positions, model_counts)]

    # Add total count labels at the end of each bar
    for i, (instr_name, total) in enumerate(zip(top_instr_names, top_instr_totals)):
        ax.text(total, i, f'  {total:,}',
                va='center', fontsize=9, fontweight='bold')

    # Formatting
    ax.set_yticks(range(len(top_instr_names)))
    ax.set_yticklabels(top_instr_names, fontsize=10)
    ax.set_xlabel('Total Instruction Count', fontweight='bold', fontsize=12)
    ax.set_title(f'Top {top_n} RVV Instructions - Usage Breakdown by Model',
                 fontsize=14, fontweight='bold', pad=20)

    # Legend - only show models that contributed
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left',
              fontsize=9, framealpha=0.9)

    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Add instruction rank numbers
    for i in range(len(top_instr_names)):
        ax.text(-max(top_instr_totals) * 0.02, i, f'#{i + 1}',
                ha='right', va='center', fontsize=8, color='gray')

    plt.tight_layout()

    output_file = output_path / 'instruction_breakdown_by_model.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Instruction breakdown chart saved to: {output_file}")


if __name__ == '__main__':
    # Example usage
    print("This module is meant to be imported by arvvi.py")
    print("Use: python arvvi.py <binary> --visualize")
