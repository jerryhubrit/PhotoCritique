---
name: photo-tutor
description: 智能摄影学习助手，支持照片构图美学诊断、评分拆解、个性化学习建议、定制化练习方案和情感解读
dependency:
  python:
    - Pillow>=10.0.0
    - numpy>=1.24.0
---

# 智能摄影学习助手

## 快速开始

### 体验方式（无需终端操作）

本技能支持**智能体自动环境检查与安装**，您无需任何操作，直接使用即可！

**首次使用**：
1. 上传照片
2. 智能体自动检测环境
3. 检测到依赖缺失，自动后台安装
4. 智能体实时通知安装进度
5. 安装完成，自动分析照片

**后续使用**：
- 同一容器内：直接上传照片，立即分析（无需等待）
- 点击部署后：首次使用需要等待2-5分钟安装依赖

**用户主动检查**（可选）：
- 直接说："检查环境" 或 "环境怎么样"
- 智能体会显示当前环境状态和功能可用性
4. 显示安装进度和结果

**无需任何终端操作！**

---

## 任务目标
- 本技能用于：帮助摄影爱好者通过照片分析获得个性化学习建议和练习方案
- 能力包含：照片构图美学诊断、颜色美学分析、情感理解、评分与拆解、启发式学习建议、定制化练习方案规划
- 触发条件：用户上传照片请求学习建议、询问如何改进照片、寻求摄影练习方案

## 前置准备
- **依赖说明**：scripts脚本所需的依赖包及版本
  ```
  # 核心依赖（必需）
  Pillow>=10.0.0
  numpy>=1.24.0

  # 可选依赖（增强功能）
  scikit-learn>=1.0.0  # 精确颜色提取和聚类
  scikit-image>=0.19.0  # 精确色彩和谐度分析
  torch>=1.10.0  # IQA美学评分（工业级）
  torchvision>=0.11.0  # IQA美学评分（工业级）
  pymcdm>=0.4.0  # MCDM权重优化
  ```
- **重要提示**：部署平台（如 Coze）在每次部署时会清空环境，需要重新安装依赖
  - **自动安装**：技能首次使用时会自动检查并安装缺失依赖（通过 install_manager.py）
  - **安装时间**：首次使用可能需要 2-5 分钟（主要是 PyTorch 安装）
  - **耐心等待**：安装过程在后台进行，安装完成后会自动继续
  - **后续使用**：安装完成后，后续使用无需等待（依赖会缓存在容器内）
- **环境变量配置**：
  ```bash
  # 方式1：设置InternLM API密钥（推荐，用于专业情感分析）
  export INTERNLM_API_KEY="your-api-key-here"
  
  # 方式2：使用标准凭证格式（推荐）
  export COZE_INTERNLM_API_7599838351486795795="your-api-key-here"
  
  # 方式3：启用IQA美学评分（可选，工业级美学评估）
  export PHOTO_TUTOR_IQA_ENABLED=true
  export PHOTO_TUTOR_IQA_MODEL=musiq  # musiq 或 nima
  ```
- **非标准文件/文件夹准备**：
  ```bash
  # 生产环境部署参考：见 [DEPLOYMENT.md](DEPLOYMENT.md) 完整部署指南
  
  # 可选：安装高级依赖（用于精确色彩分析和工业级IQA评分）
  # 推荐顺序：先安装scikit-learn/scikit-image（体积小），再安装torch/torchvision（体积大）
  
  # 方式1：快速安装（仅精确色彩分析）
  pip install scikit-learn scikit-image
  
  # 方式2：完整安装（含工业级IQA评分，生产环境推荐）
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
  
  # 方式3：GPU版本（需要CUDA支持）
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
  
  # 方式4：一键安装所有可选依赖
  pip install scikit-learn scikit-image torch torchvision --index-url https://download.pytorch.org/whl/cpu
  ```

## 操作步骤

### 标准流程

