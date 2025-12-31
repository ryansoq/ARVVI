# RISC-V Vector Extension Test Sample
# This file tests ARVVI's ability to correctly identify and count RVV instructions
#
# Expected Results:
# Total RVV instructions: 25
# Breakdown:
#   vsetvli:   3
#   vle32:     4
#   vse32:     3
#   vadd:      2
#   vmul:      2
#   vfadd:     2
#   vfmul:     2
#   vfmacc:    2
#   vslidedown: 1
#   vmerge:    1
#   vmseq:     1
#   vle8:      1
#   vse8:      1

.text
.globl _start

_start:
    # Test 1: Basic vector addition (e32, m1)
    li a0, 32
    vsetvli t0, a0, e32, m1
    vle32.v v1, (a1)
    vle32.v v2, (a2)
    vadd.vv v3, v1, v2
    vse32.v v3, (a3)

    # Test 2: Vector multiplication (e32, m2)
    vsetvli t0, a0, e32, m2
    vle32.v v4, (a4)
    vle32.v v6, (a5)
    vmul.vv v8, v4, v6
    vse32.v v8, (a6)

    # Test 3: Floating-point operations (e32, m1)
    vsetvli t0, a0, e32, m1
    vle32.v v10, (a1)
    vle32.v v11, (a2)
    vfadd.vv v12, v10, v11
    vfmul.vv v13, v10, v11
    vfmacc.vv v12, v10, v11
    vfmacc.vv v13, v11, v10
    vse32.v v12, (a3)

    # Test 4: Vector permutation
    vslidedown.vi v14, v12, 4

    # Test 5: Vector mask operations
    vmseq.vv v0, v1, v2
    vmerge.vvm v15, v1, v2, v0

    # Test 6: Different element widths (e8)
    vle8.v v16, (a1)
    vadd.vv v17, v16, v16
    vse8.v v17, (a2)

    # Return
    li a0, 0
    ret

.data
test_data:
    .word 1, 2, 3, 4, 5, 6, 7, 8
