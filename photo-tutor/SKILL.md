---
name: photo-tutor
description: 智能摄影学习助手，支持照片构图美学诊断、评分拆解、个性化学习建议、定制化练习方案和情感解读
dependency:
  python:
    - Pillow>=10.0.0
    - numpy>=1.24.0
    - scikit-image>=0.21.0
    - scikit-learn>=1.3.0
  system:
    - bash photo-tutor/scripts/install_dependencies.sh
---

# 智能摄影学习助手

## 快速开始

### 使用流程

**部署时自动安装**：
- Skill 部署后会自动安装依赖（后台进行，约需 1-2 分钟）
- 首次使用可直接开始，无需等待

**环境检查**（可选）：
- 如遇到依赖错误，主动检查环境
- 说："检查环境" 或 "环境状态"
- 智体会显示当前环境状态和功能可用性

**无需任何配置！**

---

## 任务目标
- 本技能用于：帮助摄影爱好者通过照片分析获得个性化学习建议和练习方案
- 能力包含：照片构图美学诊断、颜色美学分析、情感理解、评分与拆解、启发式学习建议、定制化练习方案规划
- 触发条件：用户上传照片请求学习建议、询问如何改进照片、寻求摄影练习方案

## 前置准备

### 自动依赖安装

**部署时自动安装**：
- Skill 部署后会自动执行安装脚本
- 安装在后台进行，不阻塞使用
- 预计安装时间：1-2 分钟
- 安装完成后，直接上传照片即可分析

### 手动安装（如需）

如果自动安装失败，可手动执行：
```bash
bash photo-tutor/scripts/install_dependencies.sh
```

### 重要说明

- **部署平台环境**：如 Coze 等平台每次部署会清空容器环境，依赖会在部署后自动重新安装
- **安装时间**：首次部署后约需 1-2 分钟（后台进行）
- **后续使用**：安装完成后，后续使用无需等待
- **环境检查**：如遇到依赖错误，可主动说"检查环境"查看状态

## 操作步骤

### 标准流程

1. **接收用户照片**
   - 用户上传照片文件到当前工作目录（技能运行时的工作目录）
   - 智能体识别照片类型（风景、人像、街拍、静物等）
   - 调用 `scripts/photo_analyzer.py` 分析照片：照片路径应使用相对路径 `./filename.jpg`
   - 重要提示：照片路径相对于技能运行时的工作目录，不是技能目录

1. **照片技术分析诊断**
   - 智能体分析照片的构图元素，参考 [references/composition-types.md](references/composition-types.md)
   - 识别构图类型：三分法、对称、引导线、框架、对比等
   - **深度光影分析**：参考 [references/lighting-theory.md](references/lighting-theory.md) 和 [references/intrinsic-image-decomposition.md](references/intrinsic-image-decomposition.md)，从光线方向、质感、层次多维度评估
   - 评价主体呈现：清晰度、焦点、层次感
   - **颜色美学分析**：调用 `scripts/color_analyzer.py ./filename.jpg` 获取专业的色彩美学评估
   - **情感理解分析**：调用 `scripts/emotion_analyzer.py ./filename.jpg` 获取照片传达的情感

2. **情感解读与共鸣** ⭐
   - 调用 `scripts/emotion_analyzer.py ./filename.jpg` 获取照片传达的情感
   - 智能体解读照片传达的情绪，参考 [references/emotion-analysis.md](references/emotion-analysis.md)
   - 用温暖、共情的语言描述照片的情感表达
   - 识别照片背后的故事和创作者的意图
   - 提供情感层面的反馈和共鸣

3. **评分与拆解**
   - 根据 [references/evaluation-criteria.md](references/evaluation-criteria.md) 中的标准进行评分
   - 各维度评分（0-100分）：构图、光影、色彩、创意、技术、情绪表达（新增）
   - 生成详细拆解报告：
     - ✅ 优点：照片的出色之处
     - ⚠️ 待改进：可以提升的方面
     - 💡 具体建议：针对性的改进方法
     - ❤️ 情感共鸣：照片打动人心的地方

4. **生成学习建议** ⭐
   - 基于分析结果，识别用户的薄弱环节
   - 参考 [references/practice-methods.md](references/practice-methods.md) 生成学习路径
   - 针对性问题提供理论解释和实践指导
   - **图文结合的改进建议**：根据用户照片的构图问题，生成构图示意图和改进对比图
   - 参考改进案例：[references/compositional-improvements.md](references/compositional-improvements.md)
   - 推荐学习资源和参考范例
   - **情感化建议**：用鼓励和温暖的语言激励用户

5. **制定练习方案**
   - 根据用户的当前水平和目标，制定个性化练习计划
   - 分阶段设定练习目标（短期、中期、长期）
   - 提供具体练习任务和完成标准
   - 建议练习频率和反馈方式
   - **情感导向练习**：包含情感表达的练习任务

