# ARVVI - Analyzer for RISC-V Vector Instructions

ARVVI 是一個用於分析 RISC-V 二進位檔案中 Vector 指令使用情況的工具。它可以幫助硬體設計人員和軟體開發者了解 AI 模型在 RISC-V 架構上的向量指令使用模式，從而優化硬體設計和軟體實現。

## 功能特性

- 🔍 **自動反組譯分析**: 使用 objdump 自動反組譯 RISC-V 二進位檔案
- 📊 **指令統計**: 統計所有 RVV (RISC-V Vector) 指令的使用次數
- 📈 **視覺化圖表**: 生成直觀的長條圖和圓餅圖展示指令分布
- 🔄 **多模型比較**: 支援對比多個 AI 模型的 RVV 指令使用情況
- 💾 **JSON 輸出**: 匯出詳細的統計資料供進一步分析
- ⚡ **批次處理**: 自動掃描目錄並分析所有模型
- 🎯 **Section 過濾**: 只分析特定 section 以加速處理（適合 IREE VMFB）

## 快速開始

### 安裝

```bash
git clone <repository-url>
cd ARVVI
pip install -r requirements.txt
chmod +x arvvi.py arvvi_compare.py
```

### 基本使用

```bash
# 分析單一檔案
./arvvi.py model.adx

# 只分析 .data section（IREE VMFB 推薦，速度更快）
./arvvi.py model.adx --section .data

# 生成視覺化圖表
./arvvi.py model.adx --section .data --visualize
```

### 批次處理（推薦）

```bash
# 自動分析整個 models 目錄
./arvvi.py --scan models/ --section .data --visualize

# 比較所有分析結果
./arvvi_compare.py --scan models/ --visualize
```

## 詳細使用說明

### 單一檔案分析

#### 基本分析
```bash
./arvvi.py /path/to/binary.adx
```

#### 指定模型名稱
```bash
./arvvi.py model.adx --model MobileNetV1
```

#### 匯出 JSON 統計
```bash
./arvvi.py model.adx -o stats.json
```

#### 生成視覺化圖表
```bash
./arvvi.py model.adx --visualize
```

#### 只分析特定 Section（加速）
```bash
# IREE VMFB: 96%+ 的 RVV 指令在 .data section
./arvvi.py model.adx --section .data

# 分析多個 sections
./arvvi.py model.adx --section .data,.text
```

#### 只分析特定函數
```bash
./arvvi.py model.adx --function main

# 分析多個函數
./arvvi.py model.adx --function main,inference,matmul
```

#### 自訂 objdump 路徑
```bash
./arvvi.py model.adx --objdump /path/to/riscv64-elf-objdump
```

#### 完整範例
```bash
./arvvi.py model.adx \
  --model MobileNetV1 \
  --section .data \
  --visualize \
  -o mobilenet_stats.json
```

### 批次處理多個模型

ARVVI 可以自動掃描目錄並分析所有模型：

#### 目錄結構要求

```
models/
├── Bird/
│   ├── bird.mlir              ← 模型定義
│   └── bird/OUTPUT/
│       └── bird.adx          ← 編譯後的二進位檔案
├── Mobile_Vit/
│   ├── Mobile_Vit.mlir
│   └── Mobile_Vit/OUTPUT/
│       └── Mobile_Vit.adx
└── YOLOv5n/
    ├── yolov5n.tosa.mlir
    └── yolov5n.tosa/OUTPUT/
        └── yolov5n.tosa.adx
```

#### 批次分析指令

```bash
# 自動分析所有模型
./arvvi.py --scan models/ --section .data --visualize
```

**輸出：**
```
Found 10 model(s) to analyze
============================================================

[1/10] Processing: bird
  📊 Analyzing: models/Bird/bird/OUTPUT/bird.adx
  ✅ Visualization saved
  ✅ Complete: 10547 RVV instructions

[2/10] Processing: Mobile_Vit
  📊 Analyzing: models/Mobile_Vit/Mobile_Vit/OUTPUT/Mobile_Vit.adx
  ✅ Visualization saved
  ✅ Complete: 15234 RVV instructions

...

============================================================
Batch Analysis Summary
============================================================
Total models found:    10
Successfully analyzed: 9
Skipped:              1
============================================================
```

#### 生成的檔案

```
models/
├── Bird/bird/OUTPUT/
│   ├── bird.adx
│   ├── bird_rvv_stats.json              ← JSON 統計
│   ├── bird_rvv_analysis.png            ← 分析圖表
│   └── bird_rvv_analysis_detailed.png   ← 詳細圖表
└── Mobile_Vit/Mobile_Vit/OUTPUT/
    ├── Mobile_Vit_rvv_stats.json
    └── Mobile_Vit_rvv_analysis.png
```

### 比較多個模型

#### 方法 1: 使用 --scan 自動掃描

```bash
./arvvi_compare.py --scan models/ --visualize
```

#### 方法 2: 手動指定 JSON 檔案

```bash
./arvvi_compare.py \
  models/Bird/bird/OUTPUT/bird_rvv_stats.json \
  models/Mobile_Vit/Mobile_Vit/OUTPUT/Mobile_Vit_rvv_stats.json \
  --visualize
```

