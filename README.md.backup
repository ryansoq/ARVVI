# ARVVI - AndeSight RISC-V Vector Instruction Analyzer

ARVVI 是一個用於分析 RISC-V 二進位檔案中 Vector 指令使用情況的工具。它可以幫助硬體設計人員和軟體開發者了解 AI 模型在 RISC-V 架構上的向量指令使用模式，從而優化硬體設計和軟體實現。

## 功能特性

- 🔍 **自動反組譯分析**: 使用 objdump 自動反組譯 RISC-V 二進位檔案
- 📊 **指令統計**: 統計所有 RVV (RISC-V Vector) 指令的使用次數
- 📈 **視覺化圖表**: 生成直觀的長條圖和圓餅圖展示指令分布
- 🔄 **多模型比較**: 支援對比多個 AI 模型的 RVV 指令使用情況
- 💾 **JSON 輸出**: 匯出詳細的統計資料供進一步分析

## RISC-V Vector Extension (RVV) 運算邏輯

### RVV 架構基礎

RISC-V Vector Extension 提供了靈活的向量處理能力，透過動態可配置的向量暫存器長度和分組機制，讓同一套程式碼可以在不同硬體實作上運行。

#### 核心概念

1. **VLEN (Vector Register Length)**
   - 硬體實作的向量暫存器位元長度
   - 可以是 128, 256, 512, 1024 bits 等
   - 由硬體決定，軟體透過 CSR 讀取

2. **VTYPE (Vector Type Register)**
   - 包含向量運算的配置資訊
   - 包括 SEW、LMUL、VTA、VMA 等欄位

3. **VL (Vector Length)**
   - 實際參與運算的向量元素數量
   - 由 vsetvl/vsetvli 指令動態設定
   - 不能超過 VLMAX

### Vector Configuration 指令：vsetvl/vsetvli

這些指令是 RVV 最重要的配置指令，決定了後續向量運算的行為。

#### vsetvli 指令格式

```assembly
vsetvli rd, rs1, vtypei
```

**參數說明：**
- `rd`: 目的暫存器，儲存實際設定的 VL 值
- `rs1`: 來源暫存器，包含請求的 AVL (Application Vector Length)
- `vtypei`: 立即值，指定向量類型配置

#### VTYPEI 欄位組成

```
vtypei = [vma | vta | vsew[2:0] | vlmul[2:0]]
```

**各欄位說明：**

1. **VSEW (Selected Element Width)** - 元素寬度
   - `000` = SEW 8 bits (e8)
   - `001` = SEW 16 bits (e16)
   - `010` = SEW 32 bits (e32)
   - `011` = SEW 64 bits (e64)

2. **VLMUL (Vector Register Group Multiplier)** - 暫存器分組倍數
   - `000` = LMUL = 1 (使用 1 個暫存器)
   - `001` = LMUL = 2 (使用 2 個暫存器)
   - `010` = LMUL = 4 (使用 4 個暫存器)
   - `011` = LMUL = 8 (使用 8 個暫存器)
   - `101` = LMUL = 1/2 (分數 LMUL)
   - `110` = LMUL = 1/4 (分數 LMUL)
   - `111` = LMUL = 1/8 (分數 LMUL)

3. **VTA (Vector Tail Agnostic)**
   - 控制尾部元素的行為

4. **VMA (Vector Mask Agnostic)**
   - 控制被遮罩元素的行為

### LMUL：Vector Register Grouping 機制

**LMUL (Register Group Multiplier)** 是 RVV 最強大的特性之一，它允許將多個向量暫存器組合成一個邏輯暫存器組，大幅增加單次運算的資料量。

#### LMUL 如何將暫存器組合在一起

假設 VLEN = 256 bits，SEW = 32 bits：

**LMUL = 1 (預設情況)**
```
v1 暫存器: [e0, e1, e2, e3, e4, e5, e6, e7]  // 8 個元素
```

**LMUL = 2 (將 2 個暫存器組合)**
```
v2 暫存器組 = {v2, v3}:
  v2: [e0,  e1,  e2,  e3,  e4,  e5,  e6,  e7 ]
  v3: [e8,  e9,  e10, e11, e12, e13, e14, e15]

總共 16 個元素在一個邏輯暫存器組中
```

**LMUL = 4 (將 4 個暫存器組合)**
```
v4 暫存器組 = {v4, v5, v6, v7}:
  v4: [e0,  e1,  e2,  e3,  e4,  e5,  e6,  e7 ]
  v5: [e8,  e9,  e10, e11, e12, e13, e14, e15]
  v6: [e16, e17, e18, e19, e20, e21, e22, e23]
  v7: [e24, e25, e26, e27, e28, e29, e30, e31]

總共 32 個元素在一個邏輯暫存器組中
```

