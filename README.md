# 智能摄影学习助手 🎨📷 / Smart Photography Learning Assistant

[中文](#中文) | [English](#english)

---

## 中文

基于 AI 的智能摄影分析与学习系统，帮助摄影爱好者提升技能。

### ✨ 主要功能

- 📸 **基础信息分析**：分辨率、长宽比、亮度、对比度
- 📊 **六维评分系统**：构图、光影、色彩、创意、技术、情绪
- 🎨 **色彩美学分析**：主色调提取、色彩和谐度、心理学分析
- ❤️ **AI情感分析**：InternLM多模态模型提供专业摄影师视角的情感解读
- 💡 **智能学习建议**：根据评分自动生成针对性改进建议
- 📅 **个性化练习方案**：短期、中期、长期的系统性训练计划
- 🌍 **多语言支持**：支持中文和英文报告生成

### 🚀 快速开始

#### 1. 环境要求

- Python 3.9+
- macOS / Linux / Windows

#### 2. 安装依赖

```bash
pip install Pillow numpy scikit-image scikit-learn requests python-dotenv
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

#### 4. 开始分析

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

#### 5. 语言支持 🌍

系统支持多语言报告生成：

- **中文（zh）**：`-l zh` 或不指定（默认）
- **English（en）**：`-l en`

示例：
```bash
# 生成中文报告
python3 batch_analyzer.py photo.jpg

# 生成英文报告  
python3 batch_analyzer.py photo.jpg -l en
```

所有界面元素、分析内容、学习建议都会根据选择的语言自动翻译。

### 📊 报告内容

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
- `photo_report_20260128_en_002.html` - 2026年1月28日第2份英文报告

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
├── .gitignore                  # Git忽略文件配置
├── reports/                    # 生成的报告目录
└── photo-tutor/
    └── scripts/
        ├── photo_analyzer.py   # 照片基础分析
        ├── color_analyzer.py   # 色彩美学分析
        └── emotion_analyzer.py # AI情感分析（支持翻译）
```

### 🛠️ 技术栈

- **图像处理**: PIL (Pillow)
- **数值计算**: NumPy
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

An AI-powered intelligent photography analysis and learning system to help photography enthusiasts improve their skills.

### ✨ Key Features

- 📸 **Basic Information Analysis**: Resolution, aspect ratio, brightness, contrast
- 📊 **Six-Dimension Scoring System**: Composition, lighting, color, creativity, technique, emotion
- 🎨 **Color Aesthetics Analysis**: Dominant color extraction, color harmony, psychological analysis
- ❤️ **AI Emotion Analysis**: Professional photographer's perspective powered by InternLM multimodal model
- 💡 **Smart Learning Suggestions**: Automatically generate targeted improvement suggestions based on scores
- 📅 **Personalized Practice Plans**: Systematic training plans for short-term, medium-term, and long-term
- 🌍 **Multilingual Support**: Generate reports in Chinese and English

### 🚀 Quick Start

#### 1. Requirements

- Python 3.9+
- macOS / Linux / Windows

#### 2. Install Dependencies

```bash
pip install Pillow numpy scikit-image scikit-learn requests python-dotenv
```

#### 3. Configure API Key

1. Copy the environment variable template:
```bash
cp .env.example .env
```

2. Edit the `.env` file and fill in your InternLM API Key:
```bash
INTERNLM_API_KEY=your_api_key_here
```

> 💡 How to get API Key: Visit [InternLM Open Platform](https://internlm.intern-ai.org.cn/) to register and obtain

#### 4. Start Analysis

```bash
# Analyze a single photo (default Chinese report)
python3 batch_analyzer.py your_photo.jpg

# Generate English report
python3 batch_analyzer.py your_photo.jpg -l en

# Analyze multiple photos
python3 batch_analyzer.py photo1.jpg photo2.jpg photo3.jpg

# Specify output filename and language
python3 batch_analyzer.py photo.jpg -o my_report.html -l en
```

#### 5. Language Support 🌍

The system supports multilingual report generation:

- **Chinese (zh)**: `-l zh` or unspecified (default)
- **English (en)**: `-l en`

Examples:
```bash
# Generate Chinese report
python3 batch_analyzer.py photo.jpg

# Generate English report
python3 batch_analyzer.py photo.jpg -l en
```

All UI elements, analysis content, and learning suggestions will be automatically translated based on the selected language.

### 📊 Report Content

The generated HTML report includes:

1. **Basic Information** - Technical parameters of the photo
2. **Six-Dimension Radar Chart** - Visualize performance across dimensions
3. **Color Aesthetics Analysis** - Color palette, harmony, psychological analysis
4. **AI Emotion Analysis** - Warm and empathetic professional interpretation (auto-translated in English mode)
5. **Learning Suggestions** - Intelligently identify weak points and provide improvement suggestions
6. **Practice Plans** - Systematic phased training plans

### 📁 Report Naming Convention

Reports are automatically saved in the `reports/` directory with the naming format:

```
photo_report_YYYYMMDD_LANG_XXX.html
```

Examples:
- `photo_report_20260128_zh_001.html` - 1st Chinese report on January 28, 2026
- `photo_report_20260128_en_001.html` - 1st English report on January 28, 2026
- `photo_report_20260128_en_002.html` - 2nd English report on January 28, 2026

### 🔒 Security Notes

- ✅ `.env` file is added to `.gitignore` and will not be uploaded to Git
- ✅ Use `.env.example` as a configuration template to share with other developers
- ✅ API Key is read from environment variables, no real keys in the code
- ✅ For detailed security guidelines, see [SECURITY.md](SECURITY.md)

### 📂 Project Structure

```
photo ai/
├── batch_analyzer.py          # Main batch analysis program
├── i18n.py                     # Internationalization module
├── .env                        # Environment configuration (not uploaded)
├── .env.example                # Environment template
├── .gitignore                  # Git ignore configuration
├── reports/                    # Generated reports directory
└── photo-tutor/
    └── scripts/
        ├── photo_analyzer.py   # Basic photo analysis
        ├── color_analyzer.py   # Color aesthetics analysis
        └── emotion_analyzer.py # AI emotion analysis (with translation)
```

### 🛠️ Tech Stack

- **Image Processing**: PIL (Pillow)
- **Numerical Computing**: NumPy
- **Image Analysis**: scikit-image
- **Color Clustering**: scikit-learn
- **AI Model**: InternLM Multimodal Large Model
- **Frontend Visualization**: HTML5 Canvas
- **Internationalization**: Custom i18n module

### 📝 License

This project is for learning and communication purposes only.

### 💬 Feedback & Support

If you have any questions or suggestions, feel free to submit an Issue!
