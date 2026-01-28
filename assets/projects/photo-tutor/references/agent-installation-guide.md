# 智能体环境检查与安装指南

## 触发场景

智能体在以下情况会自动检查环境：

1. **首次使用技能**：用户第一次上传照片或询问分析
2. **遇到脚本错误**：调用脚本时报"PyTorch未安装"等错误
3. **用户主动询问**：用户说"检查环境"或"环境怎么样"

## 智能体操作流程

### 情况1：首次使用（全新部署）

**智能体检测**：
```
用户上传照片
    ↓
智能体尝试调用分析脚本
    ↓
检测到错误：PyTorch未安装
    ↓
判断：这是首次使用，环境需要初始化
```

**智能体通知**：
```
🔍 首次使用检测

您好！这是您第一次使用本技能，系统需要自动安装必要的依赖包。

需要安装的依赖：
- 📦 PyTorch (工业级IQA美学评分）
- 📦 TorchVision
- 📦 scikit-image (精确色彩和谐度分析)
- 📦 pymcdm (MCDM权重优化)

预计安装时间：2-5 分钟
(主要是 PyTorch 的安装需要时间，请耐心等待)

✨ 正在后台自动安装...
您可以先浏览一下，安装完成后会自动继续分析。
```

**后台安装流程**：
```python
# 智能体执行
import subprocess

# 启动后台安装
subprocess.run('python3 scripts/install_manager.py --start', shell=True)

# 通知用户
notify_user("✨ 正在后台自动安装依赖...")

# 每30秒检查一次进度
import time
while True:
    status = check_install_progress()
    if status['installing']:
        progress = status['progress']
        message = status['message']
        notify_user(f"⏳ 安装进度：{progress}% - {message}")
    else:
        break
    time.sleep(30)

# 安装完成
notify_user("✅ 依赖安装完成！正在为您分析照片...")
```

**进度通知示例**：
```
智能体：⏳ 安装进度：25% - 正在安装 scikit-image...

[30秒后]
智能体：⏳ 安装进度：50% - 正在安装 PyTorch (需要时间，请耐心等待)...

[60秒后]
智能体：⏳ 安装进度：75% - 正在安装 TorchVision...

[90秒后]
智能体：✅ 依赖安装完成！正在为您分析照片...
```

### 情况2：后续使用（同一容器）

**智能体检测**：
```
用户上传照片
    ↓
智能体尝试调用分析脚本
    ↓
调用成功（依赖已安装）
    ↓
判断：依赖正常，直接分析
```

**智能体通知**：
```
✅ 环境就绪

依赖已安装，正在为您分析照片...
```

**无需通知，直接分析**。

### 情况3：环境已就绪（检查）

**智能体检测**：
```python
# 智能体主动检查（可选）
import subprocess
result = subprocess.run('python3 scripts/check_env_json.py', shell=True, capture_output=True)
env_status = json.loads(result.stdout)

if env_status['summary']['overall'] == 'ready':
    # 环境正常
    print("✅ 所有依赖已安装，可以直接使用！")
else:
    # 需要安装
    print("⚠️  需要安装依赖...")
```

**智能体通知**：
```
✅ 环境检查完成

所有依赖已安装，功能完整可用：
- ✅ IQA美学评分（PyTorch 2.10.0+cpu）
- ✅ 色彩分析（scikit-image 0.26.0）
- ✅ MCDM权重优化（pymcdm 1.3.1）

可以正常使用所有功能，请上传照片开始分析！
```

### 情况4：安装失败

**智能体检测**：
```python
status = check_install_progress()
if not status['installing'] and status['status']['status'] == 'failed':
    # 安装失败
    handle_installation_failure()
```

**智能体通知**：
```
❌ 依赖安装失败

抱歉，依赖安装遇到了问题：

可能的原因：
- 网络连接不稳定
- 磁盘空间不足
- PyTorch 下载超时

建议：
1. 请检查网络连接
2. 稍后重试（重新上传照片）
3. 如果问题持续，请联系管理员

您仍然可以使用基础功能进行照片分析（部分高级功能可能不可用）。
```

## 智能体代码示例

### 示例1：首次使用自动安装

