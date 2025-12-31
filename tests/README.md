# ARVVI Test Suite

## 測試策略

ARVVI 採用 **分層測試策略**,確保整個 objdump → 解析 → 統計 流程的正確性:

### 1️⃣ 輕量級測試 (快速,每次 CI/CD 都執行)
- 測試指令模式匹配
- 測試 objdump 輸出解析
- 測試 section 追蹤

### 2️⃣ 完整整合測試 (需要 RISC-V toolchain)
- 使用真實組合語言檔案
- 通過 riscv64-elf-as + objdump 完整流程
- 驗證 5 大類別共 37 個代表性指令

## Running Tests

```bash
# 執行所有測試
python -m pytest tests/ -v

# 直接執行測試腳本
python tests/test_rvv_parser.py

# 使用 coverage 報告
python -m pytest tests/ --cov=arvvi --cov-report=html
```

## Test Structure

### test_rvv_parser.py
包含 4 個測試函式:

1. **test_rvv_instruction_detection()** - 測試 RVV 指令模式匹配
   - 驗證 vadd, vfadd, vle32 等指令被正確識別
   - 驗證 add, mul, ld 等非 RVV 指令被正確拒絕

2. **test_disassembly_parsing()** - 測試 objdump 輸出解析
   - 使用模擬的 objdump 輸出
   - 驗證指令計數和 section 追蹤

3. **test_section_parsing()** - 測試 section 偵測
   - 驗證 .text, .data, .rodata 的正確識別
   - 驗證每個 section 的 RVV 指令計數

4. **test_comprehensive_assembly_file()** - 完整整合測試
   - ⚠️ 需要 RISC-V toolchain (riscv64-elf-as, riscv64-elf-objdump)
   - 使用 `sample_rvv.s` 測試 37 個代表性指令
   - 驗證整個 assemble → disassemble → parse → count 流程
   - 如果沒有 toolchain 會自動跳過

### sample_rvv.s
綜合測試用組合語言檔案,涵蓋 5 大類別:

#### 1. Vector Configuration (3 instructions)
- vsetvli, vsetvl, vsetivli

#### 2. Vector Load/Store (12 instructions)
- **Unit-Stride**: vle8, vle32, vse16, vse64
- **Strided**: vlse8, vlse32, vsse16, vsse64
- **Indexed**: vlxei8, vlxei32, vsxei16, vsxei64

#### 3. Vector Arithmetic (8 instructions)
- **基本運算**: vadd, vsub, vmul, vdiv
- **乘加運算**: vmacc, vnmsac
- **寬化運算**: vwadd
- **窄化運算**: vnsra

#### 4. Vector Floating-point (8 instructions)
- **基本運算**: vfadd, vfsub, vfmul, vfdiv
- **浮點乘加**: vfmadd, vfnmsub
- **浮點累加**: vfmacc
- **特殊運算**: vfsqrt

#### 5. Vector Other (6 instructions)
- **位移**: vsll
- **比較**: vmseq, vmslt
- **歸約**: vredsum
- **遮罩**: vmand
- **排列**: vslidedown

## 為什麼用代表性指令而非全部測試?

✅ **優點**:
- 測試快速 (37 個指令 vs 數百個)
- 涵蓋所有指令類別和模式
- 易於維護和理解
- 能驗證整個 objdump pipeline

❌ **不需要**測試所有變體:
- vle8, vle16, vle32, vle64 都遵循相同模式
- 測試 vle8 + vle32 已足夠驗證 `vle*` 的匹配規則

## 在 CI/CD 中設置 RISC-V Toolchain

如果你的 CI/CD 環境需要執行完整測試:

```yaml
# .github/workflows/test.yml
- name: Install RISC-V Toolchain (optional)
  run: |
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y gcc-riscv64-unknown-elf

    # 或從 GitHub releases 下載
    wget https://github.com/riscv/riscv-gnu-toolchain/releases/...
```

沒有 toolchain 時測試會自動跳過,不影響其他測試。

## 新增測試案例

要新增測試案例:

1. **簡單測試** - 直接在 `test_rvv_parser.py` 新增函式
2. **完整測試** - 修改 `sample_rvv.s` 並更新 expected_counts

範例:
```python
def test_new_instruction_category():
    """Test new RVV instruction category"""
    analyzer = RVVAnalyzer()

    sample = """
    vrgather.vv v1, v2, v3
    vcompress.vm v4, v5, v0
    """

    analyzer.parse_disassembly(sample)
    assert analyzer.instruction_stats['vrgather'] == 1
    assert analyzer.instruction_stats['vcompress'] == 1
```

## 常見問題

**Q: 為什麼有些測試會被跳過?**
A: `test_comprehensive_assembly_file()` 需要 RISC-V toolchain。沒有安裝時會自動跳過,顯示 "⏭️ Skipping"。

**Q: 如何驗證 ARVVI 能正確處理真實 IREE 輸出?**
A: 完整測試使用相同的 `.data` section 模式來模擬 IREE VMFB 的結構。

**Q: 測試失敗怎麼辦?**
A: 檢查錯誤訊息中的指令名稱和計數,對照 `sample_rvv.s` 的註解找出差異。
