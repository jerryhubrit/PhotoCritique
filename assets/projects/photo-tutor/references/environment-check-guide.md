# 环境检查交互式提示词

当用户需要检查部署环境时，智能体应该：

## 1. 自动运行环境检查
- 自动调用 `python3 scripts/check_env_json.py`
- 捕获输出结果

## 2. 解析检查结果
- 读取JSON格式输出
- 提取关键信息：
  - `summary.overall`: 整体状态（ready/degraded/critical）
  - `unavailable_features`: 不可用的功能列表
  - `degraded_features`: 降级的功能列表

## 3. 生成用户友好的报告

### 状态为 READY ✅
```
🎉 环境检查通过！

所有依赖已安装，功能完整可用：
- ✅ IQA美学评分（PyTorch 2.10.0+cpu）
- ✅ 色彩分析（scikit-image 0.26.0）
- ✅ MCDM权重优化（pymcdm 1.3.1）

可以正常使用所有功能，请上传照片开始分析！
```

### 状态为 DEGRADED ⚠️
```
⚠️  部分功能降级

环境状态：降级运行

可用的功能：
- ✅ 照片基础分析
- ✅ 构图分析
- ✅ 情感分析

降级的功能：
- ⚠️  色彩和谐度精确分析（使用简化版）

不可用的功能：
- ❌ IQA美学评分（PyTorch未安装）
- ❌ MCDM权重优化（pymcdm未安装）

建议：
- 可以继续使用基础功能
- 如需完整功能，请联系管理员安装缺失依赖
```

### 状态为 CRITICAL ❌
```
❌ 依赖缺失，部分核心功能不可用

环境状态：关键依赖缺失

可用的功能：
- ✅ 照片基础分析
- ⚠️  色彩分析（和谐度分析降级）

不可用的功能：
- ❌ IQA美学评分（PyTorch未安装）
- ❌ MCDM权重优化（pymcdm未安装）
- ❌ 精确色彩和谐度分析（scikit-image未安装）

缺失的依赖：
- PyTorch: 未安装
- scikit-image: 未安装
- pymcdm: 未安装

自动安装：
正在后台安装缺失依赖，请稍候（预计2-5分钟）...
安装进度监控中...
```

## 4. 自动安装机制

当状态为 CRITICAL 时：

### 步骤1：启动后台安装
```python
# 智能体执行
install_result = os.popen('python3 scripts/install_manager.py --start').read()
```

### 步骤2：通知用户
```
检测到依赖缺失，正在后台自动安装...

安装进度：
- 📦 检查依赖
- 📦 安装 scikit-image
- 📦 安装 pymcdm
- 📦 安装 PyTorch (需要时间，请耐心等待...)
- 📦 安装 TorchVision

预计需要：2-5分钟
请稍候，安装完成后将自动继续...
```

### 步骤3：定期检查进度
```python
# 每30秒检查一次
while installing:
    status = json.loads(os.popen('python3 scripts/install_manager.py --check').read())
    if status['installing']:
        progress = status['status']['progress']
        message = status['status']['message']
        notify_user(f"安装进度：{progress}% - {message}")
    else:
        installing = False
        break
```

### 步骤4：安装完成
```
✅ 依赖安装完成！

已安装：
- ✅ PyTorch 2.10.0+cpu
- ✅ TorchVision 0.25.0+cpu
- ✅ scikit-image 0.26.0
- ✅ pymcdm 1.3.1

正在重新检查环境...
环境状态：✅ READY

现在可以正常使用所有功能了！请上传照片开始分析。
```

## 5. 用户触发环境检查的方式

### 方式1：直接询问
用户："检查环境" 或 "环境怎么样"

### 方式2：上传照片时自动触发
用户上传照片 → 智能体先检查环境 → 再分析照片

### 方式3：首次使用时自动触发
首次调用技能 → 自动检查环境 → 提示用户

## 6. 输出格式

### 标准输出（JSON，便于智能体解析）
```json
{
  "summary": {
    "overall": "ready",
    "iqa_available": true,
    "color_analysis_available": true,
    "mcdm_available": true
  }
}
```

### 标准错误（人类可读，便于用户查看）
```
======================================================================
🔍 环境检查报告
======================================================================

📋 Python 版本: 3.13.11
📍 Python 路径: /usr/bin/python3

📦 依赖包状态:
  ✅ pytorch              版本: 2.10.0+cpu
  ✅ torchvision          版本: 0.25.0+cpu
  ✅ scikit_image         版本: 0.26.0
  ✅ scikit_learn         版本: 1.8.0
  ✅ pym备cdm             版本: unknown
  ✅ pillow               版本: 12.1.0

🎯 功能可用性:
  IQA分析:          ✅ 可用
  色彩分析:         ✅ 可用
  MCDM权重优化:     ✅ 可用

📊 整体状态: READY
======================================================================
```

## 7. 错误处理

### 安装失败
```
❌ 依赖安装失败

失败原因：
- PyTorch 安装超时
- 网络连接失败
- 磁盘空间不足

建议：
1. 检查网络连接
2. 检查磁盘空间（至少需要625MB）
3. 联系管理员手动安装

诊断信息：
运行：python3 scripts/deployment_diagnostic.py
将结果发送给开发人员分析
```

### 环境检查失败
```
❌ 环境检查失败

错误信息：[具体错误]

可能的原因：
- Python版本不兼容（需要3.6+）
- 权限问题
- 脚本文件损坏

建议：
请联系管理员检查部署环境配置
```
