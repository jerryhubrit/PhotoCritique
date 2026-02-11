#!/usr/bin/env python3
"""
色彩风格迁移引擎
支持多种迁移方法：全局LAB统计迁移、分区迁移、直方图匹配、改进组合法
全程 float64 精度，仅最终输出时量化为 uint8
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import numpy as np
from PIL import Image
from skimage.color import rgb2lab, lab2rgb
from scipy.ndimage import gaussian_filter1d


class ColorTransferEngine:
    """
    色彩风格迁移引擎
    从参考图提取色调特征，应用到目标图
    """

    METHODS = ['global_lab', 'zone_based', 'histogram', 'improved']

    # 默认亮度区间边界 (L 通道范围 0~100)，实际使用时会根据图像自适应
    ZONE_SHADOW_MAX = 33.0
    ZONE_HIGHLIGHT_MIN = 66.0
    # sigmoid 软过渡宽度（加宽到 8 以获得更平滑的区间过渡）
    ZONE_TRANSITION_WIDTH = 8.0

    def transfer(
        self,
        reference_path: str,
        target_path: str,
        method: str = 'zone_based',
        strength: float = 1.0,
        preserve_luminance: bool = False
    ) -> Dict[str, Any]:
        """
        执行色彩迁移

        参数:
            reference_path: 参考图路径（带滤镜的图）
            target_path: 目标图路径（要处理的图）
            method: 迁移方法 'global_lab' | 'zone_based' | 'histogram' | 'improved'
            strength: 迁移强度 0.0~1.0
            preserve_luminance: 是否保留目标图的亮度通道

        返回:
            {
                'result_image': PIL.Image,
                'ref_stats': dict,
                'method': str,
                'processing_time': float
            }
        """
        if method not in self.METHODS:
            raise ValueError(f"不支持的迁移方法: {method}，可选: {self.METHODS}")

        start_time = time.time()

        # 加载图像 → float64 RGB [0, 1]
        ref_rgb = self._load_image(reference_path)
        tgt_rgb = self._load_image(target_path)

        # RGB → LAB (float64, L: 0~100, A/B: -128~127)
        ref_lab = rgb2lab(ref_rgb)
        tgt_lab = rgb2lab(tgt_rgb)

        # 提取参考图统计信息（全局 + 分区）
        ref_stats = self._extract_full_stats(ref_lab)

        # 保存原始目标图 LAB（用于 strength 混合和亮度保留）
        tgt_lab_original = tgt_lab.copy()

        # 根据方法执行迁移
        if method == 'global_lab':
            result_lab = self._transfer_global_lab(ref_lab, tgt_lab)
        elif method == 'zone_based':
            result_lab = self._transfer_zone_based(ref_lab, tgt_lab)
        elif method == 'histogram':
            result_lab = self._transfer_histogram(ref_lab, tgt_lab)
        elif method == 'improved':
            result_lab = self._transfer_improved(ref_lab, tgt_lab)

        # 亮度保留：用目标图原始 L 通道替换
        if preserve_luminance:
            result_lab[:, :, 0] = tgt_lab_original[:, :, 0]

        # 强度混合：result = original * (1 - strength) + transferred * strength
        if strength < 1.0:
            result_lab = tgt_lab_original * (1.0 - strength) + result_lab * strength

        # LAB → RGB → uint8（整个流程唯一的量化步骤）
        result_rgb = lab2rgb(result_lab)  # 返回 [0, 1] float
        result_rgb = np.clip(result_rgb * 255.0, 0, 255).astype(np.uint8)
        result_image = Image.fromarray(result_rgb, 'RGB')

        processing_time = time.time() - start_time

        return {
            'result_image': result_image,
            'ref_stats': ref_stats,
            'method': method,
            'processing_time': processing_time
        }

    # ========== 图像加载 ==========

    def _load_image(self, path: str) -> np.ndarray:
        """加载图像，返回 float64 RGB [0, 1]"""
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return np.array(img).astype(np.float64) / 255.0

    # ========== 统计信息提取 ==========

    def _compute_zone_boundaries(self, lab: np.ndarray) -> Tuple[float, float]:
        """
        根据图像的 L 通道分布自适应计算分区边界
        使用 25th 和 75th 百分位数，限制在合理范围内
        """
        L = lab[:, :, 0].flatten()
        p25 = float(np.percentile(L, 25))
        p75 = float(np.percentile(L, 75))
        # 限制范围，避免极端图片导致区间退化
        shadow_max = np.clip(p25, 15.0, 45.0)
        highlight_min = np.clip(p75, 55.0, 85.0)
        return shadow_max, highlight_min

    def _extract_full_stats(self, lab: np.ndarray) -> dict:
        """提取完整的色彩统计信息（全局 + 分区 + 直方图）"""
        shadow_max, highlight_min = self._compute_zone_boundaries(lab)
        stats = {
            'global': self._extract_global_stats(lab),
            'zones': self._extract_zone_stats(lab, shadow_max, highlight_min),
            'histograms': self._extract_histograms(lab),
            'zone_boundaries': {'shadow_max': shadow_max, 'highlight_min': highlight_min},
        }
        return stats

    def _extract_global_stats(self, lab: np.ndarray) -> dict:
        """提取全局 LAB 统计（均值、标准差）"""
        return {
            'L': {'mean': float(lab[:, :, 0].mean()), 'std': float(lab[:, :, 0].std())},
            'A': {'mean': float(lab[:, :, 1].mean()), 'std': float(lab[:, :, 1].std())},
            'B': {'mean': float(lab[:, :, 2].mean()), 'std': float(lab[:, :, 2].std())},
        }

    def _extract_zone_stats(
        self,
        lab: np.ndarray,
        shadow_max: Optional[float] = None,
        highlight_min: Optional[float] = None,
    ) -> dict:
        """
        按亮度区间提取分区统计
        边界由参数指定，未指定时使用自适应计算
        """
        if shadow_max is None or highlight_min is None:
            shadow_max, highlight_min = self._compute_zone_boundaries(lab)
        L = lab[:, :, 0]
        zones = {}
        zone_defs = {
            'shadows': (0, shadow_max),
            'midtones': (shadow_max, highlight_min),
            'highlights': (highlight_min, 100.0),
        }
        for zone_name, (lo, hi) in zone_defs.items():
            mask = (L >= lo) & (L < hi)
            pixel_count = mask.sum()
            if pixel_count < 10:
                # 该区间像素太少，用全局值兜底
                zones[zone_name] = {
                    'L': {'mean': float(L.mean()), 'std': float(L.std())},
                    'A': {'mean': float(lab[:, :, 1].mean()), 'std': float(lab[:, :, 1].std())},
                    'B': {'mean': float(lab[:, :, 2].mean()), 'std': float(lab[:, :, 2].std())},
                    'pixel_ratio': 0.0,
                }
            else:
                zones[zone_name] = {
                    'L': {'mean': float(lab[:, :, 0][mask].mean()), 'std': float(lab[:, :, 0][mask].std())},
                    'A': {'mean': float(lab[:, :, 1][mask].mean()), 'std': float(lab[:, :, 1][mask].std())},
                    'B': {'mean': float(lab[:, :, 2][mask].mean()), 'std': float(lab[:, :, 2][mask].std())},
                    'pixel_ratio': float(pixel_count / L.size),
                }
        return zones

    def _extract_histograms(self, lab: np.ndarray, bins: int = 512) -> dict:
        """提取直方图（归一化），默认 512 bin 以充分利用 float64 精度"""
        hists = {}
        ranges = {'L': (0, 100), 'A': (-128, 127), 'B': (-128, 127)}
        for i, (ch_name, (lo, hi)) in enumerate(ranges.items()):
            channel = lab[:, :, i].flatten()
            hist, bin_edges = np.histogram(channel, bins=bins, range=(lo, hi))
            hist = hist.astype(np.float64)
            hist = hist / (hist.sum() + 1e-10)
            hists[ch_name] = {
                'hist': hist,
                'bin_edges': bin_edges,
                'range': (lo, hi),
            }
        return hists

    # ========== 方法 1: 全局 LAB 迁移 (Reinhard) ==========

    def _transfer_global_lab(self, ref_lab: np.ndarray, tgt_lab: np.ndarray) -> np.ndarray:
        """
        Reinhard 色彩迁移
        对 LAB 每个通道: result = (target - target_mean) / target_std * ref_std + ref_mean
        """
        result = tgt_lab.copy()
        for i in range(3):
            ref_mean = ref_lab[:, :, i].mean()
            ref_std = ref_lab[:, :, i].std()
            tgt_mean = tgt_lab[:, :, i].mean()
            tgt_std = tgt_lab[:, :, i].std()
            if tgt_std < 1e-6:
                tgt_std = 1e-6
            result[:, :, i] = (tgt_lab[:, :, i] - tgt_mean) / tgt_std * ref_std + ref_mean
        return self._clamp_lab(result)

    # ========== 方法 2: 分区迁移 ==========

    def _transfer_zone_based(self, ref_lab: np.ndarray, tgt_lab: np.ndarray) -> np.ndarray:
        """
        分区色彩迁移
        按亮度将像素分为 shadows/midtones/highlights，每个区间独立做 Reinhard
        区间边界自适应 + sigmoid 软过渡
        """
        # 用参考图的亮度分布决定分区边界
        ref_shadow_max, ref_highlight_min = self._compute_zone_boundaries(ref_lab)
        tgt_shadow_max, tgt_highlight_min = self._compute_zone_boundaries(tgt_lab)

        ref_zones = self._extract_zone_stats(ref_lab, ref_shadow_max, ref_highlight_min)
        tgt_zones = self._extract_zone_stats(tgt_lab, tgt_shadow_max, tgt_highlight_min)

        tgt_L = tgt_lab[:, :, 0]
        result = tgt_lab.copy()

        # 用目标图的边界计算软权重（因为是对目标图像素分区）
        shadow_weight = self._sigmoid(tgt_shadow_max - tgt_L, self.ZONE_TRANSITION_WIDTH)
        highlight_weight = self._sigmoid(tgt_L - tgt_highlight_min, self.ZONE_TRANSITION_WIDTH)
        midtone_weight = 1.0 - shadow_weight - highlight_weight
        midtone_weight = np.clip(midtone_weight, 0, 1)

        # 归一化权重确保和为1
        weight_sum = shadow_weight + midtone_weight + highlight_weight
        weight_sum = np.maximum(weight_sum, 1e-10)
        shadow_weight /= weight_sum
        midtone_weight /= weight_sum
        highlight_weight /= weight_sum

        # 对 A/B 通道分区迁移（L 通道不动，由 preserve_luminance 控制）
        for ch in [1, 2]:  # A, B
            ch_name = 'A' if ch == 1 else 'B'

            # 每个区间独立做 Reinhard
            transferred_shadow = self._reinhard_channel(
                tgt_lab[:, :, ch],
                tgt_zones['shadows'][ch_name]['mean'], tgt_zones['shadows'][ch_name]['std'],
                ref_zones['shadows'][ch_name]['mean'], ref_zones['shadows'][ch_name]['std']
            )
            transferred_midtone = self._reinhard_channel(
                tgt_lab[:, :, ch],
                tgt_zones['midtones'][ch_name]['mean'], tgt_zones['midtones'][ch_name]['std'],
                ref_zones['midtones'][ch_name]['mean'], ref_zones['midtones'][ch_name]['std']
            )
            transferred_highlight = self._reinhard_channel(
                tgt_lab[:, :, ch],
                tgt_zones['highlights'][ch_name]['mean'], tgt_zones['highlights'][ch_name]['std'],
                ref_zones['highlights'][ch_name]['mean'], ref_zones['highlights'][ch_name]['std']
            )

            # 按软权重混合
            result[:, :, ch] = (
                shadow_weight * transferred_shadow +
                midtone_weight * transferred_midtone +
                highlight_weight * transferred_highlight
            )

        # L 通道也做全局 Reinhard（保持亮度分布一致）
        ref_L_mean = ref_lab[:, :, 0].mean()
        ref_L_std = ref_lab[:, :, 0].std()
        tgt_L_mean = tgt_lab[:, :, 0].mean()
        tgt_L_std = max(tgt_lab[:, :, 0].std(), 1e-6)
        result[:, :, 0] = (tgt_lab[:, :, 0] - tgt_L_mean) / tgt_L_std * ref_L_std + ref_L_mean

        return self._clamp_lab(result)

    def _reinhard_channel(
        self,
        channel: np.ndarray,
        src_mean: float, src_std: float,
        ref_mean: float, ref_std: float
    ) -> np.ndarray:
        """对单个通道做 Reinhard 迁移"""
        if src_std < 1e-6:
            src_std = 1e-6
        return (channel - src_mean) / src_std * ref_std + ref_mean

    @staticmethod
    def _sigmoid(x: np.ndarray, width: float) -> np.ndarray:
        """sigmoid 软过渡函数"""
        return 1.0 / (1.0 + np.exp(-x / max(width, 0.1)))

    # ========== 方法 3: 直方图匹配 ==========

    def _transfer_histogram(self, ref_lab: np.ndarray, tgt_lab: np.ndarray) -> np.ndarray:
        """
        LAB 空间逐通道直方图匹配
        使用 512 bin + CDF 线性插值对齐
        """
        result = tgt_lab.copy()
        ranges = [(0, 100), (-128, 127), (-128, 127)]

        for i, (lo, hi) in enumerate(ranges):
            result[:, :, i] = self._histogram_match_channel(
                tgt_lab[:, :, i], ref_lab[:, :, i], lo, hi
            )

        return self._clamp_lab(result)

    def _histogram_match_channel(
        self,
        src_channel: np.ndarray,
        ref_channel: np.ndarray,
        val_min: float,
        val_max: float,
        bins: int = 512
    ) -> np.ndarray:
        """
        单通道直方图匹配 (float64 精度)
        通过 CDF 对齐 + 线性插值实现
        """
        # 计算直方图和 CDF
        src_hist, src_edges = np.histogram(src_channel.flatten(), bins=bins, range=(val_min, val_max))
        ref_hist, ref_edges = np.histogram(ref_channel.flatten(), bins=bins, range=(val_min, val_max))

        src_cdf = src_hist.astype(np.float64).cumsum()
        src_cdf /= src_cdf[-1] + 1e-10

        ref_cdf = ref_hist.astype(np.float64).cumsum()
        ref_cdf /= ref_cdf[-1] + 1e-10

        # bin 中心值
        ref_centers = (ref_edges[:-1] + ref_edges[1:]) / 2.0

        # 建立映射：用 np.interp 做 CDF 线性插值（比逐 bin argmin 更平滑）
        lut = np.interp(src_cdf, ref_cdf, ref_centers)

        # 将源通道的值映射到对应的 bin index
        bin_width = (val_max - val_min) / bins
        src_bin_idx = ((src_channel - val_min) / bin_width).astype(np.int32)
        src_bin_idx = np.clip(src_bin_idx, 0, bins - 1)

        # 应用映射
        result = lut[src_bin_idx]
        return result

    # ========== 方法 4: 改进组合法 ==========

    def _transfer_improved(self, ref_lab: np.ndarray, tgt_lab: np.ndarray) -> np.ndarray:
        """
        改进组合法:
        1. 直方图匹配（对齐 L 分布形状）
        2. 分区 Reinhard（对齐 A/B 通道的区间色调）
        全程 float64，不做中间 uint8 量化
        """
        # 步骤 1：直方图匹配（主要对齐 L 通道的分布形状）
        step1 = self._transfer_histogram(ref_lab, tgt_lab)

        # 步骤 2：在直方图匹配的结果上，对 A/B 通道做分区 Reinhard
        ref_shadow_max, ref_highlight_min = self._compute_zone_boundaries(ref_lab)
        step1_shadow_max, step1_highlight_min = self._compute_zone_boundaries(step1)

        ref_zones = self._extract_zone_stats(ref_lab, ref_shadow_max, ref_highlight_min)
        step1_zones = self._extract_zone_stats(step1, step1_shadow_max, step1_highlight_min)

        tgt_L = step1[:, :, 0]
        result = step1.copy()

        # sigmoid 软权重（用 step1 的边界）
        shadow_weight = self._sigmoid(step1_shadow_max - tgt_L, self.ZONE_TRANSITION_WIDTH)
        highlight_weight = self._sigmoid(tgt_L - step1_highlight_min, self.ZONE_TRANSITION_WIDTH)
        midtone_weight = 1.0 - shadow_weight - highlight_weight
        midtone_weight = np.clip(midtone_weight, 0, 1)

        weight_sum = shadow_weight + midtone_weight + highlight_weight
        weight_sum = np.maximum(weight_sum, 1e-10)
        shadow_weight /= weight_sum
        midtone_weight /= weight_sum
        highlight_weight /= weight_sum

        # 只对 A/B 通道做分区 Reinhard（L 通道已经被直方图匹配处理好了）
        for ch in [1, 2]:
            ch_name = 'A' if ch == 1 else 'B'

            transferred_shadow = self._reinhard_channel(
                step1[:, :, ch],
                step1_zones['shadows'][ch_name]['mean'], step1_zones['shadows'][ch_name]['std'],
                ref_zones['shadows'][ch_name]['mean'], ref_zones['shadows'][ch_name]['std']
            )
            transferred_midtone = self._reinhard_channel(
                step1[:, :, ch],
                step1_zones['midtones'][ch_name]['mean'], step1_zones['midtones'][ch_name]['std'],
                ref_zones['midtones'][ch_name]['mean'], ref_zones['midtones'][ch_name]['std']
            )
            transferred_highlight = self._reinhard_channel(
                step1[:, :, ch],
                step1_zones['highlights'][ch_name]['mean'], step1_zones['highlights'][ch_name]['std'],
                ref_zones['highlights'][ch_name]['mean'], ref_zones['highlights'][ch_name]['std']
            )

            result[:, :, ch] = (
                shadow_weight * transferred_shadow +
                midtone_weight * transferred_midtone +
                highlight_weight * transferred_highlight
            )

        return self._clamp_lab(result)

    # ========== 工具函数 ==========

    @staticmethod
    def _clamp_lab(lab: np.ndarray) -> np.ndarray:
        """将 LAB 值裁剪到有效范围"""
        result = lab.copy()
        result[:, :, 0] = np.clip(result[:, :, 0], 0, 100)
        result[:, :, 1] = np.clip(result[:, :, 1], -128, 127)
        result[:, :, 2] = np.clip(result[:, :, 2], -128, 127)
        return result


def main():
    parser = argparse.ArgumentParser(description='色彩风格迁移引擎')
    parser.add_argument('--ref', required=True, help='参考图路径（带滤镜效果的图）')
    parser.add_argument('--target', required=True, help='目标图路径（要处理的图）')
    parser.add_argument('--output', required=True, help='输出图片路径')
    parser.add_argument('--method', default='zone_based',
                        choices=ColorTransferEngine.METHODS,
                        help='迁移方法 (默认: zone_based)')
    parser.add_argument('--strength', type=float, default=1.0,
                        help='迁移强度 0.0~1.0 (默认: 1.0)')
    parser.add_argument('--preserve-luminance', action='store_true',
                        help='保留目标图的亮度通道')

    args = parser.parse_args()

    # 验证输入
    if not Path(args.ref).exists():
        print(f"错误: 参考图不存在: {args.ref}", file=sys.stderr)
        sys.exit(1)
    if not Path(args.target).exists():
        print(f"错误: 目标图不存在: {args.target}", file=sys.stderr)
        sys.exit(1)

    # 执行迁移
    engine = ColorTransferEngine()
    print(f"方法: {args.method}, 强度: {args.strength}, 保留亮度: {args.preserve_luminance}")

    result = engine.transfer(
        reference_path=args.ref,
        target_path=args.target,
        method=args.method,
        strength=args.strength,
        preserve_luminance=args.preserve_luminance
    )

    # 保存结果
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result['result_image'].save(str(output_path), quality=95)

    print(f"结果已保存: {args.output}")
    print(f"处理时间: {result['processing_time']:.2f}秒")


if __name__ == '__main__':
    main()
