#!/usr/bin/env python3
"""
环境诊断脚本
检查 PyTorch 和其他依赖的安装状态
"""

import sys
import subprocess
import os

def check_python_info():
    """检查 Python 信息"""
    print("=" * 60)
    print("📋 Python 环境信息")
    print("=" * 60)
    print(f"Python 版本: {sys.version}")
    print(f"Python 路径: {sys.executable}")
    print(f"Python 默认编码: {sys.getdefaultencoding()}")
    print()

def check_dependencies():
    """检查依赖安装状态"""
    print("=" * 60)
    print("📦 依赖包检查")
    print("=" * 60)
    
    dependencies = [
        ('torch', 'PyTorch'),
        ('torchvision', 'TorchVision'),
        ('numpy', 'NumPy'),
        ('pillow', 'Pillow'),
        ('scikit-image', 'scikit-image'),
        ('scikit-learn', 'scikit-learn'),
        ('pymcdm', 'pyMCDM'),
    ]
    
    for module_name, display_name in dependencies:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {display_name:20} - 版本: {version}")
        except ImportError as e:
            print(f"❌ {display_name:20} - 未安装 ({e})")
    
    print()

def check_torch_info():
    """检查 PyTorch 详细信息"""
    print("=" * 60)
    print("🔥 PyTorch 详细信息")
    print("=" * 60)
    
    try:
        import torch
        import torchvision
        
        print(f"PyTorch 版本: {torch.__version__}")
        print(f"TorchVision 版本: {torchvision.__version__}")
        print(f"CUDA 可用: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA 版本: {torch.version.cuda}")
            print(f"GPU 数量: {torch.cuda.device_count()}")
            print(f"GPU 名称: {torch.cuda.get_device_name(0)}")
        else:
            print(f"默认设备: cpu")
        
        print(f"PyTorch 安装路径: {torch.__file__}")
        print(f"TorchVision 安装路径: {torchvision.__file__}")
        
    except ImportError as e:
        print(f"❌ PyTorch 导入失败: {e}")
    
    print()

def check_pip_info():
    """检查 pip 信息"""
    print("=" * 60)
    print("📥 pip 包列表")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            ['pip', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            packages = result.stdout.split('\n')
            
            # 筛选相关包
            target_packages = ['torch', 'torchvision', 'numpy', 'pillow', 'scikit', 'pymcdm']
            
            print("已安装的相关包:")
            for pkg in packages:
                pkg_lower = pkg.lower()
                for target in target_packages:
                    if target in pkg_lower:
                        print(f"  - {pkg}")
                        break
        else:
            print(f"❌ pip list 执行失败: {result.stderr}")
    
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    
    print()

def check_site_packages():
    """检查 site-packages 目录"""
    print("=" * 60)
    print("📁 site-packages 目录")
    print("=" * 60)
    
    try:
        site_packages = subprocess.run(
            [sys.executable, '-m', 'site', '--user-site'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if site_packages.returncode == 0:
            print(f"用户 site-packages: {site_packages.stdout.strip()}")
        
        system_site = subprocess.run(
            [sys.executable, '-m', 'site'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if system_site.returncode == 0:
            print(f"\n系统 site-packages:")
            for line in system_site.stdout.split('\n'):
                if 'site-packages' in line and 'dist-packages' in line:
                    print(f"  - {line.strip()}")
    
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    
    print()

def main():
    """主函数"""
    print("\n" + "🔍 环境诊断工具".center(60, "=") + "\n")
    
    check_python_info()
    check_dependencies()
    check_torch_info()
    check_pip_info()
    check_site_packages()
    
    print("=" * 60)
    print("✅ 诊断完成")
    print("=" * 60)
    print()
    print("💡 建议:")
    print("   1. 如果 PyTorch 显示未安装，请运行:")
    print("      pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu")
    print()
    print("   2. 如果 PyTorch 已安装但脚本仍报错，请检查:")
    print("      - 是否在正确的 Python 环境中运行")
    print("      - 是否有多个 Python 版本冲突")
    print("      - PyTorch 是否安装在正确的 site-packages 目录")
    print()

if __name__ == '__main__':
    main()
