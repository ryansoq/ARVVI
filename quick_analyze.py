#!/usr/bin/env python3
"""
Quick analyzer to check what instructions are actually being used
"""
import subprocess
import sys
from collections import defaultdict
import re

def analyze_all_instructions(binary_path, objdump_path):
    """Analyze all instructions, not just RVV"""

    # Run objdump
    cmd = [objdump_path, '-d', binary_path]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    instruction_stats = defaultdict(int)
    total_instructions = 0

    lines = result.stdout.split('\n')

    for line in lines:
        line = line.strip()
        if not line or line.startswith('Disassembly') or line.startswith('file format'):
            continue

        # Match instruction lines
        match = re.match(r'\s*[0-9a-f]+:\s+[0-9a-f]+\s+(\w+)', line)
        if match:
            instruction = match.group(1)
            instruction_stats[instruction] += 1
            total_instructions += 1

    return instruction_stats, total_instructions

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python quick_analyze.py <binary_path>")
        sys.exit(1)

    binary = sys.argv[1]
    objdump = "/home/ymchang/AndeSight-v5_4_0/toolchains-bin/nds64le-elf-newlib-v5d/bin/riscv64-elf-objdump"

    print(f"Analyzing all instructions in: {binary}\n")

    stats, total = analyze_all_instructions(binary, objdump)

    # Sort by count
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)

    print(f"Total instructions: {total:,}\n")
    print(f"Top 50 most used instructions:")
    print(f"{'Instruction':<20} {'Count':<15} {'Percentage':<10}")
    print("-" * 50)

    for instr, count in sorted_stats[:50]:
        percentage = (count / total) * 100
        print(f"{instr:<20} {count:<15,} {percentage:>6.2f}%")

    # Categorize instructions
    rvv_count = sum(count for instr, count in stats.items() if instr.startswith('v'))
    scalar_load = sum(count for instr, count in stats.items() if instr in ['ld', 'lw', 'lh', 'lb', 'lbu', 'lhu', 'lwu'])
    scalar_store = sum(count for instr, count in stats.items() if instr in ['sd', 'sw', 'sh', 'sb'])
    scalar_arith = sum(count for instr, count in stats.items() if instr in ['add', 'addi', 'sub', 'mul', 'div', 'rem'])

    print(f"\n{'='*50}")
    print(f"Instruction Categories:")
    print(f"{'='*50}")
    print(f"RVV instructions:      {rvv_count:>10,} ({rvv_count/total*100:>6.2f}%)")
    print(f"Scalar Load:           {scalar_load:>10,} ({scalar_load/total*100:>6.2f}%)")
    print(f"Scalar Store:          {scalar_store:>10,} ({scalar_store/total*100:>6.2f}%)")
    print(f"Scalar Arithmetic:     {scalar_arith:>10,} ({scalar_arith/total*100:>6.2f}%)")
