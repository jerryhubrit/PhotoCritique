#!/usr/bin/env python3
"""
3D LUT 生成器
将色彩迁移结果导出为 .cube 格式的 3D LUT 文件
兼容 Lightroom Classic、Premiere Pro、DaVinci Resolve、FCPX、Capture One 等
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image
from scipy.interpolate import RegularGridInterpolator
from skimage.color import rgb2lab, lab2rgb

from color_transfer import ColorTransferEngine


class LUTGenerator:
    """
    3D LUT 生成与导出
    通过将色彩迁移应用到 identity lattice 来生成 LUT
    """

    def __init__(self, size: int = 33):
        """
        参数:
            size: LUT 网格大小 (常用: 17, 33, 65)
                  33 是兼顾精度和文件大小的标准选择
        """
        self.size = size

    def generate_from_transfer(
        self,
        reference_path: str,
        method: str = 'zone_based',
        strength: float = 1.0,
        engine: Optional[ColorTransferEngine] = None
    ) -> np.ndarray:
        """
        通过色彩迁移生成 3D LUT

        原理:
        1. 构建 identity lattice — 均匀覆盖整个 RGB 色彩空间的合成图
        2. 将迁移算法应用到这张合成图
        3. 输入→输出的映射关系就是 3D LUT

        参数:
            reference_path: 参考图路径
            method: 迁移方法
            strength: 迁移强度
            engine: 迁移引擎实例（可复用）

        返回:
            np.ndarray, shape (size, size, size, 3), float [0, 1]
        """
        if engine is None:
            engine = ColorTransferEngine()

        # 构建 identity lattice 作为合成图像
        identity_image = self._create_identity_image()

        # 加载参考图 → LAB
        ref_rgb = engine._load_image(reference_path)
        ref_lab = rgb2lab(ref_rgb)

        # identity 图像 → LAB
        identity_lab = rgb2lab(identity_image)

        # 提取参考图统计信息
        ref_stats = engine._extract_full_stats(ref_lab)

        # 根据方法应用迁移到 identity lattice
        if method == 'global_lab':
            result_lab = engine._transfer_global_lab(ref_lab, identity_lab)
        elif method == 'zone_based':
            result_lab = engine._transfer_zone_based(ref_lab, identity_lab)
        elif method == 'histogram':
            result_lab = engine._transfer_histogram(ref_lab, identity_lab)
        elif method == 'improved':
            result_lab = engine._transfer_improved(ref_lab, identity_lab)
        else:
            raise ValueError(f"不支持的迁移方法: {method}")

        # 强度混合
        if strength < 1.0:
            result_lab = identity_lab * (1.0 - strength) + result_lab * strength

        # LAB → RGB [0, 1]
        result_rgb = lab2rgb(result_lab)
        result_rgb = np.clip(result_rgb, 0, 1)

        # 重塑为 (size, size, size, 3)
        lut_data = result_rgb.reshape(self.size, self.size, self.size, 3)

        return lut_data

    def _create_identity_image(self) -> np.ndarray:
        """
        创建 identity lattice 合成图像
        每个像素的 RGB 值均匀覆盖 [0, 1] 色彩空间

        返回:
            np.ndarray, shape (size*size, size, 3), float [0, 1]
        """
        s = self.size
        # 生成 size^3 个均匀采样的 RGB 值
        r = np.linspace(0, 1, s)
        g = np.linspace(0, 1, s)
        b = np.linspace(0, 1, s)

        # 构建 3D 网格，然后展平为 2D 图像
        # 排列顺序: R 变化最快, 然后 G, 然后 B（.cube 标准顺序）
        rr, gg, bb = np.meshgrid(r, g, b, indexing='ij')
        lattice = np.stack([rr, gg, bb], axis=-1)  # shape: (s, s, s, 3)

        # 重塑为 2D 图像用于迁移处理: (s*s, s, 3)
        image = lattice.reshape(s * s, s, 3)
        return image

    def export_cube(self, lut_data: np.ndarray, output_path: str, title: str = "PhotoAI Filter"):
        """
        导出为 .cube 格式文件

        .cube 格式说明:
        - 行业标准 3D LUT 格式
        - 纯文本，每行一个 RGB 三元组
        - R 变化最快，然后 G，然后 B

        参数:
            lut_data: shape (size, size, size, 3), float [0, 1]
            output_path: 输出文件路径
            title: LUT 标题
        """
        s = lut_data.shape[0]

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(f'TITLE "{title}"\n')
            f.write(f'LUT_3D_SIZE {s}\n')
            f.write('\n')
            f.write('DOMAIN_MIN 0.0 0.0 0.0\n')
            f.write('DOMAIN_MAX 1.0 1.0 1.0\n')
            f.write('\n')

            # 按 .cube 标准顺序输出: B(外层) → G(中层) → R(内层)
            for bi in range(s):
                for gi in range(s):
                    for ri in range(s):
                        r, g, b = lut_data[ri, gi, bi]
                        f.write(f'{r:.6f} {g:.6f} {b:.6f}\n')

        print(f"LUT 已导出: {output_path} ({s}x{s}x{s})")

    def load_cube(self, cube_path: str) -> np.ndarray:
        """
        加载 .cube 文件

        返回:
            np.ndarray, shape (size, size, size, 3), float [0, 1]
        """
        size = None
        data_lines = []

        with open(cube_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('TITLE'):
                    continue
                if line.startswith('DOMAIN_MIN') or line.startswith('DOMAIN_MAX'):
                    continue
                if line.startswith('LUT_3D_SIZE'):
                    size = int(line.split()[-1])
                    continue
                # 数据行
                parts = line.split()
                if len(parts) == 3:
                    data_lines.append([float(x) for x in parts])

        if size is None:
            raise ValueError(f"无法解析 LUT 大小: {cube_path}")

        data = np.array(data_lines)
        expected = size ** 3
        if len(data) != expected:
            raise ValueError(f"数据行数 {len(data)} != 预期 {expected}")

        # .cube 顺序: B(外) → G(中) → R(内)，重塑为 (R, G, B, 3)
        lut = np.zeros((size, size, size, 3))
        idx = 0
        for bi in range(size):
            for gi in range(size):
                for ri in range(size):
                    lut[ri, gi, bi] = data[idx]
                    idx += 1

        return lut

    def apply_lut(
        self,
        image: np.ndarray,
        lut_data: np.ndarray,
        interpolation: str = 'cubic',
    ) -> np.ndarray:
        """
        将 3D LUT 应用到图片

        参数:
            image: RGB 图像, shape (H, W, 3), uint8 [0, 255] 或 float [0, 1]
            lut_data: LUT 数据, shape (size, size, size, 3), float [0, 1]
            interpolation: 插值方法 'linear' 或 'cubic'（默认 cubic，渐变更平滑）

        返回:
            np.ndarray, shape (H, W, 3), uint8 [0, 255]
        """
        s = lut_data.shape[0]

        # 归一化输入到 [0, 1]
        if image.dtype == np.uint8:
            img_float = image.astype(np.float64) / 255.0
        else:
            img_float = image.astype(np.float64)

        # cubic 需要 scipy >= 1.9 的 RegularGridInterpolator 支持
        # 如果不支持则回退到 linear
        method = interpolation
        if method == 'cubic' and s < 4:
            method = 'linear'

        grid = np.linspace(0, 1, s)
        results = np.zeros_like(img_float)
        h, w = img_float.shape[:2]
        points = img_float.reshape(-1, 3)

        for ch in range(3):
            try:
                interpolator = RegularGridInterpolator(
                    (grid, grid, grid),
                    lut_data[:, :, :, ch],
                    method=method,
                    bounds_error=False,
                    fill_value=None,
                )
            except ValueError:
                # scipy 版本不支持 cubic，回退 linear
                interpolator = RegularGridInterpolator(
                    (grid, grid, grid),
                    lut_data[:, :, :, ch],
                    method='linear',
                    bounds_error=False,
                    fill_value=None,
                )
            results_flat = interpolator(points)
            results[:, :, ch] = results_flat.reshape(h, w)

        results = np.clip(results * 255.0, 0, 255).astype(np.uint8)
        return results

    # ========== Hald CLUT ==========

    def generate_hald_identity(self, level: int = 8) -> Image.Image:
        """
        生成 identity Hald CLUT 图片

        Hald level L → LUT 分辨率 L² per axis → 图片尺寸 L³ x L³
        Level 8 = 64³ LUT = 512x512 PNG
        Level 12 = 144³ LUT = 1728x1728 PNG

        参数:
            level: Hald 等级 (8 或 12)

        返回:
            PIL.Image (RGB, uint8)
        """
        if level not in (8, 12):
            raise ValueError(f"仅支持 level 8 或 12，收到: {level}")

        N = level * level          # LUT 每轴条目数
        img_size = level ** 3      # 图片宽高
        total_pixels = img_size * img_size  # = N³

        indices = np.arange(total_pixels)
        r_idx = indices % N
        g_idx = (indices // N) % N
        b_idx = indices // (N * N)

        # 索引 → uint8 颜色值: [0, N-1] → [0, 255]
        scale = 255.0 / (N - 1)
        r = (r_idx * scale).round().astype(np.uint8)
        g = (g_idx * scale).round().astype(np.uint8)
        b = (b_idx * scale).round().astype(np.uint8)

        pixels = np.stack([r, g, b], axis=-1)
        image_array = pixels.reshape(img_size, img_size, 3)
        return Image.fromarray(image_array, 'RGB')

    def hald_to_lut(self, processed_hald: Image.Image) -> np.ndarray:
        """
        从处理过的 Hald CLUT 图片提取 3D LUT

        参数:
            processed_hald: 经过滤镜处理的 Hald 图片

        返回:
            np.ndarray, shape (N, N, N, 3), float [0, 1]
            N = level²（从图片尺寸推断）
        """
        processed_hald = processed_hald.convert('RGB')
        width, height = processed_hald.size

        if width != height:
            raise ValueError(f"Hald 图片必须为正方形，收到: {width}x{height}")

        # width = level³ → level = width^(1/3)
        level = round(width ** (1.0 / 3.0))
        if level ** 3 != width:
            raise ValueError(f"图片尺寸 {width} 不是完美立方数，不是有效的 Hald CLUT")

        N = level * level
        total_pixels = width * height

        proc_array = np.array(processed_hald).astype(np.float64) / 255.0
        proc_flat = proc_array.reshape(-1, 3)

        # 向量化索引映射
        indices = np.arange(total_pixels)
        ri = indices % N
        gi = (indices // N) % N
        bi = indices // (N * N)

        lut_data = np.zeros((N, N, N, 3), dtype=np.float64)
        lut_data[ri, gi, bi] = proc_flat

        return lut_data

    def lut_to_hald(self, lut_data: np.ndarray) -> Image.Image:
        """
        将 3D LUT 数据转为 Hald CLUT 图片

        参数:
            lut_data: shape (N, N, N, 3), float [0, 1]
                      N 必须是完全平方数 (N = level²)

        返回:
            PIL.Image (RGB, uint8)
        """
        N = lut_data.shape[0]
        level = round(N ** 0.5)
        if level * level != N:
            raise ValueError(
                f"LUT 大小 {N} 不是完全平方数，无法转为 Hald 格式。"
                f"需要 level² 大小的 LUT（如 64=8², 144=12²）"
            )

        img_size = level ** 3
        total_pixels = img_size * img_size

        indices = np.arange(total_pixels)
        ri = indices % N
        gi = (indices // N) % N
        bi = indices // (N * N)

        pixels = lut_data[ri, gi, bi]  # shape: (total_pixels, 3)
        pixels_uint8 = np.clip(pixels * 255.0, 0, 255).round().astype(np.uint8)
        image_array = pixels_uint8.reshape(img_size, img_size, 3)
        return Image.fromarray(image_array, 'RGB')


def main():
    parser = argparse.ArgumentParser(description='3D LUT 生成器')
    parser.add_argument('--ref', required=True, help='参考图路径')
    parser.add_argument('--output', required=True, help='输出 .cube 文件路径')
    parser.add_argument('--method', default='zone_based',
                        choices=ColorTransferEngine.METHODS,
                        help='迁移方法 (默认: zone_based)')
    parser.add_argument('--strength', type=float, default=1.0,
                        help='迁移强度 0.0~1.0')
    parser.add_argument('--size', type=int, default=33,
                        choices=[17, 33, 65],
                        help='LUT 网格大小 (默认: 33)')
    parser.add_argument('--title', default='PhotoAI Filter',
                        help='LUT 标题')

    args = parser.parse_args()

    if not Path(args.ref).exists():
        print(f"错误: 参考图不存在: {args.ref}", file=sys.stderr)
        sys.exit(1)

    print(f"生成 {args.size}x{args.size}x{args.size} LUT...")
    start = time.time()

    engine = ColorTransferEngine()
    generator = LUTGenerator(size=args.size)
    lut_data = generator.generate_from_transfer(
        reference_path=args.ref,
        method=args.method,
        strength=args.strength,
        engine=engine
    )
    generator.export_cube(lut_data, args.output, title=args.title)

    elapsed = time.time() - start
    print(f"完成，耗时: {elapsed:.2f}秒")


if __name__ == '__main__':
    main()