**LMUL = 8 (將 8 個暫存器組合)**
```
v8 暫存器組 = {v8, v9, v10, v11, v12, v13, v14, v15}:
  總共 64 個元素在一個邏輯暫存器組中
```

#### 暫存器組合規則

1. **對齊限制**: 暫存器組的起始編號必須是 LMUL 的倍數
   - LMUL=2: 只能使用 v0, v2, v4, v6, ..., v30
   - LMUL=4: 只能使用 v0, v4, v8, v12, ..., v28
   - LMUL=8: 只能使用 v0, v8, v16, v24

2. **VLMAX 計算**: 最大向量長度
   ```
   VLMAX = (VLEN / SEW) × LMUL
   ```

3. **範例計算**:
   ```
   VLEN = 256 bits
   SEW = 32 bits
   LMUL = 4

   VLMAX = (256 / 32) × 4 = 8 × 4 = 32 個元素
   ```

### 實際運算範例

#### 範例 1: 向量加法配置

```assembly
# 設定向量配置: SEW=32, LMUL=2
li a0, 64                    # 請求處理 64 個元素
vsetvli t0, a0, e32, m2      # SEW=32 bits, LMUL=2
                             # t0 = 實際的 VL 值

# 載入資料到向量暫存器組
vle32.v v2, (a1)             # v2, v3 組成暫存器組，載入資料
vle32.v v4, (a2)             # v4, v5 組成暫存器組，載入資料

# 向量加法
vadd.vv v6, v2, v4           # v6,v7 = v2,v3 + v4,v5
                             # 使用 2×(VLEN/32) 個元素進行運算

# 儲存結果
vse32.v v6, (a3)             # 儲存 v6, v7 組的結果
```

#### 範例 2: 不同 LMUL 的影響

**使用 LMUL=1 (小資料量)**
```assembly
vsetvli t0, a0, e32, m1      # SEW=32, LMUL=1
vle32.v v1, (a1)             # 僅載入到 v1
vle32.v v2, (a2)             # 僅載入到 v2
vadd.vv v3, v1, v2           # v3 = v1 + v2
```

**使用 LMUL=4 (大資料量)**
```assembly
vsetvli t0, a0, e32, m4      # SEW=32, LMUL=4
vle32.v v4, (a1)             # 載入到 v4,v5,v6,v7 組
vle32.v v8, (a2)             # 載入到 v8,v9,v10,v11 組
vadd.vv v12, v4, v8          # v12-v15 = v4-v7 + v8-v11
                             # 一次處理 4 倍的資料量！
```

#### 範例 3: 迴圈向量化

```assembly
loop_vector:
    vsetvli t0, a0, e32, m4       # 配置: SEW=32, LMUL=4

    # 載入兩個陣列的資料
    vle32.v v0, (a1)              # 載入 A[i:i+VL-1] 到 v0-v3
    vle32.v v4, (a2)              # 載入 B[i:i+VL-1] 到 v4-v7

    # 向量乘法
    vmul.vv v8, v0, v4            # C = A × B (使用 v8-v11)

    # 儲存結果
    vse32.v v8, (a3)              # 儲存 C[i:i+VL-1]

    # 更新指標
    slli t1, t0, 2                # t1 = VL × 4 (32-bit = 4 bytes)
    add a1, a1, t1                # A += VL
    add a2, a2, t1                # B += VL
    add a3, a3, t1                # C += VL
    sub a0, a0, t0                # 剩餘元素 -= VL
    bnez a0, loop_vector          # 如果還有元素，繼續迴圈
```

### LMUL 對硬體設計的影響

1. **暫存器檔案設計**
   - 需要支援多埠讀取 (LMUL=8 時，一次讀取 8 個暫存器)
   - 暫存器分組的路由邏輯

2. **執行單元設計**
   - 更寬的資料路徑 (LMUL 倍數)
   - 或設計多個執行單元並行處理

3. **記憶體頻寬需求**
   - LMUL 越大，單次載入/儲存的資料量越大
   - 需要更高的記憶體頻寬支援

## 支援的 RVV 指令類別

### Vector Configuration 指令
- `vsetvl`, `vsetvli`, `vsetivli` - 設定向量長度和類型

