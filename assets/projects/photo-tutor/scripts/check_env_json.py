#!/usr/bin/env python3
"""
环境快速检查脚本（Python版本）
由智能体在Skill执行时自动调用
返回环境状态JSON，便于智能体判断功能可用性
"""

import sys
import subprocess
import json
from typing import Dict, Any, List


def run_command(cmd: str, timeout: int = 5) -> Dict[str, Any]:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'code': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timeout',
            'code': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'code': -2
        }


def check_python_info() -> Dict[str, Any]:
    """检查Python信息"""
    return {
        'python_version': sys.version,
        'python_executable': sys.executable,
        'python_implementation': sys.implementation.name if hasattr(sys, 'implementation') else 'unknown'
    }


def check_package(package_name: str, import_name: str) -> Dict[str, Any]:
    """检查包是否可用"""
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        file_path = getattr(module, '__file__', 'unknown')
        return {
            'installed': True,
            'version': version,
            'file_path': file_path,
            'import_name': import_name
        }
    except ImportError:
        return {
            'installed': False,
            'version': None,
            'file_path': None,
            'import_name': import_name
        }


def check_functionalities() -> Dict[str, Any]:
    """检查各功能模块的可用性"""
    results = {}

    # 检查 PyTorch
    torch_info = check_package('torch', 'torch')
    results['pytorch'] = torch_info

    # 检查 TorchVision
    torchvision_info = check_package('torchvision', 'torchvision')
    results['torchvision'] = torchvision_info

    # 检查 scikit-image
    skimage_info = check_package('scikit-image', 'skimage')
    results['scikit_image'] = skimage_info

    # 检查 scikit-learn
    sklearn_info = check_package('scikit-learn', 'sklearn')
    results['scikit_learn'] = sklearn_info

    # 检查 pymcdm
    pymcdm_info = check_package('pymcdm', 'pymcdm')
    results['pymcdm'] = pymcdm_info

    # 检查 PIL/Pillow
    pil_info = check_package('pillow', 'PIL')
    results['pillow'] = pil_info

    return results


def check_iqa_analyzer() -> Dict[str, Any]:
    """检查IQA分析器是否可用"""
    try:
        # 尝试导入 IQAAnalyzer
        sys.path.insert(0, 'scripts')
        from iqa_analyzer import IQA_AVAILABLE

        if IQA_AVAILABLE:
            # 尝试初始化（可能加载模型）
            from iqa_analyzer import IQAAnalyzer
            analyzer = IQAAnalyzer(model_name="musiq", device="cpu")
            return {
                'available': True,
                'model_loaded': analyzer.model is not None,
                'device': analyzer.device,
                'model_name': analyzer.model_name
            }
        else:
            return {
                'available': False,
                'reason': 'IQA_AVAILABLE = False'
            }
    except Exception as e:
        return {
            'available': False,
            'reason': str(e)
        }


def check_color_analyzer() -> Dict[str, Any]:
    """检查颜色分析器是否可用"""
    try:
        # 检查 scikit-image 是否可用
        try:
            from skimage.color import rgb2lab
            harmonicity_available = True
        except ImportError:
            harmonicity_available = False

        return {
            'available': True,
            'harmonicity_analysis': harmonicity_available,
            'note': '和谐度分析需要 scikit-image'
        }
    except Exception as e:
        return {
            'available': False,
            'reason': str(e)
        }


def check_mcdm_analyzer() -> Dict[str, Any]:
    """检查MCDM分析器是否可用"""
    try:
        sys.path.insert(0, 'scripts')
        from mcdm_analyzer import MCDMAnalyzer

        # 尝试初始化
        analyzer = MCDMAnalyzer(method="CRITIC")

        return {
            'available': True,
            'supported_methods': 25,  # pymcdm 支持 25+ 种方法
            'default_method': 'CRITIC'
        }
    except Exception as e:
        return {
            'available': False,
            'reason': str(e)
        }


