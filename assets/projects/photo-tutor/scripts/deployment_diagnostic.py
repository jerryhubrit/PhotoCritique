#!/usr/bin/env python3
"""
部署环境完整诊断脚本
请将此脚本的输出结果复制并发送给开发人员
"""

import sys
import subprocess
import os
import platform
from pathlib import Path

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def print_subsection(title):
    """打印小节标题"""
    print(f"\n>>> {title}")
    print("-" * 70)

def run_command(cmd, timeout=10):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'code': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timeout',
            'code': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'code': -2
        }

def check_system_info():
    """检查系统信息"""
    print_section("系统信息")

    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"架构: {platform.machine()}")
    print(f"主机名: {platform.node()}")
    print(f"Python 版本: {sys.version}")
    print(f"Python 实现方式: {platform.python_implementation()}")
    print(f"Python 编译器: {platform.python_compiler()}")

def check_python_paths():
    """检查 Python 路径"""
    print_section("Python 路径")

    print(f"\nPython 可执行文件:")
    print(f"  {sys.executable}")

    print(f"\nPython 默认编码:")
    print(f"  {sys.getdefaultencoding()}")

    print(f"\nPython 文件系统编码:")
    print(f"  {sys.getfilesystemencoding()}")

    print(f"\nsys.path (Python 搜索路径):")
    for i, path in enumerate(sys.path, 1):
        if path:
            print(f"  {i}. {path}")

def check_pip_info():
    """检查 pip 信息"""
    print_section("pip 包列表")

    result = run_command('pip list 2>/dev/null | head -50')

    if result['success']:
        print_subsection("已安装的包（前50个）")
        print(result['stdout'])

        # 检查关键包
        print_subsection("关键包检查")
        target_packages = {
            'torch': 'PyTorch',
            'torchvision': 'TorchVision',
            'numpy': 'NumPy',
            'pillow': 'PIL/Pillow',
            'scikit-image': 'scikit-image (skimage)',
            'scikit-learn': 'scikit-learn (sklearn)',
            'pymcdm': 'pyMCDM'
        }

        for pkg_name, display_name in target_packages.items():
            result = run_command(f'pip show {pkg_name} 2>/dev/null')
            if result['success'] and result['stdout']:
                lines = result['stdout'].split('\n')
                version = 'unknown'
                location = 'unknown'
                for line in lines:
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                    elif line.startswith('Location:'):
                        location = line.split(':', 1)[1].strip()
                print(f"  ✅ {display_name:30} 版本: {version:15} 位置: {location}")
            else:
                print(f"  ❌ {display_name:30} 未安装")
    else:
        print(f"❌ 获取 pip 列表失败: {result['stderr']}")

def check_module_imports():
    """检查模块导入"""
    print_section("模块导入测试")

    test_modules = [
        ('torch', 'PyTorch'),
        ('torchvision', 'TorchVision'),
        ('torchvision.transforms', 'torchvision.transforms'),
        ('torchvision.models', 'torchvision.models'),
        ('PIL', 'PIL (Pillow)'),
        ('PIL.Image', 'PIL.Image'),
        ('numpy', 'NumPy'),
        ('skimage', 'scikit-image'),
        ('skimage.color', 'skimage.color'),
        ('sklearn', 'scikit-learn'),
        ('pymcdm', 'pyMCDM'),
    ]

    failed_imports = []

    for module_name, display_name in test_modules:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'N/A')
            file_path = getattr(module, '__file__', 'N/A')
            print(f"  ✅ {display_name:30} 版本: {version:10}  路径: {file_path[:50]}...")
        except ImportError as e:
            print(f"  ❌ {display_name:30} 失败: {str(e)[:40]}")
            failed_imports.append((module_name, display_name, str(e)))

    if failed_imports:
        print_subsection("失败的导入详情")
        for module_name, display_name, error in failed_imports:
            print(f"  模块: {module_name}")
            print(f"  显示名: {display_name}")
            print(f"  错误: {error}")
            print()

