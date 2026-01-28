#!/usr/bin/env python3
"""
照片基础信息提取工具
功能：提取照片元数据，为智能体分析提供基础信息
"""

import os
import sys
from datetime import datetime
from PIL import Image, ExifTags, ImageStat


def extract_basic_info(image_path):
    """
    提取照片基础信息
    
    Args:
        image_path: 照片文件路径
        
    Returns:
        dict: 包含照片基础信息的字典
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    
    try:
        with Image.open(image_path) as img:
            info = {
                'file_name': os.path.basename(image_path),
                'file_size': os.path.getsize(image_path),
                'format': img.format,
                'mode': img.mode,
                'width': img.width,
                'height': img.height,
                'aspect_ratio': round(img.width / img.height, 2),
                'resolution': f"{img.width}x{img.height}",
                'is_portrait': img.height > img.width,
                'is_landscape': img.width > img.height,
                'is_square': img.width == img.height
            }
            
            # 提取EXIF信息
            exif_info = extract_exif(img)
            info.update(exif_info)
            
            # 提取色彩信息
            color_info = extract_color_info(img)
            info.update(color_info)
            
            return info
            
    except Exception as e:
        raise Exception(f"处理图片失败: {str(e)}")


def extract_exif(img):
    """
    提取EXIF元数据
    
    Args:
        img: PIL Image对象
        
    Returns:
        dict: EXIF信息字典
    """
    exif_info = {}
    
    try:
        exif_data = img._getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                
                # 过滤不需要的字段
                if isinstance(tag_name, str) and not tag_name.startswith(('MakerNote', 'UserComment')):
                    # 转换特殊类型
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8')
                        except:
                            value = str(value)
                    exif_info[f'exif_{tag_name}'] = str(value)
                    
                    # 提取关键摄影参数
                    if tag_name == 'FNumber':
                        exif_info['aperture'] = f"f/{value}"
                    elif tag_name == 'ExposureTime':
                        exif_info['shutter_speed'] = f"{value}s" if value >= 1 else f"1/{int(1/value)}s"
                    elif tag_name == 'ISOSpeedRatings':
                        exif_info['iso'] = value
                    elif tag_name == 'FocalLength':
                        exif_info['focal_length'] = f"{value}mm"
                    elif tag_name == 'DateTimeOriginal':
                        exif_info['shooting_time'] = value
    except Exception as e:
        exif_info['exif_error'] = str(e)
    
    return exif_info


def extract_color_info(img):
    """
    提取色彩统计信息
    
    Args:
        img: PIL Image对象
        
    Returns:
        dict: 色彩信息字典
    """
    color_info = {}
    
    try:
        # 转换为RGB模式（如果是其他模式）
        if img.mode != 'RGB':
            img_rgb = img.convert('RGB')
        else:
            img_rgb = img
        
        # 计算平均亮度
        stat = ImageStat.Stat(img_rgb)
        mean_brightness = sum(stat.mean) / len(stat.mean)
        color_info['mean_brightness'] = round(mean_brightness, 2)
        color_info['brightness_level'] = 'bright' if mean_brightness > 200 else 'dark' if mean_brightness < 80 else 'normal'
        
        # 计算对比度
        stdev = stat.stddev
        color_info['contrast'] = round(sum(stdev) / len(stdev), 2)
        color_info['contrast_level'] = 'high' if color_info['contrast'] > 60 else 'low' if color_info['contrast'] < 30 else 'medium'
        
        # 色彩分布
        r_mean, g_mean, b_mean = stat.mean
        color_info['dominant_channel'] = ['R', 'G', 'B'][[r_mean, g_mean, b_mean].index(max([r_mean, g_mean, b_mean]))]
        
    except Exception as e:
        color_info['color_error'] = str(e)
    
    return color_info


def print_info(info):
    """
    打印照片信息（格式化输出）
    
    Args:
        info: 照片信息字典
    """
    print("=" * 60)
    print("照片基础信息")
    print("=" * 60)
    print(f"文件名: {info.get('file_name')}")
    print(f"文件大小: {info.get('file_size', 0) / 1024:.2f} KB")
    print(f"格式: {info.get('format')} | 模式: {info.get('mode')}")
    print(f"分辨率: {info.get('resolution')}")
    print(f"长宽比: {info.get('aspect_ratio')} ({'竖拍' if info.get('is_portrait') else '横拍' if info.get('is_landscape') else '方形'})")
    print()
    
    if 'aperture' in info or 'shutter_speed' in info or 'iso' in info:
        print("-" * 60)
        print("拍摄参数")
        print("-" * 60)
        if 'aperture' in info:
            print(f"光圈: {info['aperture']}")
        if 'shutter_speed' in info:
            print(f"快门: {info['shutter_speed']}")
        if 'iso' in info:
            print(f"ISO: {info['iso']}")
        if 'focal_length' in info:
            print(f"焦距: {info['focal_length']}")
        print()
    
    if 'mean_brightness' in info:
        print("-" * 60)
        print("色彩分析")
        print("-" * 60)
        print(f"平均亮度: {info['mean_brightness']} ({info['brightness_level']})")
        print(f"对比度: {info['contrast']} ({info['contrast_level']})")
        print(f"主色调通道: {info['dominant_channel']}")
        print()
    
    print("=" * 60)


def main():
    """
    主函数：命令行接口
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='照片基础信息提取工具')
    parser.add_argument('image_path', help='照片文件路径')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    try:
        info = extract_basic_info(args.image_path)
        
        if args.json:
            import json
            print(json.dumps(info, ensure_ascii=False, indent=2))
        else:
            print_info(info)
            
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
