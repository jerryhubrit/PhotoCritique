#!/usr/bin/env python3
"""
颜色美学与质量评估工具（优化版）
集成色彩心理学、色彩和谐度计算、调色板美学评分
"""

import os
import sys
import json
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional, List, Tuple


class ColorAestheticsAnalyzer:
    """颜色美学分析器（优化版）"""
    
    # 色彩心理学映射表
    COLOR_PSYCHOLOGY = {
        'red': {
            'emotion': ['热情', '活力', '激情', '危险', '爱'],
            'temperature': 'warm',
            'intensity': 'high'
        },
        'orange': {
            'emotion': ['温暖', '友好', '活力', '创意'],
            'temperature': 'warm',
            'intensity': 'medium'
        },
        'yellow': {
            'emotion': ['快乐', '乐观', '活力', '注意'],
            'temperature': 'warm',
            'intensity': 'high'
        },
        'green': {
            'emotion': ['自然', '平静', '成长', '健康'],
            'temperature': 'cool',
            'intensity': 'medium'
        },
        'blue': {
            'emotion': ['平静', '信任', '专业', '忧郁'],
            'temperature': 'cool',
            'intensity': 'medium'
        },
        'purple': {
            'emotion': ['神秘', '高贵', '创意', '浪漫'],
            'temperature': 'cool',
            'intensity': 'medium'
        },
        'pink': {
            'emotion': ['温柔', '浪漫', '甜美'],
            'temperature': 'warm',
            'intensity': 'low'
        },
        'black': {
            'emotion': ['神秘', '力量', '优雅', '悲伤'],
            'temperature': 'neutral',
            'intensity': 'high'
        },
        'white': {
            'emotion': ['纯净', '简洁', '和平'],
            'temperature': 'neutral',
            'intensity': 'low'
        },
        'gray': {
            'emotion': ['中性', '专业', '沉稳'],
            'temperature': 'neutral',
            'intensity': 'low'
        }
    }
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化分析器
        
        Args:
            model_path: 预训练模型路径（可选）
        """
        self.model_path = model_path
        self.model_loaded = False
        
    def analyze_color_palette(self, image_path: str) -> Dict[str, Any]:
        """
        分析照片的色彩调色板（优化版）
        
        Args:
            image_path: 照片文件路径
            
        Returns:
            色彩调色板信息，包含心理学分析
        """
        dominant_colors = []  # 初始化
        try:
            with Image.open(image_path) as img:
                # 转换为RGB模式
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 缩小图片以加速分析（256x256 保留更多色彩细节）
                img_small = img.resize((256, 256), Image.Resampling.LANCZOS)
                
                # 提取像素
                pixels = np.array(img_small).reshape(-1, 3)
                
                # 提取主要颜色
                dominant_colors = self._extract_dominant_colors(pixels, n_colors=5)
                
                # 分析色彩和谐度（优化版）
                harmony = self._analyze_color_harmony_advanced(dominant_colors)
                
                # 分析色彩心理学（新增）
                psychology = self._analyze_color_psychology(dominant_colors)
                
                # 评估色彩质量（需要包装成dict）
                quality = self.assess_color_quality(image_path, dominant_colors)
                
                # 计算色彩美学评分（新增）
                aesthetics_score = self._calculate_aesthetics_score(
                    harmony, psychology, quality
                )
                
                return {
                    'dominant_colors': dominant_colors,
                    'harmony': harmony,
                    'psychology': psychology,
                    'quality': quality,
                    'aesthetics_score': aesthetics_score
                }
                
        except Exception as e:
            raise Exception(f"色彩调色板分析失败: {str(e)}")
    
    def _extract_dominant_colors(self, pixels: np.ndarray, n_colors: int = 5) -> list:
        """
        提取主要颜色（优化版）
        
        Args:
            pixels: 像素数组
            n_colors: 提取颜色数量
            
        Returns:
            主要颜色列表
        """
        try:
            from sklearn.cluster import MiniBatchKMeans
            
            # 使用K-means聚类提取主要颜色
            kmeans = MiniBatchKMeans(n_clusters=n_colors, random_state=42)
            kmeans.fit(pixels)
            
            colors = kmeans.cluster_centers_.astype(int)
            percentages = np.bincount(kmeans.labels_) / len(pixels)
            
            # 按比例排序
            sorted_indices = np.argsort(percentages)[::-1]
            
            result = []
            for idx in sorted_indices:
                color = colors[idx]
                # 确保颜色值在0-255范围内
                color = np.clip(color, 0, 255)
                result.append({
                    'r': int(color[0]),
                    'g': int(color[1]),
                    'b': int(color[2]),
                    'hex': self._rgb_to_hex(color),
                    'percentage': float(percentages[idx]),
                    'color_name': self._get_color_name(color)
                })
            
            return result
            
        except ImportError:
            # 如果没有sklearn，使用简化的颜色统计
            print("警告: sklearn未安装，使用简化颜色提取")
            unique, counts = np.unique(pixels, axis=0, return_counts=True)
            percentages = counts / len(pixels)
            sorted_indices = np.argsort(percentages)[::-1][:n_colors]
            
            result = []
            for idx in sorted_indices:
                color = unique[idx]
                color = np.clip(color, 0, 255)
                result.append({
                    'r': int(color[0]),
                    'g': int(color[1]),
                    'b': int(color[2]),
                    'hex': self._rgb_to_hex(color),
                    'percentage': float(percentages[idx]),
                    'color_name': self._get_color_name(color)
                })
            
            return result
    
    def _analyze_color_harmony_advanced(self, dominant_colors: list) -> Dict[str, Any]:
        """
        分析色彩和谐度（优化版）
        
        Args:
            dominant_colors: 主要颜色列表
            
        Returns:
            和谐度分析结果（基于色彩理论）
        """
        try:
            from skimage.color import rgb2lab, deltaE_cie76
            
            # 转换为LAB颜色空间
            colors_lab = []
            for color in dominant_colors[:5]:
                rgb = np.array([color['r'], color['g'], color['b']]) / 255.0
                lab = rgb2lab([[rgb]])[0][0]
                colors_lab.append(lab)
            
            # 计算颜色之间的距离
            distances = []
            for i in range(len(colors_lab)):
                for j in range(i + 1, len(colors_lab)):
                    dist = deltaE_cie76(colors_lab[i], colors_lab[j])
                    distances.append(dist)
            
            if not distances:
                return {
                    'score': 100,
                    'type': 'single_color',
                    'description': '单色系',
                    'theory': '单色系：使用同一色相，通过改变亮度和饱和度创造和谐',
                    'rating': 'excellent'
                }
            
            # 平均距离
            avg_distance = np.mean(distances)
            max_distance = np.max(distances)
            min_distance = np.min(distances)
            
            # 基于色彩理论评估和谐度（优化）
            if avg_distance < 15:
                # 单色系
                score = 95
                harmony_type = 'monochromatic'
                description = '单色系：和谐统一，但可能略显单调'
                theory = '单色系：使用同一色相，通过改变亮度和饱和度创造和谐'
                rating = 'excellent'
            elif avg_distance < 30:
                # 类似色系
                score = 90
                harmony_type = 'analogous'
                description = '类似色系：和谐统一，有一定变化'
                theory = '类似色系：使用色相环上相邻的颜色，创造和谐且有变化的视觉效果'
                rating = 'excellent'
            elif avg_distance < 50:
                # 互补色系
                score = 85
                harmony_type = 'complementary'
                description = '互补色系：对比强烈，视觉冲击力强'
                theory = '互补色系：使用色相环上相对的颜色，创造强烈的视觉对比'
                rating = 'good'
            elif avg_distance < 70:
                # 分裂互补色系
                score = 80
                harmony_type = 'split_complementary'
                description = '分裂互补色系：对比适中，和谐与冲击力平衡'
                theory = '分裂互补色系：使用一个颜色的互补色两侧的相邻色，创造平衡的对比'
                rating = 'good'
            else:
                # 三分色系或更多
                score = 75
                harmony_type = 'triadic'
                description = '三分色系：色彩丰富，活力强'
                theory = '三分色系：使用色相环上等距的三个颜色，创造丰富的视觉效果'
                rating = 'fair'
            
            return {
                'score': score,
                'type': harmony_type,
                'description': description,
                'theory': theory,
                'rating': rating,
                'avg_distance': float(avg_distance),
                'max_distance': float(max_distance),
                'min_distance': float(min_distance)
            }
            
        except ImportError:
            print("警告: scikit-image未安装，使用简化的和谐度分析")
            # 简化版本（降低评分）
            return {
                'score': 60,  # 原80 → 60
                'type': 'unknown',
                'description': '和谐度分析简化版',
                'theory': '需要scikit-image进行精确分析',
                'rating': 'fair'
            }
    
    def _analyze_color_psychology(self, dominant_colors: list) -> Dict[str, Any]:
        """
        分析色彩心理学（新增功能）
        
        Args:
            dominant_colors: 主要颜色列表
            
        Returns:
            色彩心理学分析结果
        """
        emotions = []
        temperatures = []
        intensities = []
        
        # 分析每个主要颜色
        for color in dominant_colors[:3]:
            color_name = color.get('color_name', 'unknown')
            if color_name in self.COLOR_PSYCHOLOGY:
                psych = self.COLOR_PSYCHOLOGY[color_name]
                emotions.extend(psych['emotion'])
                temperatures.append(psych['temperature'])
                intensities.append(psych['intensity'])
        
        # 统计情感倾向
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # 找出最主要的情感
        dominant_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # 统计色温
        warm_count = temperatures.count('warm')
        cool_count = temperatures.count('cool')
        neutral_count = temperatures.count('neutral')
        
        if warm_count > cool_count and warm_count > neutral_count:
            temperature = 'warm'
            temperature_description = '暖色调：传递温暖、活力、激情'
        elif cool_count > warm_count and cool_count > neutral_count:
            temperature = 'cool'
            temperature_description = '冷色调：传递冷静、理性、忧郁'
        else:
            temperature = 'neutral'
            temperature_description = '中性色调：传递平和、专业、沉稳'
        
        # 统计强度
        high_intensity = intensities.count('high')
        medium_intensity = intensities.count('medium')
        low_intensity = intensities.count('low')
        
        if high_intensity > medium_intensity and high_intensity > low_intensity:
            intensity = 'high'
            intensity_description = '高饱和度：色彩鲜艳，视觉冲击力强'
        elif medium_intensity >= high_intensity and medium_intensity >= low_intensity:
            intensity = 'medium'
            intensity_description = '中等饱和度：色彩适中，视觉舒适'
        else:
            intensity = 'low'
            intensity_description = '低饱和度：色彩柔和，视觉舒适'
        
        return {
            'dominant_emotions': [e[0] for e in dominant_emotions],
            'emotion_counts': dict(dominant_emotions),
            'temperature': temperature,
            'temperature_description': temperature_description,
            'intensity': intensity,
            'intensity_description': intensity_description,
            'psychology_score': self._calculate_psychology_score(dominant_emotions)
        }
    
    def _calculate_psychology_score(self, dominant_emotions: list) -> float:
        """
        计算心理学评分
        
        Args:
            dominant_emotions: 主导情感列表
            
        Returns:
            心理学评分（0-100）
        """
        if not dominant_emotions:
            return 50.0
        
        # 情感数量越多，分数越高（表明情感表达更丰富）
        emotion_count = len(dominant_emotions)
        base_score = min(emotion_count * 20, 100.0)
        
        # 正向情感加分
        positive_emotions = ['热情', '活力', '快乐', '乐观', '爱', '温暖', '友好', '创意', '自然', '平静', '信任', '优雅', '纯净']
        negative_emotions = ['危险', '悲伤', '忧郁', '危险']
        
        positive_count = sum(1 for e in dominant_emotions if e in positive_emotions)
        negative_count = sum(1 for e in dominant_emotions if e in negative_emotions)
        
        # 调整分数
        adjusted_score = base_score + (positive_count * 5) - (negative_count * 10)
        
        return np.clip(adjusted_score, 0, 100.0)
    
    def assess_color_quality(self, image_path: str, dominant_colors: list) -> Dict[str, Any]:
        """
        评估色彩质量（优化版）
        
        Args:
            image_path: 图片路径
            dominant_colors: 主要颜色
            
        Returns:
            色彩质量评估结果
        """
        try:
            with Image.open(image_path) as img:
                # 评估饱和度
                saturation_score = self._assess_saturation(dominant_colors)
                
                # 评估对比度
                contrast_score = self._assess_contrast(image_path)
                
                # 综合评分
                overall_score = (saturation_score + contrast_score) / 2
                
                return {
                    'saturation_score': saturation_score,
                    'contrast_score': contrast_score,
                    'overall_score': overall_score,
                    'rating': self._get_quality_rating(overall_score)
                }
                
        except Exception as e:
            raise Exception(f"色彩质量评估失败: {str(e)}")
    
    def _assess_saturation(self, dominant_colors: list) -> float:
        """
        评估饱和度（优化版）
        
        Args:
            palette: 调色板
            
        Returns:
            饱和度评分（0-100）
        """
        dominant_colors = dominant_colors
        if not dominant_colors:
            return 50.0
        
        # 计算平均饱和度
        saturations = []
        for color in dominant_colors[:5]:
            r, g, b = color['r'], color['g'], color['b']
            # 转换为HSV
            r_norm = r / 255.0
            g_norm = g / 255.0
            b_norm = b / 255.0
            
            max_val = max(r_norm, g_norm, b_norm)
            min_val = min(r_norm, g_norm, b_norm)
            
            if max_val == min_val:
                saturation = 0.0
            else:
                saturation = (max_val - min_val) / max_val
            
            saturations.append(saturation)
        
        avg_saturation = np.mean(saturations) * 100
        
        # 理想饱和度为60-80（强化版，降低评分）
        if 60 <= avg_saturation <= 80:
            return 85.0  # 原100 → 85
        elif 50 <= avg_saturation < 60:
            return 70.0  # 原90 → 70
        elif 80 < avg_saturation <= 90:
            return 75.0  # 原85 → 75
        elif avg_saturation < 50:
            return max(avg_saturation / 50 * 100, 40.0)  # 原50 → 40
        else:  # > 90
            return max(100.0 - (avg_saturation - 90) * 2, 70.0)
    
    def _assess_contrast(self, image_path: str) -> float:
        """
        评估对比度（优化版）
        
        Args:
            image_path: 图片路径
            
        Returns:
            对比度评分（0-100）
        """
        try:
            with Image.open(image_path) as img:
                # 转换为灰度
                gray = img.convert('L')
                
                # 计算标准差（对比度指标）
                gray_array = np.array(gray)
                contrast = gray_array.std()
                
                # 归一化到0-100
                contrast_score = min(contrast / 64.0 * 100, 100.0)
                
                # 理想对比度为30-50（强化版，降低评分）
                if 30 <= contrast <= 50:
                    return 85.0  # 原100 → 85
                elif 20 <= contrast < 30:
                    return 70.0  # 原90 → 70
                elif 50 < contrast <= 70:
                    return 75.0  # 原85 → 75
                elif contrast < 20:
                    return max(contrast / 20 * 100, 40.0)  # 原50 → 40
                else:  # > 70
                    return max(85.0 - (contrast - 70) * 1.5, 50.0)  # 原100 → 85, 原70 → 50
                
        except Exception:
            return 50.0
    
    def _calculate_aesthetics_score(self, harmony: Dict[str, Any], 
                                     psychology: Dict[str, Any],
                                     quality: Dict[str, Any]) -> float:
        """
        计算色彩美学评分（强化版，降低默认分）
        
        Args:
            harmony: 和谐度分析结果
            psychology: 心理学分析结果
            quality: 质量评估结果
            
        Returns:
            美学评分（0-100）
        """
        # 降低默认评分（强化版）
        harmony_score = harmony.get('score', 60)  # 原80 → 60
        psychology_score = psychology.get('psychology_score', 50)  # 原70 → 50
        quality_score = quality.get('overall_score', 55)  # 原75 → 55
        
        # 权重：和谐度40%，心理学30%，质量30%
        aesthetics_score = (
            harmony_score * 0.4 +
            psychology_score * 0.3 +
            quality_score * 0.3
        )
        
        return round(aesthetics_score, 2)
    
    def _get_quality_rating(self, score: float) -> str:
        """
        获取质量评级
        
        Args:
            score: 评分
            
        Returns:
            评级字符串
        """
        if score >= 90:
            return 'excellent'
        elif score >= 80:
            return 'good'
        elif score >= 70:
            return 'fair'
        else:
            return 'poor'
    
    def _rgb_to_hex(self, rgb: np.ndarray) -> str:
        """
        转换RGB为HEX
        
        Args:
            rgb: RGB值
            
        Returns:
            HEX字符串
        """
        return '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0]),
            int(rgb[1]),
            int(rgb[2])
        )
    
    def _get_color_name(self, rgb: np.ndarray) -> str:
        """
        获取颜色名称
        
        Args:
            rgb: RGB值
            
        Returns:
            颜色名称
        """
        r, g, b = rgb
        
        # 简单的颜色识别
        if r > 200 and g > 200 and b > 200:
            return 'white'
        elif r < 50 and g < 50 and b < 50:
            return 'black'
        elif r > 200 and g < 100 and b < 100:
            return 'red'
        elif r < 100 and g > 200 and b < 100:
            return 'green'
        elif r < 100 and g < 100 and b > 200:
            return 'blue'
        elif r > 200 and g > 200 and b < 100:
            return 'yellow'
        elif r > 200 and g < 100 and b > 200:
            return 'purple'
        elif r > 200 and g > 100 and b < 100:
            return 'orange'
        elif r > 200 and g > 150 and b > 150:
            return 'pink'
        else:
            # 计算灰度
            gray = (r + g + b) / 3
            if gray > 150:
                return 'white'
            elif gray < 100:
                return 'black'
            else:
                return 'gray'
    
    def analyze(self, image_path: str) -> Dict[str, Any]:
        """
        综合分析（优化版）
        
        Args:
            image_path: 图片路径
            
        Returns:
            综合分析结果
        """
        try:
            # 分析调色板
            palette = self.analyze_color_palette(image_path)
            
            # 生成报告
            report = {
                'image_path': image_path,
                'palette_analysis': palette,
                'summary': self._generate_summary(palette)
            }
            
            return report
            
        except Exception as e:
            raise Exception(f"综合分析失败: {str(e)}")
    
    def _generate_summary(self, palette: Dict[str, Any]) -> str:
        """
        生成分析总结
        
        Args:
            palette: 调色板分析结果
            
        Returns:
            总结文本
        """
        harmony = palette.get('harmony', {})
        psychology = palette.get('psychology', {})
        quality = palette.get('quality', {})
        aesthetics_score = palette.get('aesthetics_score', 75)
        
        summary_parts = []
        
        # 和谐度
        harmony_desc = harmony.get('description', '和谐度一般')
        summary_parts.append(f"色彩和谐度：{harmony_desc}")
        
        # 情感倾向
        dominant_emotions = psychology.get('dominant_emotions', [])
        if dominant_emotions:
            emotions_text = '、'.join(dominant_emotions[:3])
            summary_parts.append(f"情感倾向：{emotions_text}")
        
        # 色温
        temperature_desc = psychology.get('temperature_description', '色温中性')
        summary_parts.append(temperature_desc)
        
        # 美学评分
        rating = 'excellent' if aesthetics_score >= 90 else 'good' if aesthetics_score >= 80 else 'fair'
        summary_parts.append(f"美学评分：{aesthetics_score}/100（{rating}）")
        
        return '；'.join(summary_parts)


def print_analysis(result: Dict[str, Any]):
    """
    打印分析结果
    
    Args:
        result: 分析结果
    """
    print("=" * 60)
    print("色彩美学分析报告（优化版）")
    print("=" * 60)
    
    # 调色板
    palette = result['palette_analysis']
    dominant_colors = palette['dominant_colors']
    
    print("\n【主要色彩】")
    for i, color in enumerate(dominant_colors[:5], 1):
        print(f"{i}. {color['hex']} ({color['color_name']}) - {color['percentage']:.1%}")
    
    # 和谐度
    harmony = palette.get('harmony', {})
    print(f"\n【和谐度】")
    print(f"类型：{harmony.get('type', 'unknown')}")
    print(f"评分：{harmony.get('score', 0)}/100")
    print(f"描述：{harmony.get('description', 'N/A')}")
    print(f"理论：{harmony.get('theory', 'N/A')}")
    
    # 心理学
    psychology = palette.get('psychology', {})
    print(f"\n【色彩心理学】")
    print(f"主导情感：{', '.join(psychology.get('dominant_emotions', []))}")
    print(f"色温：{psychology.get('temperature', 'neutral')} - {psychology.get('temperature_description', 'N/A')}")
    print(f"强度：{psychology.get('intensity', 'medium')} - {psychology.get('intensity_description', 'N/A')}")
    print(f"心理学评分：{psychology.get('psychology_score', 0)}/100")
    
    # 质量
    quality = palette.get('quality', {})
    print(f"\n【色彩质量】")
    print(f"饱和度评分：{quality.get('saturation_score', 0)}/100")
    print(f"对比度评分：{quality.get('contrast_score', 0)}/100")
    print(f"综合评分：{quality.get('overall_score', 0)}/100 ({quality.get('rating', 'fair')})")
    
    # 美学评分
    aesthetics_score = palette.get('aesthetics_score', 75)
    print(f"\n【美学评分】")
    print(f"总分：{aesthetics_score}/100")
    
    # 总结
    summary = result.get('summary', '')
    print(f"\n【总结】")
    print(summary)
    
    print("=" * 60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='色彩美学分析工具（优化版）')
    parser.add_argument('image_path', help='图片路径')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = ColorAestheticsAnalyzer()
    
    try:
        # 分析
        result = analyzer.analyze(args.image_path)
        
        # 输出
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print_analysis(result)
            
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
