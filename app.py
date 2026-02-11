#!/usr/bin/env python3
"""
智能摄影学习助手 - Web 界面
支持多图上传、批量分析、报告生成、滤镜提取与色彩迁移
"""

import os
import sys
import tempfile
import time
import gradio as gr
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import numpy as np
from PIL import Image

# 添加脚本路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'photo-tutor/scripts'))

from photo_analyzer import extract_basic_info
from color_analyzer import ColorAestheticsAnalyzer
from emotion_analyzer import EmotionAnalyzer
from color_transfer import ColorTransferEngine
from lut_generator import LUTGenerator
from xmp_exporter import XMPExporter


class PhotoTutorApp:
    """智能摄影学习助手应用"""

    def __init__(self):
        """初始化应用"""
        self._load_env()
        self.color_analyzer = ColorAestheticsAnalyzer()
        self.emotion_analyzer = EmotionAnalyzer()
        self.transfer_engine = ColorTransferEngine()
        self.lut_generator = LUTGenerator(size=33)
        self.xmp_exporter = XMPExporter()

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
        """分析单张照片"""
        result = {
            "image_path": image_path,
            "image_name": os.path.basename(image_path),
            "timestamp": datetime.now().isoformat()
        }

        try:
            basic_info = extract_basic_info(image_path)
            result["basic_info"] = basic_info

            color_analysis = self.color_analyzer.analyze(image_path)
            result["color_analysis"] = color_analysis

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
        lines.append("### 基础信息")
        lines.append(f"- **文件名**: {info.get('file_name', 'N/A')}")
        lines.append(f"- **分辨率**: {info.get('resolution', 'N/A')}")
        lines.append(f"- **长宽比**: {info.get('aspect_ratio', 'N/A')} ({'竖拍' if info.get('is_portrait') else '横拍' if info.get('is_landscape') else '方形'})")
        lines.append(f"- **平均亮度**: {info.get('mean_brightness', 'N/A')} ({info.get('brightness_level', 'N/A')})")
        lines.append(f"- **对比度**: {info.get('contrast', 'N/A')} ({info.get('contrast_level', 'N/A')})")

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
        lines.append("### 色彩美学分析")

        palette = analysis.get('palette', {})
        dominant_colors = palette.get('dominant_colors', [])
        if dominant_colors:
            lines.append("\n**主要色彩**:")
            for i, color in enumerate(dominant_colors[:5], 1):
                hex_code = color.get('hex', 'N/A')
                name = color.get('name', 'unknown')
                percentage = color.get('percentage', 0)
                lines.append(f"{i}. <span style='color:{hex_code};font-weight:bold;'>●</span> {hex_code} ({name}) - {percentage}%")

        harmony = analysis.get('harmony', {})
        if harmony:
            lines.append(f"\n**色彩和谐度**: {harmony.get('score', 'N/A')}/100")
            lines.append(f"- 类型: {harmony.get('type', 'N/A')}")
            lines.append(f"- 描述: {harmony.get('description', 'N/A')}")

        emotion = palette.get('emotion', {})
        if emotion:
            lines.append(f"\n**色彩心理学**:")
            lines.append(f"- 主导情感: {', '.join(emotion.get('keywords', []))}")
            lines.append(f"- 色温: {emotion.get('temperature', 'N/A')}")
            lines.append(f"- 强度: {emotion.get('intensity', 'N/A')}")
            lines.append(f"- 心理学评分: {emotion.get('score', 'N/A')}/100")

        lines.append(f"\n**美学综合评分**: {analysis.get('overall_score', 'N/A')}/100")

        return "\n".join(lines)

    def format_emotion_analysis(self, analysis: Dict[str, Any]) -> str:
        """格式化情感分析"""
        lines = []
        lines.append("### 情感分析")

        emotion_data = analysis.get('emotion_analysis', {})
        status = analysis.get('status', 'unknown')

        lines.append(f"\n**分析模式**: {status}")
        lines.append(f"**使用模型**: {analysis.get('model', 'N/A')}")

        if emotion_data.get('method') == 'internlm_api' and emotion_data.get('success'):
            lines.append("\n**专业摄影师视角分析**:")
            lines.append("---")
            lines.append(emotion_data.get('analysis', ''))

            usage = emotion_data.get('usage', {})
            if usage:
                lines.append("\n---")
                lines.append(f"*API使用: 输入 {usage.get('prompt_tokens', 0)} tokens, 输出 {usage.get('completion_tokens', 0)} tokens*")
        else:
            lines.append("\n**基础情感分析**:")
            lines.append(f"- 主要情感: {emotion_data.get('primary_emotion', 'neutral')}")
            keywords = emotion_data.get('emotion_keywords', [])
            if keywords:
                lines.append(f"- 情感关键词: {', '.join(keywords)}")

            if emotion_data.get('error'):
                lines.append(f"\n{emotion_data.get('error')}")

            lines.append("\n*配置 InternLM API Key 可获得专业摄影师视角的深度分析*")

        return "\n".join(lines)

    def generate_report(self, image_files: List) -> str:
        """生成完整分析报告"""
        if not image_files:
            return "请先上传照片"

        report_lines = []
        report_lines.append("# 智能摄影学习助手 - 分析报告")
        report_lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"\n分析照片数量: {len(image_files)}")
        report_lines.append("\n---\n")

        for idx, image_file in enumerate(image_files, 1):
            image_path = image_file.name if hasattr(image_file, 'name') else str(image_file)

            report_lines.append(f"\n## 照片 {idx}: {os.path.basename(image_path)}")
            report_lines.append("\n")

            try:
                result = self.analyze_single_photo(image_path)

                if result.get('status') == 'success':
                    if 'basic_info' in result:
                        report_lines.append(self.format_basic_info(result['basic_info']))
                        report_lines.append("\n")
                    if 'color_analysis' in result:
                        report_lines.append(self.format_color_analysis(result['color_analysis']))
                        report_lines.append("\n")
                    if 'emotion_analysis' in result:
                        report_lines.append(self.format_emotion_analysis(result['emotion_analysis']))
                        report_lines.append("\n")
                else:
                    report_lines.append(f"分析失败: {result.get('error', '未知错误')}")

            except Exception as e:
                report_lines.append(f"处理出错: {str(e)}")

            report_lines.append("\n---\n")

        report_lines.append("\n## 分析总结")
        report_lines.append(f"\n本次共分析了 {len(image_files)} 张照片。")
        report_lines.append("\n建议根据以上分析结果，针对性地改进摄影技巧。")

        return "\n".join(report_lines)

    # ========== 滤镜迁移功能 ==========

    def handle_transfer(
        self,
        ref_image: Optional[str],
        tgt_image: Optional[str],
        method: str,
        strength: float,
        preserve_lum: bool,
    ) -> Tuple:
        """
        处理色彩迁移请求

        返回: (result_image, comparison_image, result_file, lut_file, xmp_file, report_md)
        """
        if ref_image is None or tgt_image is None:
            return None, None, None, None, None, "请上传参考图和目标图"

        try:
            # 解析方法名
            method_map = {
                "全局LAB统计迁移 (快速)": "global_lab",
                "分区迁移 (暗部/中间调/高光)": "zone_based",
                "直方图匹配 (精确)": "histogram",
                "改进组合法 (推荐)": "improved",
            }
            method_key = method_map.get(method, "zone_based")

            # 执行迁移
            result = self.transfer_engine.transfer(
                reference_path=ref_image,
                target_path=tgt_image,
                method=method_key,
                strength=strength,
                preserve_luminance=preserve_lum,
            )

            result_pil = result['result_image']
            proc_time = result['processing_time']

            # 生成前后对比图
            target_pil = Image.open(tgt_image).convert('RGB')
            comparison = self._create_comparison(target_pil, result_pil)

            # 保存结果图片到临时文件
            ts = int(time.time())
            result_path = os.path.join(tempfile.gettempdir(), f"transfer_result_{ts}.jpg")
            result_pil.save(result_path, quality=95)

            # 生成 .cube LUT
            lut_path = os.path.join(tempfile.gettempdir(), f"filter_{method_key}_{ts}.cube")
            lut_data = self.lut_generator.generate_from_transfer(
                reference_path=ref_image,
                method=method_key,
                strength=strength,
                engine=self.transfer_engine,
            )
            self.lut_generator.export_cube(lut_data, lut_path, title=f"PhotoAI {method_key}")

            # 生成 .xmp 预设
            xmp_path = os.path.join(tempfile.gettempdir(), f"preset_{ts}.xmp")
            self.xmp_exporter.export(ref_image, xmp_path)

            # 生成报告
            report = self._generate_transfer_report(result, method, strength, preserve_lum, proc_time)

            return result_pil, comparison, result_path, lut_path, xmp_path, report

        except Exception as e:
            error_msg = f"迁移失败: {str(e)}"
            return None, None, None, None, None, error_msg

    def _create_comparison(self, original: Image.Image, result: Image.Image) -> Image.Image:
        """创建前后对比图（并排）"""
        # 统一高度
        height = min(original.height, result.height, 800)

        orig_w = int(original.width * height / original.height)
        result_w = int(result.width * height / result.height)

        orig_resized = original.resize((orig_w, height), Image.Resampling.LANCZOS)
        result_resized = result.resize((result_w, height), Image.Resampling.LANCZOS)

        # 拼接，中间加 4px 白色分割线
        gap = 4
        total_w = orig_w + gap + result_w
        canvas = Image.new('RGB', (total_w, height), (255, 255, 255))
        canvas.paste(orig_resized, (0, 0))
        canvas.paste(result_resized, (orig_w + gap, 0))

        return canvas

    def _generate_transfer_report(
        self, result: dict, method: str, strength: float, preserve_lum: bool, proc_time: float
    ) -> str:
        """生成迁移结果报告"""
        ref_stats = result.get('ref_stats', {})
        zones = ref_stats.get('zones', {})

        lines = [
            "### 迁移结果",
            f"- **方法**: {method}",
            f"- **强度**: {strength}",
            f"- **保留亮度**: {'是' if preserve_lum else '否'}",
            f"- **处理时间**: {proc_time:.2f}秒",
            "",
            "### 参考图色彩特征",
        ]

        global_stats = ref_stats.get('global', {})
        if global_stats:
            a_mean = global_stats.get('A', {}).get('mean', 0)
            b_mean = global_stats.get('B', {}).get('mean', 0)
            if a_mean > 3:
                lines.append("- 整体偏暖（偏红/品红）")
            elif a_mean < -3:
                lines.append("- 整体偏冷（偏绿/青）")
            if b_mean > 3:
                lines.append("- 整体偏黄/暖调")
            elif b_mean < -3:
                lines.append("- 整体偏蓝/冷调")

        if zones:
            lines.append("")
            lines.append("### 分区色调分析")
            for zone_name in ['shadows', 'midtones', 'highlights']:
                zone = zones.get(zone_name, {})
                a = zone.get('A', {}).get('mean', 0)
                b = zone.get('B', {}).get('mean', 0)
                ratio = zone.get('pixel_ratio', 0)
                zone_cn = {'shadows': '暗部', 'midtones': '中间调', 'highlights': '高光'}
                tone_desc = self._describe_ab(a, b)
                lines.append(f"- **{zone_cn[zone_name]}** ({ratio*100:.0f}%): {tone_desc}")

        lines.append("")
        lines.append("### 导出文件")
        lines.append("- 结果图片 (.jpg)")
        lines.append("- 3D LUT (.cube) — 可导入 Premiere/达芬奇/FCPX")
        lines.append("- XMP 预设 (.xmp) — 可导入 Lightroom")

        return "\n".join(lines)

    @staticmethod
    def _describe_ab(a: float, b: float) -> str:
        """根据 A/B 值描述色调倾向"""
        parts = []
        if abs(a) < 2 and abs(b) < 2:
            return "中性"
        if a > 2:
            parts.append("偏红/品红")
        elif a < -2:
            parts.append("偏绿/青")
        if b > 2:
            parts.append("偏黄/暖")
        elif b < -2:
            parts.append("偏蓝/冷")
        return "、".join(parts) if parts else "接近中性"

    # ========== Hald CLUT 精确滤镜提取 ==========

    def handle_hald_generate(self, level: int) -> Tuple:
        """生成 Identity Hald CLUT 图片"""
        try:
            level = int(level)
            hald_img = self.lut_generator.generate_hald_identity(level=level)

            ts = int(time.time())
            hald_path = os.path.join(
                tempfile.gettempdir(), f"identity_hald_L{level}_{ts}.png"
            )
            hald_img.save(hald_path)

            return hald_img, hald_path
        except Exception as e:
            return None, None

    def handle_hald_extract(
        self,
        processed_hald_path: Optional[str],
        target_image_path: Optional[str],
    ) -> Tuple:
        """
        从处理过的 Hald 图提取 LUT，应用到目标图

        返回: (result_image, comparison_image, result_file, lut_file, hald_file, report_md)
        """
        if processed_hald_path is None:
            return None, None, None, None, None, "请上传处理过的 Hald 图片"

        try:
            processed_hald = Image.open(processed_hald_path).convert('RGB')

            # 提取 LUT
            lut_data = self.lut_generator.hald_to_lut(processed_hald)
            N = lut_data.shape[0]
            level = round(N ** 0.5)

            ts = int(time.time())

            # 导出 .cube
            lut_path = os.path.join(
                tempfile.gettempdir(), f"hald_extracted_{ts}.cube"
            )
            gen = LUTGenerator(size=N)
            gen.export_cube(lut_data, lut_path, title=f"Hald Extracted L{level}")

            # 导出 Hald PNG
            hald_export = self.lut_generator.lut_to_hald(lut_data)
            hald_export_path = os.path.join(
                tempfile.gettempdir(), f"hald_filter_{ts}.png"
            )
            hald_export.save(hald_export_path)

            # 应用到目标图
            result_pil = None
            comparison = None
            result_path = None

            if target_image_path is not None:
                target_pil = Image.open(target_image_path).convert('RGB')
                target_arr = np.array(target_pil)
                result_arr = gen.apply_lut(target_arr, lut_data)
                result_pil = Image.fromarray(result_arr, 'RGB')

                comparison = self._create_comparison(target_pil, result_pil)

                result_path = os.path.join(
                    tempfile.gettempdir(), f"hald_result_{ts}.jpg"
                )
                result_pil.save(result_path, quality=95)

            # 检查 JPEG 警告
            is_jpeg = processed_hald_path.lower().endswith(('.jpg', '.jpeg'))

            # 生成报告
            report = self._generate_hald_report(N, level, is_jpeg, lut_data)

            return result_pil, comparison, result_path, lut_path, hald_export_path, report

        except Exception as e:
            error_msg = f"提取失败: {str(e)}"
            return None, None, None, None, None, error_msg

    def _generate_hald_report(
        self, N: int, level: int, is_jpeg: bool, lut_data: np.ndarray
    ) -> str:
        """生成 Hald 提取结果报告"""
        # 计算 LUT 与 identity 的偏差
        grid = np.linspace(0, 1, N)
        rr, gg, bb = np.meshgrid(grid, grid, grid, indexing='ij')
        identity = np.stack([rr, gg, bb], axis=-1)
        diff = np.abs(lut_data - identity)
        avg_shift = float(diff.mean()) * 255
        max_shift = float(diff.max()) * 255

        # 通道偏移分析
        r_shift = float((lut_data[:, :, :, 0] - identity[:, :, :, 0]).mean()) * 255
        g_shift = float((lut_data[:, :, :, 1] - identity[:, :, :, 1]).mean()) * 255
        b_shift = float((lut_data[:, :, :, 2] - identity[:, :, :, 2]).mean()) * 255

        lines = [
            "### Hald 滤镜提取结果",
            f"- **Hald 等级**: {level}",
            f"- **LUT 分辨率**: {N}x{N}x{N} ({N**3:,} 种颜色映射)",
            "",
        ]

        if is_jpeg:
            lines.append("**注意**: 上传的 Hald 图片为 JPEG 格式，压缩可能导致精度损失。建议使用 PNG 格式。")
            lines.append("")

        lines.extend([
            "### 滤镜特征分析",
            f"- **平均色彩偏移**: {avg_shift:.1f}/255",
            f"- **最大色彩偏移**: {max_shift:.1f}/255",
            f"- **红色通道偏移**: {r_shift:+.1f}",
            f"- **绿色通道偏移**: {g_shift:+.1f}",
            f"- **蓝色通道偏移**: {b_shift:+.1f}",
            "",
        ])

        if avg_shift < 1:
            lines.append("滤镜强度: 极弱（几乎无变化）")
        elif avg_shift < 5:
            lines.append("滤镜强度: 轻微调色")
        elif avg_shift < 15:
            lines.append("滤镜强度: 中等")
        elif avg_shift < 30:
            lines.append("滤镜强度: 较强")
        else:
            lines.append("滤镜强度: 强烈风格化")

        lines.extend([
            "",
            "### 导出文件",
            "- 3D LUT (.cube) — 可导入 Premiere/达芬奇/FCPX/Lightroom",
            "- Hald CLUT (.png) — 可分享的滤镜文件",
        ])

        return "\n".join(lines)


