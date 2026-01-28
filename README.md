# 智能摄影学习助手 🎨📷

基于 AI 的智能摄影分析与学习系统，帮助摄影爱好者提升技能。

## ✨ 主要功能

- 📸 **基础信息分析**：分辨率、长宽比、亮度、对比度
- 📊 **六维评分系统**：构图、光影、色彩、创意、技术、情绪
- 🎨 **色彩美学分析**：主色调提取、色彩和谐度、心理学分析
- ❤️ **AI情感分析**：InternLM多模态模型提供专业摄影师视角的情感解读
- 💡 **智能学习建议**：根据评分自动生成针对性改进建议
- 📅 **个性化练习方案**：短期、中期、长期的系统性训练计划

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- macOS / Linux / Windows

### 2. 安装依赖

```bash
pip install Pillow numpy scikit-image scikit-learn requests python-dotenv
```

### 3. 配置 API Key

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的 InternLM API Key：
```bash
INTERNLM_API_KEY=your_api_key_here
```

> 💡 如何获取 API Key：访问 [InternLM 开放平台](https://internlm.intern-ai.org.cn/) 注册并获取

### 4. 开始分析

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

### 5. 语言支持 🌍

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

## 📊 报告内容

生成的 HTML 报告包含：

1. **基础信息** - 照片的技术参数
2. **六维评分雷达图** - 可视化展示各维度表现
3. **色彩美学分析** - 色彩调色板、和谐度、心理学分析
4. **AI情感分析** - 温暖、共情的专业解读
5. **学习建议** - 智能识别薄弱环节并提供改进建议
6. **练习方案** - 系统化的分阶段训练计划

## 🔒 安全说明

- ✅ `.env` 文件已添加到 `.gitignore`，不会被上传到 Git
- ✅ 使用 `.env.example` 作为配置模板分享给其他开发者
- ✅ API Key 从环境变量读取，代码中不包含真实密钥

## 📂 项目结构

```
photo ai/
├── batch_analyzer.py          # 批量分析主程序
├── .env                        # 环境变量配置（不会上传）
├── .env.example                # 环境变量模板
├── .gitignore                  # Git忽略文件配置
└── photo-tutor/
    └── scripts/
        ├── photo_analyzer.py   # 照片基础分析
        ├── color_analyzer.py   # 色彩美学分析
        └── emotion_analyzer.py # AI情感分析
```

## 🛠️ 技术栈

- **图像处理**: PIL (Pillow)
- **数值计算**: NumPy
- **图像分析**: scikit-image
- **色彩聚类**: scikit-learn
- **AI模型**: InternLM 多模态大模型
- **前端可视化**: HTML5 Canvas

## 📝 许可证

本项目仅供学习交流使用。

## 💬 反馈与支持

如有问题或建议，欢迎提 Issue！