**輸出範例：**
```
================================================================================
RVV Instruction Usage Comparison
================================================================================

Model                Total Instr     RVV Instr       RVV %
--------------------------------------------------------------------------------
bird                 5,941,809       10,547          0.18
Mobile_Vit           4,523,123       15,234          0.34
yolov5n.tosa         8,234,567       23,456          0.28

================================================================================
Top RVV Instructions Across All Models
================================================================================

Instruction     Total      bird        Mobile_Vit  yolov5n.tosa
--------------------------------------------------------------------------------
vnmsac          4234       1173        2027        1034
vslidedown      3145       1026        1025        1094
vsetvli         2998       878         1560        560
...
```

## 輸出說明

### 終端輸出

```
============================================================
Model: MobileNetV1
============================================================

Total instructions: 45678
RVV instructions: 12345
RVV usage: 27.03%

RVV Instructions by Section:
------------------------------------------------------------
.data                         :   9849 ( 93.4%)
.text                         :    552 (  5.2%)
.eh_frame                     :     50 (  0.5%)

RVV Instruction Distribution:
------------------------------------------------------------
vnmsac              :   1173
vslide1down         :   1026
vsetvli             :    878
vfmacc              :    838
vle32               :    746
```

### 視覺化圖表

1. **主分析圖** (`{Model}_rvv_analysis.png`)
   - 左側：前 20 個最常用指令的長條圖
   - 右側：前 10 個指令的圓餅圖
   - 底部：總體統計資訊

2. **詳細分析圖** (`{Model}_rvv_analysis_detailed.png`)
   - 包含所有 RVV 指令的完整長條圖

3. **模型對比圖** (`model_comparison.png`)
   - 多模型間的指令使用對比

### JSON 輸出格式

```json
{
  "model": "MobileNetV1",
  "statistics": {
    "total_instructions": 45678,
    "rvv_instructions": 12345,
    "instruction_stats": {
      "vnmsac": 1173,
      "vslide1down": 1026,
      "vsetvli": 878,
      ...
    },
    "section_stats": {
      ".data": 9849,
      ".text": 552,
      ...
    }
  }
}
```

## 支援的 RVV 指令

### Vector Configuration 指令
- `vsetvl`, `vsetvli`, `vsetivli` - 設定向量長度和類型

### Vector Load/Store 指令
- **Unit-Stride**: `vle8`, `vle16`, `vle32`, `vle64`, `vse8`, `vse16`, `vse32`, `vse64`
- **Strided**: `vlse8~64`, `vsse8~64`
- **Indexed**: `vlxei8~64`, `vsxei8~64`

### Vector 算術指令
- `vadd`, `vsub`, `vmul`, `vdiv` - 基本運算
- `vmadd`, `vnmsub`, `vmacc`, `vnmsac` - 乘加運算
- `vwadd`, `vwsub`, `vwmul` - 寬化運算
- `vnsra`, `vnsrl` - 窄化運算

### Vector 浮點指令
- `vfadd`, `vfsub`, `vfmul`, `vfdiv` - 浮點基本運算
- `vfmadd`, `vfnmadd`, `vfmsub`, `vfnmsub` - 浮點乘加
- `vfmacc`, `vfnmacc`, `vfmsac`, `vfnmsac` - 浮點累加
- `vfsqrt`, `vfmin`, `vfmax` - 浮點特殊運算

### Vector 其他指令
- 位移指令：`vsll`, `vsrl`, `vsra`
- 比較指令：`vmseq`, `vmslt`, `vmsle`
- 歸約指令：`vredsum`, `vredmax`, `vredmin`
- 遮罩指令：`vmand`, `vmor`, `vmxor`
- 排列指令：`vslideup`, `vslidedown`, `vrgather`

