# ARVVI - AndeSight RISC-V Vector Instruction Analyzer

ARVVI 是一个用于分析 RISC-V 二进制文件中 Vector 指令使用情况的工具。它可以帮助硬件设计人员和软件开发者了解 AI 模型在 RISC-V 架构上的向量指令使用模式，从而优化硬件设计和软件实现。

## 功能特性

- 🔍 **自动反汇编分析**: 使用 objdump 自动反汇编 RISC-V 二进制文件
- 📊 **指令统计**: 统计所有 RVV (RISC-V Vector) 指令的使用次数
- 📈 **可视化图表**: 生成直观的柱状图和饼图展示指令分布
- 🔄 **多模型比较**: 支持对比多个 AI 模型的 RVV 指令使用情况
- 💾 **JSON 输出**: 导出详细的统计数据供进一步分析

## 支持的 RVV 指令类别

- Vector 算术指令 (vadd, vsub, vmul, vdiv 等)
- Vector 位移指令 (vsll, vsrl, vsra 等)
- Vector 比较指令 (vmseq, vmslt, vmsle 等)
- Vector 加载/存储指令 (vle, vse, vlse, vsse 等)
- Vector 浮点指令 (vfadd, vfmul, vfdiv 等)
- Vector 归约指令 (vredsum, vredmax, vredmin 等)
- Vector 掩码指令 (vmand, vmor, vmxor 等)
- Vector 排列指令 (vslideup, vslidedown, vrgather 等)
- Vector 配置指令 (vsetvl, vsetvli 等)

## 安装

### 前置要求

- Python 3.7 或更高版本
- AndeSight RISC-V toolchain (或其他 RISC-V objdump 工具)
- matplotlib (可选，用于生成图表)

### 安装步骤

1. 克隆或下载此仓库

```bash
git clone <repository-url>
cd ARVVI
```

2. 安装 Python 依赖 (可选，用于可视化)

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

分析单个二进制文件：

```bash
python arvvi.py /path/to/your/model/output.adx
```

### 高级用法

#### 1. 指定模型名称

```bash
python arvvi.py /models/mobilenetV1/OUTPUT/output.adx --model MobileNetV1
```

#### 2. 生成可视化图表

```bash
python arvvi.py /models/mobilenetV1/OUTPUT/output.adx --visualize
```

这将生成包含以下内容的 PNG 图表：
- 前 20 个最常用的 RVV 指令柱状图
- 前 10 个 RVV 指令的饼图分布
- 总体统计信息

#### 3. 导出 JSON 统计数据

```bash
python arvvi.py /models/mobilenetV1/OUTPUT/output.adx -o mobilenet_stats.json
```

#### 4. 指定自定义 objdump 路径

如果你的 toolchain 不在默认位置，可以指定：

```bash
python arvvi.py /models/bev/output.adx \
  --objdump /path/to/your/toolchain/bin/riscv64-elf-objdump
```

#### 5. 完整示例

```bash
python arvvi.py /models/mobilenetV1/OUTPUT/output.adx \
  --model MobileNetV1 \
  --visualize \
  -o mobilenet_stats.json \
  --objdump /home/ymchang/AndeSight-v5_4_0/toolchains-bin/nds64le-elf-newlib-v5d/bin/riscv64-elf-objdump
```

### 比较多个模型

使用 `arvvi_compare.py` 脚本对比多个模型的 RVV 指令使用情况：

```bash
# 首先为每个模型生成 JSON 统计文件
python arvvi.py /models/mobilenetV1/output.adx -o mobilenet.json --model MobileNetV1
python arvvi.py /models/bev/output.adx -o bev.json --model BEV
python arvvi.py /models/resnet/output.adx -o resnet.json --model ResNet

# 然后进行比较
python arvvi_compare.py mobilenet.json bev.json resnet.json --visualize
```

这将生成一个对比图表，展示不同模型间的 RVV 指令使用差异。

## 输出示例

### 终端输出

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

### 可视化图表

工具会生成以下图表：

1. **主分析图** (`{ModelName}_rvv_analysis.png`)
   - 左侧：前 20 个最常用指令的横向柱状图
   - 右侧：前 10 个指令的饼图分布
   - 底部：总体统计信息

2. **详细分析图** (`{ModelName}_rvv_analysis_detailed.png`)
   - 包含所有 RVV 指令的完整柱状图

3. **模型对比图** (`model_comparison.png`)
   - 多模型间的指令使用对比

## 配置

### 默认 objdump 路径

默认的 objdump 路径设置在 `arvvi.py` 的开头：

```python
DEFAULT_OBJDUMP = "/home/ymchang/AndeSight-v5_4_0/toolchains-bin/nds64le-elf-newlib-v5d/bin/riscv64-elf-objdump"
```

你可以修改这个路径以匹配你的 toolchain 安装位置。

## 应用场景

### 1. 硬件设计优化

通过分析 AI 模型的 RVV 指令使用模式，硬件设计师可以：
- 识别最常用的向量指令
- 优化这些指令的硬件实现
- 决定哪些指令需要更多的硬件资源
- 评估不同向量长度的影响

### 2. 软件优化

软件开发者可以：
- 了解编译器生成的向量指令模式
- 识别优化机会
- 比较不同编译选项的效果
- 评估手写汇编代码的性能

### 3. 模型对比分析

AI 研究人员可以：
- 比较不同 AI 模型的向量化程度
- 分析模型的硬件友好性
- 选择最适合特定硬件的模型架构

## 文件说明

- `arvvi.py` - 主程序，用于分析单个二进制文件
- `arvvi_visualizer.py` - 可视化模块，生成图表
- `arvvi_compare.py` - 多模型比较工具
- `requirements.txt` - Python 依赖列表

## 技术细节

### RVV 指令识别

工具使用正则表达式匹配 RISC-V Vector Extension 规范中定义的指令。支持的指令集包括：

- RVV 1.0 标准指令
- 整数和浮点向量运算
- 不同数据宽度的加载/存储操作
- 掩码和排列操作

### 性能考虑

- 使用流式处理 objdump 输出，支持大型二进制文件
- 正则表达式经过优化以提高匹配速度
- 可选的可视化功能避免不必要的依赖

## 故障排除

### objdump 未找到

```
Error: objdump not found at /path/to/objdump
```

**解决方法**: 使用 `--objdump` 参数指定正确的 objdump 路径

### matplotlib 未安装

```
Warning: matplotlib not installed. Install with: pip install matplotlib
```

**解决方法**: 运行 `pip install matplotlib` 安装可视化依赖

### 二进制文件格式不支持

确保你的二进制文件是 RISC-V 格式，可以使用 `file` 命令检查：

```bash
file /path/to/binary
```

## 许可证

[在此添加许可证信息]

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

[在此添加联系信息]

---

**ARVVI** - Analyze RISC-V Vector Instructions, Optimize AI Accelerators
