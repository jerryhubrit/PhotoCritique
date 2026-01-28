#!/bin/bash
# 部署环境快速检查脚本
# 请运行此脚本并将输出结果发送给开发人员

echo "=========================================="
echo "部署环境快速检查"
echo "=========================================="
echo ""

echo "1. Python 版本和路径"
echo "----------------------------------------"
which python3
python3 --version
echo ""

echo "2. pip 版本"
echo "----------------------------------------"
pip --version
echo ""

echo "3. 关键包安装状态"
echo "----------------------------------------"
pip show torch 2>/dev/null || echo "❌ torch 未安装"
pip show torchvision 2>/dev/null || echo "❌ torchvision 未安装"
pip show scikit-image 2>/dev/null || echo "❌ scikit-image 未安装"
pip show scikit-learn 2>/dev/null || echo "❌ scikit-learn 未安装"
pip show pymcdm 2>/dev/null || echo "❌ pymcdm 未安装"
pip show pillow 2>/dev/null || echo "❌ pillow 未安装"
echo ""

echo "4. PyTorch 导入测试"
echo "----------------------------------------"
python3 -c "import torch; print('✅ PyTorch 版本:', torch.__version__)" 2>&1 || echo "❌ PyTorch 导入失败"
echo ""

echo "5. TorchVision 导入测试"
echo "----------------------------------------"
python3 -c "import torchvision; print('✅ TorchVision 版本:', torchvision.__version__)" 2>&1 || echo "❌ TorchVision 导入失败"
echo ""

echo "6. IQAAnalyzer 测试"
echo "----------------------------------------"
cd "$(dirname "$0")/.." || exit 1
python3 scripts/test_iqa_imports.py 2>&1 | grep -E "(✅|❌|测试通过|测试失败)"
echo ""

echo "=========================================="
echo "✅ 快速检查完成"
echo "=========================================="
echo ""
echo "💡 如果以上测试全部通过，则环境正常"
echo "💡 如果有任何 ❌，请运行完整的诊断脚本："
echo "   python3 scripts/deployment_diagnostic.py"
echo ""