### Vector Load/Store 指令
- **Unit-Stride**: `vle8`, `vle16`, `vle32`, `vle64`, `vse8`, `vse16`, `vse32`, `vse64`
- **Strided**: `vlse8`, `vlse16`, `vlse32`, `vlse64`, `vsse8`, `vsse16`, `vsse32`, `vsse64`
- **Indexed**: `vlxei8`, `vlxei16`, `vlxei32`, `vlxei64`, `vsxei8`, `vsxei16`, `vsxei32`, `vsxei64`

### Vector 算術指令
- `vadd`, `vsub`, `vrsub` - 加法、減法
- `vmul`, `vmulh`, `vmulhu`, `vmulhsu` - 乘法
- `vdiv`, `vdivu`, `vrem`, `vremu` - 除法、餘數
- `vmadd`, `vnmsub`, `vmacc`, `vnmsac` - 乘加運算

### Vector 位移指令
- `vsll`, `vsrl`, `vsra` - 左移、邏輯右移、算術右移

### Vector 比較指令
- `vmseq`, `vmsne` - 相等、不等
- `vmsltu`, `vmslt`, `vmsleu`, `vmsle` - 小於比較
- `vmsgtu`, `vmsgt` - 大於比較

### Vector 浮點指令
- `vfadd`, `vfsub`, `vfmul`, `vfdiv` - 浮點運算
- `vfmadd`, `vfnmadd`, `vfmsub`, `vfnmsub` - 浮點乘加
- `vfsqrt`, `vfmin`, `vfmax` - 浮點特殊運算

### Vector 歸約指令
- `vredsum`, `vredand`, `vredor`, `vredxor` - 歸約運算
- `vredmin`, `vredminu`, `vredmax`, `vredmaxu` - 最小/最大值歸約

### Vector 遮罩指令
- `vmand`, `vmnand`, `vmor`, `vmnor`, `vmxor` - 遮罩邏輯運算
- `vpopc`, `vfirst` - 遮罩計數和查找

### Vector 排列指令
- `vslideup`, `vslidedown` - 元素滑動
- `vrgather`, `vcompress` - 元素重新排列

## 安裝

### 前置要求

- Python 3.7 或更高版本
- AndeSight RISC-V toolchain (或其他 RISC-V objdump 工具)
- matplotlib (可選，用於生成圖表)

### 安裝步驟

1. 克隆或下載此儲存庫

```bash
git clone <repository-url>
cd ARVVI
```

2. 安裝 Python 相依套件 (可選，用於視覺化)

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

分析單個二進位檔案：

```bash
python arvvi.py /path/to/your/model/output.adx
```

### 進階用法

#### 1. 指定模型名稱

```bash
python arvvi.py /models/mobilenetV1/OUTPUT/output.adx --model MobileNetV1
```

#### 2. 生成視覺化圖表

```bash
python arvvi.py /models/mobilenetV1/OUTPUT/output.adx --visualize
```

這將生成包含以下內容的 PNG 圖表：
- 前 20 個最常用的 RVV 指令長條圖
- 前 10 個 RVV 指令的圓餅圖分布
- 總體統計資訊

#### 3. 匯出 JSON 統計資料

```bash
python arvvi.py /models/mobilenetV1/OUTPUT/output.adx -o mobilenet_stats.json
```

#### 4. 指定自訂 objdump 路徑

如果你的 toolchain 不在預設位置，可以指定：

```bash
python arvvi.py /models/bev/output.adx \
  --objdump /path/to/your/toolchain/bin/riscv64-elf-objdump
```

#### 5. 完整範例

```bash
python arvvi.py /models/mobilenetV1/OUTPUT/output.adx \
  --model MobileNetV1 \
  --visualize \
  -o mobilenet_stats.json \
  --objdump /home/ymchang/AndeSight-v5_4_0/toolchains-bin/nds64le-elf-newlib-v5d/bin/riscv64-elf-objdump
```

### 比較多個模型

使用 `arvvi_compare.py` 腳本對比多個模型的 RVV 指令使用情況：

```bash
# 首先為每個模型生成 JSON 統計檔案
python arvvi.py /models/mobilenetV1/output.adx -o mobilenet.json --model MobileNetV1
python arvvi.py /models/bev/output.adx -o bev.json --model BEV
python arvvi.py /models/resnet/output.adx -o resnet.json --model ResNet

# 然後進行比較
python arvvi_compare.py mobilenet.json bev.json resnet.json --visualize
```

這將生成一個對比圖表，展示不同模型間的 RVV 指令使用差異。

## 輸出範例

### 終端輸出