```python
def check_and_install_dependencies():
    """检查并安装依赖"""
    # 尝试导入 PyTorch
    try:
        import torch
        return {'installed': True, 'message': '依赖已安装'}
    except ImportError:
        return {'installed': False, 'message': 'PyTorch未安装'}

# 智能体在用户上传照片时调用
result = check_and_install_dependencies()

if not result['installed']:
    # 首次使用，需要安装
    print("🔍 首次使用检测")
    print("需要安装依赖：PyTorch, TorchVision, scikit-image, pymcdm")
    print("预计时间：2-5 分钟")
    print("✨ 正在后台自动安装...")
    
    # 启动后台安装
    import subprocess
    subprocess.Popen('python3 scripts/install_manager.py --start', shell=True)
    
    # 通知用户可以等待
    print("您可以先浏览一下，安装完成后会自动继续分析。")
else:
    # 依赖已安装，直接分析
    print("✅ 依赖已安装，正在分析照片...")
```

### 示例2：监控安装进度

```python
def monitor_installation():
    """监控安装进度"""
    import subprocess
    import json
    import time

    last_progress = -1

    while True:
        # 检查安装状态
        result = subprocess.run(
            'python3 scripts/install_manager.py --check',
            shell=True,
            capture_output=True,
            text=True
        )

        try:
            status = json.loads(result.stdout)
        except:
            break

        if not status['installing']:
            # 安装完成或失败
            print(f"✅ 安装{'完成' if status['status']['status'] == 'completed' else '失败'}")
            break

        # 显示进度（只在变化时通知）
        progress = status['status']['progress']
        if progress > last_progress:
            message = status['status']['message']
            print(f"⏳ 安装进度：{progress}% - {message}")
            last_progress = progress

        # 等待30秒
        time.sleep(30)
```

### 示例3：安装完成后继续分析

```python
def analyze_photo(photo_path: str):
    """分析照片"""
    # 检查依赖
    result = check_and_install_dependencies()

    if not result['installed']:
        # 需要安装
        print("正在安装依赖，请稍候...")
        monitor_installation()

        # 重新检查
        result = check_and_install_dependencies()
        if not result['installed']:
            print("❌ 安装失败，请联系管理员")
            return

    # 依赖已安装，开始分析
    print("✅ 依赖就绪，正在分析照片...")
    # ... 执行分析逻辑
```

## 用户交互示例

### 完整首次使用流程

```
用户：[上传照片.jpg]

智能体：🔍 首次使用检测

您好！这是您第一次使用本技能，系统需要自动安装必要的依赖包。

需要安装的依赖：
- 📦 PyTorch (工业级IQA美学评分)
- 📦 TorchVision
- 📦 scikit-image (精确色彩和谐度分析)
- 📦 pymcdm (MCDM权重优化)

预计安装时间：2-5 分钟
✨ 正在后台自动安装...
您可以先浏览一下，安装完成后会自动继续分析。

[30秒后]
智能体：⏳ 安装进度：25% - 正在安装 scikit-image...

[30秒后]
智能体：⏳ 安装进度：50% - 正在安装 PyTorch (需要时间，请耐心等待)...

[60秒后]
智能体：⏳ 安装进度：75% - 正在安装 TorchVision...

[30秒后]
智能体：✅ 依赖安装完成！正在为您分析照片...

智能体：[开始分析照片...]

智能体：📊 照片分析报告

[分析结果...]
```

### 后续使用流程

```
用户：[上传照片.jpg]

智能体：✅ 依赖已安装，正在分析照片...

智能体：[开始分析照片...]

智能体：📊 照片分析报告

[分析结果...]
```

### 用户主动检查

```
用户：检查环境

智能体：✅ 环境检查完成

所有依赖已安装，功能完整可用：
- ✅ IQA美学评分（PyTorch 2.10.0+cpu）
- ✅ 色彩分析（scikit-image 0.26.0）
- ✅ MCDM权重优化（pymcdm 1.3.1）

可以正常使用所有功能，请上传照片开始分析！
```

## 智能体实现要点

### 1. 自动检测
- 尝试导入依赖 → 判断是否安装
- 捕获脚本错误 → 检测依赖缺失

### 2. 智能通知
- 首次使用：明确告知需要安装，预计时间
- 安装过程：实时通知进度（每30秒）
- 安装完成：自动继续分析

### 3. 用户友好
- 解释原因（首次使用需要初始化）
- 提供预期（安装时间、功能说明）
- 减少焦虑（可以等待，不阻塞）

### 4. 错误处理
- 安装失败：清晰说明原因和建议
- 降级方案：基础功能仍可用
- 重试机制：支持用户重新上传触发重试
