# 摄影知识图谱

## 目录
- [构图理论](#构图理论)
- [光影理论](#光影理论)
- [色彩理论](#色彩理论)
- [美学理论](#美学理论)
- [大师理论](#大师理论)
- [知识关联](#知识关联)

---

## 构图理论

### 核心概念

#### 三分法（Rule of Thirds）
- **定义**：将画面用两条横线和两条竖线分为九等分，将主体放在交叉点上
- **理论基础**：黄金分割（Golden Ratio）的简化版
- **相关文档**：[composition-types.md](composition-types.md)
- **大师**：布列松（Henri Cartier-Bresson）、安塞尔·亚当斯（Ansel Adams）
- **应用场景**：风景摄影、人像摄影、街拍
- **相关概念**：
  - 黄金分割（Golden Ratio）
  - 视觉引导（Visual Leading）
  - 视觉平衡（Visual Balance）
  - 负空间（Negative Space）

#### 黄金分割（Golden Ratio）
- **定义**：准确数值是(√5-1)/2 ≈ 0.618
- **理论基础**：自然美学定律，广泛存在于自然界
- **相关文档**：[composition-types.md](composition-types.md)、[intrinsic-image-decomposition.md](intrinsic-image-decomposition.md)
- **大师**：斐波那契（Fibonacci）、达芬奇（Leonardo da Vinci）
- **应用场景**：构图设计、色彩搭配、比例控制
- **相关概念**：
  - 斐波那契数列（Fibonacci Sequence）
  - 螺旋线（Spiral）
  - 三分法（Rule of Thirds）
  - 构图美学（Composition Aesthetics）

#### 视觉引导（Visual Leading）
- **定义**：利用线条、形状、色彩引导观众视线
- **理论基础**：视觉心理学、格式塔心理学
- **相关文档**：[composition-types.md](composition-types.md)、[compositional-improvements.md](compositional-improvements.md)
- **大师**：布列松（Henri Cartier-Bresson）
- **应用场景**：街拍、风景、建筑
- **相关概念**：
  - 引导线（Leading Lines）
  - 视觉路径（Visual Path）
  - 焦点（Focal Point）
  - 视觉流动（Visual Flow）

#### 负空间（Negative Space）
- **定义**：主体周围的空白区域，用于突出主体
- **理论基础**：极简主义美学、视觉重量理论
- **相关文档**：[composition-types.md](composition-types.md)、[compositional-improvements.md](compositional-improvements.md)
- **大师**：艾略特·厄威特（Elliott Erwitt）
- **应用场景**：极简摄影、建筑、人像
- **相关概念**：
  - 留白（White Space）
  - 视觉平衡（Visual Balance）
  - 极简主义（Minimalism）
  - 呼吸感（Breathing Room）

#### 视觉平衡（Visual Balance）
- **定义**：画面左右、上下的视觉重量分布均衡
- **理论基础**：视觉心理学、构图美学
- **相关文档**：[composition-types.md](composition-types.md)、[evaluation-criteria.md](evaluation-criteria.md)
- **大师**：安塞尔·亚当斯（Ansel Adams）
- **应用场景**：风景、建筑、静物
- **相关概念**：
  - 对称（Symmetry）
  - 渐变平衡（Asymmetric Balance）
  - 视觉重量（Visual Weight）
  - 构图平衡（Composition Balance）

---

## 光影理论

### 核心概念

#### Intrinsic Image Decomposition（内在图像分解）
- **定义**：观察图像 = 反照率 × 光照（I = R × L）
- **理论基础**：计算机视觉、物理学
- **相关文档**：[intrinsic-image-decomposition.md](intrinsic-image-decomposition.md)
- **应用**：理解光影本质、诊断光线问题
- **相关概念**：
  - 反照率（Albedo）：物体固有颜色
  - 光照（Shading）：光线产生的亮度变化
  - 立体感（Depth Perception）
  - 光线层次（Lighting Layers）

#### 光线方向（Lighting Direction）
- **定义**：光线相对于相机的照射方向
- **理论基础**：光学、摄影美学
- **相关文档**：[lighting-theory.md](lighting-theory.md)、[concert-photography.md](concert-photography.md)
- **类型**：
  - 顺光（Front Light）
  - 侧光（Side Light）
  - 逆光（Back Light）
  - 顶光（Top Light）
- **相关概念**：
  - 立体感（Depth）
  - 阴影（Shadow）
  - 轮廓光（Rim Light）
  - 剪影（Silhouette）

#### 光线质感（Lighting Quality）
- **定义**：光线的柔和或坚硬程度
- **理论基础**：光学、摄影美学
- **相关文档**：[lighting-theory.md](lighting-theory.md)、[concert-photography.md](concert-photography.md)
- **类型**：
  - 硬光（Hard Light）：方向性强，阴影清晰
  - 柔光（Soft Light）：方向性弱，阴影柔和
- **相关概念**：
  - 阴影硬度（Shadow Hardness）
  - 氛围（Atmosphere）
  - 戏剧性（Drama）
  - 梦幻感（Dreamy）

#### 光影层次（Lighting Layers）
- **定义**：画面中不同层次的明暗变化
- **理论基础**：Intrinsic Image Decomposition、摄影美学
- **相关文档**：[intrinsic-image-decomposition.md](intrinsic-image-decomposition.md)、[lighting-theory.md](lighting-theory.md)
- **应用**：创造立体感、丰富画面层次
- **相关概念**：
  - 明暗对比（Contrast）
  - 立体感（Depth）
  - 空间感（Space）
  - 层次感（Layering）

---

## 色彩理论

### 核心概念

#### 调色板（Color Palette）
- **定义**：照片中使用的颜色集合
- **理论基础**：色彩心理学、色彩理论
- **相关文档**：[scripts/color_analyzer.py](../scripts/color_analyzer.py)、[emotion-analysis.md](emotion-analysis.md)
- **分析**：提取5个主色调
- **相关概念**：
  - 主色调（Dominant Colors）
  - 色彩分布（Color Distribution）
  - 色彩比例（Color Proportions）
  - 色彩搭配（Color Combination）

#### 色彩和谐度（Color Harmony）
- **定义**：颜色搭配的和谐程度
- **理论基础**：色彩理论、色彩心理学
- **相关文档**：[scripts/color_analyzer.py](../scripts/color_analyzer.py)、[evaluation-criteria.md](evaluation-criteria.md)
- **类型**：
  - 单色系（Monochromatic）
  - 类似色系（Analogous）
  - 互补色系（Complementary）
  - 分裂互补色系（Split Complementary）
  - 三分色系（Triadic）
- **相关概念**：
  - 色彩理论（Color Theory）
  - 色彩心理学（Color Psychology）
  - 色彩搭配（Color Scheme）
  - 色彩美学（Color Aesthetics）

#### 色彩心理学（Color Psychology）
- **定义**：色彩对人类心理的影响
- **理论基础**：心理学、色彩理论
- **相关文档**：[scripts/color_analyzer.py](../scripts/color_analyzer.py)、[emotion-analysis.md](emotion-analysis.md)
- **主要颜色**：
  - 暖色调（Warm）：红色、橙色、黄色 → 温暖、活力、激情
  - 冷色调（Cool）：蓝色、绿色、紫色 → 冷静、理性、忧郁
  - 中性色（Neutral）：白色、黑色、灰色 → 纯净、力量、沉稳
- **相关概念**：
  - 色彩情绪（Color Emotion）
  - 色彩象征（Color Symbolism）
  - 色彩文化（Color Culture）
  - 情感表达（Emotional Expression）

#### 色彩情感（Color Emotion）
- **定义**：色彩传达的情绪和情感
- **理论基础**：色彩心理学、情感理论
- **相关文档**：[scripts/color_analyzer.py](../scripts/color_analyzer.py)、[emotion-analysis.md](emotion-analysis.md)
- **应用**：情感表达、氛围营造
- **相关概念**：
  - 暖色调情感（Warm Color Emotion）
  - 冷色调情感（Cool Color Emotion）
  - 色彩强度（Color Intensity）
  - 情绪传达（Emotion Conveyance）

---

## 美学理论

### 核心概念

#### 情感表达（Emotional Expression）
- **定义**：照片传达的情绪和情感
- **理论基础**：心理学、美学理论
- **相关文档**：[emotion-analysis.md](emotion-analysis.md)、[evaluation-criteria.md](evaluation-criteria.md)
- **维度**：
  - 情感明确度（Emotion Clarity）
  - 共鸣强度（Resonance Intensity）
  - 感染力（Infectiousness）
  - 故事性（Storytelling）
- **相关概念**：
  - 情感共鸣（Emotional Resonance）
  - 情感深度（Emotional Depth）
  - 情感层次（Emotional Layers）
  - 情感符号（Emotional Symbols）

#### 情感共鸣（Emotional Resonance）
- **定义**：照片引发观众情感共鸣的能力
- **理论基础**：心理学、美学理论
- **相关文档**：[emotion-analysis.md](emotion-analysis.md)、[evaluation-criteria.md](evaluation-criteria.md)
- **要素**：
  - 共同经历（Shared Experience）
  - 情感触发（Emotional Trigger）
  - 视觉冲击（Visual Impact）
  - 故事性（Storytelling）
- **相关概念**：
  - 情感连接（Emotional Connection）
  - 共情（Empathy）
  - 感染力（Infectiousness）
  - 情感传达（Emotion Conveyance）

#### 视觉美学（Visual Aesthetics）
- **定义**：照片的视觉美感
- **理论基础**：美学理论、视觉心理学
- **相关文档**：[evaluation-criteria.md](evaluation-criteria.md)、[scripts/color_analyzer.py](../scripts/color_analyzer.py)
- **维度**：
  - 构图美学（Composition Aesthetics）
  - 色彩美学（Color Aesthetics）
  - 光影美学（Lighting Aesthetics）
  - 创意美学（Creativity Aesthetics）
- **相关概念**：
  - 美学评分（Aesthetics Score）
  - 美学理论（Aesthetics Theory）
  - 视觉愉悦（Visual Pleasure）
  - 美学价值（Aesthetic Value）

#### 创意美学（Creativity Aesthetics）
- **定义**：照片的创意和独特性
- **理论基础**：创意理论、美学理论
- **相关文档**：[evaluation-criteria.md](evaluation-criteria.md)、[practice-methods.md](practice-methods.md)
- **维度**：
  - 视角独特度（Perspective Uniqueness）
  - 构图创新度（Composition Innovation）
  - 表现手法新颖度（Expression Novelty）
  - 风格化程度（Stylistic Distinctiveness）
- **相关概念**：
  - 创意思维（Creative Thinking）
  - 艺术性（Artistry）
  - 个性表达（Personal Expression）
  - 独特视角（Unique Perspective）

---

## 大师理论

### 核心概念

#### 决定性瞬间（The Decisive Moment）
- **定义**：摄影中决定性的瞬间，人物、光线、构图完美结合的时刻
- **大师**：亨利·卡蒂埃-布列松（Henri Cartier-Bresson）
- **相关文档**：[practice-methods.md](practice-methods.md)、[composition-types.md](composition-types.md)
- **核心思想**：
  - 时机把握（Timing）
  - 构图美学（Composition Aesthetics）
  - 情感捕捉（Emotion Capture）
  - 瞬间永恒（Moment Eternity）
- **应用**：街拍、纪实摄影
- **相关概念**：
  - 时机把握（Timing）
  - 瞬间捕捉（Moment Capture）
  - 街拍（Street Photography）
  - 纪实摄影（Documentary Photography）

#### 区域曝光法（Zone System）
- **定义**：一种精确控制曝光的方法，将影调分为11个区域
- **大师**：安塞尔·亚当斯（Ansel Adams）
- **相关文档**：[lighting-theory.md](lighting-theory.md)、[evaluation-criteria.md](evaluation-criteria.md)
- **核心思想**：
  - 精确曝光（Precise Exposure）
  - 影调控制（Tone Control）
  - 黑白摄影（Black and White Photography）
  - 后期处理（Post-processing）
- **应用**：黑白摄影、风光摄影
- **相关概念**：
  - 曝光控制（Exposure Control）
  - 影调范围（Tone Range）
  - 动态范围（Dynamic Range）
  - 黑白美学（Black and White Aesthetics）

---

## 知识关联

### 构图 → 光影
- 三分法 → 光线方向（配合使用）
- 视觉引导 → 侧光/逆光（利用光线引导）
- 负空间 → 柔光（营造氛围）
- 视觉平衡 → 明暗对比（平衡画面）

### 光影 → 色彩
- 光线方向 → 色彩饱和度（影响色彩表现）
- 光线质感 → 色彩情绪（硬光=戏剧性，柔光=温馨）
- 光影层次 → 色彩和谐度（层次影响和谐）
- 光线类型 → 色彩心理学（暖光=温暖，冷光=冷静）

### 色彩 → 情感
- 色彩心理学 → 情感表达（色彩决定情绪）
- 调色板 → 情感共鸣（色彩搭配影响共鸣）
- 色彩和谐度 → 情感深度（和谐度影响深度）
- 色彩强度 → 情感感染力（强度影响感染力）

### 构图 → 情感
- 视觉引导 → 情感明确度（引导影响情感传达）
- 视觉平衡 → 情感稳定性（平衡影响情感稳定）
- 负空间 → 情感呼吸感（留白影响情感呼吸）
- 构图美学 → 情感美学（构图美学影响情感美学）

### 光影 → 情感
- 光线方向 → 情绪类型（侧光=立体，逆光=神秘）
- 光线质感 → 情感氛围（硬光=戏剧性，柔光=温馨）
- 光影层次 → 情感深度（层次影响深度）
- 光线时机 → 情感瞬间（黄金时刻=温暖）

### 构图 → 创意
- 视角独特度 → 创意美学（视角影响创意）
- 构图创新度 → 艺术性（创新影响艺术性）
- 视觉引导 → 表现手法（引导影响手法）
- 负空间 → 个性表达（留白影响表达）

### 色彩 → 创意
- 色彩搭配 → 创意美学（搭配影响创意）
- 色彩和谐度 → 艺术性（和谐度影响艺术性）
- 色彩心理学 → 个性表达（心理学影响表达）
- 调色板 → 风格化（调色板影响风格）

### 大师理论关联

#### 布列松（Henri Cartier-Bresson）
- 决定性瞬间 → 时机把握
- 街拍 → 视觉引导
- 构图美学 → 三分法、视觉平衡

#### 亚当斯（Ansel Adams）
- 区域曝光法 → 曝光控制
- 黑白摄影 → 色彩美学
- 风光摄影 → 构图美学、光影层次

---

## 知识网络

### 构图网络
```
三分法 → 黄金分割 → 构图美学
  ↓         ↓          ↓
视觉引导 → 视觉平衡 → 负空间
  ↓         ↓          ↓
街拍应用  风景应用  人像应用
```

### 光影网络
```
光线方向 → 光线质感 → 光影层次
  ↓         ↓          ↓
立体感   氛围营造   明暗对比
  ↓         ↓          ↓
Intrinsic Image Decomposition → 光线理论
```

### 色彩网络
```
调色板 → 色彩和谐度 → 色彩心理学
  ↓         ↓             ↓
色彩搭配  色彩理论    色彩情感
  ↓         ↓             ↓
色彩美学  情感共鸣   情感表达
```

### 情感网络
```
情感明确度 → 共鸣强度 → 感染力
    ↓           ↓          ↓
情感深度   情感连接   故事性
    ↓           ↓          ↓
情感美学   情感符号   情感层次
```

---

## 搜索优化

### 关键词映射

当用户搜索"三分法"时：
- 主要结果：[composition-types.md](composition-types.md)
- 相关结果：
  - [evaluation-criteria.md](evaluation-criteria.md)（评分标准）
  - [compositional-improvements.md](compositional-improvements.md)（改进案例）
  - [knowledge-graph.md](knowledge-graph.md)（知识图谱）

当用户搜索"布列松的决定性瞬间"时：
- 主要结果：[knowledge-graph.md](knowledge-graph.md)（大师理论）
- 相关结果：
  - [practice-methods.md](practice-methods.md)（练习方法）
  - [composition-types.md](composition-types.md)（构图类型）
  - [emotion-analysis.md](emotion-analysis.md)（情感分析）

当用户搜索"黄金分割"时：
- 主要结果：[knowledge-graph.md](knowledge-graph.md)（构图理论）
- 相关结果：
  - [composition-types.md](composition-types.md)（构图类型）
  - [intrinsic-image-decomposition.md](intrinsic-image-decomposition.md)（光影理论）

当用户搜索"Intrinsic Image Decomposition"时：
- 主要结果：[intrinsic-image-decomposition.md](intrinsic-image-decomposition.md)
- 相关结果：
  - [lighting-theory.md](lighting-theory.md)（光影理论）
  - [evaluation-criteria.md](evaluation-criteria.md)（评分标准）

当用户搜索"色彩心理学"时：
- 主要结果：[scripts/color_analyzer.py](../scripts/color_analyzer.py)
- 相关结果：
  - [emotion-analysis.md](emotion-analysis.md)（情感分析）
  - [evaluation-criteria.md](evaluation-criteria.md)（评分标准）

---

## 总结

本知识图谱旨在建立摄影各概念之间的关联，帮助智能体通过混合搜索（关键词+语义）找到最相关的知识。

**核心目标**：
1. 建立概念之间的关联
2. 提供大师理论和应用
3. 支持混合搜索
4. 提升检索准确性

**使用建议**：
- 当用户搜索"三分法"时，返回构图相关内容
- 当用户搜索"布列松"时，返回大师理论
- 当用户搜索"Intrinsic Image Decomposition"时，返回光影理论
- 当用户搜索"情感表达"时，返回美学理论

**知识覆盖**：
- 构图理论：三分法、黄金分割、视觉引导、负空间、视觉平衡
- 光影理论：Intrinsic Image Decomposition、光线方向、光线质感、光影层次
- 色彩理论：调色板、色彩和谐度、色彩心理学、色彩情感
- 美学理论：情感表达、情感共鸣、视觉美学、创意美学
- 大师理论：决定性瞬间、区域曝光法