```
Analyzing binary: /models/mobilenetV1/OUTPUT/output.adx
Using objdump: /home/ymchang/AndeSight-v5_4_0/toolchains-bin/nds64le-elf-newlib-v5d/bin/riscv64-elf-objdump

Running objdump...
Parsing instructions...

============================================================
Model: MobileNetV1
============================================================

Total instructions: 45678
RVV instructions: 12345
RVV usage: 27.03%

RVV Instruction Distribution:
------------------------------------------------------------
vle8                :   1234
vse8                :   1123
vadd                :    987
vmul                :    856
vfadd               :    654
vfmul               :    543
vsetvli             :    432
...
```

### 視覺化圖表

工具會生成以下圖表：

1. **主分析圖** (`{ModelName}_rvv_analysis.png`)
   - 左側：前 20 個最常用指令的橫向長條圖
   - 右側：前 10 個指令的圓餅圖分布
   - 底部：總體統計資訊

2. **詳細分析圖** (`{ModelName}_rvv_analysis_detailed.png`)
   - 包含所有 RVV 指令的完整長條圖

3. **模型對比圖** (`model_comparison.png`)
   - 多模型間的指令使用對比

## 配置

### 預設 objdump 路徑

預設的 objdump 路徑設定在 `arvvi.py` 的開頭：

```python
DEFAULT_OBJDUMP = "/home/ymchang/AndeSight-v5_4_0/toolchains-bin/nds64le-elf-newlib-v5d/bin/riscv64-elf-objdump"
```

你可以修改這個路徑以符合你的 toolchain 安裝位置。

## 應用場景

### 1. 硬體設計最佳化

透過分析 AI 模型的 RVV 指令使用模式，硬體設計師可以：
- 識別最常用的向量指令
- 最佳化這些指令的硬體實作
- 決定哪些指令需要更多的硬體資源
- 評估不同向量長度 (VLEN) 的影響
- 分析 LMUL 使用模式以最佳化暫存器檔案設計
- 決定執行單元的數量和寬度

### 2. 軟體最佳化

軟體開發者可以：
- 了解編譯器生成的向量指令模式
- 識別最佳化機會
- 比較不同編譯選項的效果
- 評估手寫組合語言程式碼的效能
- 分析 vsetvl 配置指令的使用頻率
- 最佳化 LMUL 選擇以平衡效能和暫存器壓力

### 3. 模型對比分析

AI 研究人員可以：
- 比較不同 AI 模型的向量化程度
- 分析模型的硬體友善性
- 選擇最適合特定硬體的模型架構
- 評估不同模型對 RVV 特性的利用率

### 4. 效能調校

根據指令統計結果進行效能調校：
- 如果 `vsetvli` 出現頻繁，考慮減少配置切換
- 如果看到大量 unit-stride load/store，確保記憶體頻寬充足
- 如果 LMUL=8 使用頻繁，需要更多暫存器和執行單元
- 如果浮點運算占比高，需要強化浮點執行單元

## 檔案說明

- `arvvi.py` - 主程式，用於分析單個二進位檔案
- `arvvi_visualizer.py` - 視覺化模組，生成圖表
- `arvvi_compare.py` - 多模型比較工具
- `requirements.txt` - Python 相依套件清單

## 技術細節

### RVV 指令識別

工具使用正規表示式配對 RISC-V Vector Extension 規範中定義的指令。支援的指令集包括：

- RVV 1.0 標準指令
- 整數和浮點向量運算
- 不同資料寬度的載入/儲存操作
- 遮罩和排列操作
- 向量配置指令 (vsetvl/vsetvli)

### 效能考量

- 使用串流處理 objdump 輸出，支援大型二進位檔案
- 正規表示式經過最佳化以提高配對速度
- 可選的視覺化功能避免不必要的相依性

## 故障排除

### objdump 未找到

```
Error: objdump not found at /path/to/objdump
```

**解決方法**: 使用 `--objdump` 參數指定正確的 objdump 路徑

### matplotlib 未安裝

```
Warning: matplotlib not installed. Install with: pip install matplotlib
```

**解決方法**: 執行 `pip install matplotlib` 安裝視覺化相依套件

### 二進位檔案格式不支援

確保你的二進位檔案是 RISC-V 格式，可以使用 `file` 命令檢查：

```bash
file /path/to/binary
```

## 授權條款

[在此新增授權條款資訊]

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 聯絡方式

[在此新增聯絡資訊]

---

**ARVVI** - Analyze RISC-V Vector Instructions, Optimize AI Accelerators
