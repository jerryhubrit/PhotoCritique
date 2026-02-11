# 智能摄影学习助手 🎨📷 / Smart Photography Learning Assistant

[中文](#中文) | [English](#english)

---

## 中文

基于 AI 的智能摄影分析与学习系统，帮助摄影爱好者提升技能。支持照片分析、色彩调优和专业预设导出。

### ✨ 主要功能

#### 📊 照片分析系统
- 📸 **基础信息分析**：分辨率、长宽比、亮度、对比度
- 📊 **六维评分系统**：构图、光影、色彩、创意、技术、情绪
- 🎨 **色彩美学分析**：主色调提取、色彩和谐度、心理学分析
- ❤️ **AI情感分析**：InternLM多模态模型提供专业摄影师视角的情感解读
- 💡 **智能学习建议**：根据评分自动生成针对性改进建议
- 📅 **个性化练习方案**：短期、中期、长期的系统性训练计划
- 🌍 **多语言支持**：支持中文和英文报告生成

#### 🎨 色彩处理工具
- 🎭 **色彩风格迁移**：从参考图提取色调特征应用到目标图
  - 支持 4 种迁移算法：全局LAB统计、分区迁移、直方图匹配、改进组合法
  - 可调节迁移强度（0.0-1.0）
  - 可选保留原图亮度
- 📦 **3D LUT 导出**：将色彩迁移结果导出为 .cube 格式 LUT
  - 兼容 Lightroom Classic、Premiere Pro、DaVinci Resolve、FCPX
  - 支持 17/33/65 网格精度
- 🎯 **Lightroom XMP 预设生成**：自动生成专业调色预设
  - 基于分区色彩统计（阴影/中间调/高光）
  - 支持 Split Toning、Color Grading、HSL 分通道调整

### 🚀 快速开始

#### 1. 环境要求

- Python 3.9+
- macOS / Linux / Windows

#### 2. 安装依赖

```bash
pip install Pillow numpy scikit-image scikit-learn scipy requests python-dotenv
```

#### 3. 配置 API Key

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的 InternLM API Key：
```bash
INTERNLM_API_KEY=your_api_key_here
```

> 💡 如何获取 API Key：访问 [InternLM 开放平台](https://internlm.intern-ai.org.cn/) 注册并获取

#### 4. 使用示例

##### 📊 照片分析

```bash
# 分析单张照片（默认中文报告）
python3 batch_analyzer.py your_photo.jpg

# 生成英文报告
python3 batch_analyzer.py your_photo.jpg -l en

# 分析多张照片
python3 batch_analyzer.py photo1.jpg photo2.jpg photo3.jpg

# 指定输出文件名和语言
python3 batch_analyzer.py photo.jpg -o my_report.html -l en
```

##### 🎨 色彩风格迁移

```bash
# 基础迁移（使用默认分区算法）
python3 photo-tutor/scripts/color_transfer.py reference.jpg target.jpg

# 使用全局LAB统计方法
python3 photo-tutor/scripts/color_transfer.py reference.jpg target.jpg --method global_lab

# 调节迁移强度为60%
python3 photo-tutor/scripts/color_transfer.py reference.jpg target.jpg --strength 0.6

# 保留原图亮度，只迁移色彩
python3 photo-tutor/scripts/color_transfer.py reference.jpg target.jpg --preserve-luminance
```

##### 📦 生成 3D LUT

```bash
# 从参考图生成 LUT（默认33x33x33网格）
python3 photo-tutor/scripts/lut_generator.py reference.jpg -o my_lut.cube

# 生成高精度 LUT（65x65x65）
python3 photo-tutor/scripts/lut_generator.py reference.jpg -o my_lut.cube --size 65

# 指定迁移方法和强度
python3 photo-tutor/scripts/lut_generator.py reference.jpg -o my_lut.cube --method improved --strength 0.8
```

##### 🎯 生成 Lightroom XMP 预设

```bash
# 从参考图生成 XMP 预设
python3 photo-tutor/scripts/xmp_exporter.py reference.jpg -o MyPreset.xmp

# 自定义预设名称
python3 photo-tutor/scripts/xmp_exporter.py reference.jpg -o MyPreset.xmp --name "Vintage Film Look"
```

### 🎨 色彩迁移算法对比

| 算法 | 特点 | 适用场景 |
|------|------|----------|
| `global_lab` | 全局LAB统计匹配 | 整体色调一致的场景 |
| `zone_based` | 分区（阴影/中间调/高光）独立迁移 | 明暗对比强的场景 |
| `histogram` | 直方图匹配 | 需要精确色彩还原 |
| `improved` | 组合算法（推荐） | 通用场景，效果最佳 |

### 📊 分析报告内容

生成的 HTML 报告包含：

1. **基础信息** - 照片的技术参数
2. **六维评分雷达图** - 可视化展示各维度表现
3. **色彩美学分析** - 色彩调色板、和谐度、心理学分析
4. **AI情感分析** - 温暖、共情的专业解读（英文模式自动翻译）
5. **学习建议** - 智能识别薄弱环节并提供改进建议
6. **练习方案** - 系统化的分阶段训练计划

### 📁 报告命名规则

报告文件自动保存在 `reports/` 目录，命名格式：

```
photo_report_YYYYMMDD_LANG_XXX.html
```

示例：
- `photo_report_20260128_zh_001.html` - 2026年1月28日第1份中文报告
- `photo_report_20260128_en_001.html` - 2026年1月28日第1份英文报告

### 🔒 安全说明

- ✅ `.env` 文件已添加到 `.gitignore`，不会被上传到 Git
- ✅ 使用 `.env.example` 作为配置模板分享给其他开发者
- ✅ API Key 从环境变量读取，代码中不包含真实密钥
- ✅ 详细安全指南请查看 [SECURITY.md](SECURITY.md)

### 📂 项目结构

```
photo ai/
├── batch_analyzer.py          # 批量分析主程序
├── i18n.py                     # 国际化翻译模块
├── .env                        # 环境变量配置（不会上传）
├── .env.example                # 环境变量模板
├── reports/                    # 生成的报告目录
└── photo-tutor/
    └── scripts/
        ├── photo_analyzer.py   # 照片基础分析
        ├── color_analyzer.py   # 色彩美学分析
        ├── emotion_analyzer.py # AI情感分析（支持翻译）
        ├── color_transfer.py   # 色彩风格迁移引擎
        ├── lut_generator.py    # 3D LUT 生成器
        └── xmp_exporter.py     # Lightroom XMP 预设导出
```

### 🛠️ 技术栈

- **图像处理**: PIL (Pillow)
- **数值计算**: NumPy, SciPy
- **图像分析**: scikit-image
- **色彩聚类**: scikit-learn
- **AI模型**: InternLM 多模态大模型
- **前端可视化**: HTML5 Canvas
- **国际化**: 自定义 i18n 模块

### 📝 许可证

本项目仅供学习交流使用。

### 💬 反馈与支持

如有问题或建议，欢迎提 Issue！

---

## English

An AI-powered intelligent photography analysis and learning system to help photography enthusiasts improve their skills. Supports photo analysis, color optimization, and professional preset export.

### ✨ Key Features

#### 📊 Photo Analysis System
- 📸 **Basic Information Analysis**: Resolution, aspect ratio, brightness, contrast
- 📊 **Six-Dimension Scoring**: Composition, lighting, color, creativity, technique, emotion
- 🎨 **Color Aesthetics Analysis**: Dominant color extraction, color harmony, psychological analysis
- ❤️ **AI Emotion Analysis**: Professional photographer's perspective powered by InternLM
- 💡 **Smart Learning Suggestions**: Auto-generate targeted improvement suggestions
- 📅 **Personalized Practice Plans**: Systematic training plans
- 🌍 **Multilingual Support**: Generate reports in Chinese and English

#### 🎨 Color Processing Tools
- 🎭 **Color Style Transfer**: Extract and apply color features from reference images
  - 4 algorithms: Global LAB, Zone-based, Histogram matching, Improved combination
  - Adjustable transfer strength (0.0-1.0)
  - Optional luminance preservation
- 📦 **3D LUT Export**: Export as .cube format LUT files
  - Compatible with Lightroom, Premiere Pro, DaVinci Resolve, FCPX
  - Support 17/33/65 grid precision
- 🎯 **Lightroom XMP Presets**: Auto-generate professional grading presets
  - Based on zone statistics (shadows/midtones/highlights)
  - Support Split Toning, Color Grading, HSL adjustments

### 🚀 Quick Start

#### 1. Requirements

- Python 3.9+
- macOS / Linux / Windows

#### 2. Install Dependencies

```bash
pip install Pillow numpy scikit-image scikit-learn scipy requests python-dotenv
```

#### 3. Configure API Key

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` and add your InternLM API Key:
```bash
INTERNLM_API_KEY=your_api_key_here
```

> 💡 Get API Key: Visit [InternLM Open Platform](https://internlm.intern-ai.org.cn/)

#### 4. Usage Examples

##### 📊 Photo Analysis

```bash
# Analyze single photo (default Chinese)
python3 batch_analyzer.py your_photo.jpg

# Generate English report
python3 batch_analyzer.py your_photo.jpg -l en

# Analyze multiple photos
python3 batch_analyzer.py photo1.jpg photo2.jpg photo3.jpg
```

##### 🎨 Color Style Transfer

```bash
# Basic transfer
python3 photo-tutor/scripts/color_transfer.py reference.jpg target.jpg

# Use global LAB method
python3 photo-tutor/scripts/color_transfer.py reference.jpg target.jpg --method global_lab

# Adjust strength to 60%
python3 photo-tutor/scripts/color_transfer.py reference.jpg target.jpg --strength 0.6
```

##### 📦 Generate 3D LUT

```bash
# Generate LUT (default 33x33x33)
python3 photo-tutor/scripts/lut_generator.py reference.jpg -o my_lut.cube

# High precision (65x65x65)
python3 photo-tutor/scripts/lut_generator.py reference.jpg -o my_lut.cube --size 65
```

##### 🎯 Generate Lightroom XMP

```bash
# Generate XMP preset
python3 photo-tutor/scripts/xmp_exporter.py reference.jpg -o MyPreset.xmp

# Custom name
python3 photo-tutor/scripts/xmp_exporter.py reference.jpg -o MyPreset.xmp --name "Vintage Film"
```

### 🎨 Algorithm Comparison

| Algorithm | Features | Best For |
|-----------|----------|----------|
| `global_lab` | Global LAB statistics | Consistent overall tone |
| `zone_based` | Zone-independent transfer | Strong contrast scenes |
| `histogram` | Histogram matching | Precise color reproduction |
| `improved` | Combination (recommended) | General scenes |

### 📊 Report Content

HTML reports include:

1. **Basic Information** - Technical parameters
2. **Six-Dimension Radar Chart** - Visual performance metrics
3. **Color Aesthetics** - Palette, harmony, psychology
4. **AI Emotion Analysis** - Professional interpretation
5. **Learning Suggestions** - Improvement recommendations
6. **Practice Plans** - Phased training programs

### 📁 Report Naming

Format: `photo_report_YYYYMMDD_LANG_XXX.html`

Examples:
- `photo_report_20260128_zh_001.html`
- `photo_report_20260128_en_001.html`

### 🔒 Security

- ✅ `.env` in `.gitignore`
- ✅ Use `.env.example` as template
- ✅ API Key from environment variables
- ✅ See [SECURITY.md](SECURITY.md) for details

### 📂 Project Structure

```
photo ai/
├── batch_analyzer.py          # Main analysis program
├── i18n.py                     # i18n module
├── reports/                    # Generated reports
└── photo-tutor/scripts/
    ├── color_transfer.py       # Color transfer engine
    ├── lut_generator.py        # LUT generator
    └── xmp_exporter.py         # XMP exporter
```

### 🛠️ Tech Stack

- **Image Processing**: PIL (Pillow)
- **Computing**: NumPy, SciPy
- **Analysis**: scikit-image, scikit-learn
- **AI Model**: InternLM Multimodal Model
- **Visualization**: HTML5 Canvas

### 📝 License

For learning and communication purposes only.

### 💬 Support

Questions? Submit an Issue!