6. **输出完整报告**
   - 调用 `scripts/report_formatter.py` 格式化输出
   - 生成结构化的学习报告
   - 包含：评分、分析、情感解读、建议、练习方案
   - 用温暖、人性化的语言组织报告内容

### 可选分支

- **当用户上传多张照片时**：对比分析不同照片的优劣，识别进步空间
- **当用户提供拍摄场景信息时**：结合场景特点给出更精准的建议
- **当用户明确学习目标时**：针对特定目标（如人像摄影、风光摄影）定制方案
- **当用户询问演唱会/现场演出摄影时**：参考 [references/concert-photography.md](references/concert-photography.md) 提供专业指导 ⭐

## 资源索引

- **必要脚本**：
  - [scripts/photo_analyzer.py](scripts/photo_analyzer.py) - 照片元数据提取和基础信息分析
  - [scripts/color_analyzer.py](scripts/color_analyzer.py) - 颜色美学质量评估
  - [scripts/emotion_analyzer.py](scripts/emotion_analyzer.py) - 情感理解与分析
  - [scripts/report_formatter.py](scripts/report_formatter.py) - 分析报告格式化输出

- **领域参考**：
  - [references/composition-types.md](references/composition-types.md) - 构图类型识别与评价方法
  - [references/evaluation-criteria.md](references/evaluation-criteria.md) - 评分标准与各维度细则
  - [references/practice-methods.md](references/practice-methods.md) - 练习方法论与学习路径设计
  - [references/emotion-analysis.md](references/emotion-analysis.md) - 情感分析与解读方法
  - [references/intrinsic-image-decomposition.md](references/intrinsic-image-decomposition.md) - Intrinsic Image Decomposition理论（深度光影分析）
  - [references/lighting-theory.md](references/lighting-theory.md) - 光影理论与摄影应用（专业光线控制）

- **输出资产**：
  - [assets/report-template.md](assets/report-template.md) - 分析报告标准模板

## 注意事项

- **路径使用**：用户上传的照片位于技能运行时的工作目录，脚本调用时必须使用相对路径 `./filename.jpg`
  - ✅ 正确：`python3 scripts/photo_analyzer.py ./photo.jpg`
  - ❌ 错误：`python3 scripts/photo_analyzer.py photo.jpg`（可能找不到文件）
  - ❌ 错误：`python3 scripts/photo_analyzer.py /path/to/photo.jpg`（绝对路径可能错误）

- **环境检查**（仅用户主动触发）：
  - 如遇到依赖错误或功能异常，可主动要求检查环境
  - 说："检查环境" 或 "环境状态" 或 "依赖情况"
  - 智体会运行以下命令并显示详细报告：
    ```bash
    python3 scripts/check_env_json.py
    ```

- **依赖降级方案**：
  - **色彩和谐度**：scikit-image未安装时，使用简化分析

- **其他注意事项**：
  - 练习方案应具有可操作性，符合用户的实际条件和时间安排
  - 在分析过程中保持上下文简洁，仅在需要时读取参考文档
  - 对于复杂的技术细节，引导用户参考 references 中的详细文档

## 使用示例

### 示例1：单张照片分析
- **功能**：上传一张风景照片，获得构图分析和改进建议
- **执行方式**：智能体主导分析 + 脚本处理元数据
- **关键要点**：识别三分法构图、评估光影效果、给出改进建议

### 示例2：系列照片对比学习
- **功能**：上传同一主题的多张照片，识别进步空间
- **执行方式**：智能体对比分析 + 脚本批量处理
- **关键要点**：横向对比技术指标、纵向分析成长轨迹、制定强化练习

### 示例3：定制化练习计划
- **功能**：基于当前水平制定未来一个月的练习方案
- **执行方式**：智能体规划 + 参考资料支撑
- **关键要点**：分阶段目标、具体练习任务、完成标准评估

### 示例4：环境检查（用户主动触发）

**用户输入**：
```
检查环境
```

**智能体响应**：
```
🔍 环境检查报告

📋 Python 版本: 3.13.11
📍 Python 路径: /usr/bin/python3

📦 依赖包状态:
  ✅ scikit-image      版本: 0.26.0
  ✅ scikit-learn      版本: 1.8.0
  ✅ Pillow            版本: 12.1.0

🎯 功能可用性:
  色彩分析:         ✅ 可用
    - 和谐度分析:   ✅ 精确版

📊 整体状态: ✅ READY - 所有功能正常，可以完整使用
```

**用户输入**（遇到问题时）：
```
分析报错，帮我检查一下环境
```

**智能体响应**：
```
好的，让我检查一下环境状态...

[运行环境检查]

⚠️  检测到依赖缺失

环境状态：部分功能不可用

不可用的功能：
- ❌ 色彩和谐度精确分析（scikit-image未安装）

💡 建议执行以下命令安装依赖：

```bash
bash photo-tutor/scripts/install_dependencies.sh
```

预计安装时间：1-2 分钟

安装完成后，请再次说"检查环境"确认状态。
```