完整指令列表請參考 [RISC-V V Extension Specification](https://github.com/riscv/riscv-v-spec)

## 應用場景

### 1. 硬體設計最佳化

透過分析 AI 模型的 RVV 指令使用模式，硬體設計師可以：
- ✅ 識別最常用的向量指令
- ✅ 最佳化這些指令的硬體實作
- ✅ 決定哪些指令需要更多的硬體資源
- ✅ 評估不同向量長度 (VLEN) 的影響
- ✅ 分析 LMUL 使用模式以最佳化暫存器檔案設計
- ✅ 決定執行單元的數量和寬度

### 2. 軟體最佳化

軟體開發者可以：
- ✅ 了解編譯器生成的向量指令模式
- ✅ 識別最佳化機會
- ✅ 比較不同編譯選項的效果
- ✅ 評估手寫組合語言程式碼的效能
- ✅ 分析 vsetvl 配置指令的使用頻率
- ✅ 最佳化 LMUL 選擇以平衡效能和暫存器壓力

### 3. 模型對比分析

AI 研究人員可以：
- ✅ 比較不同 AI 模型的向量化程度
- ✅ 分析模型的硬體友善性
- ✅ 選擇最適合特定硬體的模型架構
- ✅ 評估不同模型對 RVV 特性的利用率

### 4. 效能調校

根據指令統計結果進行效能調校：
- 如果 `vsetvli` 出現頻繁，考慮減少配置切換
- 如果看到大量 unit-stride load/store，確保記憶體頻寬充足
- 如果 LMUL=8 使用頻繁，需要更多暫存器和執行單元
- 如果浮點運算占比高，需要強化浮點執行單元

## IREE 特殊說明

### 為什麼 IREE 模型的 RVV 指令在 .data Section？

IREE (Intermediate Representation Execution Environment) 使用特殊的編譯策略：

1. **VMFB (VM FlatBuffer) 格式**
   - IREE 將 kernel 編譯成 VMFB 格式
   - VMFB 包含已編譯的機器碼作為資料
   - 儲存在 `.data` section 而非 `.text` section

2. **Runtime 執行模式**
   - Runtime 在執行時載入 VMFB
   - 動態執行其中的向量指令
   - 這就是為什麼 93-97% 的 RVV 指令在 `.data`

3. **最佳化建議**
   ```bash
   # 只分析 .data section 可大幅加速
   ./arvvi.py model.adx --section .data --visualize
   ```

## 配置

### 預設 objdump 路徑

預設路徑設定在 `arvvi.py`:
```python
DEFAULT_OBJDUMP = "/home/ymchang/AndeSight-v5_4_0/toolchains-bin/nds64le-elf-newlib-v5d/bin/riscv64-elf-objdump"
```

可使用 `--objdump` 參數覆蓋：
```bash
./arvvi.py model.adx --objdump /custom/path/to/objdump
```

## 故障排除

### objdump 未找到

**錯誤：**
```
Error: objdump not found at /path/to/objdump
```

**解決：**
```bash
./arvvi.py model.adx --objdump /correct/path/to/riscv64-elf-objdump
```

### matplotlib 未安裝

**警告：**
```
Warning: matplotlib not installed. Install with: pip install matplotlib
```

**解決：**
```bash
pip install matplotlib
```

### 批次掃描找到過多檔案

**問題：** 掃描找到數千個 .mlir 檔案

**原因：** 包含了 temp/, transform_library/ 等子目錄的檔案

**解決：** ARVVI 只掃描頂層目錄（`models/*/*.mlir`），不會遞迴子目錄。確保你的 .mlir 檔案在正確位置。

## 檔案說明

- `arvvi.py` - 主程式，用於分析單個或批次分析二進位檔案
- `arvvi_visualizer.py` - 視覺化模組，生成圖表
- `arvvi_compare.py` - 多模型比較工具
- `requirements.txt` - Python 相依套件清單
- `tests/` - 測試檔案和範例
- `.github/workflows/` - CI/CD 設定

## 開發與測試

### 執行測試

```bash
# 執行所有測試
python -m pytest tests/ -v

# 執行單一測試檔案
python tests/test_rvv_parser.py
```

### CI/CD

專案使用 GitHub Actions 進行持續整合：
- 自動執行單元測試
- 驗證工具功能正常
- 檢查程式碼風格

## 授權條款

[在此新增授權條款資訊]

## 貢獻

歡迎提交 Issue 和 Pull Request！

---

## 附錄：RISC-V Vector Extension (RVV) 運算邏輯詳解

> **注意：** 本章節為進階教學內容，介紹 RVV 的底層運算邏輯和硬體實作細節。
> 如果你只想使用 ARVVI 工具，可以跳過此章節。

### RVV 架構基礎

RISC-V Vector Extension 提供了靈活的向量處理能力，透過動態可配置的向量暫存器長度和分組機制，讓同一套程式碼可以在不同硬體實作上運行。

#### 核心概念

1. **VLEN (Vector Register Length)** - 硬體決定
   - 硬體實作的向量暫存器位元長度
   - 常見值：128, 256, 512, 1024, 2048 bits
   - **由硬體決定，軟體無法更改**
   - 可透過 CSR 暫存器讀取

2. **VTYPE (Vector Type Register)** - 軟體配置
   - 包含向量運算的配置資訊
   - 包括 SEW、LMUL、VTA、VMA 等欄位
   - **由軟體透過 vsetvl 指令設定**

3. **VL (Vector Length)** - 動態決定
   - 實際參與運算的向量元素數量
   - 由 vsetvl/vsetvli 指令動態設定
   - **由硬體根據 AVL 和 VLMAX 決定**
   - 不能超過 VLMAX

### Vector Configuration 指令：vsetvl/vsetvli

這些指令是 RVV 最重要的配置指令，決定了後續向量運算的行為。

#### vsetvli 指令格式

```assembly
vsetvli rd, rs1, vtypei
```

**參數說明：**
- `rd`: 目的暫存器，儲存實際設定的 VL 值（**硬體回傳**）
- `rs1`: 來源暫存器，包含請求的 AVL (Application Vector Length)（**軟體提供**）
- `vtypei`: 立即值，指定向量類型配置（**軟體指定**）

#### 硬體如何決定 VL

```
VL = MIN(AVL, VLMAX)
```

其中：
```
VLMAX = (VLEN / SEW) × LMUL
```

**硬體決定流程：**
1. 軟體透過 `rs1` 提供 AVL (想要處理的元素數量)
2. 硬體計算 VLMAX (根據 VLEN、SEW、LMUL)
3. 硬體取 MIN(AVL, VLMAX) 作為實際 VL
4. 硬體將 VL 寫回 `rd` 暫存器

**範例：**
```assembly
li a0, 100           # 軟體想處理 100 個元素
vsetvli t0, a0, e32, m4

# 假設 VLEN = 256 bits
# VLMAX = (256 / 32) × 4 = 8 × 4 = 32
# VL = MIN(100, 32) = 32
# t0 = 32（硬體回傳實際能處理的元素數）
```

#### VTYPEI 欄位組成

```
vtypei = [vma | vta | vsew[2:0] | vlmul[2:0]]
```

**各欄位說明：**

1. **VSEW (Selected Element Width)** - 軟體指定
   - `000` = SEW 8 bits (e8)
   - `001` = SEW 16 bits (e16)
   - `010` = SEW 32 bits (e32)
   - `011` = SEW 64 bits (e64)
   - **決定每個元素的資料寬度**

2. **VLMUL (Vector Register Group Multiplier)** - 軟體指定
   - `000` = LMUL = 1 (使用 1 個暫存器)
   - `001` = LMUL = 2 (使用 2 個暫存器)
   - `010` = LMUL = 4 (使用 4 個暫存器)
   - `011` = LMUL = 8 (使用 8 個暫存器)
   - `101` = LMUL = 1/2 (分數 LMUL)
   - `110` = LMUL = 1/4 (分數 LMUL)
   - `111` = LMUL = 1/8 (分數 LMUL)
   - **決定暫存器分組數量**

3. **VTA (Vector Tail Agnostic)** - 軟體指定
   - 控制尾部元素（VL 之後的元素）的行為
   - `0`: 保持不變
   - `1`: 設為未定義（允許硬體最佳化）

4. **VMA (Vector Mask Agnostic)** - 軟體指定
   - 控制被遮罩元素的行為
   - `0`: 保持不變
   - `1`: 設為未定義（允許硬體最佳化）

### LMUL：Vector Register Grouping 機制

**LMUL (Register Group Multiplier)** 是 RVV 最強大的特性之一，它允許將多個向量暫存器組合成一個邏輯暫存器組，大幅增加單次運算的資料量。

#### LMUL 如何將暫存器組合在一起

**硬體層面的實作：**

假設 VLEN = 256 bits，SEW = 32 bits：

**LMUL = 1 (預設情況)**
```
v1 暫存器: [e0, e1, e2, e3, e4, e5, e6, e7]  // 8 個元素

硬體實作：
- 1 個實體向量暫存器
- ALU 一次處理 8 個 32-bit 元素
```

**LMUL = 2 (將 2 個暫存器組合)**
```
v2 暫存器組 = {v2, v3}:
  v2: [e0,  e1,  e2,  e3,  e4,  e5,  e6,  e7 ]
  v3: [e8,  e9,  e10, e11, e12, e13, e14, e15]

硬體實作：
- 2 個實體向量暫存器
- ALU 一次處理 16 個 32-bit 元素
- 或使用多個 ALU 並行處理
```

**LMUL = 4 (將 4 個暫存器組合)**
```
v4 暫存器組 = {v4, v5, v6, v7}:
  v4: [e0,  e1,  e2,  e3,  e4,  e5,  e6,  e7 ]
  v5: [e8,  e9,  e10, e11, e12, e13, e14, e15]
  v6: [e16, e17, e18, e19, e20, e21, e22, e23]
  v7: [e24, e25, e26, e27, e28, e29, e30, e31]

硬體實作：
- 4 個實體向量暫存器
- ALU 一次處理 32 個 32-bit 元素
- 可能需要 4 個並行 ALU 或分時處理
```

**LMUL = 8 (將 8 個暫存器組合)**
```
v8 暫存器組 = {v8, v9, v10, v11, v12, v13, v14, v15}:
  總共 64 個元素在一個邏輯暫存器組中

硬體實作：
- 8 個實體向量暫存器
- ALU 一次處理 64 個 32-bit 元素
- 通常需要多週期或多個並行 ALU
```

#### 暫存器組合規則（硬體限制）

1. **對齊限制** - 硬體強制要求
   - 暫存器組的起始編號必須是 LMUL 的倍數
   - LMUL=2: 只能使用 v0, v2, v4, v6, ..., v30
   - LMUL=4: 只能使用 v0, v4, v8, v12, ..., v28
   - LMUL=8: 只能使用 v0, v8, v16, v24
   - **硬體會檢查，違反會產生例外**

2. **VLMAX 計算** - 硬體參數
   ```
   VLMAX = (VLEN / SEW) × LMUL
   ```
   - VLEN: 硬體決定（晶片設計時固定）
   - SEW: 軟體指定（指令中的 e8/e16/e32/e64）
   - LMUL: 軟體指定（指令中的 m1/m2/m4/m8）
   - VLMAX: 硬體計算（可處理的最大元素數）

3. **範例計算**:
   ```
   硬體參數：VLEN = 256 bits（晶片設計時決定）
   軟體指定：SEW = 32 bits (e32)
   軟體指定：LMUL = 4 (m4)

   硬體計算：VLMAX = (256 / 32) × 4 = 8 × 4 = 32 個元素
   ```

### 硬體實作細節

#### 1. 向量暫存器檔案 (Vector Register File)

**硬體結構：**
```
總共 32 個向量暫存器：v0 ~ v31
每個暫存器長度 = VLEN bits（硬體決定）

實體配置範例（VLEN=256）：
┌─────────────────────────────────────┐
│ v0  [255:0]  256 bits               │
├─────────────────────────────────────┤
│ v1  [255:0]  256 bits               │
├─────────────────────────────────────┤
│ v2  [255:0]  256 bits               │
...
├─────────────────────────────────────┤
│ v31 [255:0]  256 bits               │
└─────────────────────────────────────┘

總容量 = 32 × 256 = 8192 bits = 1 KB
```

**硬體讀取埠（Read Ports）：**
```
典型設計：2-3 個讀取埠
- 支援同時讀取 2-3 個向量暫存器
- LMUL 大時可能需要多週期讀取

範例：vadd.vv v3, v1, v2 (LMUL=4)
週期 1: 讀取 v1[0], v2[0] → ALU → v3[0]
週期 2: 讀取 v1[1], v2[1] → ALU → v3[1]
週期 3: 讀取 v1[2], v2[2] → ALU → v3[2]
週期 4: 讀取 v1[3], v2[3] → ALU → v3[3]
```

#### 2. 向量執行單元 (Vector Execution Unit)

**ALU 寬度決定效能：**

**選項 A: 單一寬 ALU**
```
VLEN = 256 bits, SEW = 32 bits
→ ALU 寬度 = 256 bits
→ 一次處理 8 個 32-bit 元素

┌────────────────────────────────────────┐
│  256-bit Wide Vector ALU               │
│  ┌──┬──┬──┬──┬──┬──┬──┬──┐            │
│  │ 0│ 1│ 2│ 3│ 4│ 5│ 6│ 7│            │
│  └──┴──┴──┴──┴──┴──┴──┴──┘            │
│   8 個並行 32-bit ALU lane            │
└────────────────────────────────────────┘

LMUL=1: 1 週期完成
LMUL=4: 4 週期完成（4 個暫存器輪流處理）
```

**選項 B: 多個窄 ALU**
```
VLEN = 256 bits, 但只有 128-bit ALU
→ 需要 2 個週期處理一個 VLEN

┌──────────────────────┐
│  128-bit Vector ALU  │
│  ┌──┬──┬──┬──┐       │
│  │ 0│ 1│ 2│ 3│       │
│  └──┴──┴──┴──┴──┘    │
└──────────────────────┘

LMUL=1: 2 週期完成（處理 v1[127:0] 和 v1[255:128]）
LMUL=4: 8 週期完成
```

**選項 C: 多個並行 ALU**
```
4 個獨立的 256-bit ALU
→ LMUL=4 時可並行處理

ALU 0: 處理 v4 (週期 1)
ALU 1: 處理 v5 (週期 1)
ALU 2: 處理 v6 (週期 1)
ALU 3: 處理 v7 (週期 1)

LMUL=4: 1 週期完成（但面積和功耗 4 倍）
```

#### 3. 從參數推算硬體 ALU 寬度

**方法：執行簡單的向量運算並測量週期數**

```assembly
# 測試程式
vsetvli t0, a0, e32, m1    # LMUL=1, 一個暫存器
vadd.vv v1, v2, v3

# 假設：
# - VLEN = 512 bits
# - SEW = 32 bits
# - 理論上可處理 512/32 = 16 個元素

# 測量結果：
# 如果 1 週期完成 → ALU 寬度 = 512 bits (16 lanes)
# 如果 2 週期完成 → ALU 寬度 = 256 bits (8 lanes)
# 如果 4 週期完成 → ALU 寬度 = 128 bits (4 lanes)
```

**實際範例：AndeStar AX45MP**
```
VLEN = 256 bits（從 vlenb CSR 讀取）
實測 vadd (LMUL=1, SEW=32) = 2 週期

推算：
256 / 32 = 8 個元素
2 週期處理 8 個元素
→ ALU 寬度 = 128 bits (4 lanes)
→ 每週期處理 4 個 32-bit 元素
```

#### 5. 如何從 RVV 指令使用模式推測 ALU 寬度

**關鍵觀念：ALU 寬度是不可見的硬體參數**

RVV 指令集 **刻意不暴露** ALU 寬度，讓不同硬體實作有彈性。但我們可以透過多種方法推測：

##### 方法 1：效能計數器測量（最準確）

**需要工具：**
- Performance counter (perf, 或 vendor 提供的 profiler)
- 能跑在硬體上的測試程式

**測試步驟：**
```assembly
# 測試程式 1: LMUL=1
vsetvli t0, a0, e32, m1    # 設定 LMUL=1
loop1:
    vle32.v  v1, (a1)
    vle32.v  v2, (a2)
    vadd.vv  v3, v1, v2
    vse32.v  v3, (a3)
    addi a1, a1, 32        # 移動 8 個元素 (32 bytes)
    addi a2, a2, 32
    addi a3, a3, 32
    bnez a0, loop1

# 測量: 總 cycle 數 C1

# 測試程式 2: LMUL=2
vsetvli t0, a0, e32, m2    # 設定 LMUL=2
loop2:
    vle32.v  v4, (a1)
    vle32.v  v8, (a2)
    vadd.vv  v12, v4, v8
    vse32.v  v12, (a3)
    addi a1, a1, 64        # 移動 16 個元素 (64 bytes)
    addi a2, a2, 64
    addi a3, a3, 64
    bnez a0, loop2

# 測量: 總 cycle 數 C2
```

**分析結果：**
```python
# 假設測量結果
# VLEN = 256 bits, SEW = 32 bits

# LMUL=1: 處理 8 個元素，耗時 10 cycles
# LMUL=2: 處理 16 個元素，耗時 20 cycles

# 推論 1: 週期數線性成長
# → ALU 可能按 LMUL 分批處理

# 如果 LMUL=1 的 10 cycles 中:
#   - Load v1: 2 cycles
#   - Load v2: 2 cycles
#   - Add:     2 cycles
#   - Store:   2 cycles
#   - 其他:     2 cycles

# 推論 Add 部分:
# 2 cycles 處理 8 個元素 → 每 cycle 4 個元素
# → ALU 寬度 = 4 × 32 = 128 bits
```

##### 方法 2：從 ARVVI 統計結果推測（間接方法）

**觀察指令使用模式：**

假設你用 ARVVI 分析後得到：
```json
{
  "instruction_stats": {
    "vsetvli": 45,
    "vsetivli": 12,
    "vle32": 892,
    "vse32": 654,
    "vfmacc": 1247,
    "vfadd": 432
  }
}
```

**推論步驟 1：觀察 vsetvl 指令的參數**
```bash
# 用 objdump 查看實際的 vsetvli 指令
riscv64-elf-objdump -D model.adx | grep vsetvli

輸出範例：
  20000: cd027057  vsetvli  zero,zero,e32,m1,ta,ma
  20100: cd047057  vsetvli  zero,zero,e32,m2,ta,ma
  20200: cd067057  vsetvli  zero,zero,e32,m4,ta,ma
```

**發現**:
- 大部分使用 **m1** (LMUL=1)
- 少數使用 m2, m4

**推論**:
```
如果編譯器選擇 LMUL=1，可能因為:
1. 硬體 ALU 寬度 = VLEN → LMUL>1 不會更快
2. 或記憶體頻寬限制 → LMUL>1 會卡在記憶體存取

如果編譯器選擇 LMUL=4，可能因為:
1. 硬體有多個並行 ALU
2. 記憶體頻寬足夠
3. 想減少迴圈次數
```

**推論步驟 2：觀察 Load/Store vs Compute 的比例**
```python
load_store_count = vle32 + vse32 = 892 + 654 = 1546
compute_count = vfmacc + vfadd = 1247 + 432 = 1679

ratio = load_store / compute = 1546 / 1679 ≈ 0.92
```

**推論**:
```
Load/Store 和 Compute 數量接近:
→ 可能有記憶體頻寬瓶頸
→ ALU 可能處於等待資料的狀態
→ 即使有大 ALU，也因記憶體限制無法發揮

如果 ratio < 0.5 (Compute 多很多):
→ 可能有寄存器再用 (register reuse)
→ ALU 較忙，記憶體不是瓶頸
```

**推論步驟 3：觀察複雜指令的使用**
```json
"vfmacc": 1247   // Fused Multiply-Accumulate
"vfmul":  123    // 單純乘法
"vfadd":  432    // 單純加法
```

**推論**:
```
大量使用 vfmacc (FMA):
→ 編譯器知道硬體有 FMA 單元
→ 硬體 ALU 較複雜，支援融合運算
→ 可能每個 lane 都有獨立的 FMA

如果硬體沒有 FMA，編譯器會用:
vfmul + vfadd (分開的指令)
```

##### 方法 3：廠商規格文件（最直接）

**查詢方向：**
```
Andes AX45MP 規格文件關鍵字:
- "Vector ALU width"
- "Vector execution lanes"
- "Vector processing elements"
- "VLEN implementation"

範例文件內容:
┌─────────────────────────────────────┐
│ Andes AX45MP Vector Unit Spec      │
├─────────────────────────────────────┤
│ VLEN:        256 bits               │
│ ALU Width:   128 bits (4 lanes)    │
│ FPU Lanes:   4 × FP32 FMA units    │
│ Memory:      128-bit interface      │
└─────────────────────────────────────┘

從文件直接得知:
→ 4 個並行的 32-bit lane
→ 每個 lane 有 FMA 單元
→ 記憶體介面也是 128-bit
```

##### 方法 4：比較不同 SEW 的效能（進階）

**測試程式：**
```assembly
# 測試 1: SEW=32
vsetvli t0, a0, e32, m1
vadd.vv v1, v2, v3
# 測量 cycles: C32

# 測試 2: SEW=64
vsetvli t0, a0, e64, m1
vadd.vv v1, v2, v3
# 測量 cycles: C64

# 測試 3: SEW=16
vsetvli t0, a0, e16, m1
vadd.vv v1, v2, v3
# 測量 cycles: C16
```

**分析結果：**
```python
# 假設 VLEN = 256 bits

# 結果 A: 所有 SEW 都是相同 cycles
# e32: 2 cycles (8 個元素)
# e64: 2 cycles (4 個元素)
# e16: 2 cycles (16 個元素)
# → ALU 是 256-bit 全寬，不管 SEW 都用滿

# 結果 B: cycles 與元素數成比例
# e32: 2 cycles (8 個元素) → 4 elem/cycle
# e64: 1 cycle (4 個元素) → 4 elem/cycle
# e16: 4 cycles (16 個元素) → 4 elem/cycle
# → ALU 固定每 cycle 處理 4 個元素（不管寬度）

# 結果 C: cycles 與資料量成比例
# e32: 2 cycles (32 bytes)
# e64: 2 cycles (32 bytes)
# e16: 1 cycle (32 bytes)
# → 受記憶體頻寬限制（128-bit memory bus）
```

##### 方法 5：從編譯器生成的程式碼推測

**觀察重點：**
```assembly
# IREE 生成的程式碼範例

# 模式 A: 總是用 LMUL=1
vsetvli t0, a0, e32, m1
...
# → 可能硬體 ALU = VLEN，LMUL>1 沒好處

# 模式 B: 總是用 LMUL=8
vsetvli t0, a0, e32, m8
...
# → 可能硬體有 8 個並行 ALU 或非常寬的 ALU

# 模式 C: 混用 m1, m2, m4
vsetvli t0, a0, e32, m1   # 小運算
...
vsetvli t0, a0, e32, m4   # 大運算
...
# → 編譯器在平衡效能和暫存器壓力
```

##### 實際案例分析

**案例：分析 MobileNet 模型**

使用 ARVVI 分析得到：
```json
{
  "total_instructions": 8234,
  "rvv_instructions": 7543,
  "instruction_stats": {
    "vsetvli": 156,
    "vle32": 1247,
    "vse32": 1089,
    "vfmacc": 2456,
    "vfadd": 892,
    "vfmul": 234
  }
}
```

**分析步驟：**

1. **觀察 FMA 使用率**
   ```
   vfmacc = 2456
   vfmul + vfadd = 234 + 892 = 1126

   FMA 使用率 = 2456 / (2456 + 1126) = 68.5%

   推論: 硬體很可能有 FMA 單元
   ```

2. **檢查 vsetvli 實際參數**（需要 objdump）
   ```bash
   riscv64-elf-objdump -D mobilenet.adx | grep vsetvli | head -20

   大部分是 e32, m1
   → 可能 ALU 寬度 = VLEN
   ```

3. **計算理論 vs 實際比例**
   ```
   如果 VLEN = 256, SEW = 32, LMUL = 1:
   VLMAX = 8 個元素

   如果有 1247 次 vle32:
   → 理論載入 1247 × 8 = 9976 個元素
   → 約 39.9 KB 資料

   對照模型大小和運算量 → 可推測迴圈次數
   ```

##### 總結：ALU 寬度推測的層次

| 方法 | 準確度 | 難度 | 需要資源 |
|------|--------|------|----------|
| **Performance Counter** | ⭐⭐⭐⭐⭐ | 高 | 硬體、測試程式 |
| **廠商文件** | ⭐⭐⭐⭐⭐ | 低 | 取得文件 |
| **SEW 效能比較** | ⭐⭐⭐⭐ | 中 | 硬體、測試程式 |
| **LMUL 效能比較** | ⭐⭐⭐⭐ | 中 | 硬體、測試程式 |
| **指令統計分析** | ⭐⭐⭐ | 低 | ARVVI + objdump |
| **編譯器模式觀察** | ⭐⭐ | 低 | ARVVI + objdump |

**實務建議：**
```
1. 先查廠商文件（如果有的話）
2. 用 ARVVI 分析指令模式，建立初步假設
3. 寫小型 benchmark 在硬體上驗證
4. 使用 performance counter 精確測量
```

**ARVVI 能幫助你：**
- ✅ 觀察編譯器選擇的 LMUL 模式
- ✅ 統計不同指令類型的使用頻率
- ✅ 分析 Load/Store vs Compute 的平衡
- ✅ 找出效能熱點（最常用的指令）

**ARVVI 無法直接告訴你：**
- ❌ 確切的 ALU 寬度（需要效能測試）
- ❌ 實際執行時間（需要在硬體上跑）
- ❌ 記憶體頻寬（需要硬體規格）

但透過 ARVVI 的統計資料 + objdump 的詳細輸出 + 硬體測試，
你可以完整了解 RVV 硬體的實作特性！

#### 4. 記憶體頻寬需求

**LMUL 對記憶體頻寬的影響：**

```
LMUL=1, SEW=32, VLEN=256:
vle32.v v1, (a1)
→ 載入 8 個元素 = 32 bytes
→ 需要 32 bytes 記憶體頻寬

LMUL=4, SEW=32, VLEN=256:
vle32.v v4, (a1)
→ 載入 32 個元素 = 128 bytes
→ 需要 128 bytes 記憶體頻寬

硬體設計考量：
- LMUL 越大，記憶體頻寬需求越高
- 需要更寬的記憶體匯流排
- 或使用多個記憶體 bank 並行存取
```

### 實際運算範例

#### 範例 1: 向量加法配置

```assembly
# 軟體設定向量配置: SEW=32, LMUL=2
li a0, 64                    # 軟體：想處理 64 個元素
vsetvli t0, a0, e32, m2      # 硬體：SEW=32 bits, LMUL=2
                             # 硬體計算：VLMAX = (VLEN/32) × 2
                             # 假設 VLEN=256: VLMAX = 8 × 2 = 16
                             # 硬體決定：VL = MIN(64, 16) = 16
                             # t0 = 16（硬體回傳）

# 載入資料到向量暫存器組
vle32.v v2, (a1)             # 硬體：v2, v3 組成暫存器組
                             # 載入 16 個 32-bit 元素 = 64 bytes

vle32.v v4, (a2)             # 硬體：v4, v5 組成暫存器組
                             # 載入 16 個 32-bit 元素 = 64 bytes

# 向量加法
vadd.vv v6, v2, v4           # 硬體：v6,v7 = v2,v3 + v4,v5
                             # 使用 2×(VLEN/32) 個元素進行運算
                             # 實際處理 16 個元素

# 儲存結果
vse32.v v6, (a3)             # 硬體：儲存 v6, v7 組的結果
                             # 儲存 16 個 32-bit 元素 = 64 bytes
```

**硬體執行細節（假設 ALU 寬度 = VLEN）：**
```
VLEN = 256 bits, ALU 寬度 = 256 bits

vle32.v v2, (a1) - LMUL=2:
  週期 1: 從記憶體載入 256 bits → v2
  週期 2: 從記憶體載入 256 bits → v3
  總共: 2 週期, 64 bytes

vadd.vv v6, v2, v4 - LMUL=2:
  週期 1: v2 + v4 → v6 (8 個元素)
  週期 2: v3 + v5 → v7 (8 個元素)
  總共: 2 週期, 16 個元素

總執行時間：
  載入 v2,v3: 2 週期
  載入 v4,v5: 2 週期
  加法：       2 週期
  儲存 v6,v7: 2 週期
  合計：       8 週期
```

#### 範例 2: 不同 LMUL 的效能影響

**使用 LMUL=1 (小資料量)**
```assembly
vsetvli t0, a0, e32, m1      # SEW=32, LMUL=1
                             # VLMAX = (256/32) × 1 = 8
vle32.v v1, (a1)             # 僅載入到 v1: 8 個元素
vle32.v v2, (a2)             # 僅載入到 v2: 8 個元素
vadd.vv v3, v1, v2           # v3 = v1 + v2: 8 個元素

硬體執行：
  載入 v1: 1 週期 (8 個元素)
  載入 v2: 1 週期 (8 個元素)
  加法：    1 週期 (8 個元素)
  合計：    3 週期
  吞吐量：  8 元素 / 3 週期 = 2.67 元素/週期
```

**使用 LMUL=4 (大資料量)**
```assembly
vsetvli t0, a0, e32, m4      # SEW=32, LMUL=4
                             # VLMAX = (256/32) × 4 = 32
vle32.v v4, (a1)             # 載入到 v4,v5,v6,v7 組: 32 個元素
vle32.v v8, (a2)             # 載入到 v8,v9,v10,v11 組: 32 個元素
vadd.vv v12, v4, v8          # v12-v15 = v4-v7 + v8-v11: 32 個元素

硬體執行（假設 ALU 寬度 = VLEN）：
  載入 v4-v7:   4 週期 (32 個元素)
  載入 v8-v11:  4 週期 (32 個元素)
  加法：        4 週期 (32 個元素)
  合計：        12 週期
  吞吐量：      32 元素 / 12 週期 = 2.67 元素/週期

但如果有 4 個並行 ALU：
  加法：        1 週期 (並行處理 4 個暫存器)
  合計：        9 週期
  吞吐量：      32 元素 / 9 週期 = 3.56 元素/週期
```

### LMUL 對硬體設計的影響

#### 1. 暫存器檔案設計

**讀取埠需求：**
```
LMUL=1: 2 個讀取埠（2 個來源暫存器）
LMUL=2: 4 個讀取埠（2 個暫存器組，每組 2 個）
LMUL=4: 8 個讀取埠（2 個暫存器組，每組 4 個）
LMUL=8: 16 個讀取埠（2 個暫存器組，每組 8 個）

實際設計：
- 通常只有 2-4 個讀取埠
- LMUL 大時需要多週期讀取
- 或使用暫存器檔案分組 (banking)
```

**暫存器分組路由邏輯：**
```
需要硬體邏輯來：
1. 檢查暫存器對齊（v4, v8, v12... for LMUL=4）
2. 將多個暫存器組合成邏輯組
3. 循序或並行讀取暫存器組成員
4. 路由到對應的 ALU lane
```

#### 2. 執行單元設計

**方案 A: 寬 ALU + 多週期**
```
優點：面積小，功耗低
缺點：LMUL 大時需要多週期

VLEN=256, ALU=256-bit
LMUL=4: 4 週期完成
```

**方案 B: 窄 ALU + 更多週期**
```
優點：面積更小，功耗更低
缺點：所有操作都需要多週期

VLEN=256, ALU=128-bit
LMUL=1: 2 週期
LMUL=4: 8 週期
```

**方案 C: 多個並行 ALU**
```
優點：LMUL 大時效能好
缺點：面積大，功耗高，繞線複雜

VLEN=256, 4 個並行 256-bit ALU
LMUL=4: 1 週期完成（最佳效能）
```

#### 3. 記憶體系統設計

**記憶體頻寬需求：**
```
LMUL 越大 → 單次載入/儲存資料量越大 → 需要更高頻寬

設計考量：
1. 記憶體匯流排寬度
   - 256-bit 匯流排 vs 512-bit 匯流排

2. 記憶體 Bank 數量
   - 單 bank vs 多 bank 並行存取

3. Cache 設計
   - Line size 要能容納 LMUL 組的資料
   - LMUL=8, SEW=32, VLEN=256 → 需要 256 bytes
```

### 總結：軟硬體協作

**硬體決定（晶片設計時固定）：**
- ✅ VLEN（向量暫存器長度）
- ✅ ALU 寬度（一次能處理多少元素）
- ✅ 記憶體頻寬（匯流排寬度）
- ✅ 讀取埠數量（暫存器檔案設計）

**軟體指定（程式執行時配置）：**
- ✅ SEW（元素寬度：e8/e16/e32/e64）
- ✅ LMUL（暫存器分組：m1/m2/m4/m8）
- ✅ AVL（想處理的元素數量）
- ✅ VTA/VMA（尾部和遮罩行為）

**硬體動態決定（執行時計算）：**
- ✅ VLMAX = (VLEN / SEW) × LMUL
- ✅ VL = MIN(AVL, VLMAX)
- ✅ 實際執行週期數（根據 ALU 寬度和 LMUL）

**效能分析關鍵：**
```
理論 VLMAX = (VLEN / SEW) × LMUL
實際吞吐量 = (ALU 寬度 / SEW) × (並行 ALU 數量)

範例：
VLEN = 512 bits
SEW = 32 bits
LMUL = 4
→ VLMAX = (512/32) × 4 = 64 個元素

如果 ALU 寬度 = 256 bits (8 lanes):
→ 每週期處理 8 個 32-bit 元素
→ LMUL=4 需要 4 週期（處理 4 個暫存器）

如果有 4 個並行 ALU:
→ LMUL=4 只需 1 週期
→ 吞吐量提升 4 倍！
```

這些硬體細節對於：
1. **硬體設計師**：決定 ALU 數量、寬度、記憶體系統設計
2. **軟體開發者**：選擇最佳的 LMUL 以平衡效能和暫存器壓力
3. **效能調校**：理解瓶頸在 ALU、記憶體還是暫存器

---

**ARVVI** - Analyze RISC-V Vector Instructions, Optimize AI Accelerators
