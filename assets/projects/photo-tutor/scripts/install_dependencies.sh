#!/bin/bash
# photo-tutor 依赖安装脚本
# 适用于部署环境自动安装缺失的依赖

set -e  # 遇到错误立即退出

echo "=========================================="
echo "photo-tutor 依赖安装脚本"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 步骤 1: 检查 Python 版本
echo "步骤 1/4: 检查 Python 版本"
echo "----------------------------------------"
PYTHON_VERSION=$(python3 --version)
echo "Python 版本: $PYTHON_VERSION"

if ! python3 --version | grep -q "Python 3\."; then
    echo -e "${RED}❌ 需要 Python 3.6 或更高版本${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 版本符合要求${NC}"
echo ""

# 步骤 2: 检查并升级 pip
echo "步骤 2/4: 检查 pip 版本"
echo "----------------------------------------"
pip3 --version

echo "升级 pip..."
pip3 install --upgrade pip --quiet
echo -e "${GREEN}✅ pip 已升级${NC}"
echo ""

# 步骤 3: 安装小包（快速完成）
echo "步骤 3/4: 安装小包依赖"
echo "----------------------------------------"

echo "安装 scikit-image..."
pip3 install scikit-image --quiet || {
    echo -e "${RED}❌ scikit-image 安装失败${NC}"
    exit 1
}
echo -e "${GREEN}✅ scikit-image 安装成功${NC}"

echo "安装 pymcdm..."
pip3 install pymcdm --quiet || {
    echo -e "${RED}❌ pymcdm 安装失败${NC}"
    exit 1
}
echo -e "${GREEN}✅ pymcdm 安装成功${NC}"
echo ""

# 步骤 4: 安装 PyTorch（需要时间）
echo "步骤 4/4: 安装 PyTorch 和 TorchVision"
echo "----------------------------------------"
echo "⚠️  这可能需要几分钟，请耐心等待..."
echo ""

# 检测是否支持 CUDA
if command -v nvidia-smi &> /dev/null; then
    echo -e "${YELLOW}检测到 NVIDIA GPU，安装 GPU 版本${NC}"
    pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121 || {
        echo -e "${RED}❌ PyTorch GPU 版本安装失败，尝试安装 CPU 版本${NC}"
        pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    }
else
    echo -e "${YELLOW}未检测到 NVIDIA GPU，安装 CPU 版本${NC}"
    pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu || {
        echo -e "${RED}❌ PyTorch 安装失败${NC}"
        exit 1
    }
fi

echo ""
echo -e "${GREEN}✅ PyTorch 和 TorchVision 安装成功${NC}"
echo ""

# 验证安装
echo "=========================================="
echo "验证安装"
echo "=========================================="
echo ""

python3 << 'EOF'
import sys

checks = [
    ('torch', 'PyTorch'),
    ('torchvision', 'TorchVision'),
    ('skimage', 'scikit-image'),
    ('sklearn', 'scikit-learn'),
    ('pymcdm', 'pymcdm'),
    ('PIL', 'Pillow'),
]

failed = []
for module_name, display_name in checks:
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {display_name:20} 版本: {version}")
    except ImportError:
        print(f"❌ {display_name:20} 未安装")
        failed.append(display_name)

if failed:
    print(f"\n❌ 以下包安装失败: {', '.join(failed)}")
    sys.exit(1)
else:
    print("\n✅ 所有依赖安装成功！")
EOF

# 最终检查
echo ""
echo "=========================================="
echo -e "${GREEN}✅ 安装完成！${NC}"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 运行环境检查：python3 scripts/check_env_json.py"
echo "2. 确认状态为 READY 后，开始使用 photo-tutor"
echo ""
