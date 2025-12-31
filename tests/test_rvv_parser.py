#!/usr/bin/env python3
"""
Unit tests for ARVVI RVV instruction parser
"""

import sys
import os

# Add parent directory to path for importing arvvi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import subprocess  # noqa: E402
import shutil  # noqa: E402
from arvvi import RVVAnalyzer  # noqa: E402

# Check if RISC-V toolchain is available
HAS_RISCV_TOOLCHAIN = (shutil.which('riscv64-elf-as') is not None and
                       shutil.which('riscv64-elf-objdump') is not None)


def test_rvv_instruction_detection():
    """Test RVV instruction pattern matching"""
    analyzer = RVVAnalyzer()

    # Test vector arithmetic instructions
    assert analyzer._is_rvv_instruction('vadd') is True
    assert analyzer._is_rvv_instruction('vsub') is True
    assert analyzer._is_rvv_instruction('vmul') is True

    # Test vector floating-point instructions
    assert analyzer._is_rvv_instruction('vfadd') is True
    assert analyzer._is_rvv_instruction('vfmul') is True
    assert analyzer._is_rvv_instruction('vfmacc') is True

    # Test vector load/store instructions
    assert analyzer._is_rvv_instruction('vle8') is True
    assert analyzer._is_rvv_instruction('vle32') is True
    assert analyzer._is_rvv_instruction('vse64') is True

    # Test vector configuration instructions
    assert analyzer._is_rvv_instruction('vsetvli') is True
    assert analyzer._is_rvv_instruction('vsetivli') is True

    # Test non-RVV instructions
    assert analyzer._is_rvv_instruction('add') is False
    assert analyzer._is_rvv_instruction('mul') is False
    assert analyzer._is_rvv_instruction('ld') is False


def test_disassembly_parsing():
    """Test objdump output parsing"""
    analyzer = RVVAnalyzer()

    # Sample objdump output
    sample_disassembly = """
bird.adx:     file format elf64-littleriscv

Disassembly of section .text:

0000000000010000 <_start>:
   10000:       00000517                auipc   a0,0x0
   10004:       02010113                addi    sp,sp,32

Disassembly of section .data:

0000000000020000 <vector_code>:
   20000:       0d007057                vsetvli zero,zero,e32,m2
   20004:       02050207                vle32.v v4,(a0)
   20008:       02058287                vle32.v v5,(a1)
   2000c:       020282d7                vadd.vv v5,v4,v5
   20010:       02058227                vse32.v v4,(a1)
"""

    analyzer.parse_disassembly(sample_disassembly)

    # Check statistics
    # Total: 2 instructions in .text (auipc, addi) + 5 RVV in .data = 7
    assert analyzer.total_instructions == 7
    assert analyzer.rvv_instructions == 5
    assert analyzer.instruction_stats['vsetvli'] == 1
    assert analyzer.instruction_stats['vle32'] == 2
    assert analyzer.instruction_stats['vadd'] == 1
    assert analyzer.instruction_stats['vse32'] == 1

    # Check section tracking
    # .data section contains all 5 RVV instructions
    assert analyzer.section_stats['.data'] == 5
    # .text section contains 0 RVV instructions (auipc and addi are not RVV)
    assert analyzer.section_stats.get('.text', 0) == 0


def test_section_parsing():
    """Test section detection"""
    analyzer = RVVAnalyzer()

    disassembly = """
Disassembly of section .text:
   10000:       00000517                auipc   a0,0x0

Disassembly of section .data:
   20000:       0d007057                vsetvli zero,zero,e32,m2
   20004:       02050207                vle32.v v4,(a0)

Disassembly of section .rodata:
   30000:       02058287                vle32.v v5,(a1)
"""

    analyzer.parse_disassembly(disassembly)

    assert analyzer.section_stats['.data'] == 2
    assert analyzer.section_stats['.rodata'] == 1


def test_comprehensive_assembly_file():
    """Test complete pipeline with actual assembly file (requires RISC-V toolchain)"""
    if not HAS_RISCV_TOOLCHAIN:
        print("⏭️  Skipping: RISC-V toolchain not available")
        return

    # Path to test files
    test_dir = os.path.dirname(__file__)
    asm_file = os.path.join(test_dir, 'sample_rvv.s')
    obj_file = os.path.join(test_dir, 'sample_rvv.o')

    try:
        # Step 1: Assemble the test file
        subprocess.run(['riscv64-elf-as', asm_file, '-o', obj_file],
                       check=True, capture_output=True)

        # Step 2: Disassemble using objdump
        result = subprocess.run(['riscv64-elf-objdump', '-D', obj_file],
                                check=True, capture_output=True, text=True)
        disassembly = result.stdout

        # Step 3: Parse with ARVVI
        analyzer = RVVAnalyzer()
        analyzer.parse_disassembly(disassembly)

        # Step 4: Validate expected counts
        # Total RVV instructions should be 37
        assert analyzer.rvv_instructions == 37, \
            f"Expected 37 RVV instructions, got {analyzer.rvv_instructions}"

        # Validate instruction breakdown by category
        expected_counts = {
            # 1. Vector Configuration (3)
            'vsetvli': 1,
            'vsetvl': 1,
            'vsetivli': 1,

            # 2. Vector Load/Store (12)
            'vle8': 1,
            'vle32': 1,
            'vse16': 1,
            'vse64': 1,
            'vlse8': 1,
            'vlse32': 1,
            'vsse16': 1,
            'vsse64': 1,
            'vlxei8': 1,
            'vlxei32': 1,
            'vsxei16': 1,
            'vsxei64': 1,

            # 3. Vector Arithmetic (8)
            'vadd': 1,
            'vsub': 1,
            'vmul': 1,
            'vdiv': 1,
            'vmacc': 1,
            'vnmsac': 1,
            'vwadd': 1,
            'vnsra': 1,

            # 4. Vector Floating-point (8)
            'vfadd': 1,
            'vfsub': 1,
            'vfmul': 1,
            'vfdiv': 1,
            'vfmadd': 1,
            'vfnmsub': 1,
            'vfmacc': 1,
            'vfsqrt': 1,

            # 5. Vector Other (6)
            'vsll': 1,
            'vmseq': 1,
            'vmslt': 1,
            'vredsum': 1,
            'vmand': 1,
            'vslidedown': 1,
        }

        for instr, expected_count in expected_counts.items():
            actual_count = analyzer.instruction_stats.get(instr, 0)
            assert actual_count == expected_count, \
                f"Expected {instr}: {expected_count}, got {actual_count}"

        # Validate most instructions are in .data section (IREE pattern)
        data_count = analyzer.section_stats.get('.data', 0)
        assert data_count > 0, "Expected RVV instructions in .data section"

        print(f"✅ Comprehensive test passed: {analyzer.rvv_instructions} RVV instructions detected")

    finally:
        # Cleanup
        if os.path.exists(obj_file):
            os.remove(obj_file)


if __name__ == '__main__':
    test_rvv_instruction_detection()
    test_disassembly_parsing()
    test_section_parsing()
    test_comprehensive_assembly_file()
    print("✅ All tests passed!")