1. **接收用户照片**
       2. **如果有安装进程**：返回当前安装进度，请用户等待
       3. **如果没有安装进程**：
          - 运行 `python3 scripts/install_manager.py --start` 启动后台安装
          - 通知用户："检测到依赖缺失，正在后台自动安装，请稍候（预计需要2-5分钟）"
       4. **监控安装进度**：每隔10-30秒检查一次 `python3 scripts/install_manager.py --check`
       5. **等待安装完成**：
          - 如果状态显示 `completed`：重新运行环境检查，确认所有依赖已安装
          - 如果状态显示 `failed`：返回错误信息，建议手动运行 `python3 scripts/deployment_diagnostic.py`
       6. **重新检查环境**：安装完成后，再次运行 `python3 scripts/check_env_json.py`
       7. **如果新状态为 `ready`**：正常分析流程
       8. **如果新状态仍为 `critical`**：返回详细错误信息，建议联系开发者

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
   - **颜色美学分析**：调用 `scripts/color_analyzer.py ./filename.jpg` 获取专业的色彩美学评估（可选）
   - **IQA美学评分**（可选）：调用 `scripts/iqa_analyzer.py ./filename.jpg` 获取工业级整体美学评分（MUSIQ/NIMA模型）
   - **情感理解分析**：调用 `scripts/emotion_analyzer.py ./filename.jpg` 获取照片传达的情感（支持InternLM API）

2. **情感解读与共鸣** ⭐
   - **优先使用InternLM API**（如果配置了API Key）：获得专业摄影师视角的深度情感解读
   - API未配置时：基于色彩和场景提供基础情感分析
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
  - [scripts/color_analyzer.py](scripts/color_analyzer.py) - 颜色美学质量评估（可选）
  - [scripts/iqa_analyzer.py](scripts/iqa_analyzer.py) - IQA美学评分分析（可选，工业级美学评估）⭐ 新增
  - [scripts/emotion_analyzer.py](scripts/emotion_analyzer.py) - 情感理解与分析（可选）
  - [scripts/report_formatter.py](scripts/report_formatter.py) - 分析报告格式化输出

- **领域参考**：
  - [references/knowledge-graph.md](references/knowledge-graph.md) - 摄影知识图谱（概念关联与混合搜索）⭐ 新增
  - [references/keyword-index.md](references/keyword-index.md) - 摄影关键词索引（中英文映射与搜索优化）⭐ 新增
  - [references/composition-types.md](references/composition-types.md) - 构图类型识别与评价方法
  - [references/compositional-improvements.md](references/compositional-improvements.md) - 构图改进案例与图文指导
  - [references/evaluation-criteria.md](references/evaluation-criteria.md) - 评分标准与各维度细则
  - [references/practice-methods.md](references/practice-methods.md) - 练习方法论与学习路径设计
  - [references/emotion-analysis.md](references/emotion-analysis.md) - 情感分析与解读方法
  - [references/intrinsic-image-decomposition.md](references/intrinsic-image-decomposition.md) - Intrinsic Image Decomposition理论（深度光影分析）
  - [references/lighting-theory.md](references/lighting-theory.md) - 光影理论与摄影应用（专业光线控制）
  - [references/concert-photography.md](references/concert-photography.md) - 演唱会/现场演出摄影完全指南

- **输出资产**：
  - [assets/report-template.md](assets/report-template.md) - 分析报告标准模板

## 注意事项

- **智能体环境检查与安装（方式2：智能体通知）**：
  - **首次使用检测**：智能体在调用分析脚本时，自动检测依赖是否已安装
    - 如果检测到 ImportError（如"PyTorch未安装"）→ 判断为首次使用
    - 智能体主动通知用户：
      ```
      🔍 首次使用检测
      
      您好！这是您第一次使用本技能，系统需要自动安装必要的依赖包。
      
      需要安装的依赖：
      - 📦 PyTorch (工业级IQA美学评分)
      - 📦 TorchVision
      - 📦 scikit-image (精确色彩和谐度分析)
      - 📦 pymcdm (MCDM权重优化)
      
      预计安装时间：2-5 分钟
      ✨ 正在后台自动安装...
      ```
    - 智能体启动后台安装：`python3 scripts/install_manager.py --start`
    - 智能体监控安装进度：每30秒检查一次，实时通知用户
      ```
      ⏳ 安装进度：25% - 正在安装 scikit-image...
      ⏳ 安装进度：50% - 正在安装 PyTorch (需要时间，请耐心等待)...
      ⏳ 安装进度：75% - 正在安装 TorchVision...
      ✅ 依赖安装完成！正在为您分析照片...
      ```
  - **后续使用**：同一容器内多次使用，无需重新安装，直接分析
  - **环境检查参考**：详细流程见 [references/agent-installation-guide.md](references/agent-installation-guide.md)

