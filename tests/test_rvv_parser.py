#!/usr/bin/env python3
"""
Unit tests for ARVVI RVV instruction parser
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arvvi import RVVAnalyzer


def test_rvv_instruction_detection():
    """Test RVV instruction pattern matching"""
    analyzer = RVVAnalyzer()

    # Test vector arithmetic instructions
    assert analyzer._is_rvv_instruction('vadd') == True
    assert analyzer._is_rvv_instruction('vsub') == True
    assert analyzer._is_rvv_instruction('vmul') == True

    # Test vector floating-point instructions
    assert analyzer._is_rvv_instruction('vfadd') == True
    assert analyzer._is_rvv_instruction('vfmul') == True
    assert analyzer._is_rvv_instruction('vfmacc') == True

    # Test vector load/store instructions
    assert analyzer._is_rvv_instruction('vle8') == True
    assert analyzer._is_rvv_instruction('vle32') == True
    assert analyzer._is_rvv_instruction('vse64') == True

    # Test vector configuration instructions
    assert analyzer._is_rvv_instruction('vsetvli') == True
    assert analyzer._is_rvv_instruction('vsetivli') == True

    # Test non-RVV instructions
    assert analyzer._is_rvv_instruction('add') == False
    assert analyzer._is_rvv_instruction('mul') == False
    assert analyzer._is_rvv_instruction('ld') == False


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
    assert analyzer.total_instructions == 8
    assert analyzer.rvv_instructions == 5
    assert analyzer.instruction_stats['vsetvli'] == 1
    assert analyzer.instruction_stats['vle32'] == 2
    assert analyzer.instruction_stats['vadd'] == 1
    assert analyzer.instruction_stats['vse32'] == 1

    # Check section tracking
    assert analyzer.section_stats['.data'] == 5
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


if __name__ == '__main__':
    test_rvv_instruction_detection()
    test_disassembly_parsing()
    test_section_parsing()
    print("✅ All tests passed!")
