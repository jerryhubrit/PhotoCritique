#!/usr/bin/env python3
"""
智能摄影学习助手 - Web 界面
支持多图上传、批量分析和报告生成
"""

import os
import sys
import json
import gradio as gr
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# 添加脚本路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'photo-tutor/scripts'))

from photo_analyzer import extract_basic_info
from color_analyzer import ColorAestheticsAnalyzer
from emotion_analyzer import EmotionAnalyzer


class PhotoTutorApp:
    """智能摄影学习助手应用"""
    
    def __init__(self):
        """初始化应用"""
        # 加载环境变量
        self._load_env()
        
        # 初始化分析器
        self.color_analyzer = ColorAestheticsAnalyzer()
        self.emotion_analyzer = EmotionAnalyzer()
        
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
    
    def analyze_single_photo(self, image_path: str) -> Dict[str, Any]:
        """
        分析单张照片
        
        Args:
            image_path: 照片路径
            
        Returns:
            分析结果字典
        """
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
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def format_basic_info(self, info: Dict[str, Any]) -> str:
        """格式化基础信息"""
        lines = []
        lines.append("### 📸 基础信息")
        lines.append(f"- **文件名**: {info.get('file_name', 'N/A')}")
        lines.append(f"- **分辨率**: {info.get('resolution', 'N/A')}")
        lines.append(f"- **长宽比**: {info.get('aspect_ratio', 'N/A')} ({'竖拍' if info.get('is_portrait') else '横拍' if info.get('is_landscape') else '方形'})")
        lines.append(f"- **平均亮度**: {info.get('mean_brightness', 'N/A')} ({info.get('brightness_level', 'N/A')})")
        lines.append(f"- **对比度**: {info.get('contrast', 'N/A')} ({info.get('contrast_level', 'N/A')})")
        
        # EXIF信息
        if 'aperture' in info or 'shutter_speed' in info or 'iso' in info:
            lines.append("\n**拍摄参数**:")
            if 'aperture' in info:
                lines.append(f"- 光圈: {info['aperture']}")
            if 'shutter_speed' in info:
                lines.append(f"- 快门: {info['shutter_speed']}")
            if 'iso' in info:
                lines.append(f"- ISO: {info['iso']}")
            if 'focal_length' in info:
                lines.append(f"- 焦距: {info['focal_length']}")
        
        return "\n".join(lines)
    
    def format_color_analysis(self, analysis: Dict[str, Any]) -> str:
        """格式化色彩分析"""
        lines = []
        lines.append("### 🎨 色彩美学分析")
        
        # 主要色彩
        palette = analysis.get('palette', {})
        dominant_colors = palette.get('dominant_colors', [])
        if dominant_colors:
            lines.append("\n**主要色彩**:")
            for i, color in enumerate(dominant_colors[:5], 1):
                hex_code = color.get('hex', 'N/A')
                name = color.get('name', 'unknown')
                percentage = color.get('percentage', 0)
                lines.append(f"{i}. <span style='color:{hex_code};font-weight:bold;'>●</span> {hex_code} ({name}) - {percentage}%")
        
        # 和谐度
        harmony = analysis.get('harmony', {})
        if harmony:
            lines.append(f"\n**色彩和谐度**: {harmony.get('score', 'N/A')}/100")
            lines.append(f"- 类型: {harmony.get('type', 'N/A')}")
            lines.append(f"- 描述: {harmony.get('description', 'N/A')}")
        
        # 色彩心理学
        emotion = palette.get('emotion', {})
        if emotion:
            lines.append(f"\n**色彩心理学**:")
            lines.append(f"- 主导情感: {', '.join(emotion.get('keywords', []))}")
            lines.append(f"- 色温: {emotion.get('temperature', 'N/A')}")
            lines.append(f"- 强度: {emotion.get('intensity', 'N/A')}")
            lines.append(f"- 心理学评分: {emotion.get('score', 'N/A')}/100")
        
        # 综合评分
        lines.append(f"\n**美学综合评分**: {analysis.get('overall_score', 'N/A')}/100")
        
        return "\n".join(lines)
    
    def format_emotion_analysis(self, analysis: Dict[str, Any]) -> str:
        """格式化情感分析"""
        lines = []
        lines.append("### ❤️ 情感分析")
        
        emotion_data = analysis.get('emotion_analysis', {})
        status = analysis.get('status', 'unknown')
        
        lines.append(f"\n**分析模式**: {status}")
        lines.append(f"**使用模型**: {analysis.get('model', 'N/A')}")
        
        if emotion_data.get('method') == 'internlm_api' and emotion_data.get('success'):
            lines.append("\n**📸 专业摄影师视角分析**:")
            lines.append("---")
            lines.append(emotion_data.get('analysis', ''))
            
            usage = emotion_data.get('usage', {})
            if usage:
                lines.append("\n---")
                lines.append(f"*API使用: 输入 {usage.get('prompt_tokens', 0)} tokens, 输出 {usage.get('completion_tokens', 0)} tokens*")
        else:
            # 基础分析
            lines.append("\n**基础情感分析**:")
            lines.append(f"- 主要情感: {emotion_data.get('primary_emotion', 'neutral')}")
            keywords = emotion_data.get('emotion_keywords', [])
            if keywords:
                lines.append(f"- 情感关键词: {', '.join(keywords)}")
            
            if emotion_data.get('error'):
                lines.append(f"\n⚠️ {emotion_data.get('error')}")
            
            lines.append("\n💡 *配置 InternLM API Key 可获得专业摄影师视角的深度分析*")
        
        return "\n".join(lines)
    
    def generate_report(self, image_files: List) -> str:
        """
        生成完整分析报告
        
        Args:
            image_files: 上传的图片文件列表
            
        Returns:
            Markdown格式的报告
        """
        if not image_files:
            return "⚠️ 请先上传照片"
        
        report_lines = []
        report_lines.append("# 📷 智能摄影学习助手 - 分析报告")
        report_lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"\n分析照片数量: {len(image_files)}")
        report_lines.append("\n---\n")
        
        # 分析每张照片
        for idx, image_file in enumerate(image_files, 1):
            image_path = image_file.name if hasattr(image_file, 'name') else str(image_file)
            
            report_lines.append(f"\n## 照片 {idx}: {os.path.basename(image_path)}")
            report_lines.append("\n")
            
            try:
                # 分析照片
                result = self.analyze_single_photo(image_path)
                
                if result.get('status') == 'success':
                    # 基础信息
                    if 'basic_info' in result:
                        report_lines.append(self.format_basic_info(result['basic_info']))
                        report_lines.append("\n")
                    
                    # 色彩分析
                    if 'color_analysis' in result:
                        report_lines.append(self.format_color_analysis(result['color_analysis']))
                        report_lines.append("\n")
                    
                    # 情感分析
                    if 'emotion_analysis' in result:
                        report_lines.append(self.format_emotion_analysis(result['emotion_analysis']))
                        report_lines.append("\n")
                else:
                    report_lines.append(f"❌ 分析失败: {result.get('error', '未知错误')}")
                
            except Exception as e:
                report_lines.append(f"❌ 处理出错: {str(e)}")
            
            report_lines.append("\n---\n")
        
        # 总结
        report_lines.append("\n## 📊 分析总结")
        report_lines.append(f"\n本次共分析了 {len(image_files)} 张照片。")
        report_lines.append("\n建议根据以上分析结果，针对性地改进摄影技巧。")
        report_lines.append("\n💡 更多摄影知识，请参考 `photo-tutor/references/` 目录下的资料。")
        
        return "\n".join(report_lines)