- **路径使用**：用户上传的照片位于技能运行时的工作目录，脚本调用时必须使用相对路径 `./filename.jpg`
  - ✅ 正确：`python3 scripts/photo_analyzer.py ./photo.jpg`
  - ❌ 错误：`python3 scripts/photo_analyzer.py photo.jpg`（可能找不到文件）
  - ❌ 错误：`python3 scripts/photo_analyzer.py /path/to/photo.jpg`（绝对路径可能错误）
- **按需环境检查**（仅在遇到问题时使用）：
  - **正常情况下**：直接调用脚本进行照片分析，跳过环境检查
  - **遇到脚本报错时**（如"PyTorch未安装"）：
    1. 运行 `python3 scripts/smart_env_check.py` 智能环境检查
    2. 脚本会自动判断：
       - 如果缓存中有"ready"状态 → 跳过检查，直接返回缓存
       - 如果缓存中有"degraded"状态 → 跳过检查，直接返回缓存
       - 如果缓存过期或不存在 → 执行实际检查
    3. 如果检查结果为 `critical`：
       - 运行 `python3 scripts/install_manager.py --start` 启动后台安装
       - 通知用户："检测到依赖缺失，正在后台自动安装，请稍候（预计2-5分钟）"
       - 监控安装进度，等待完成
    4. 安装完成后，重新执行分析
    5. 检查结果会自动缓存1小时，避免重复检查
  - **环境检查缓存**：
    - 缓存文件：`.env_check_cache.json`
    - 缓存有效期：1小时（3600秒）
    - 强制重新检查：`python3 scripts/smart_env_check.py --force`
    - 清除缓存：`python3 scripts/smart_env_check.py --clear`
    - 跳过检查：`python3 scripts/smart_env_check.py --skip` 或设置环境变量 `PHOTO_TUTOR_SKIP_CHECK=1`
- **依赖降级方案**：
  - **IQA分析**：PyTorch未安装时，使用模拟评分（降低精确度）
  - **色彩和谐度**：scikit-image未安装时，使用简化分析（评分从80降至60）
  - **情感分析**：InternLM API未配置时，使用基础色彩和场景分析
  - **MCDM权重**：pymcdm未安装时，使用默认权重
- 充分利用智能体的图像识别和理解能力，避免过度依赖外部工具
- 评分和建议应客观公正，同时具有建设性和激励性
- **情感表达**：用温暖、共情的语言与用户交流，让建议更有温度
- **构图示例生成**：针对构图问题，智能体应生成以下类型的示意图：
  - 构图示意图（标注三分线、引导线等）
  - 改进前后对比图
  - 构图问题标注图
  - 参考改进案例文档：[references/compositional-improvements.md](references/compositional-improvements.md)
- **InternLM API推荐**：配置API Key后可获得专业摄影师视角的情感分析，效果更佳
- 练习方案应具有可操作性，符合用户的实际条件和时间安排
- 在分析过程中保持上下文简洁，仅在需要时读取参考文档
- 对于复杂的技术细节，引导用户参考 references 中的详细文档
- 颜色美学和情感分析脚本是可选增强功能，即使不可用，智能体也能基于图像理解完成核心分析
- **RAG知识库使用**：当用户询问专业理论问题（如"什么是光影层次"、"如何理解Intrinsic Image Decomposition"、"布列松的决定性瞬间"）时，优先使用混合搜索（关键词+语义）检索相关文档：
  - 构图理论：优先检索 [references/knowledge-graph.md](references/knowledge-graph.md) 和 [references/composition-types.md](references/composition-types.md)
  - 大师理论：优先检索 [references/knowledge-graph.md](references/knowledge-graph.md) 和 [references/practice-methods.md](references/practice-methods.md)
  - 光影理论：优先检索 [references/intrinsic-image-decomposition.md](references/intrinsic-image-decomposition.md) 和 [references/lighting-theory.md](references/lighting-theory.md)
  - 关键词搜索：使用 [references/keyword-index.md](references/keyword-index.md) 进行中英文关键词映射
  - **混合搜索策略**：当用户搜索"三分法"时，同时返回构图类型、评分标准、改进案例等相关内容

