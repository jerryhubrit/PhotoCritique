#!/usr/bin/env python3
"""
环境快速检查脚本（Python版本，轻量版）
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

    # 检查 scikit-image
    skimage_info = check_package('scikit-image', 'skimage')
    results['scikit_image'] = skimage_info

    # 检查 scikit-learn
    sklearn_info = check_package('scikit-learn', 'sklearn')
    results['scikit_learn'] = sklearn_info

    # 检查 PIL/Pillow
    pil_info = check_package('pillow', 'PIL')
    results['pillow'] = pil_info

    return results


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


def generate_summary(checks: Dict[str, Any]) -> Dict[str, Any]:
    """生成环境检查总结"""
    python_info = checks['python']
    functionalities = checks['functionalities']

    # 评估整体状态
    status = {
        'overall': 'ready',  # ready, degraded, critical
        'color_analysis_available': checks['color']['available'],
        'degraded_features': [],
        'unavailable_features': []
    }

    # 检查每个功能的可用性
    if not checks['color']['available']:
        status['unavailable_features'].append('色彩分析')
        status['overall'] = 'degraded'

    # 如果所有功能都不可用，则为 critical
    if len(status['unavailable_features']) > 0 and not functionalities['pillow']['installed']:
        status['overall'] = 'critical'

    return status


def print_report(checks: Dict[str, Any], status: Dict[str, Any]):
    """打印环境检查报告"""
    print("=" * 70, file=sys.stderr)
    print("🔍 环境检查报告", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("", file=sys.stderr)

    # Python 信息
    python_info = checks['python']
    print(f"📋 Python 版本: {python_info['python_version'].split()[0]}", file=sys.stderr)
    print(f"📍 Python 路径: {python_info['python_executable']}", file=sys.stderr)
    print("", file=sys.stderr)

    # 依赖包状态
    print("📦 依赖包状态:", file=sys.stderr)
    for key, info in checks['functionalities'].items():
        name = key.replace('_', ' ').title()
        if info['installed']:
            version = info.get('version', 'unknown')
            print(f"  ✅ {name:20} 版本: {version}", file=sys.stderr)
        else:
            print(f"  ❌ {name:20} 未安装", file=sys.stderr)
    print("", file=sys.stderr)

    # 功能可用性
    print("🎯 功能可用性:", file=sys.stderr)

    # 颜色分析
    color_available = checks['color']['available']
    harmonicity_available = checks['color'].get('harmonicity_analysis', False)
    if color_available:
        print(f"  色彩分析:         ✅ 可用", file=sys.stderr)
        if harmonicity_available:
            print(f"    - 和谐度分析:   ✅ 精确版", file=sys.stderr)
        else:
            print(f"    - 和谐度分析:   ⚠️  简化版（需要scikit-image）", file=sys.stderr)
    else:
        print(f"  色彩分析:         ❌ 不可用", file=sys.stderr)

    print("", file=sys.stderr)

    # 整体状态
    overall = status['overall']
    status_text = {
        'ready': '✅ READY - 所有功能正常，可以完整使用',
        'degraded': '⚠️  DEGRADED - 部分功能降级，基本可用',
        'critical': '❌ CRITICAL - 关键依赖缺失，核心功能不可用'
    }
    print(f"📊 整体状态: {status_text[overall]}", file=sys.stderr)

    if status['unavailable_features']:
        print(f"  不可用功能: {', '.join(status['unavailable_features'])}", file=sys.stderr)

    if status['degraded_features']:
        print(f"  降级功能: {', '.join(status['degraded_features'])}", file=sys.stderr)

    print("", file=sys.stderr)
    print("=" * 70, file=sys.stderr)


def main():
    """主函数"""
    checks = {}

    # 检查 Python 信息
    checks['python'] = check_python_info()

    # 检查各功能模块
    checks['functionalities'] = check_functionalities()

    # 检查颜色分析器
    checks['color'] = check_color_analyzer()

    # 生成总结
    status = generate_summary(checks)
    checks['summary'] = status

    # 输出 JSON
    print(json.dumps(checks, indent=2, ensure_ascii=False))

    # 打印可读报告
    print("", file=sys.stderr)
    print_report(checks, status)


if __name__ == '__main__':
    main()
