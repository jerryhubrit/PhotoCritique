#!/bin/bash
# photo-tutor 依赖安装脚本（轻量版）
# 适用于部署环境自动安装缺失的依赖

echo "=========================================="
echo "photo-tutor 依赖安装中（后台运行）"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 步骤 1: 检查 Python 版本
echo "步骤 1/2: 检查 Python 版本"
echo "----------------------------------------"
PYTHON_VERSION=$(python3 --version)
echo "Python 版本: $PYTHON_VERSION"

if ! python3 --version | grep -q "Python 3\."; then
    echo -e "${RED}❌ 需要 Python 3.6 或更高版本${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 版本符合要求${NC}"
echo ""

# 步骤 2: 安装依赖包
echo "步骤 2/2: 安装依赖包"
echo "----------------------------------------"

echo "安装 scikit-image..."
pip3 install scikit-image --quiet || {
    echo -e "${RED}❌ scikit-image 安装失败${NC}"
    exit 1
}
echo -e "${GREEN}✅ scikit-image 安装成功${NC}"

echo "安装 scikit-learn..."
pip3 install scikit-learn --quiet || {
    echo -e "${RED}❌ scikit-learn 安装失败${NC}"
    exit 1
}
echo -e "${GREEN}✅ scikit-learn 安装成功${NC}"
echo ""

# 验证安装
echo "=========================================="
echo "验证安装"
echo "=========================================="
echo ""

python3 << 'EOF' 2>/dev/null
import sys

checks = [
    ('skimage', 'scikit-image'),
    ('sklearn', 'scikit-learn'),
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
echo "photo-tutor 已就绪，可以直接使用！"
echo ""