def create_ui():
    """创建 Gradio 界面"""
    app = PhotoTutorApp()
    
    # 使用简单的 Interface 而不是 Blocks
    demo = gr.Interface(
        fn=app.generate_report,
        inputs=gr.File(
            label="上传照片（支持多张）",
            file_count="multiple"
        ),
        outputs=gr.Markdown(label="分析报告"),
        title="📷 智能摄影学习助手",
        description="""
        上传你的照片，获得专业的摄影分析和学习建议！
        
        **功能特点**：
        - 📸 基础信息提取（分辨率、EXIF、曝光参数）
        - 🎨 色彩美学分析（和谐度、心理学、质量评分）
        - ❤️ AI 情感分析（InternLM 专业摄影师视角）
        
        **使用说明**：
        1. 上传一张或多张照片
        2. 点击"Submit"按钮
        3. 等待分析完成（每张图约需10-30秒）
        4. 查看生成的详细报告
        """,
        article="""
        ### 💡 提示
        - 支持 JPG、PNG 等常见格式
        - 建议上传清晰、完整的照片
        - 已配置 InternLM API，可获得专业分析
        
        ### 🔧 技术支持
        - **基础分析**: PIL、NumPy、scikit-image
        - **AI 分析**: InternLM 多模态模型
        - **界面**: Gradio
        """,
        allow_flagging="never"
    )
    
    return demo


if __name__ == "__main__":
    # 创建并启动应用
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
