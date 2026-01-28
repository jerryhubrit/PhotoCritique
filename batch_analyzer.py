#!/usr/bin/env python3
"""
智能摄影学习助手 - 批量分析工具
可以分析多张照片并生成HTML格式的综合报告
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()  # 从 .env 文件加载环境变量
except ImportError:
    print("⚠️  提示: 未安装 python-dotenv，将从系统环境变量读取配置")

# 添加脚本路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'photo-tutor/scripts'))

from photo_analyzer import extract_basic_info
from color_analyzer import ColorAestheticsAnalyzer
from emotion_analyzer import EmotionAnalyzer
from i18n import get_i18n


class BatchPhotoAnalyzer:
    """批量照片分析器"""
    
    def __init__(self, lang='zh'):
        """
        初始化分析器
        
        Args:
            lang: 语言，'zh' 或 'en'
        """
        # 加载环境变量
        self._load_env()
        
        # 初始化分析器
        self.color_analyzer = ColorAestheticsAnalyzer()
        self.emotion_analyzer = EmotionAnalyzer(lang=lang)  # 传递语言参数
        
        # 初始化国际化
        self.i18n = get_i18n(lang)
        self.lang = lang
        
    def _load_env(self):
        """加载 .env 文件"""
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    
    def analyze_photo(self, image_path: str) -> Dict[str, Any]:
        """分析单张照片"""
        print(f"  正在分析: {os.path.basename(image_path)}...")
        
        result = {
            "image_path": image_path,
            "image_name": os.path.basename(image_path),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # 1. 基础信息提取
            basic_info = extract_basic_info(image_path)
            result["basic_info"] = basic_info
            
            # 2. 色彩美学分析
            color_analysis = self.color_analyzer.analyze(image_path)
            result["color_analysis"] = color_analysis
            
            # 3. 情感分析
            emotion_result = self.emotion_analyzer.analyze(
                image_path=image_path,
                photo_info=basic_info,
                color_analysis=color_analysis
            )
            result["emotion_analysis"] = emotion_result
            
            result["status"] = "success"
            print(f"  ✅ 完成")
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"  ❌ 失败: {str(e)}")
        
        return result
    
    def analyze_batch(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """批量分析多张照片"""
        print(f"\n开始分析 {len(image_paths)} 张照片...\n")
        
        results = []
        for idx, image_path in enumerate(image_paths, 1):
            print(f"[{idx}/{len(image_paths)}]", end=" ")
            result = self.analyze_photo(image_path)
            results.append(result)
        
        print("\n分析完成！\n")
        return results
    
    def generate_html_report(self, results: List[Dict[str, Any]], output_path: str = None):
        """生成HTML格式的报告
        所有测试报告统一保存在 reports/ 目录下
        文件命名规则: photo_report_YYYYMMDD_LANG_XXX.html
        例如: photo_report_20260128_en_001.html
        """
        base_dir = Path('reports')
        
        # 处理输出路径
        if output_path:
            out_path = Path(output_path)
            # 如果用户只给了文件名（没有目录），统一放到 reports/ 下
            if not out_path.parent or str(out_path.parent) == '.':
                out_path = base_dir / out_path.name
        else:
            date_str = datetime.now().strftime('%Y%m%d')
            index = self._get_next_report_index(base_dir, date_str)
            file_name = f"photo_report_{date_str}_{self.lang}_{index:03d}.html"
            out_path = base_dir / file_name
        
        # 确保输出目录存在
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = self._build_html(results)
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 HTML报告已生成: {out_path}")
        return str(out_path)
    
    def _get_next_report_index(self, base_dir: Path, date_str: str) -> int:
        """获取指定日期和语言下的下一个顺序号（从001开始）"""
        pattern = re.compile(rf"^photo_report_{date_str}_{self.lang}_(\\d{{3}})\\.html$")
        max_index = 0
        if base_dir.exists():
            for item in base_dir.iterdir():
                if item.is_file():
                    m = pattern.match(item.name)
                    if m:
                        idx = int(m.group(1))
                        if idx > max_index:
                            max_index = idx
        return max_index + 1
    
    def _build_html(self, results: List[Dict[str, Any]]) -> str:
        """构建HTML内容"""
        html_parts = []
        t = self.i18n.t  # 翻译函数简写
        
        # HTML头部
        html_parts.append('''
<!DOCTYPE html>
<html lang="''' + self.lang + '''">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>''' + t('report_title') + ' - ' + t('report_subtitle') + '''</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .content {
            padding: 40px;
        }
        .photo-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .photo-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #667eea;
        }
        .photo-number {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }
        .photo-title {
            font-size: 1.5em;
            color: #333;
            font-weight: 600;
        }
        .section {
            margin: 25px 0;
        }
        .section-title {
            font-size: 1.3em;
            color: #667eea;
            margin-bottom: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
        }
        .section-title::before {
            content: "";
            width: 4px;
            height: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin-right: 10px;
            border-radius: 2px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        .info-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }
        .info-label {
            font-weight: 600;
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .info-value {
            font-size: 1.1em;
            color: #333;
        }
        .color-palette {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .color-item {
            display: flex;
            align-items: center;
            background: white;
            padding: 10px 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .color-swatch {
            width: 40px;
            height: 40px;
            border-radius: 6px;
            margin-right: 12px;
            border: 2px solid #e0e0e0;
        }
        .color-info {
            font-size: 0.9em;
        }
        .score {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.1em;
        }
        .emotion-text {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #764ba2;
            line-height: 1.8;
            font-size: 1.05em;
        }
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #c33;
        }
        .footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📷 ''' + t('report_title') + '''</h1>
            <p>''' + t('report_subtitle') + '''</p>
            <p style="font-size: 0.9em; margin-top: 10px;">''' + t('generated_time') + ''': ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
        </div>
        <div class="content">
''')
        
        # 每张照片的分析结果
        for idx, result in enumerate(results, 1):
            html_parts.append(self._build_photo_section(idx, result))
        
        # HTML尾部
        html_parts.append('''
        </div>
        <div class="footer">
            <p><strong>''' + t('report_title') + '''</strong></p>
            <p>''' + t('footer_tech') + '''</p>
            <p style="margin-top: 10px;">💡 ''' + t('footer_tip') + '''</p>
        </div>
    </div>
</body>
</html>
''')
        
        return ''.join(html_parts)
    
    def _build_photo_section(self, idx: int, result: Dict[str, Any]) -> str:
        """构建单张照片的HTML部分"""
        parts = []
        
        parts.append(f'''
        <div class="photo-card">
            <div class="photo-header">
                <div class="photo-number">{idx}</div>
                <div class="photo-title">{result['image_name']}</div>
            </div>
''')
        
        if result['status'] == 'error':
            parts.append(f'''
            <div class="error">
                ❌ 分析失败: {result.get('error', '未知错误')}
            </div>
''')
        else:
            # 基础信息
            if 'basic_info' in result:
                parts.append(self._build_basic_info(result['basic_info']))
            
            # 六维评分雷达图
            parts.append(self._build_six_dimension_scores(result))
            
            # 色彩分析
            if 'color_analysis' in result:
                parts.append(self._build_color_analysis(result['color_analysis']))
            
            # 情感分析
            if 'emotion_analysis' in result:
                parts.append(self._build_emotion_analysis(result['emotion_analysis']))
            
            # 学习建议
            parts.append(self._build_learning_suggestions(result))
            
            # 练习方案
            parts.append(self._build_practice_plan(result))
        
        parts.append('        </div>\n')
        
        return ''.join(parts)
    
    def _build_six_dimension_scores(self, result: Dict[str, Any]) -> str:
        """构建六维评分雷达图"""
        t = self.i18n.t
        # 提取评分数据
        basic_info = result.get('basic_info', {})
        color_analysis = result.get('color_analysis', {})
        emotion_analysis = result.get('emotion_analysis', {})
        
        # 从 color_analysis 中正确提取评分
        palette = color_analysis.get('palette_analysis', {})
        color_score = palette.get('aesthetics_score', 0) if palette else 0
        
        # 六个维度的评分（0-100）
        scores = {
            t('composition'): self._calculate_composition_score(basic_info),
            t('lighting'): self._calculate_lighting_score(basic_info),
            t('color'): color_score,
            t('creativity'): 75,  # 默认值
            t('technique'): self._calculate_technical_score(basic_info),
            t('emotion'): self._calculate_emotion_score(emotion_analysis)
        }
        
        # 生成雷达图HTML
        parts = []
        parts.append('''
            <div class="section">
                <div class="section-title">📊 ''' + t('six_dimensions') + '''</div>
                <div style="display: flex; gap: 30px; align-items: center; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 300px;">
                        <canvas id="radarChart''' + str(hash(result['image_name'])) + '''" width="300" height="300"></canvas>
                    </div>
                    <div style="flex: 1; min-width: 300px;">
''')
        
        # 评分详情
        for dimension, score in scores.items():
            color = self._get_score_color(score)
            parts.append(f'''
                        <div style="margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span><strong>{dimension}</strong></span>
                                <span style="color: {color}; font-weight: bold;">{score}/100</span>
                            </div>
                            <div style="background: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background: {color}; height: 100%; width: {score}%; transition: width 0.3s;"></div>
                            </div>
                        </div>
''')
        
        parts.append('''
                    </div>
                </div>
            </div>
            <script>
                (function() {
                    const canvas = document.getElementById('radarChart''' + str(hash(result['image_name'])) + '''');
                    const ctx = canvas.getContext('2d');
                    const centerX = canvas.width / 2;
                    const centerY = canvas.height / 2;
                    const radius = 120;
                    
                    const dimensions = ''' + str(list(scores.keys())) + ''';
                    const scores = ''' + str(list(scores.values())) + ''';
                    const angleStep = (Math.PI * 2) / dimensions.length;
                    
                    // Draw background grid
                    ctx.strokeStyle = '#e0e0e0';
                    ctx.lineWidth = 1;
                    for (let i = 1; i <= 5; i++) {
                        ctx.beginPath();
                        const r = (radius / 5) * i;
                        for (let j = 0; j <= dimensions.length; j++) {
                            const angle = angleStep * j - Math.PI / 2;
                            const x = centerX + r * Math.cos(angle);
                            const y = centerY + r * Math.sin(angle);
                            if (j === 0) ctx.moveTo(x, y);
                            else ctx.lineTo(x, y);
                        }
                        ctx.closePath();
                        ctx.stroke();
                    }
                    
                    // Draw axis lines
                    ctx.strokeStyle = '#ccc';
                    ctx.lineWidth = 1;
                    for (let i = 0; i < dimensions.length; i++) {
                        const angle = angleStep * i - Math.PI / 2;
                        ctx.beginPath();
                        ctx.moveTo(centerX, centerY);
                        ctx.lineTo(
                            centerX + radius * Math.cos(angle),
                            centerY + radius * Math.sin(angle)
                        );
                        ctx.stroke();
                    }
                    
                    // Draw data area
                    ctx.fillStyle = 'rgba(102, 126, 234, 0.2)';
                    ctx.strokeStyle = 'rgba(102, 126, 234, 0.8)';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    for (let i = 0; i <= scores.length; i++) {
                        const score = scores[i % scores.length];
                        const angle = angleStep * i - Math.PI / 2;
                        const r = (radius * score) / 100;
                        const x = centerX + r * Math.cos(angle);
                        const y = centerY + r * Math.sin(angle);
                        if (i === 0) ctx.moveTo(x, y);
                        else ctx.lineTo(x, y);
                    }
                    ctx.closePath();
                    ctx.fill();
                    ctx.stroke();
                    
                    // Draw data points
                    ctx.fillStyle = '#667eea';
                    for (let i = 0; i < scores.length; i++) {
                        const score = scores[i];
                        const angle = angleStep * i - Math.PI / 2;
                        const r = (radius * score) / 100;
                        const x = centerX + r * Math.cos(angle);
                        const y = centerY + r * Math.sin(angle);
                        ctx.beginPath();
                        ctx.arc(x, y, 4, 0, Math.PI * 2);
                        ctx.fill();
                    }
                    
                    // Draw labels
                    ctx.fillStyle = '#333';
                    ctx.font = 'bold 12px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    for (let i = 0; i < dimensions.length; i++) {
                        const angle = angleStep * i - Math.PI / 2;
                        const labelRadius = radius + 25;
                        const x = centerX + labelRadius * Math.cos(angle);
                        const y = centerY + labelRadius * Math.sin(angle);
                        ctx.fillText(dimensions[i], x, y);
                    }
                })();
            </script>
''')
        
        return ''.join(parts)
    
    def _calculate_composition_score(self, basic_info: Dict[str, Any]) -> int:
        """计算构图评分"""
        score = 70  # 基础分
        
        # 根据长宽比判断
        aspect_ratio = basic_info.get('aspect_ratio', 1.0)
        if 0.6 <= aspect_ratio <= 0.7 or 1.4 <= aspect_ratio <= 1.7:  # 黄金比例附近
            score += 10
        
        return min(100, score)
    
    def _calculate_lighting_score(self, basic_info: Dict[str, Any]) -> int:
        """计算光影评分"""
        score = 60  # 基础分
        
        # 根据对比度判断
        contrast = basic_info.get('contrast', 0)
        contrast_level = basic_info.get('contrast_level', 'medium')
        
        if contrast_level == 'medium':
            score += 20
        elif contrast_level == 'high':
            score += 10
        
        # 根据亮度判断
        brightness_level = basic_info.get('brightness_level', 'normal')
        if brightness_level == 'normal':
            score += 10
        
        return min(100, score)
    
    def _calculate_technical_score(self, basic_info: Dict[str, Any]) -> int:
        """计算技术评分"""
        score = 70  # 基础分
        
        # 根据分辨率判断
        resolution = basic_info.get('resolution', '')
        if resolution:
            width, height = map(int, resolution.split('x'))
            total_pixels = width * height
            if total_pixels >= 2000000:  # 2MP+
                score += 15
            elif total_pixels >= 1000000:  # 1MP+
                score += 10
        
        return min(100, score)
    
    def _calculate_emotion_score(self, emotion_analysis: Dict[str, Any]) -> int:
        """计算情绪评分"""
        emotion_data = emotion_analysis.get('emotion_analysis', {})
        
        # 如果有AI分析，给高分
        if emotion_data.get('method') == 'internlm_api' and emotion_data.get('success'):
            return 85
        
        return 65  # 基础分
    
    def _get_score_color(self, score: int) -> str:
        """根据分数返回颜色"""
        if score >= 80:
            return '#4caf50'  # 绿色
        elif score >= 60:
            return '#ff9800'  # 橙色
        else:
            return '#f44336'  # 红色
    
    def _build_learning_suggestions(self, result: Dict[str, Any]) -> str:
        """构建学习建议部分"""
        parts = []
        t = self.i18n.t
        parts.append('''
            <div class="section">
                <div class="section-title">💡 ''' + t('learning_suggestions') + '''</div>
''')
        
        # 分析薄弱环节
        basic_info = result.get('basic_info', {})
        color_analysis = result.get('color_analysis', {})
        palette = color_analysis.get('palette_analysis', {})
        
        # 提取各维度分数
        composition_score = self._calculate_composition_score(basic_info)
        lighting_score = self._calculate_lighting_score(basic_info)
        color_score = palette.get('aesthetics_score', 0) if palette else 0
        
        suggestions = []
        
        # 根据分数生成建议 - 使用翻译
        if composition_score < 75:
            suggestions.append({
                'title': '📐 ' + t('composition_improvement'),
                'level': t('focus_area'),
                'content': '''
                    <p><strong>''' + t('current_issue') + '''：</strong>''' + t('composition_issue') + '''</p>
                    <p><strong>''' + t('improvement_suggestions') + '''：</strong></p>
                    <ul>
''' + t('composition_suggestions') + '''
                    </ul>
                    <p><strong>''' + t('reference_resources') + '''：</strong>photo-tutor/references/composition-types.md</p>
                '''
            })
        
        if lighting_score < 75:
            suggestions.append({
                'title': '💡 ' + t('lighting_control'),
                'level': t('need_improvement'),
                'content': '''
                    <p><strong>''' + t('current_issue') + '''：</strong>''' + t('lighting_issue') + '''</p>
                    <p><strong>''' + t('improvement_suggestions') + '''：</strong></p>
                    <ul>
''' + t('lighting_suggestions') + '''
                    </ul>
                    <p><strong>''' + t('reference_resources') + '''：</strong>photo-tutor/references/lighting-theory.md</p>
                '''
            })
        
        if color_score < 75:
            suggestions.append({
                'title': '🎨 ' + t('color_usage'),
                'level': t('need_improvement'),
                'content': '''
                    <p><strong>''' + t('current_issue') + '''：</strong>''' + t('color_issue') + '''</p>
                    <p><strong>''' + t('improvement_suggestions') + '''：</strong></p>
                    <ul>
''' + t('color_suggestions') + '''
                    </ul>
                '''
            })
        
        # 如果都不错，给出进阶建议
        if not suggestions:
            suggestions.append({
                'title': '🌟 ' + t('advanced_improvement'),
                'level': t('excellent_level'),
                'content': '''
                    <p><strong>''' + t('current_level') + '''：</strong>''' + t('excellent_foundation') + '''</p>
                    <p><strong>''' + t('advanced_suggestions') + '''：</strong></p>
                    <ul>
''' + t('advanced_suggestions') + '''
                    </ul>
                '''
            })
        
        # 生成建议HTML
        for suggestion in suggestions:
            level_color = '#f44336' if suggestion['level'] == '重点关注' else '#ff9800' if suggestion['level'] == '需要提升' else '#4caf50'
            parts.append(f'''
                <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid {level_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <h4 style="margin: 0; color: #333;">{suggestion['title']}</h4>
                        <span style="background: {level_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">{suggestion['level']}</span>
                    </div>
                    {suggestion['content']}
                </div>
''')
        
        parts.append('            </div>\n')
        return ''.join(parts)
    
    def _build_practice_plan(self, result: Dict[str, Any]) -> str:
        """构建练习方案部分"""
        parts = []
        t = self.i18n.t
        parts.append('''
            <div class="section">
                <div class="section-title">📅 ''' + t('practice_plan') + '''</div>
                <p style="margin-bottom: 20px; color: #666;">''' + t('practice_intro') + '''</p>
''')
        
        # 短期练习（1-2周）
        parts.append('''
                <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                    <h4 style="color: #1976d2; margin-bottom: 12px;">📌 ''' + t('short_term') + '''</h4>
                    <div style="background: white; padding: 15px; border-radius: 6px; margin-bottom: 10px;">
                        <p><strong>''' + t('task1_title') + '''</strong></p>
                        <p style="margin-top: 8px;">''' + t('task1_content').replace('\n', '<br>') + '''</p>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 6px;">
                        <p><strong>''' + t('task2_title') + '''</strong></p>
                        <p style="margin-top: 8px;">''' + t('task2_content').replace('\n', '<br>') + '''</p>
                    </div>
                </div>
''')
        
        # 中期练习（1个月）
        parts.append('''
                <div style="background: #fff3e0; padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                    <h4 style="color: #f57c00; margin-bottom: 12px;">🎯 ''' + t('medium_term') + '''</h4>
                    <div style="background: white; padding: 15px; border-radius: 6px; margin-bottom: 10px;">
                        <p><strong>''' + t('task3_title') + '''</strong></p>
                        <p style="margin-top: 8px;">''' + t('task3_content').replace('\n', '<br>') + '''</p>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 6px;">
                        <p><strong>''' + t('task4_title') + '''</strong></p>
                        <p style="margin-top: 8px;">''' + t('task4_content').replace('\n', '<br>') + '''</p>
                    </div>
                </div>
''')
        
        # 长期目标（3个月）
        parts.append('''
                <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                    <h4 style="color: #388e3c; margin-bottom: 12px;">🚀 ''' + t('long_term') + '''</h4>
                    <div style="background: white; padding: 15px; border-radius: 6px; margin-bottom: 10px;">
                        <p><strong>''' + t('task5_title') + '''</strong></p>
                        <p style="margin-top: 8px;">''' + t('task5_content').replace('\n', '<br>') + '''</p>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 6px;">
                        <p><strong>''' + t('task6_title') + '''</strong></p>
                        <p style="margin-top: 8px;">''' + t('task6_content').replace('\n', '<br>') + '''</p>
                    </div>
                </div>
''')
        
        # 练习建议
        parts.append('''
                <div style="background: #f5f5f5; padding: 20px; border-radius: 8px;">
                    <h4 style="color: #333; margin-bottom: 12px;">💪 ''' + t('practice_tips') + '''</h4>
                    <p><strong>''' + t('frequency_suggestion') + '''：</strong></p>
                    <p style="margin-top: 8px;">''' + t('frequency_details').replace('\n', '<br>') + '''</p>
                    
                    <p style="margin-top: 15px;"><strong>''' + t('feedback_method') + '''：</strong></p>
                    <p style="margin-top: 8px;">''' + t('feedback_details').replace('\n', '<br>') + '''</p>
                    
                    <p style="margin-top: 15px; color: #667eea; font-weight: 600;">💡 ''' + t('remember') + '''</p>
                </div>
''')
        
        parts.append('            </div>\n')
        return ''.join(parts)
    
    def _build_basic_info(self, info: Dict[str, Any]) -> str:
        """构建基础信息HTML"""
        t = self.i18n.t
        
        # 确定方向
        if info.get('is_portrait'):
            orientation = t('orientation_portrait')
        elif info.get('is_landscape'):
            orientation = t('orientation_landscape')
        else:
            orientation = t('orientation_square')
        
        return f'''
            <div class="section">
                <div class="section-title">📸 {t('basic_info')}</div>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">{t('resolution')}</div>
                        <div class="info-value">{info.get('resolution', 'N/A')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">{t('aspect_ratio')}</div>
                        <div class="info-value">{info.get('aspect_ratio', 'N/A')} ({orientation})</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">{t('average_brightness')}</div>
                        <div class="info-value">{info.get('mean_brightness', 'N/A')} ({info.get('brightness_level', 'N/A')})</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">{t('contrast')}</div>
                        <div class="info-value">{info.get('contrast', 'N/A')} ({info.get('contrast_level', 'N/A')})</div>
                    </div>
                </div>
            </div>
'''
    
    def _build_color_analysis(self, analysis: Dict[str, Any]) -> str:
        """构建色彩分析HTML"""
        parts = []
        t = self.i18n.t
        parts.append('''
            <div class="section">
                <div class="section-title">🎨 ''' + t('color_analysis') + '''</div>
''')
        
        # 从 palette_analysis 中提取数据
        palette_data = analysis.get('palette_analysis', {})
        dominant_colors = palette_data.get('dominant_colors', [])
        harmony = palette_data.get('harmony', {})
        psychology = palette_data.get('psychology', {})
        quality = palette_data.get('quality', {})
        aesthetics_score = palette_data.get('aesthetics_score', 0)
        
        # 主要色彩
        if dominant_colors:
            parts.append('                <p style="margin-bottom: 10px;"><strong>' + t('dominant_colors') + ':</strong></p>\n')
            parts.append('                <div class="color-palette">\n')
            for color in dominant_colors[:5]:
                hex_code = color.get('hex', '#000000')
                name = color.get('color_name', 'unknown')
                percentage = round(color.get('percentage', 0) * 100, 1)
                parts.append(f'''
                    <div class="color-item">
                        <div class="color-swatch" style="background-color: {hex_code};"></div>
                        <div class="color-info">
                            <div><strong>{hex_code}</strong></div>
                            <div style="color: #666;">{name} · {percentage}%</div>
                        </div>
                    </div>
''')
            parts.append('                </div>\n')
        
        # 和谐度与评分 - 翻译描述
        harmony_score = harmony.get('score', 0) if harmony else 0
        harmony_type = harmony.get('type', 'N/A') if harmony else 'N/A'
        
        # 根据类型翻译描述
        harmony_desc = 'N/A'
        if harmony and harmony_type != 'N/A':
            desc_key = f'harmony_{harmony_type}'
            harmony_desc = t(desc_key, harmony.get('description', 'N/A'))
        
        parts.append('''
                <div style="margin-top: 20px;">
                    <p><strong>''' + t('color_harmony') + ''':</strong> <span class="score">''' + str(harmony_score) + '''/100</span></p>
                    <p style="margin-top: 10px;"><strong>''' + t('harmony_type') + ''':</strong> ''' + harmony_type + '''</p>
                    <p style="margin-top: 10px;"><strong>''' + t('description') + ''':</strong> ''' + harmony_desc + '''</p>
                    <p style="margin-top: 10px;"><strong>''' + t('aesthetics_score') + ''':</strong> <span class="score">''' + str(round(aesthetics_score, 1)) + '''/100</span></p>
                </div>
''')
        
        # 色彩心理学 - 翻译温度和强度描述
        if psychology:
            # 翻译情感关键词
            emotion_list = psychology.get('dominant_emotions', [])[:3]
            translated_emotions = []
            for emotion in emotion_list:
                emotion_key = f'emotion_{emotion}'
                translated_emotion = t(emotion_key, emotion)  # 如果找不到翻译，使用原文
                translated_emotions.append(translated_emotion)
            emotions = ', '.join(translated_emotions)
            
            temp = psychology.get('temperature', '')
            intensity = psychology.get('intensity', '')
            psych_score = round(psychology.get('psychology_score', 0), 1)
            
            # 翻译温度和强度描述
            temp_desc = ''
            if temp:
                temp_desc = t(f'temp_{temp}', psychology.get('temperature_description', ''))
            
            intensity_desc = ''
            if intensity:
                intensity_desc = t(f'intensity_{intensity}', psychology.get('intensity_description', ''))
            
            if emotions or temp_desc:
                parts.append('''
                <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 8px;">
                    <p><strong>''' + t('color_psychology') + ''':</strong></p>
                    <p style="margin-top: 8px;">• ''' + t('emotional_tendency') + ''': ''' + emotions + '''</p>
                    <p style="margin-top: 5px;">• ''' + temp_desc + '''</p>
                    <p style="margin-top: 5px;">• ''' + intensity_desc + '''</p>
                    <p style="margin-top: 8px;">• ''' + t('psychology_score') + ''': <strong>''' + str(psych_score) + '''/100</strong></p>
                </div>
''')
        
        parts.append('            </div>\n')
        return ''.join(parts)
    
    def _build_emotion_analysis(self, analysis: Dict[str, Any]) -> str:
        """构建情感分析HTML"""
        parts = []
        t = self.i18n.t
        parts.append('''
            <div class="section">
                <div class="section-title">❤️ ''' + t('emotion_analysis') + '''</div>
''')
        
        emotion_data = analysis.get('emotion_analysis', {})
        status = analysis.get('status', 'unknown')
        
        if emotion_data.get('method') == 'internlm_api' and emotion_data.get('success'):
            # AI分析
            parts.append(f'''
                <div class="emotion-text">
                    {emotion_data.get('analysis', '').replace(chr(10), '<br>')}
                </div>
''')
        else:
            # 基础分析
            parts.append(f'''
                <p><strong>主要情感:</strong> {emotion_data.get('primary_emotion', 'neutral')}</p>
''')
        
        parts.append('            </div>\n')
        return ''.join(parts)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量分析照片并生成HTML报告')
    parser.add_argument('images', nargs='+', help='照片文件路径（支持多个）')
    parser.add_argument('-o', '--output', help='输出HTML文件路径', default=None)
    parser.add_argument('-l', '--lang', choices=['zh', 'en'], default='zh', 
                       help='报告语言 (zh=中文, en=English)')
    
    args = parser.parse_args()
    
    # 创建分析器（传入语言参数）
    analyzer = BatchPhotoAnalyzer(lang=args.lang)
    
    # 验证文件存在
    valid_images = []
    for img_path in args.images:
        if os.path.exists(img_path):
            valid_images.append(img_path)
        else:
            print(f"⚠️  文件不存在: {img_path}")
    
    if not valid_images:
        print("❌ 没有有效的图片文件")
        return
    
    # 分析照片
    results = analyzer.analyze_batch(valid_images)
    
    # 生成报告
    output_path = analyzer.generate_html_report(results, args.output)
    
    print(f"\n✅ 所有完成！")
    print(f"   分析照片数: {len(results)}")
    print(f"   HTML报告: {os.path.abspath(output_path)}")
    print(f"\n💡 在浏览器中打开报告查看详细分析结果")


if __name__ == '__main__':
    main()
