#!/usr/bin/env python3
"""
ARVVI - AndeSight RISC-V Vector Instruction Analyzer
Analyzes RVV instruction usage in RISC-V binaries for AI model optimization
"""

import argparse
import subprocess
import re
import sys
from collections import defaultdict
from pathlib import Path
import json

# Default toolchain path
DEFAULT_OBJDUMP = "/home/ymchang/AndeSight-v5_4_0/toolchains-bin/nds64le-elf-newlib-v5d/bin/riscv64-elf-objdump"


class RVVAnalyzer:
    """Analyzer for RISC-V Vector instructions"""

    # RVV instruction patterns (v-prefix instructions)
    RVV_PATTERNS = [
        # Vector arithmetic instructions
        r'\bvadd\b', r'\bvsub\b', r'\bvrsub\b',
        r'\bvmul\b', r'\bvmulh\b', r'\bvmulhu\b', r'\bvmulhsu\b',
        r'\bvdiv\b', r'\bvdivu\b', r'\bvrem\b', r'\bvremu\b',
        r'\bvmadd\b', r'\bvnmsub\b', r'\bvmacc\b', r'\bvnmsac\b',

        # Vector widening/narrowing arithmetic
        r'\bvwadd\b', r'\bvwsub\b', r'\bvwmul\b', r'\bvwmulu\b', r'\bvwmulsu\b',
        r'\bvnsra\b', r'\bvnsrl\b',

        # Vector shift instructions
        r'\bvsll\b', r'\bvsrl\b', r'\bvsra\b',

        # Vector comparison instructions
        r'\bvmseq\b', r'\bvmsne\b', r'\bvmsltu\b', r'\bvmslt\b',
        r'\bvmsleu\b', r'\bvmsle\b', r'\bvmsgtu\b', r'\bvmsgt\b',

        # Vector min/max
        r'\bvmin\b', r'\bvminu\b', r'\bvmax\b', r'\bvmaxu\b',

        # Vector logical instructions
        r'\bvand\b', r'\bvor\b', r'\bvxor\b', r'\bvnot\b',

        # Vector load/store instructions
        r'\bvle\d+\b', r'\bvse\d+\b',  # unit-stride
        r'\bvlse\d+\b', r'\bvsse\d+\b',  # strided
        r'\bvlxe\d+\b', r'\bvsxe\d+\b', r'\bvsuxe\d+\b',  # indexed
        r'\bvleff\b', r'\bvlm\b', r'\bvsm\b',

        # Vector AMO operations
        r'\bvamoswap\b', r'\bvamoadd\b', r'\bvamoxor\b', r'\bvamoand\b',
        r'\bvamoor\b', r'\bvamomin\b', r'\bvamomax\b', r'\bvamominu\b', r'\bvamomaxu\b',

        # Vector fixed-point arithmetic
        r'\bvsadd\b', r'\bvsaddu\b', r'\bvssub\b', r'\bvssubu\b',
        r'\bvaaddu\b', r'\bvaadd\b', r'\bvasubu\b', r'\bvasub\b',
        r'\bvsmul\b', r'\bvssra\b', r'\bvssrl\b',

        # Vector reduction operations
        r'\bvredsum\b', r'\bvredand\b', r'\bvredor\b', r'\bvredxor\b',
        r'\bvredminu\b', r'\bvredmin\b', r'\bvredmaxu\b', r'\bvredmax\b',
        r'\bvwredsum\b', r'\bvwredsumu\b',

        # Vector mask operations
        r'\bvmand\b', r'\bvmnand\b', r'\bvmandn\b', r'\bvmxor\b',
        r'\bvmor\b', r'\bvmnor\b', r'\bvmorn\b', r'\bvmxnor\b',
        r'\bvpopc\b', r'\bvfirst\b', r'\bvmsbf\b', r'\bvmsif\b', r'\bvmsof\b',
        r'\bviota\b', r'\bvid\b',

        # Vector permutation instructions
        r'\bvslideup\b', r'\bvslidedown\b', r'\bvslide1up\b', r'\bvslide1down\b',
        r'\bvrgather\b', r'\bvrgatherei16\b', r'\bvcompress\b',

        # Vector merge and move
        r'\bvmerge\b', r'\bvmv\b',

        # Vector floating-point instructions
        r'\bvfadd\b', r'\bvfsub\b', r'\bvfrsub\b',
        r'\bvfmul\b', r'\bvfdiv\b', r'\bvfrdiv\b',
        r'\bvfmadd\b', r'\bvfnmadd\b', r'\bvfmsub\b', r'\bvfnmsub\b',
        r'\bvfmacc\b', r'\bvfnmacc\b', r'\bvfmsac\b', r'\bvfnmsac\b',
        r'\bvfwadd\b', r'\bvfwsub\b', r'\bvfwmul\b',
        r'\bvfsqrt\b', r'\bvfrsqrt7\b', r'\bvfrec7\b',
        r'\bvfmin\b', r'\bvfmax\b',
        r'\bvfsgnj\b', r'\bvfsgnjn\b', r'\bvfsgnjx\b',
        r'\bvfclass\b', r'\bvfmerge\b',

        # Vector floating-point compare
        r'\bvmfeq\b', r'\bvmfne\b', r'\bvmflt\b', r'\bvmfle\b', r'\bvmfgt\b', r'\bvmfge\b',

        # Vector floating-point conversion
        r'\bvfcvt\b', r'\bvfwcvt\b', r'\bvfncvt\b',

        # Vector configuration instructions
        r'\bvsetvl\b', r'\bvsetvli\b', r'\bvsetivli\b',
    ]

    def __init__(self, objdump_path=DEFAULT_OBJDUMP, functions=None, sections=None):
        self.objdump_path = objdump_path
        self.functions = functions  # List of function names to analyze
        self.sections = sections  # List of sections to analyze
        self.instruction_stats = defaultdict(int)
        self.section_stats = defaultdict(int)  # Track RVV instructions per section
        self.total_instructions = 0
        self.rvv_instructions = 0

    def run_objdump(self, binary_path):
        """Run objdump on the binary file"""
        try:
            cmd = [self.objdump_path, '-D']  # Use -D to disassemble ALL sections

            # Add -j <section> for each specified section (for speed optimization)
            if self.sections:
                for section in self.sections:
                    cmd.append('-j')
                    cmd.append(section)

            # Add --disassemble=<function> for each specified function
            if self.functions:
                for func in self.functions:
                    cmd.append(f'--disassemble={func}')

            cmd.append(binary_path)

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running objdump: {e}", file=sys.stderr)
            print(f"stderr: {e.stderr}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print(f"Error: objdump not found at {self.objdump_path}", file=sys.stderr)
            print("Please check your toolchain installation", file=sys.stderr)
            sys.exit(1)

    def parse_disassembly(self, disassembly):
        """Parse objdump output and count RVV instructions"""
        lines = disassembly.split('\n')
        current_section = 'unknown'

        for line in lines:
            # Detect section headers
            # Format: "Disassembly of section .text:"
            section_match = re.match(r'Disassembly of section (.+):', line)
            if section_match:
                current_section = section_match.group(1)
                continue

            # Skip empty lines and file format headers
            line = line.strip()
            if not line or line.startswith('file format'):
                continue

            # Match instruction lines (format: address: bytes  instruction operands)
            # Example: 10000: 02010113  addi  sp,sp,32
            match = re.match(r'\s*[0-9a-f]+:\s+[0-9a-f]+\s+(\w+)', line)
            if match:
                instruction = match.group(1)
                self.total_instructions += 1

                # Check if it's an RVV instruction
                if self._is_rvv_instruction(instruction):
                    self.instruction_stats[instruction] += 1
                    self.section_stats[current_section] += 1
                    self.rvv_instructions += 1

    def _is_rvv_instruction(self, instruction):
        """Check if an instruction is an RVV instruction"""
        # Most RVV instructions start with 'v'
        for pattern in self.RVV_PATTERNS:
            if re.match(pattern, instruction, re.IGNORECASE):
                return True
        return False

    def print_statistics(self, model_name=None):
        """Print instruction statistics"""
        if model_name:
            print(f"\n{'='*60}")
            print(f"Model: {model_name}")
            print(f"{'='*60}")

        print(f"\nTotal instructions: {self.total_instructions}")
        print(f"RVV instructions: {self.rvv_instructions}")
        if self.total_instructions > 0:
            percentage = (self.rvv_instructions / self.total_instructions) * 100
            print(f"RVV usage: {percentage:.2f}%")

        # Print section distribution
        if self.section_stats:
            print("\nRVV Instructions by Section:")
            print("-" * 60)
            sorted_sections = sorted(self.section_stats.items(), key=lambda x: x[1], reverse=True)
            for section, count in sorted_sections:
                percentage = (count / self.rvv_instructions) * 100 if self.rvv_instructions > 0 else 0
                print(f"{section:30s}: {count:6d} ({percentage:5.1f}%)")

        print("\nRVV Instruction Distribution:")
        print("-" * 60)

        # Sort by count (descending)
        sorted_stats = sorted(self.instruction_stats.items(), key=lambda x: x[1], reverse=True)

        for instruction, count in sorted_stats:
            print(f"{instruction:20s}: {count:6d}")

    def get_statistics(self):
        """Return statistics as a dictionary"""
        return {
            'total_instructions': self.total_instructions,
            'rvv_instructions': self.rvv_instructions,
            'instruction_stats': dict(self.instruction_stats),
            'section_stats': dict(self.section_stats)
        }

    def save_json(self, output_path, model_name=None):
        """Save statistics to JSON file"""
        data = {
            'model': model_name or 'unknown',
            'statistics': self.get_statistics()
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\nStatistics saved to: {output_path}")


def scan_models(models_dir, objdump_path, sections=None, visualize=False):
    """
    Scan a directory for IREE models and analyze all .adx files

    Directory structure expected:
    models/
    ├── Bird/
    │   ├── bird.mlir
    │   └── bird/OUTPUT/bird.adx
    ├── Mobile_Vit/
    │   ├── Mobile_Vit.mlir
    │   └── Mobile_Vit/OUTPUT/Mobile_Vit.adx
    └── YOLOv5n/
        ├── yolov5n.tosa.mlir
        └── yolov5n.tosa/OUTPUT/yolov5n.tosa.adx
    """
    models_path = Path(models_dir)
    if not models_path.exists():
        print(f"Error: Directory not found: {models_dir}", file=sys.stderr)
        return []

    # Find all .mlir files in direct subdirectories only (not recursive)
    # Pattern: models/*/xxx.mlir (one level deep)
    mlir_files = []
    for subdir in models_path.iterdir():
        if subdir.is_dir():
            # Find .mlir files in this subdirectory (not deeper)
            mlir_files.extend(subdir.glob('*.mlir'))

    if not mlir_files:
        print(f"No .mlir files found in {models_dir}", file=sys.stderr)
        return []

    print(f"\nFound {len(mlir_files)} model(s) to analyze")
    print(f"{'='*60}\n")

    results = []
    analyzed_count = 0
    skipped_count = 0

    for idx, mlir_file in enumerate(mlir_files, 1):
        # Extract model name (remove .mlir extension)
        model_basename = mlir_file.stem  # e.g., "bird" or "yolov5n.tosa"
        model_dir = mlir_file.parent

        # Construct expected .adx path
        # models/Bird/bird.mlir -> models/Bird/bird/OUTPUT/bird.adx
        adx_path = model_dir / model_basename / "OUTPUT" / f"{model_basename}.adx"

        print(f"[{idx}/{len(mlir_files)}] Processing: {model_basename}")

        if not adx_path.exists():
            print(f"  ⚠️  Skipping: {adx_path} not found")
            skipped_count += 1
            continue

        try:
            # Analyze the model
            analyzer = RVVAnalyzer(objdump_path=objdump_path, sections=sections)

            print(f"  📊 Analyzing: {adx_path}")
            disassembly = analyzer.run_objdump(str(adx_path))
            analyzer.parse_disassembly(disassembly)

            # Save JSON to OUTPUT directory
            output_dir = adx_path.parent
            json_path = output_dir / f"{model_basename}_rvv_stats.json"
            analyzer.save_json(str(json_path), model_basename)

            # Generate visualization if requested
            if visualize:
                try:
                    from arvvi_visualizer import visualize_statistics
                    visualize_statistics(analyzer.get_statistics(), model_basename, str(output_dir))
                    print("  ✅ Visualization saved")
                except ImportError:
                    print("  ⚠️  matplotlib not installed, skipping visualization")

            results.append({
                'model': model_basename,
                'adx_path': str(adx_path),
                'json_path': str(json_path),
                'stats': analyzer.get_statistics()
            })

            analyzed_count += 1
            print(f"  ✅ Complete: {analyzer.rvv_instructions} RVV instructions\n")

        except Exception as e:
            print(f"  ❌ Error analyzing {model_basename}: {e}\n")
            skipped_count += 1
            continue

    # Print summary
    print("\n" + "=" * 60)
    print("Batch Analysis Summary")
    print("=" * 60)
    print(f"Total models found:    {len(mlir_files)}")
    print(f"Successfully analyzed: {analyzed_count}")
    print(f"Skipped:              {skipped_count}")
    print("=" * 60 + "\n")

    return results


def main():
    parser = argparse.ArgumentParser(
        description='ARVVI - AndeSight RISC-V Vector Instruction Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Single file analysis:
    %(prog)s /models/mobilenetV1/OUTPUT/output.adx
    %(prog)s /models/mobilenetV1/OUTPUT/output.adx -o stats.json
    %(prog)s /models/mobilenetV1/OUTPUT/output.adx --section .data
    %(prog)s /models/mobilenetV1/OUTPUT/output.adx --function main

  Batch analysis (scan directory):
    %(prog)s --scan models/ --section .data --visualize
    %(prog)s --scan ../AutoIREE_zoo/models/ --section .data -v
        """
    )

    parser.add_argument('binary', nargs='?', help='Path to the binary file to analyze (not used with --scan)')
    parser.add_argument('--scan', dest='scan_dir', metavar='DIR',
                        help='Scan directory for models and analyze all .adx files (batch mode)')
    parser.add_argument('-o', '--output', help='Output JSON file for statistics')
    parser.add_argument('-m', '--model', help='Model name for the report')
    parser.add_argument('--objdump', default=DEFAULT_OBJDUMP,
                        help=f'Path to objdump (default: {DEFAULT_OBJDUMP})')
    parser.add_argument('-s', '--section', dest='sections',
                        help='Analyze specific section(s) only (comma-separated). Example: .data or .data,.text (faster for IREE VMFB)')
    parser.add_argument('-f', '--function', dest='functions',
                        help='Analyze specific function(s) only (comma-separated). Example: main,inference')
    parser.add_argument('-v', '--visualize', action='store_true',
                        help='Generate visualization charts')

    args = parser.parse_args()

    # Parse section list if provided
    sections = None
    if args.sections:
        sections = [s.strip() for s in args.sections.split(',')]

    # Check if using scan mode
    if args.scan_dir:
        # Batch mode: scan directory
        scan_models(
            models_dir=args.scan_dir,
            objdump_path=args.objdump,
            sections=sections,
            visualize=args.visualize
        )
        return 0

    # Single file mode
    if not args.binary:
        parser.error("Either provide a binary file or use --scan <directory>")

    # Check if binary file exists
    binary_path = Path(args.binary)
    if not binary_path.exists():
        print(f"Error: Binary file not found: {args.binary}", file=sys.stderr)
        sys.exit(1)

    # Determine model name
    model_name = args.model
    if not model_name:
        # Try to extract from path
        model_name = binary_path.parent.parent.name if binary_path.parent.parent.name else binary_path.stem

    # Parse function list if provided
    functions = None
    if args.functions:
        functions = [f.strip() for f in args.functions.split(',')]

    # Run analysis
    print(f"Analyzing binary: {args.binary}")
    print(f"Using objdump: {args.objdump}")
    if sections:
        print(f"Analyzing section(s): {', '.join(sections)} (faster mode)")
    else:
        print("Analyzing all sections")
    if functions:
        print(f"Analyzing function(s): {', '.join(functions)}")
    else:
        print("Analyzing all functions")

    analyzer = RVVAnalyzer(objdump_path=args.objdump, functions=functions, sections=sections)

    print("\nRunning objdump...")
    disassembly = analyzer.run_objdump(args.binary)

    print("Parsing instructions...")
    analyzer.parse_disassembly(disassembly)

    # Print statistics
    analyzer.print_statistics(model_name)

    # Save to JSON if requested
    if args.output:
        analyzer.save_json(args.output, model_name)

    # Generate visualization if requested
    if args.visualize:
        try:
            from arvvi_visualizer import visualize_statistics
            visualize_statistics(analyzer.get_statistics(), model_name)
        except ImportError:
            print("\nWarning: matplotlib not installed. Install with: pip install matplotlib")
            print("Skipping visualization.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
