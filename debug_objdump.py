#!/usr/bin/env python3
"""
Debug tool to inspect objdump output
"""
import subprocess
import sys

def inspect_objdump(binary_path, objdump_path, num_lines=100):
    """Show first N lines of objdump output for inspection"""

    cmd = [objdump_path, '-d', binary_path]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    lines = result.stdout.split('\n')

    print(f"Binary: {binary_path}")
    print(f"Total output lines: {len(lines)}")
    print(f"\nFirst {num_lines} lines of objdump output:")
    print("=" * 80)

    for i, line in enumerate(lines[:num_lines], 1):
        print(f"{i:4d}: {line}")

    print("\n" + "=" * 80)
    print(f"\nLast {num_lines} lines of objdump output:")
    print("=" * 80)

    for i, line in enumerate(lines[-num_lines:], len(lines)-num_lines+1):
        print(f"{i:4d}: {line}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python debug_objdump.py <binary_path>")
        sys.exit(1)

    binary = sys.argv[1]
    objdump = "/home/ymchang/AndeSight-v5_4_0/toolchains-bin/nds64le-elf-newlib-v5d/bin/riscv64-elf-objdump"

    inspect_objdump(binary, objdump, num_lines=50)
