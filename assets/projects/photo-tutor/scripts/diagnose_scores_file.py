#!/usr/bin/env python3
"""
评分数据文件诊断工具
检查JSON格式和编码问题
"""

import sys
import json
import os
from pathlib import Path


def diagnose_file(file_path: str) -> dict:
    """诊断文件问题"""
    result = {
        'file_exists': False,
        'file_size': 0,
        'encoding': 'unknown',
        'json_valid': False,
        'json_error': None,
        'data_structure': None,
        'suggestions': []
    }

    # 检查文件是否存在
    if not os.path.exists(file_path):
        result['suggestions'].append(f"❌ 文件不存在: {file_path}")
        return result

    result['file_exists'] = True
    result['file_size'] = os.path.getsize(file_path)

    # 尝试检测编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'cp936']
    successful_encoding = None

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            successful_encoding = encoding
            print(f"✅ 成功用 {encoding} 编码读取文件", file=sys.stderr)
            break
        except (UnicodeDecodeError, UnicodeError) as e:
            print(f"⚠️  {encoding} 编码失败: {str(e)[:50]}", file=sys.stderr)
            continue
        except Exception as e:
            print(f"⚠️  读取文件失败: {str(e)[:50]}", file=sys.stderr)
            break

    if not successful_encoding:
        result['suggestions'].append("❌ 无法用任何编码读取文件，可能是二进制文件或损坏")
        result['encoding'] = 'unknown'
        return result

    result['encoding'] = successful_encoding

    # 尝试用成功编码读取并验证JSON
    try:
        with open(file_path, 'r', encoding=successful_encoding) as f:
            data = json.load(f)
        result['json_valid'] = True
        result['data_structure'] = analyze_structure(data)
        print(f"✅ JSON 格式有效", file=sys.stderr)
    except json.JSONDecodeError as e:
        result['json_valid'] = False
        result['json_error'] = str(e)
        result['suggestions'].append(f"❌ JSON 格式错误: {e}")
        print(f"❌ JSON 解析失败: {e}", file=sys.stderr)
    except Exception as e:
        result['json_valid'] = False
        result['json_error'] = str(e)
        result['suggestions'].append(f"❌ 读取JSON失败: {e}")
        print(f"❌ 读取JSON失败: {e}", file=sys.stderr)

    # 生成建议
    if result['json_valid']:
        if result['data_structure']['is_list']:
            if not result['data_structure']['has_six_dimensions']:
                result['suggestions'].append("⚠️  数据项缺少必需的六个维度（composition, lighting, color, creativity, technical, emotion）")
            elif result['data_structure']['sample_count'] < 3:
                result['suggestions'].append("⚠️  数据样本太少，建议至少提供3-5张照片的评分")

    return result


def analyze_structure(data: any) -> dict:
    """分析数据结构"""
    structure = {
        'is_list': False,
        'is_dict': False,
        'sample_count': 0,
        'has_six_dimensions': False,
        'dimensions': []
    }

    if isinstance(data, list):
        structure['is_list'] = True
        structure['sample_count'] = len(data)

        if data:
            first_item = data[0]
            if isinstance(first_item, dict):
                structure['is_dict'] = True
                structure['dimensions'] = list(first_item.keys())
                required_dims = ['composition', 'lighting', 'color', 'creativity', 'technical', 'emotion']
                structure['has_six_dimensions'] = all(dim in structure['dimensions'] for dim in required_dims)

    elif isinstance(data, dict):
        structure['is_dict'] = True
        structure['dimensions'] = list(data.keys())
        required_dims = ['composition', 'lighting', 'color', 'creativity', 'technical', 'emotion']
        structure['has_six_dimensions'] = all(dim in structure['dimensions'] for dim in required_dims)

    return structure


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='评分数据文件诊断工具')
    parser.add_argument('file', help='评分数据文件路径')
    args = parser.parse_args()

    print(f"\n{'=' * 70}", file=sys.stderr)
    print(f"🔍 评分数据文件诊断工具", file=sys.stderr)
    print(f"{'=' * 70}\n", file=sys.stderr)

    # 诊断文件
    result = diagnose_file(args.file)

    # 打印结果
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 打印人类可读报告
    print(f"\n{'=' * 70}", file=sys.stderr)
    print(f"📋 诊断报告", file=sys.stderr)
    print(f"{'=' * 70}", file=sys.stderr)

    print(f"\n文件信息:", file=sys.stderr)
    print(f"  文件路径: {args.file}", file=sys.stderr)
    print(f"  文件存在: {'✅ 是' if result['file_exists'] else '❌ 否'}", file=sys.stderr)
    if result['file_exists']:
        print(f"  文件大小: {result['file_size']} 字节", file=sys.stderr)
        print(f"  文件编码: {result['encoding']}", file=sys.stderr)

    print(f"\nJSON 格式:", file=sys.stderr)
    print(f"  格式有效: {'✅ 是' if result['json_valid'] else '❌ 否'}", file=sys.stderr)
    if result['json_error']:
        print(f"  错误信息: {result['json_error']}", file=sys.stderr)

    if result['json_valid'] and result['data_structure']:
        print(f"\n数据结构:", file=sys.stderr)
        struct = result['data_structure']
        print(f"  类型: {'列表' if struct['is_list'] else '字典'}", file=sys.stderr)
        print(f"  样本数量: {struct['sample_count']}", file=sys.stderr)
        print(f"  维度列表: {', '.join(struct['dimensions'])}", file=sys.stderr)
        print(f"  包含六个维度: {'✅ 是' if struct['has_six_dimensions'] else '❌ 否'}", file=sys.stderr)

    if result['suggestions']:
        print(f"\n💡 建议:", file=sys.stderr)
        for suggestion in result['suggestions']:
            print(f"  {suggestion}", file=sys.stderr)

    print(f"\n{'=' * 70}\n", file=sys.stderr)

    # 退出码
    if result['json_valid']:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