def check_pytorch_details():
    """检查 PyTorch 详细信息"""
    print_section("PyTorch 详细信息")

    try:
        import torch
        import torchvision

        print(f"PyTorch 版本: {torch.__version__}")
        print(f"TorchVision 版本: {torchvision.__version__}")
        print(f"CUDA 可用: {torch.cuda.is_available()}")

        if torch.cuda.is_available():
            print(f"CUDA 版本: {torch.version.cuda}")
            print(f"cuDNN 版本: {torch.backends.cudnn.version()}")
            print(f"GPU 数量: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
        else:
            print("默认设备: cpu")

        print(f"\nPyTorch 安装路径:")
        print(f"  {torch.__file__}")

        print(f"\nTorchVision 安装路径:")
        print(f"  {torchvision.__file__}")

    except ImportError as e:
        print(f"❌ PyTorch 导入失败: {e}")

def test_iqa_analyzer():
    """测试 IQA 分析器"""
    print_section("IQA 分析器测试")

    # 添加 scripts 目录到路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    try:
        print_subsection("导入 IQAAnalyzer")
        from iqa_analyzer import IQA_AVAILABLE

        if IQA_AVAILABLE:
            print(f"✅ IQA_AVAILABLE = True (PyTorch 可用)")
        else:
            print(f"❌ IQA_AVAILABLE = False (PyTorch 不可用)")
            print(f"   这意味着在导入 iqa_analyzer.py 时，PyTorch 导入失败")
            return

        print_subsection("初始化 IQAAnalyzer")
        from iqa_analyzer import IQAAnalyzer

        try:
            analyzer = IQAAnalyzer(model_name="musiq", device="cpu")
            print(f"✅ IQAAnalyzer 初始化成功")
            print(f"   模型名称: {analyzer.model_name}")
            print(f"   设备: {analyzer.device}")
            print(f"   模型已加载: {analyzer.model is not None}")
        except RuntimeError as e:
            print(f"❌ IQAAnalyzer 初始化失败: {e}")
        except Exception as e:
            print(f"❌ IQAAnalyzer 初始化异常: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"❌ 导入 IQAAnalyzer 失败: {e}")
        import traceback
        traceback.print_exc()

def check_environment_variables():
    """检查环境变量"""
    print_section("环境变量")

    env_vars = [
        'PATH',
        'PYTHONPATH',
        'VIRTUAL_ENV',
        'CONDA_PREFIX',
        'LD_LIBRARY_PATH',
    ]

    for var in env_vars:
        if var in os.environ:
            value = os.environ[var]
            # 截断过长的值
            if len(value) > 100:
                value = value[:100] + "..."
            print(f"{var:20} = {value}")
        else:
            print(f"{var:20} = (未设置)")

def check_disk_space():
    """检查磁盘空间"""
    print_section("磁盘空间")

    import shutil

    print_subsection("当前目录磁盘使用情况")
    try:
        total, used, free = shutil.disk_usage(os.getcwd())

        print(f"总空间: {total / (1024**3):.2f} GB")
        print(f"已使用: {used / (1024**3):.2f} GB ({used/total*100:.1f}%)")
        print(f"可用空间: {free / (1024**3):.2f} GB")
    except Exception as e:
        print(f"❌ 获取磁盘空间失败: {e}")

def check_memory():
    """检查内存"""
    print_section("内存信息")

    try:
        import psutil
        mem = psutil.virtual_memory()

        print(f"总内存: {mem.total / (1024**3):.2f} GB")
        print(f"可用内存: {mem.available / (1024**3):.2f} GB")
        print(f"已使用: {mem.used / (1024**3):.2f} GB ({mem.percent}%)")
    except ImportError:
        print("⚠️  psutil 未安装，无法获取内存信息")

def generate_summary():
    """生成总结"""
    print_section("诊断总结")

    print("\n✅ 请将此脚本的完整输出复制并发送给开发人员\n")

    print("💡 关键检查点:")
    print("   1. PyTorch 和 TorchVision 是否已安装？")
    print("   2. PyTorch 是否可以正常导入？")
    print("   3. IQA_AVAILABLE 是否为 True？")
    print("   4. IQAAnalyzer 是否可以成功初始化？")
    print()

    print("🔧 如果 IQA_AVAILABLE 为 False:")
    print("   - 检查 PyTorch 是否安装在正确的 Python 环境中")
    print("   - 重新安装 PyTorch:")
    print("     pip uninstall torch torchvision -y")
    print("     pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu")
    print()

    print("📧 联系方式:")
    print("   - 请将完整输出发送给开发人员")
    print("   - 说明问题现象（例如：IQA分析功能不可用）")
    print()

def main():
    """主函数"""
    print("\n" + "🔍 部署环境完整诊断工具".center(70, "=") + "\n")

    try:
        check_system_info()
        check_python_paths()
        check_environment_variables()
        check_pip_info()
        check_module_imports()
        check_pytorch_details()
        test_iqa_analyzer()
        check_disk_space()
        check_memory()
        generate_summary()

        print("=" * 70)
        print("✅ 诊断完成")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断诊断")
    except Exception as e:
        print(f"\n\n❌ 诊断过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