## 使用示例

### 示例0：环境检查（无终端访问时）

**用户输入**：
```
检查环境
```

**智能体响应（状态为READY）**：
```
🎉 环境检查通过！

所有依赖已安装，功能完整可用：
- ✅ IQA美学评分（PyTorch 2.10.0+cpu）
- ✅ 色彩分析（scikit-image 0.26.0）
- ✅ MCDM权重优化（pymcdm 1.3.1）

可以正常使用所有功能，请上传照片开始分析！
```

**智能体响应（状态为CRITICAL，自动安装）**：
```
⚠️  检测到依赖缺失

环境状态：关键依赖缺失

不可用的功能：
- ❌ IQA美学评分（PyTorch未安装）
- ❌ MCDM权重优化（pymcdm未安装）

✨ 正在后台自动安装依赖...
请稍候，预计需要2-5分钟...

[30秒后]
安装进度：20% - 正在安装 scikit-image...

[60秒后]
安装进度：50% - 正在安装 PyTorch (需要时间，请耐心等待)...

[180秒后]
✅ 依赖安装完成！

已安装：
- ✅ PyTorch 2.10.0+cpu
- ✅ TorchVision 0.25.0+cpu
- ✅ scikit-image 0.26.0
- ✅ pymcdm 1.3.1

🎉 环境检查通过！可以正常使用所有功能了。
请上传照片开始分析。
```

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

## 扩展工具说明

本技能集成了以下外部工具，增强分析能力：

- **InternLM ChatAPI**（已集成）：多模态大模型，提供专业摄影师视角的情感解读（推荐配置API Key）
  - 默认模型：internvl3.5-241b-a28b（多模态模型，图文理解能力强）
  - API地址：https://chat.intern-ai.org.cn/api/v1/
  - 获取API Key：https://internlm.intern-ai.org.cn/
- **IQA-PyTorch**（已集成）：工业级图像质量评估和美学评分库（可选，推荐启用）
  - MUSIQ模型：Google的多尺度图像质量Transformer
  - NIMA模型：Google的神经图像评估，输出分布预测
  - 用途：提供0-100的工业级美学评分，作为RAG系统的优质"判别器"
  - 安装：`pip install torch torchvision`
  - 启用：设置环境变量 `PHOTO_TUTOR_IQA_ENABLED=true`
- **Image-Color-Aesthetics-and-Quality-Assessment**：颜色美学质量评估项目，已集成到 `scripts/color_analyzer.py`
- **libcom**：构图分析标杆工具，可集成到 `scripts/photo_analyzer.py` 增强构图分析能力（可选）
- **CADB**：构图评价数据库，可作为评分基准参考（可选）

**配置InternLM API（推荐）**：
```bash
# 设置API密钥
export INTERNLM_API_KEY="sk-8cMRQdLOuoSGGztCT3SQiGR8aZqem0dcLQHncyfgltCk6wUU"

# 或者使用标准凭证格式
export COZE_INTERNLM_API_7599838351486795795="sk-8cMRQdLOuoSGGztCT3SQiGR8aZqem0dcLQHncyfgltCk6wUU"
```

**启用IQA美学评分（生产环境推荐）**：
```bash
# 安装PyTorch和TorchVision（详细安装指南见 DEPLOYMENT.md）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 启用IQA功能
export PHOTO_TUTOR_IQA_ENABLED=true
export PHOTO_TUTOR_IQA_MODEL=musiq  # 或 nima
export PHOTO_TUTOR_DEVICE=cpu  # 或 cuda
```

配置后，情感分析将自动使用InternLM API，获得专业摄影师视角的深度解读；美学评分将自动使用IQA工业级模型，获得接近人类审美的评分。

**生产环境完整部署指南**：详见 [DEPLOYMENT.md](DEPLOYMENT.md)
