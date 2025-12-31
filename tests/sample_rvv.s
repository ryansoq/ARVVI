# ARVVI Test Assembly - Comprehensive RVV Instruction Coverage
# 測試每個類別的代表性指令,驗證整個 objdump → 解析 → 統計 流程
#
# Expected Results (for CI/CD validation):
# Total RVV instructions: 37
#
# Breakdown by category:
#   1. Vector Configuration (3 instructions)
#      vsetvli:    1
#      vsetvl:     1
#      vsetivli:   1
#
#   2. Vector Load/Store (12 instructions)
#      Unit-Stride:  vle8(1) + vle32(1) + vse16(1) + vse64(1) = 4
#      Strided:      vlse8(1) + vlse32(1) + vsse16(1) + vsse64(1) = 4
#      Indexed:      vlxei8(1) + vlxei32(1) + vsxei16(1) + vsxei64(1) = 4
#
#   3. Vector Arithmetic (8 instructions)
#      Basic:    vadd(1) + vsub(1) + vmul(1) + vdiv(1) = 4
#      Multiply: vmacc(1) + vnmsac(1) = 2
#      Widen:    vwadd(1) = 1
#      Narrow:   vnsra(1) = 1
#
#   4. Vector Floating-point (8 instructions)
#      Basic:    vfadd(1) + vfsub(1) + vfmul(1) + vfdiv(1) = 4
#      Multiply: vfmadd(1) + vfnmsub(1) = 2
#      Accumulate: vfmacc(1) = 1
#      Special:    vfsqrt(1) = 1
#
#   5. Vector Other (6 instructions)
#      Shift:    vsll(1) = 1
#      Compare:  vmseq(1) + vmslt(1) = 2
#      Reduce:   vredsum(1) = 1
#      Mask:     vmand(1) = 1
#      Permute:  vslidedown(1) = 1

.text
.globl _start

_start:
    # Non-RVV setup (should NOT be counted)
    li      a0, 0x1000
    li      a1, 0x2000
    li      a2, 64

.section .data
vector_code:
    # ============================================================
    # 1. Vector Configuration 指令 (3 instructions)
    # ============================================================
    vsetvli     t0, a2, e32, m1, ta, ma    # 1
    vsetvl      t1, a2, t0                 # 2
    vsetivli    zero, 8, e64, m2, ta, ma   # 3

    # ============================================================
    # 2. Vector Load/Store 指令 (12 instructions)
    # ============================================================

    # Unit-Stride (4 instructions)
    vle8.v      v0, (a0)                   # 4
    vle32.v     v4, (a0)                   # 5
    vse16.v     v2, (a1)                   # 6
    vse64.v     v8, (a1)                   # 7

    # Strided (4 instructions)
    vlse8.v     v1, (a0), t0               # 8
    vlse32.v    v5, (a0), t0               # 9
    vsse16.v    v3, (a1), t0               # 10
    vsse64.v    v9, (a1), t0               # 11

    # Indexed (4 instructions)
    vlxei8.v    v10, (a0), v0              # 12
    vlxei32.v   v12, (a0), v4              # 13
    vsxei16.v   v11, (a1), v2              # 14
    vsxei64.v   v13, (a1), v8              # 15

    # ============================================================
    # 3. Vector 算術指令 (8 instructions)
    # ============================================================

    # 基本運算 (4 instructions)
    vadd.vv     v4, v4, v5                 # 16
    vsub.vv     v5, v5, v4                 # 17
    vmul.vv     v6, v4, v5                 # 18
    vdiv.vv     v7, v6, v5                 # 19

    # 乘加/累加運算 (2 instructions)
    vmacc.vv    v4, v5, v6                 # 20 - multiply-accumulate
    vnmsac.vv   v5, v6, v7                 # 21 - negative multiply-subtract-accumulate

    # 寬化運算 (1 instruction)
    vwadd.vv    v8, v4, v5                 # 22 - widening add

    # 窄化運算 (1 instruction)
    vnsra.wi    v4, v8, 4                  # 23 - narrowing shift right arithmetic

    # ============================================================
    # 4. Vector 浮點指令 (8 instructions)
    # ============================================================

    # 浮點基本運算 (4 instructions)
    vfadd.vv    v16, v16, v17              # 24
    vfsub.vv    v17, v17, v16              # 25
    vfmul.vv    v18, v16, v17              # 26
    vfdiv.vv    v19, v18, v17              # 27

    # 浮點乘加 (2 instructions)
    vfmadd.vv   v16, v17, v18              # 28 - multiply-add
    vfnmsub.vv  v17, v18, v19              # 29 - negative multiply-subtract

    # 浮點累加 (1 instruction)
    vfmacc.vv   v16, v17, v18              # 30 - multiply-accumulate

    # 浮點特殊運算 (1 instruction)
    vfsqrt.v    v20, v16                   # 31 - square root

    # ============================================================
    # 5. Vector 其他指令 (6 instructions)
    # ============================================================

    # 位移指令 (1 instruction)
    vsll.vi     v4, v4, 2                  # 32 - shift left logical

    # 比較指令 (2 instructions)
    vmseq.vv    v0, v4, v5                 # 33 - mask set equal
    vmslt.vv    v1, v4, v5                 # 34 - mask set less than

    # 歸約指令 (1 instruction)
    vredsum.vs  v8, v4, v5                 # 35 - reduction sum

    # 遮罩指令 (1 instruction)
    vmand.mm    v0, v0, v1                 # 36 - mask and

    # 排列指令 (1 instruction)
    vslidedown.vi v4, v5, 4                # 37 - slide down

    # Non-RVV epilogue (should NOT be counted)
    ret

.size vector_code, .-vector_code
