#!/usr/bin/env python3
"""
XMP 预设导出（改进版）
基于分区色彩统计生成 Lightroom XMP 预设
支持 Split Toning、Color Grading、HSL 分通道调整
"""

import argparse
import sys
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

import numpy as np
from PIL import Image
from skimage.color import rgb2lab

from color_transfer import ColorTransferEngine


class XMPExporter:
    """
    将色彩统计信息转换为 Lightroom XMP 预设
    基于分区统计（shadows/midtones/highlights）驱动参数映射
    """

    # Lightroom HSL 色相区间（H 值范围，0-360）
    HSL_RANGES = {
        'Red':     (345, 15),    # 345-360, 0-15
        'Orange':  (15, 45),
        'Yellow':  (45, 75),
        'Green':   (75, 165),
        'Aqua':    (165, 195),
        'Blue':    (195, 255),
        'Purple':  (255, 315),
        'Magenta': (315, 345),
    }

    def export(
        self,
        reference_path: str,
        output_path: str,
        preset_name: Optional[str] = None,
    ) -> str:
        """
        从参考图生成 XMP 预设文件

        参数:
            reference_path: 参考图路径
            output_path: XMP 输出路径
            preset_name: 预设名称

        返回:
            输出文件路径
        """
        # 加载参考图
        img = Image.open(reference_path).convert('RGB')
        rgb = np.array(img).astype(np.float64) / 255.0
        lab = rgb2lab(rgb)

        # 提取统计信息
        engine = ColorTransferEngine()
        stats = engine._extract_full_stats(lab)
        zone_stats = stats['zones']
        global_stats = stats['global']

        # 计算各模块参数
        tone_params = self._compute_tone_params(zone_stats, global_stats)
        split_toning = self._compute_split_toning(zone_stats)
        hsl_params = self._compute_hsl_params(rgb)
        curves = self._compute_curves(zone_stats, global_stats)
        detail_params = self._compute_detail_params(global_stats)

        # 生成 XMP
        if preset_name is None:
            preset_name = f"Color Transfer from {Path(reference_path).stem}"

        xmp_content = self._build_xmp(
            preset_name, tone_params, split_toning, hsl_params, curves, detail_params
        )

        # 写入文件
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xmp_content)

        print(f"XMP 预设已生成: {output_path}")
        self._print_summary(tone_params, split_toning)
        return str(output_path)

    # ========== 参数计算 ==========

    def _compute_tone_params(self, zone_stats: dict, global_stats: dict) -> dict:
        """
        基于分区统计计算曝光/对比度参数
        """
        mid_L = zone_stats['midtones']['L']['mean']
        shadow_L = zone_stats['shadows']['L']['mean']
        highlight_L = zone_stats['highlights']['L']['mean']
        global_L_std = global_stats['L']['std']

        # 曝光: 基于中间调亮度（中间调才反映整体曝光意图）
        # 中性值约 50，偏离越大曝光偏移越大
        exposure = self._clamp((mid_L - 50) / 50.0 * 0.6, -5.0, 5.0)

        # 对比度: 基于高光和阴影的 L 差值
        tone_range = highlight_L - shadow_L
        # 正常范围约 40-60，低于 30 低对比，高于 70 高对比
        contrast = self._clamp((tone_range - 50) / 30.0 * 30.0, -100, 100)

        # 高光: 基于高光区的 L 值压缩程度
        # highlights_L 越低说明高光被压制
        highlights = self._clamp((highlight_L - 80) / 20.0 * -40.0, -100, 100)

        # 阴影: 基于阴影区的 L 值提亮程度
        # shadows_L 越高说明阴影被提亮
        shadows = self._clamp((shadow_L - 15) / 15.0 * 40.0, -100, 100)

        # 白色色阶和黑色色阶
        whites = self._clamp(highlights * 0.4, -100, 100)
        blacks = self._clamp(shadows * 0.6, -100, 100)

        # 清晰度: 基于 L 标准差（反映局部对比度）
        clarity = self._clamp((global_L_std - 20) / 15.0 * 25.0, -100, 100)

        # 去朦胧
        dehaze = self._clamp(clarity * 0.5, -100, 100)

        # 纹理
        texture = self._clamp(clarity * 0.2, -100, 100)

        # 自然饱和度: 基于 A/B 通道的全局色彩强度
        a_mean = global_stats['A']['mean']
        b_mean = global_stats['B']['mean']
        ab_magnitude = np.sqrt(a_mean**2 + b_mean**2)
        vibrance = self._clamp(ab_magnitude * 4.0, 0, 100)

        # 饱和度: 保守调整
        saturation = self._clamp(vibrance * 0.05, -10, 10)

        return {
            'Exposure2012': exposure,
            'Contrast2012': contrast,
            'Highlights2012': highlights,
            'Shadows2012': shadows,
            'Whites2012': whites,
            'Blacks2012': blacks,
            'Texture': texture,
            'Clarity2012': clarity,
            'Dehaze': dehaze,
            'Vibrance': vibrance,
            'Saturation': saturation,
        }

    def _compute_split_toning(self, zone_stats: dict) -> dict:
        """
        从分区的 A/B 均值推导 Split Toning 参数
        阴影的 A/B → ShadowHue/Sat
        高光的 A/B → HighlightHue/Sat
        """
        # 阴影着色
        shadow_a = zone_stats['shadows']['A']['mean']
        shadow_b = zone_stats['shadows']['B']['mean']
        shadow_hue = self._ab_to_hue(shadow_a, shadow_b)
        shadow_sat = self._clamp(np.sqrt(shadow_a**2 + shadow_b**2) * 1.5, 0, 100)

        # 高光着色
        high_a = zone_stats['highlights']['A']['mean']
        high_b = zone_stats['highlights']['B']['mean']
        highlight_hue = self._ab_to_hue(high_a, high_b)
        highlight_sat = self._clamp(np.sqrt(high_a**2 + high_b**2) * 1.5, 0, 100)

        # 色彩强度太弱时不着色（阈值降低以保留微妙色调）
        if shadow_sat < 2:
            shadow_sat = 0
        if highlight_sat < 2:
            highlight_sat = 0

        # Color Grading (Lightroom 新版)
        mid_a = zone_stats['midtones']['A']['mean']
        mid_b = zone_stats['midtones']['B']['mean']
        midtone_hue = self._ab_to_hue(mid_a, mid_b)
        midtone_sat = self._clamp(np.sqrt(mid_a**2 + mid_b**2) * 1.0, 0, 100)
        if midtone_sat < 2:
            midtone_sat = 0

        return {
            'SplitToningShadowHue': int(shadow_hue),
            'SplitToningShadowSaturation': int(shadow_sat),
            'SplitToningHighlightHue': int(highlight_hue),
            'SplitToningHighlightSaturation': int(highlight_sat),
            'SplitToningBalance': 0,
            'ColorGradeMidtoneHue': int(midtone_hue),
            'ColorGradeMidtoneSat': int(midtone_sat),
            'ColorGradeShadowLum': 0,
            'ColorGradeMidtoneLum': 0,
            'ColorGradeHighlightLum': 0,
            'ColorGradeBlending': 50,
            'ColorGradeGlobalHue': 0,
            'ColorGradeGlobalSat': 0,
            'ColorGradeGlobalLum': 0,
        }

    def _compute_hsl_params(self, rgb: np.ndarray) -> dict:
        """
        基于实际色相分布计算 HSL 分通道调整
        将图像按 Lightroom 的 8 个色相区间分别统计
        """
        from skimage.color import rgb2hsv

        hsv = rgb2hsv(rgb)
        h_channel = hsv[:, :, 0] * 360.0  # 0-360
        s_channel = hsv[:, :, 1]           # 0-1
        v_channel = hsv[:, :, 2]           # 0-1

        hue_adj = {}
        sat_adj = {}
        lum_adj = {}

        # 中性参考值（标准色相、标准饱和度、标准亮度）
        for color_name, (h_lo, h_hi) in self.HSL_RANGES.items():
            # 创建色相范围掩码
            if h_lo > h_hi:  # 跨越 0 度（如 Red: 345-15）
                mask = (h_channel >= h_lo) | (h_channel < h_hi)
            else:
                mask = (h_channel >= h_lo) & (h_channel < h_hi)

            # 只统计有一定饱和度的像素（排除灰色区域）
            mask = mask & (s_channel > 0.1)

            pixel_count = mask.sum()
            if pixel_count < 100:
                # 该色相范围内像素太少，不调整
                hue_adj[color_name] = 0
                sat_adj[color_name] = 0
                lum_adj[color_name] = 0
                continue

            # 该区间的平均饱和度和亮度
            avg_sat = float(s_channel[mask].mean())
            avg_val = float(v_channel[mask].mean())

            # 饱和度偏移: 与中性值 0.5 的偏差
            sat_adj[color_name] = int(self._clamp((avg_sat - 0.45) * 30.0, -20, 20))

            # 亮度偏移: 与中性值 0.5 的偏差
            lum_adj[color_name] = int(self._clamp((avg_val - 0.5) * 30.0, -20, 25))

            # 色相偏移: 保守不动（色相偏移很难从统计推断）
            hue_adj[color_name] = 0

        return {'hue': hue_adj, 'saturation': sat_adj, 'luminance': lum_adj}

    def _compute_curves(self, zone_stats: dict, global_stats: dict) -> dict:
        """
        计算参数化曲线和 RGB 通道曲线
        所有 RGB 通道曲线均由参考图的分区 A/B 统计推导
        LAB A 通道: +A 偏红/品红, -A 偏绿/青 → 影响红/绿通道
        LAB B 通道: +B 偏黄, -B 偏蓝 → 影响蓝/红通道
        """
        shadow_L = zone_stats['shadows']['L']['mean']
        highlight_L = zone_stats['highlights']['L']['mean']

        # 参数化曲线锚点
        parametric = {
            'ParametricShadows': int(self._clamp((shadow_L - 15) * 0.8, -50, 50)),
            'ParametricDarks': int(self._clamp((shadow_L - 20) * 1.0, -50, 50)),
            'ParametricLights': int(self._clamp((highlight_L - 80) * -0.6, -50, 50)),
            'ParametricHighlights': int(self._clamp((highlight_L - 85) * -0.4, -50, 50)),
            'ParametricShadowSplit': 25,
            'ParametricMidtoneSplit': 50,
            'ParametricHighlightSplit': 75,
        }

        # 基础曲线点
        shadow_lift = max(0, int((shadow_L - 10) * 0.5))
        tone_curve = [(0, 0), (63, min(80, 56 + shadow_lift)), (141, 141), (255, 255)]

        # 提取各区间 A/B 统计
        shadow_a = zone_stats['shadows']['A']['mean']
        shadow_b = zone_stats['shadows']['B']['mean']
        mid_a = zone_stats['midtones']['A']['mean']
        mid_b = zone_stats['midtones']['B']['mean']
        high_a = zone_stats['highlights']['A']['mean']
        high_b = zone_stats['highlights']['B']['mean']

        # === 红色通道 ===
        # A>0 偏红 → 提升红通道; B>0 偏黄 → 也含红色分量
        red_shadow_shift = int(self._clamp(shadow_a * 0.12 + shadow_b * 0.05, -12, 12))
        red_mid_shift = int(self._clamp(mid_a * 0.08 + mid_b * 0.03, -8, 8))
        red_high_shift = int(self._clamp(high_a * 0.10 + high_b * 0.04, -10, 10))

        red_curve = [
            (0, 0),
            (25, max(0, min(40, 22 + red_shadow_shift))),
            (128, max(80, min(175, 128 + red_mid_shift))),
            (200, max(160, min(240, 200 + red_high_shift))),
            (255, 255),
        ]

        # === 绿色通道 ===
        # A<0 偏绿 → 提升绿通道
        green_shadow_shift = int(self._clamp(-shadow_a * 0.10, -10, 10))
        green_mid_shift = int(self._clamp(-mid_a * 0.06, -6, 6))
        green_high_shift = int(self._clamp(-high_a * 0.08, -8, 8))

        green_curve = [
            (0, 0),
            (25, max(0, min(40, 22 + green_shadow_shift))),
            (128, max(80, min(175, 128 + green_mid_shift))),
            (200, max(160, min(240, 200 + green_high_shift))),
            (255, 255),
        ]

        # === 蓝色通道 ===
        # B<0 偏蓝 → 提升蓝通道; A<0 偏青也含蓝分量
        blue_shadow_shift = int(self._clamp(-shadow_b * 0.15 - shadow_a * 0.05, -15, 15))
        blue_mid_shift = int(self._clamp(-mid_b * 0.08, -8, 8))
        blue_high_shift = int(self._clamp(-high_b * 0.12 - high_a * 0.04, -12, 12))

        blue_curve = [
            (0, 0),
            (25, max(0, min(45, 22 + blue_shadow_shift))),
            (128, max(80, min(175, 128 + blue_mid_shift))),
            (200, max(160, min(245, 200 + blue_high_shift))),
            (255, 255),
        ]

        return {
            'parametric': parametric,
            'tone_curve': tone_curve,
            'red_curve': red_curve,
            'green_curve': green_curve,
            'blue_curve': blue_curve,
        }

    def _compute_detail_params(self, global_stats: dict) -> dict:
        """计算锐化和降噪参数"""
        L_std = global_stats['L']['std']
        clarity_factor = (L_std - 20) / 15.0

        return {
            'Sharpness': int(self._clamp(12 + clarity_factor * 8, 0, 80)),
            'SharpenRadius': 1.0,
            'SharpenDetail': 25,
            'SharpenEdgeMasking': 0,
            'LuminanceSmoothing': int(self._clamp(5 - clarity_factor * 2, 0, 50)),
            'LuminanceNoiseReductionDetail': 50,
            'LuminanceNoiseReductionContrast': 0,
            'ColorNoiseReduction': 25,
            'ColorNoiseReductionDetail': 50,
            'ColorNoiseReductionSmoothness': 50,
        }

    # ========== XMP 构建 ==========

    def _build_xmp(
        self,
        preset_name: str,
        tone: dict,
        split_toning: dict,
        hsl: dict,
        curves: dict,
        detail: dict,
    ) -> str:
        """构建完整的 XMP 文件内容"""
        uuid_str = str(uuid.uuid4())
        parametric = curves['parametric']

        lines = []
        lines.append('<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>')
        lines.append('<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 7.0-c000 1.000000, 0000/00/00-00:00:00        ">')
        lines.append(' <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">')
        lines.append('  <rdf:Description rdf:about=""')
        lines.append('    xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"')
        lines.append('    crs:PresetType="Normal"')
        lines.append('    crs:Cluster=""')
        lines.append(f'    crs:UUID="{uuid_str}"')
        lines.append('    crs:SupportsAmount="False"')
        lines.append('    crs:SupportsColor="True"')
        lines.append('    crs:SupportsMonochrome="True"')
        lines.append('    crs:SupportsHighDynamicRange="True"')
        lines.append('    crs:SupportsNormalDynamicRange="True"')
        lines.append('    crs:SupportsSceneReferred="True"')
        lines.append('    crs:SupportsOutputReferred="True"')
        lines.append('    crs:RequiresRGBTables="False"')
        lines.append('    crs:ShowInPresets="True"')
        lines.append('    crs:ShowInQuickActions="False"')
        lines.append('    crs:CameraModelRestriction=""')
        lines.append('    crs:Copyright=""')
        lines.append('    crs:ContactInfo=""')
        lines.append('    crs:Version="18.1"')
        lines.append('    crs:CompatibleVersion="285212672"')
        lines.append('    crs:ProcessVersion="15.4"')
        lines.append('    crs:WhiteBalance="As Shot"')

        # 基础调整参数
        lines.append(f'    crs:Exposure2012="{self._fmt(tone["Exposure2012"], plus=True)}"')
        lines.append(f'    crs:Contrast2012="{self._fmt(tone["Contrast2012"], plus=True)}"')
        lines.append(f'    crs:Highlights2012="{self._fmt(tone["Highlights2012"], plus=True)}"')
        lines.append(f'    crs:Shadows2012="{self._fmt(tone["Shadows2012"], plus=True)}"')
        lines.append(f'    crs:Whites2012="{self._fmt(tone["Whites2012"], plus=True)}"')
        lines.append(f'    crs:Blacks2012="{self._fmt(tone["Blacks2012"], plus=True)}"')
        lines.append(f'    crs:Texture="{int(tone["Texture"])}"')
        lines.append(f'    crs:Clarity2012="{self._fmt(tone["Clarity2012"], plus=True)}"')
        lines.append(f'    crs:Dehaze="{self._fmt(tone["Dehaze"], plus=True)}"')
        lines.append(f'    crs:Vibrance="{self._fmt(tone["Vibrance"], plus=True)}"')
        lines.append(f'    crs:Saturation="{int(tone["Saturation"])}"')

        # 参数化曲线
        lines.append(f'    crs:ParametricShadows="{parametric["ParametricShadows"]}"')
        lines.append(f'    crs:ParametricDarks="{parametric["ParametricDarks"]}"')
        lines.append(f'    crs:ParametricLights="{parametric["ParametricLights"]}"')
        lines.append(f'    crs:ParametricHighlights="{parametric["ParametricHighlights"]}"')
        lines.append(f'    crs:ParametricShadowSplit="{parametric["ParametricShadowSplit"]}"')
        lines.append(f'    crs:ParametricMidtoneSplit="{parametric["ParametricMidtoneSplit"]}"')
        lines.append(f'    crs:ParametricHighlightSplit="{parametric["ParametricHighlightSplit"]}"')

        # 锐化和降噪
        for key, val in detail.items():
            if isinstance(val, float):
                lines.append(f'    crs:{key}="{val:.1f}"')
            else:
                lines.append(f'    crs:{key}="{val}"')

        # HSL 调整
        for adj_type, adj_name in [('hue', 'Hue'), ('saturation', 'Saturation'), ('luminance', 'Luminance')]:
            for color in self.HSL_RANGES:
                val = hsl[adj_type].get(color, 0)
                lines.append(f'    crs:{adj_name}Adjustment{color}="{int(val)}"')

        # Split Toning
        for key, val in split_toning.items():
            lines.append(f'    crs:{key}="{val}"')

        # 其他固定参数
        lines.append('    crs:PerspectiveUpright="0"')
        lines.append('    crs:PerspectiveVertical="0"')
        lines.append('    crs:PerspectiveHorizontal="0"')
        lines.append('    crs:PerspectiveRotate="0.0"')
        lines.append('    crs:PerspectiveAspect="0"')
        lines.append('    crs:PerspectiveScale="100"')
        lines.append('    crs:PerspectiveX="0.00"')
        lines.append('    crs:PerspectiveY="0.00"')
        lines.append('    crs:ShadowTint="0"')
        lines.append('    crs:RedHue="0"')
        lines.append('    crs:RedSaturation="0"')
        lines.append('    crs:GreenHue="0"')
        lines.append('    crs:GreenSaturation="0"')
        lines.append('    crs:BlueHue="0"')
        lines.append('    crs:BlueSaturation="0"')
        lines.append('    crs:HDREditMode="0"')
        lines.append('    crs:CurveRefineSaturation="100"')
        lines.append('    crs:ConvertToGrayscale="False"')
        lines.append('    crs:ToneCurveName2012="Custom"')
        lines.append('    crs:AllowFilters="1"')
        lines.append('    crs:HasSettings="True"')
        lines.append('    crs:CropConstrainToWarp="0"')
        lines.append('   >')

        # Name
        lines.append('   <crs:Name>')
        lines.append('    <rdf:Alt>')
        lines.append(f'     <rdf:li xml:lang="x-default">{preset_name}</rdf:li>')
        lines.append('    </rdf:Alt>')
        lines.append('   </crs:Name>')

        for tag in ['ShortName', 'SortName', 'Group', 'Description']:
            lines.append(f'   <crs:{tag}>')
            lines.append('    <rdf:Alt>')
            lines.append('     <rdf:li xml:lang="x-default"/>')
            lines.append('    </rdf:Alt>')
            lines.append(f'   </crs:{tag}>')

        # ToneCurvePV2012
        lines.append('   <crs:ToneCurvePV2012>')
        lines.append('    <rdf:Seq>')
        for x, y in curves['tone_curve']:
            lines.append(f'     <rdf:li>{x}, {y}</rdf:li>')
        lines.append('    </rdf:Seq>')
        lines.append('   </crs:ToneCurvePV2012>')

        # RGB 通道曲线
        for ch_name, curve_key in [('Red', 'red_curve'), ('Green', 'green_curve'), ('Blue', 'blue_curve')]:
            lines.append(f'   <crs:ToneCurvePV2012{ch_name}>')
            lines.append('    <rdf:Seq>')
            for x, y in curves[curve_key]:
                lines.append(f'     <rdf:li>{x}, {y}</rdf:li>')
            lines.append('    </rdf:Seq>')
            lines.append(f'   </crs:ToneCurvePV2012{ch_name}>')

        # 闭合标签
        lines.append('  </rdf:Description>')
        lines.append(' </rdf:RDF>')
        lines.append('</x:xmpmeta>')
        lines.append('<?xpacket end="w"?>')

        return '\n'.join(lines)

    # ========== 工具函数 ==========

    @staticmethod
    def _ab_to_hue(a: float, b: float) -> float:
        """LAB 的 A/B 通道 → 色相角 (0-360)"""
        hue = np.degrees(np.arctan2(b, a))
        if hue < 0:
            hue += 360
        return hue

    @staticmethod
    def _clamp(value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, value))

    @staticmethod
    def _fmt(value: float, plus: bool = False) -> str:
        if plus and value >= 0:
            return f"+{value:.2f}"
        return f"{value:.2f}"

    def _print_summary(self, tone: dict, split_toning: dict):
        print(f"  曝光: {self._fmt(tone['Exposure2012'], plus=True)}")
        print(f"  对比度: {self._fmt(tone['Contrast2012'], plus=True)}")
        print(f"  自然饱和度: {self._fmt(tone['Vibrance'], plus=True)}")
        print(f"  清晰度: {self._fmt(tone['Clarity2012'], plus=True)}")
        shadow_hue = split_toning['SplitToningShadowHue']
        shadow_sat = split_toning['SplitToningShadowSaturation']
        high_hue = split_toning['SplitToningHighlightHue']
        high_sat = split_toning['SplitToningHighlightSaturation']
        print(f"  阴影着色: Hue={shadow_hue}, Sat={shadow_sat}")
        print(f"  高光着色: Hue={high_hue}, Sat={high_sat}")


def main():
    parser = argparse.ArgumentParser(description='XMP 预设导出（改进版）')
    parser.add_argument('--ref', required=True, help='参考图路径')
    parser.add_argument('--output', required=True, help='XMP 输出路径')
    parser.add_argument('--name', default=None, help='预设名称')

    args = parser.parse_args()

    if not Path(args.ref).exists():
        print(f"错误: 参考图不存在: {args.ref}", file=sys.stderr)
        sys.exit(1)

    exporter = XMPExporter()
    exporter.export(args.ref, args.output, preset_name=args.name)


if __name__ == '__main__':
    main()
