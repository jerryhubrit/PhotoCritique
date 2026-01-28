#!/bin/bash
# 智能摄影学习助手 - 快速分析脚本

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Python 路径
PYTHON="/usr/bin/python3"

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}智能摄影学习助手 - 照片分析工具${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# 检查参数
if [ -z "$1" ]; then
    echo -e "${YELLOW}用法: $0 <照片路径>${NC}"
    echo ""
    echo "示例："
    echo "  $0 ./test_image.jpg"
    echo "  $0 ~/Pictures/photo.jpg"
    echo ""
    exit 1
fi

PHOTO_PATH="$1"

# 检查文件是否存在
if [ ! -f "$PHOTO_PATH" ]; then
    echo -e "${YELLOW}错误：文件不存在 - $PHOTO_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}📸 开始分析照片: $PHOTO_PATH${NC}"
echo ""

# 1. 基础信息提取
echo -e "${BLUE}[1/3] 提取照片基础信息...${NC}"
echo ""
$PYTHON photo-tutor/scripts/photo_analyzer.py "$PHOTO_PATH"
echo ""

# 2. 色彩美学分析
echo -e "${BLUE}[2/3] 色彩美学分析...${NC}"
echo ""
$PYTHON photo-tutor/scripts/color_analyzer.py "$PHOTO_PATH"
echo ""

# 3. 情感分析（如果配置了API）
echo -e "${BLUE}[3/3] 情感分析...${NC}"
if [ -n "$INTERNLM_API_KEY" ]; then
    $PYTHON photo-tutor/scripts/emotion_analyzer.py "$PHOTO_PATH"
else
    echo -e "${YELLOW}提示：未配置 INTERNLM_API_KEY，跳过情感分析${NC}"
    echo "设置方法: export INTERNLM_API_KEY='your-api-key'"
fi
echo ""

echo -e "${GREEN}✅ 分析完成！${NC}"
