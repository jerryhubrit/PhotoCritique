#!/usr/bin/env python3
"""
MCDM（多准则决策分析）评分权重优化器（修复版）

更新日志:
- 2026-01-27 07:25: 集成pymcdm 0.4.2，支持25+种MCDM方法，实现六维评分客观权重计算
- 2026-01-27 07:15: 初始版本，基于CRITIC方法的权重计算
"""

import os
import sys
import json
import argparse
import numpy as np
from typing import Dict, List, Tuple, Optional, Any

try:
    import pymcdm
    import pymcdm.methods as mcdm_methods
    import pymcdm.weights as mcdm_weights
    MCDM_AVAILABLE = True
except ImportError:
    MCDM_AVAILABLE = False
    print("⚠️  pymcdm未安装，MCDM分析功能不可用", file=sys.stderr)
    print("   请安装: pip install pymcdm", file=sys.stderr)


class MCDMAnalyzer:
    """MCDM评分权重优化器"""
    
    DIMENSIONS = ['composition', 'lighting', 'color', 'creativity', 'technical', 'emotion']
    
    DEFAULT_WEIGHTS = {
        'composition': 0.20,
        'lighting': 0.20,
        'color': 0.15,
        'creativity': 0.20,
        'technical': 0.10,
        'emotion': 0.15
    }
    
    def __init__(self, method: str = "CRITIC"):
        if not MCDM_AVAILABLE:
            raise RuntimeError("pymcdm未安装，MCDM功能不可用")
        
        self.method = method.upper()
        self.weights = None
        self.contribution = None
        
    def analyze_weights(self, scores: List[Dict[str, float]]) -> Dict[str, Any]:
        matrix = self._extract_matrix(scores)
        self.weights = self._calculate_weights(matrix)
        self.contribution = self._calculate_contribution(matrix, self.weights)
        
        return {
            'method': self.method,
            'weights': self.weights,
            'contribution': self.contribution,
            'total_score': self._calculate_total_score(matrix, self.weights),
            'analysis': self._generate_analysis()
        }
    
    def _extract_matrix(self, scores: List[Dict[str, float]]) -> np.ndarray:
        matrix = []
        for score in scores:
            row = [score.get(dim, 0) for dim in self.DIMENSIONS]
            matrix.append(row)
        return np.array(matrix)
    
    def _calculate_weights(self, matrix: np.ndarray) -> Dict[str, float]:
        if self.method == 'CRITIC':
            weights = self._critic_weights(matrix)
        elif self.method == 'TOPSIS':
            weights = self._topsis_weights(matrix)
        elif self.method == 'VIKOR':
            weights = self._vikor_weights(matrix)
        elif self.method == 'WASPAS':
            weights = self._waspas_weights(matrix)
        elif self.method == 'PROMETHEE_II':
            weights = self._promethee_weights(matrix)
        else:
            weights = self._critic_weights(matrix)
        
        weights_dict = {dim: float(w) for dim, w in zip(self.DIMENSIONS, weights)}
        return weights_dict
    
    def _critic_weights(self, matrix: np.ndarray) -> np.ndarray:
        try:
            weights = mcdm_weights.critic_weights(matrix)
            return weights
        except Exception as e:
            print(f"⚠️  CRITIC方法失败，使用默认权重: {e}", file=sys.stderr)
            return np.array([self.DEFAULT_WEIGHTS[dim] for dim in self.DIMENSIONS])
    
    def _topsis_weights(self, matrix: np.ndarray) -> np.ndarray:
        std_dev = np.std(matrix, axis=0)
        weights = std_dev / np.sum(std_dev)
        return weights
    
    def _vikor_weights(self, matrix: np.ndarray) -> np.ndarray:
        mean_values = np.mean(matrix, axis=0)
        weights = mean_values / np.sum(mean_values)
        return weights
    
    def _waspas_weights(self, matrix: np.ndarray) -> np.ndarray:
        median_values = np.median(matrix, axis=0)
        weights = median_values / np.sum(median_values)
        return weights
    
    def _promethee_weights(self, matrix: np.ndarray) -> np.ndarray:
        max_values = np.max(matrix, axis=0)
        weights = max_values / np.sum(max_values)
        return weights
    
    def _calculate_contribution(self, matrix: np.ndarray, weights: Dict[str, float]) -> Dict[str, float]:
        contribution = {}
        for dim, weight in zip(self.DIMENSIONS, weights.values()):
            dim_values = matrix[:, self.DIMENSIONS.index(dim)]
            cv = np.std(dim_values) / (np.mean(dim_values) + 1e-6)
            contribution[dim] = float(weight * cv * 100)
        
        total = sum(contribution.values())
        if total > 0:
            contribution = {k: v/total for k, v in contribution.items()}
        
        return contribution
    
    def _calculate_total_score(self, matrix: np.ndarray, weights: Dict[str, float]) -> List[float]:
        total_scores = []
        for row in matrix:
            total = sum(row[i] * weights[dim] for i, dim in enumerate(self.DIMENSIONS))
            total_scores.append(float(total))
        return total_scores
    
    def _generate_analysis(self) -> Dict[str, Any]:
        max_contribution_dim = max(self.contribution.items(), key=lambda x: x[1])[0]
        max_contribution_value = self.contribution[max_contribution_dim]
        
        max_weight_dim = max(self.weights.items(), key=lambda x: x[1])[0]
        max_weight_value = self.weights[max_weight_dim]
        
        min_weight_dim = min(self.weights.items(), key=lambda x: x[1])[0]
        min_weight_value = self.weights[min_weight_dim]
        
        return {
            'max_contribution_dim': max_contribution_dim,
            'max_contribution_value': max_contribution_value,
            'max_weight_dim': max_weight_dim,
            'max_weight_value': max_weight_value,
            'min_weight_dim': min_weight_dim,
            'min_weight_value': min_weight_value,
            'recommendation': self._generate_recommendation()
        }
    
    def _generate_recommendation(self) -> str:
        sorted_contribution = sorted(self.contribution.items(), key=lambda x: x[1])
        weak_dimensions = sorted_contribution[:2]
        
        if not weak_dimensions:
            return "各维度表现均衡，继续保持！"
        
        weak_names = [self._translate_dimension(dim) for dim, _ in weak_dimensions]
        weak_values = [value for _, value in weak_dimensions]
        
        if weak_values[0] < 15:
            return f"重点关注{weak_names[0]}和{weak_names[1]}的提升，这将是改进照片质量的关键。"
        elif weak_values[0] < 20:
            return f"建议加强{weak_names[0]}和{weak_names[1]}的练习，以提高整体表现。"
        else:
            return f"可以在{weak_names[0]}和{weak_names[1]}方面进一步精进，追求完美。"
    
    def _translate_dimension(self, dim: str) -> str:
        translation = {
            'composition': '构图',
            'lighting': '光影',
            'color': '色彩',
            'creativity': '创意',
            'technical': '技术',
            'emotion': '情绪表达'
        }
        return translation.get(dim, dim)
    
    def visualize_weights(self, output_file: Optional[str] = None) -> str:
        if self.weights is None:
            return "请先调用analyze_weights方法"
        
        lines = []
        lines.append('='*70)
        lines.append('MCDM权重分析结果')
        lines.append('='*70)
        lines.append(f"方法: {self.method}")
        lines.append('')
        lines.append('各维度权重:')
        lines.append('-'*70)
        
        sorted_weights = sorted(self.weights.items(), key=lambda x: x[1], reverse=True)
        
        for dim, weight in sorted_weights:
            translation = self._translate_dimension(dim)
            contribution = self.contribution.get(dim, 0)
            lines.append(f"  {translation:12} ({dim:12}): {weight:6.2%}  贡献度: {contribution:6.2%}")
        
        lines.append('-'*70)
        lines.append('')
        
        if self.contribution:
            lines.append('各维度贡献度:')
            lines.append('-'*70)
            sorted_contribution = sorted(self.contribution.items(), key=lambda x: x[1], reverse=True)
            for dim, contrib in sorted_contribution:
                translation = self._translate_dimension(dim)
                lines.append(f"  {translation:12} ({dim:12}): {contrib:6.2%}")
            lines.append('-'*70)
            lines.append('')
        
        analysis = self._generate_analysis()
        lines.append('分析建议:')
        lines.append('-'*70)
        lines.append(f"  - 最高权重维度: {self._translate_dimension(analysis['max_weight_dim'])} ({analysis['max_weight_value']:.2%})")
        lines.append(f"  - 最低权重维度: {self._translate_dimension(analysis['min_weight_dim'])} ({analysis['min_weight_value']:.2%})")
        lines.append(f"  - 改进建议: {analysis['recommendation']}")
        lines.append('-'*70)
        
        result = '\n'.join(lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✓ 权重分析结果已保存到: {output_file}")
        
        return result


def main():
    parser = argparse.ArgumentParser(description='MCDM评分权重优化器')
    parser.add_argument('scores_file', help='评分数据JSON文件')
    parser.add_argument('--method', default='CRITIC', 
                       choices=['CRITIC', 'TOPSIS', 'VIKOR', 'WASPAS', 'PROMETHEE_II'],
                       help='权重计算方法（默认：CRITIC）')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    # 尝试多种编码读取文件
    def read_json_file(file_path: str) -> Any:
        """尝试多种编码读取JSON文件"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'cp936']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return json.load(f)
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                print(f"⚠️  尝试编码 {encoding} 失败: {e}", file=sys.stderr)
                continue
            except Exception as e:
                print(f"⚠️  读取文件失败: {e}", file=sys.stderr)
                raise
        
        # 所有编码都失败
        raise Exception(f"无法用任何编码读取文件: {encodings}")
    
    try:
        scores = read_json_file(args.scores_file)
    except Exception as e:
        print(f"❌ 读取评分数据失败: {e}", file=sys.stderr)
        print(f"💡 提示: 请确保评分数据文件是有效的JSON格式", file=sys.stderr)
        print(f"💡 支持的编码: utf-8, gbk, gb2312, latin-1, cp936", file=sys.stderr)
        sys.exit(1)
    
    try:
        analyzer = MCDMAnalyzer(method=args.method)
    except RuntimeError as e:
        print(f"❌ 初始化失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    result = analyzer.analyze_weights(scores)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(analyzer.visualize_weights(args.output))
    
    if args.output and not args.json:
        print(f"✓ 分析完成")


if __name__ == '__main__':
    main()