def create_ui():
    """创建 Gradio 界面"""
    app = PhotoTutorApp()

    with gr.Blocks(title="智能摄影学习助手") as demo:
        gr.Markdown("# 智能摄影学习助手")

        with gr.Tabs():
            # ========== Tab 1: 照片分析（保持原有功能） ==========
            with gr.TabItem("照片分析"):
                gr.Markdown("""
                上传你的照片，获得专业的摄影分析和学习建议！

                **功能**: 基础信息提取、色彩美学分析、AI 情感分析
                """)

                file_input = gr.File(
                    label="上传照片（支持多张）",
                    file_count="multiple"
                )
                analyze_btn = gr.Button("开始分析", variant="primary")
                report_output = gr.Markdown(label="分析报告")

                analyze_btn.click(
                    fn=app.generate_report,
                    inputs=file_input,
                    outputs=report_output
                )

            # ========== Tab 2: 滤镜提取与迁移 ==========
            with gr.TabItem("滤镜提取与迁移"):
                gr.Markdown("""
                上传一张带滤镜效果的参考图，将其色调风格迁移到目标图上。
                支持导出 .cube LUT 和 .xmp Lightroom 预设。
                """)

                with gr.Row():
                    ref_image = gr.Image(
                        label="参考图（风格来源 - 带滤镜的照片）",
                        type="filepath"
                    )
                    tgt_image = gr.Image(
                        label="目标图（待处理的照片）",
                        type="filepath"
                    )

                with gr.Row():
                    method_dropdown = gr.Dropdown(
                        choices=[
                            "全局LAB统计迁移 (快速)",
                            "分区迁移 (暗部/中间调/高光)",
                            "直方图匹配 (精确)",
                            "改进组合法 (推荐)",
                        ],
                        value="改进组合法 (推荐)",
                        label="迁移方法"
                    )
                    strength_slider = gr.Slider(
                        minimum=0.0, maximum=1.0, value=0.8, step=0.05,
                        label="迁移强度"
                    )
                    preserve_lum = gr.Checkbox(
                        label="保留原图亮度",
                        value=False
                    )

                transfer_btn = gr.Button("开始迁移", variant="primary")

                with gr.Row():
                    result_image = gr.Image(label="迁移结果")
                    comparison_image = gr.Image(label="前后对比")

                with gr.Row():
                    download_image = gr.File(label="下载结果图片 (.jpg)")
                    download_lut = gr.File(label="下载 3D LUT (.cube)")
                    download_xmp = gr.File(label="下载 XMP 预设 (.xmp)")

                quality_report = gr.Markdown(label="迁移报告")

                transfer_btn.click(
                    fn=app.handle_transfer,
                    inputs=[ref_image, tgt_image, method_dropdown, strength_slider, preserve_lum],
                    outputs=[result_image, comparison_image, download_image, download_lut, download_xmp, quality_report]
                )

            # ========== Tab 3: Hald 精确滤镜提取 ==========
            with gr.TabItem("Hald 精确滤镜提取"):
                gr.Markdown("""
                通过 Hald CLUT 技术精确提取任意滤镜的完整色彩映射。

                **使用流程**:
                1. 生成 Identity Hald 图片并下载
                2. 在目标 App 中（如 Instagram、VSCO、Lightroom）对该图片应用滤镜，保存为 **PNG** 格式
                3. 上传处理后的 Hald 图片，即可精确提取滤镜并应用到任意照片
                """)

                gr.Markdown("### 第1步：生成 Identity Hald")

                with gr.Row():
                    hald_level = gr.Dropdown(
                        choices=["8 (512x512, 推荐)", "12 (1728x1728, 高精度)"],
                        value="8 (512x512, 推荐)",
                        label="Hald 等级",
                    )
                    hald_gen_btn = gr.Button("生成 Identity Hald", variant="primary")

                with gr.Row():
                    hald_preview = gr.Image(label="Identity Hald 预览")
                    hald_download = gr.File(label="下载 Identity Hald (.png)")

                # 解析 level 并生成
                def _parse_and_generate(level_str):
                    level = int(level_str.split(" ")[0])
                    return app.handle_hald_generate(level)

                hald_gen_btn.click(
                    fn=_parse_and_generate,
                    inputs=hald_level,
                    outputs=[hald_preview, hald_download],
                )

                gr.Markdown("### 第2步：上传处理过的 Hald")

                hald_processed = gr.Image(
                    label="处理过的 Hald 图片（应用滤镜后的结果，建议 PNG 格式）",
                    type="filepath",
                )

                gr.Markdown("### 第3步：应用到目标照片")

                hald_target = gr.Image(
                    label="目标照片（可选 — 不上传则只导出 LUT）",
                    type="filepath",
                )
                hald_extract_btn = gr.Button("提取滤镜并应用", variant="primary")

                with gr.Row():
                    hald_result_image = gr.Image(label="应用结果")
                    hald_comparison = gr.Image(label="前后对比")

                with gr.Row():
                    hald_dl_result = gr.File(label="下载结果图片 (.jpg)")
                    hald_dl_cube = gr.File(label="下载 3D LUT (.cube)")
                    hald_dl_hald = gr.File(label="下载滤镜 Hald (.png)")

                hald_report = gr.Markdown(label="提取报告")

                hald_extract_btn.click(
                    fn=app.handle_hald_extract,
                    inputs=[hald_processed, hald_target],
                    outputs=[
                        hald_result_image, hald_comparison,
                        hald_dl_result, hald_dl_cube, hald_dl_hald,
                        hald_report,
                    ],
                )

    return demo


def _patch_gradio_api_bug():
    """
    修复 Gradio 4.39.0 的 json_schema_to_python_type bug:
    当 additionalProperties 为 bool 时 get_type(True) 会崩溃
    """
    try:
        import gradio_client.utils as gu
        original_fn = gu._json_schema_to_python_type

        def _patched(schema, defs):
            if isinstance(schema, bool):
                return "Any"
            return original_fn(schema, defs)

        gu._json_schema_to_python_type = _patched
    except Exception:
        pass


if __name__ == "__main__":
    _patch_gradio_api_bug()
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