def generate_summary(checks: Dict[str, Any]) -> Dict[str, Any]:
    """生成环境检查总结"""
    python_info = checks['python']
    functionalities = checks['functionalities']

    # 评估整体状态
    status = {
        'overall': 'ready',  # ready, degraded, critical
        'iqa_available': checks['iqa']['available'],
        'color_analysis_available': checks['color']['available'],
        'mcdm_available': checks['mcdm']['available'],
        'degraded_features': [],
        'unavailable_features': []
    }

    # 检查每个功能的可用性
    if not checks['iqa']['available']:
        status['unavailable_features'].append('IQA美学评分')
        status['overall'] = 'degraded'
    elif not checks['iqa'].get('model_loaded', False):
        status['degraded_features'].append('IQA模型加载')

    if not checks['color']['available']:
        status['unavailable_features'].append('色彩分析')
        status['overall'] = 'critical'
    elif not checks['color'].get('harmonicity_analysis', False):
        status['degraded_features'].append('色彩和谐度精确分析')

    if not checks['mcdm']['available']:
        status['unavailable_features'].append('MCDM权重优化')
        status['overall'] = 'degraded'

    # 检查关键依赖
    if not functionalities['pytorch']['installed']:
        status['overall'] = 'critical'
    if not functionalities['scikit_image']['installed']:
        status['overall'] = 'critical'

    return status


def main():
    """主函数"""
    # 执行所有检查
    checks = {
        'python': check_python_info(),
        'functionalities': check_functionalities(),
        'iqa': check_iqa_analyzer(),
        'color': check_color_analyzer(),
        'mcdm': check_mcdm_analyzer()
    }

    # 生成总结
    summary = generate_summary(checks)

    # 构建完整报告
    report = {
        'timestamp': None,  # 由调用方添加
        'checks': checks,
        'summary': summary
    }

    # 输出 JSON 格式（便于智能体解析）
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # 同时输出人类可读格式（便于用户查看）
    print("\n" + "=" * 70, file=sys.stderr)
    print("🔍 环境检查报告", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    print(f"\n📋 Python 版本: {checks['python']['python_version']}", file=sys.stderr)
    print(f"📍 Python 路径: {checks['python']['python_executable']}", file=sys.stderr)

    print(f"\n📦 依赖包状态:", file=sys.stderr)
    for name, info in checks['functionalities'].items():
        if info['installed']:
            version = info.get('version', 'unknown')
            print(f"  ✅ {name:20} 版本: {version}", file=sys.stderr)
        else:
            print(f"  ❌ {name:20} 未安装", file=sys.stderr)

    print(f"\n🎯 功能可用性:", file=sys.stderr)
    print(f"  IQA分析:          {'✅ 可用' if checks['iqa']['available'] else '❌ 不可用'}", file=sys.stderr)
    print(f"  色彩分析:         {'✅ 可用' if checks['color']['available'] else '❌ 不可用'}", file=sys.stderr)
    if checks['color'].get('harmonicity_analysis'):
        print(f"    - 和谐度分析:   ✅ 精确版", file=sys.stderr)
    else:
        print(f"    - 和谐度分析:   ⚠️  简化版（需要scikit-image）", file=sys.stderr)
    print(f"  MCDM权重优化:     {'✅ 可用' if checks['mcdm']['available'] else '❌ 不可用'}", file=sys.stderr)

    print(f"\n📊 整体状态: {summary['overall'].upper()}", file=sys.stderr)

    if summary['overall'] == 'ready':
        print("  ✅ 所有功能正常，可以完整使用", file=sys.stderr)
    elif summary['overall'] == 'degraded':
        print("  ⚠️  部分功能降级，但仍可使用", file=sys.stderr)
        if summary['degraded_features']:
            print(f"  降级功能: {', '.join(summary['degraded_features'])}", file=sys.stderr)
    else:  # critical
        print("  ❌ 关键依赖缺失，部分核心功能不可用", file=sys.stderr)
        if summary['unavailable_features']:
            print(f"  不可用功能: {', '.join(summary['unavailable_features'])}", file=sys.stderr)

    print("\n" + "=" * 70, file=sys.stderr)

    return report


if __name__ == '__main__':
    main()
