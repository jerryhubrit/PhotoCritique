#!/usr/bin/env python3
"""
IQA分析器导入测试脚本
测试 PyTorch 和 IQAAnalyzer 的导入过程
"""

import sys
import os

def test_imports_step_by_step():
    """逐步测试导入"""
    print("=" * 60)
    print("🧪 IQAAnalyzer 导入测试")
    print("=" * 60)
    print()

    # 步骤 1: 测试 torch 导入
    print("步骤 1/5: 测试 torch 导入")
    try:
        import torch
        print(f"  ✅ torch 导入成功 (版本: {torch.__version__})")
        print(f"  📍 torch 路径: {torch.__file__}")
    except ImportError as e:
        print(f"  ❌ torch 导入失败: {e}")
        return False
    print()

    # 步骤 2: 测试 torchvision 导入
    print("步骤 2/5: 测试 torchvision 导入")
    try:
        import torchvision
        print(f"  ✅ torchvision 导入成功 (版本: {torchvision.__version__})")
        print(f"  📍 torchvision 路径: {torchvision.__file__}")
    except ImportError as e:
        print(f"  ❌ torchvision 导入失败: {e}")
        return False
    print()

    # 步骤 3: 测试 torchvision.transforms 导入
    print("步骤 3/5: 测试 torchvision.transforms 导入")
    try:
        import torchvision.transforms as transforms
        print(f"  ✅ torchvision.transforms 导入成功")
        print(f"  📍 transforms 类型: {type(transforms)}")
    except ImportError as e:
        print(f"  ❌ torchvision.transforms 导入失败: {e}")
        return False
    print()

    # 步骤 4: 测试 torchvision.models 导入
    print("步骤 4/5: 测试 torchvision.models 导入")
    try:
        import torchvision.models as models
        print(f"  ✅ torchvision.models 导入成功")
        print(f"  📍 models 类型: {type(models)}")
    except ImportError as e:
        print(f"  ❌ torchvision.models 导入失败: {e}")
        return False
    print()

    # 步骤 5: 测试 PIL 导入
    print("步骤 5/5: 测试 PIL.Image 导入")
    try:
        from PIL import Image
        print(f"  ✅ PIL.Image 导入成功")
        print(f"  📍 Image 模块: {Image}")
    except ImportError as e:
        print(f"  ❌ PIL.Image 导入失败: {e}")
        print(f"  💡 提示: Pillow 的导入名称是 'PIL'，不是 'pillow'")
        return False
    print()

    # 总结
    print("=" * 60)
    print("✅ 所有导入测试通过")
    print("=" * 60)
    print()
    return True

def test_iqa_analyzer_init():
    """测试 IQAAnalyzer 初始化"""
    print("=" * 60)
    print("🚀 IQAAnalyzer 初始化测试")
    print("=" * 60)
    print()

    try:
        # 导入 IQAAnalyzer
        sys.path.insert(0, 'scripts')
        from iqa_analyzer import IQAAnalyzer

        print("步骤 1/3: 导入 IQAAnalyzer 类")
        print(f"  ✅ IQAAnalyzer 导入成功")
        print(f"  📍 IQAAnalyzer 路径: {IQAAnalyzer.__module__}")
        print()

        # 检查 IQA_AVAILABLE 标志
        print("步骤 2/3: 检查 IQA_AVAILABLE 标志")
        from iqa_analyzer import IQA_AVAILABLE
        if IQA_AVAILABLE:
            print(f"  ✅ IQA_AVAILABLE = True (PyTorch 可用)")
        else:
            print(f"  ❌ IQA_AVAILABLE = False (PyTorch 不可用)")
            print(f"  💡 这意味着在导入时，PyTorch 导入失败")
            return False
        print()

        # 初始化分析器
        print("步骤 3/3: 初始化 IQAAnalyzer 实例")
        try:
            analyzer = IQAAnalyzer(model_name="musiq", device="cpu")
            print(f"  ✅ IQAAnalyzer 初始化成功")
            print(f"  📦 模型名称: {analyzer.model_name}")
            print(f"  💻 设备: {analyzer.device}")
            print(f"  🧠 模型: {analyzer.model is not None}")
            print()
            return True
        except RuntimeError as e:
            print(f"  ❌ 初始化失败: {e}")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """测试环境变量"""
    print("=" * 60)
    print("🔧 环境变量检查")
    print("=" * 60)
    print()

    # Python 路径
    print(f"Python 可执行文件:")
    print(f"  {sys.executable}")
    print()

    # Python 版本
    print(f"Python 版本:")
    print(f"  {sys.version}")
    print()

    # PYTHONPATH
    print(f"PYTHONPATH:")
    if 'PYTHONPATH' in os.environ:
        print(f"  {os.environ['PYTHONPATH']}")
    else:
        print(f"  (未设置)")
    print()

    # sys.path
    print(f"sys.path (前5项):")
    for i, path in enumerate(sys.path[:5], 1):
        print(f"  {i}. {path}")
    print()

def main():
    """主函数"""
    print("\n" + "🔍 IQAAnalyzer 详细诊断".center(60, "=") + "\n")

    # 测试环境变量
    test_environment_variables()

    # 测试导入
    imports_ok = test_imports_step_by_step()

    # 测试初始化
    if imports_ok:
        analyzer_ok = test_iqa_analyzer_init()
    else:
        analyzer_ok = False

    # 总结
    print("=" * 60)
    print("📊 诊断总结")
    print("=" * 60)
    print(f"导入测试: {'✅ 通过' if imports_ok else '❌ 失败'}")
    print(f"初始化测试: {'✅ 通过' if analyzer_ok else '❌ 失败'}")
    print()

    if imports_ok and analyzer_ok:
        print("✅ IQAAnalyzer 可以正常使用")
    else:
        print("❌ IQAAnalyzer 存在问题")
        print()
        print("💡 可能的原因:")
        print("   1. PyTorch 安装在不同的 Python 环境中")
        print("   2. 依赖版本不兼容")
        print("   3. 环境变量配置错误")
        print()
        print("🔧 解决方案:")
        print("   1. 确认在正确的 Python 环境中安装依赖:")
        print("      pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu")
        print()
        print("   2. 检查 Python 环境:")
        print("      which python3")
        print("      python3 --version")
        print()
        print("   3. 重新安装依赖:")
        print("      pip uninstall torch torchvision -y")
        print("      pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu")
    print()

if __name__ == '__main__':
    main()
