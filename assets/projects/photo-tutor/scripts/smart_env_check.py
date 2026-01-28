#!/usr/bin/env python3
"""
智能环境检查（带缓存机制）
仅在首次或检测到依赖缺失时进行检查，避免重复检查
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional


class EnvCheckCache:
    """环境检查缓存管理器"""

    def __init__(self, cache_file: str = ".env_check_cache.json", cache_ttl: int = 3600):
        self.cache_file = cache_file
        self.cache_ttl = cache_ttl  # 缓存有效期（秒），默认1小时

    def get_cached_status(self) -> Optional[Dict[str, Any]]:
        """获取缓存的状态"""
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)

            # 检查缓存是否过期
            cache_time = cache_data.get('timestamp', 0)
            if time.time() - cache_time > self.cache_ttl:
                return None

            return cache_data.get('status')

        except Exception:
            return None

    def set_cached_status(self, status: Dict[str, Any]):
        """设置缓存的状态"""
        cache_data = {
            'timestamp': time.time(),
            'status': status
        }

        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  无法写入缓存: {e}", file=sys.stderr)

    def clear_cache(self):
        """清除缓存"""
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
            except Exception as e:
                print(f"⚠️  无法清除缓存: {e}", file=sys.stderr)


def should_skip_check() -> bool:
    """检查是否应该跳过环境检查"""
    # 方式1：环境变量控制
    if os.environ.get('PHOTO_TUTOR_SKIP_CHECK') == '1':
        return True

    # 方式2：检查缓存
    cache = EnvCheckCache()
    cached_status = cache.get_cached_status()

    if cached_status:
        overall = cached_status.get('summary', {}).get('overall', 'unknown')
        if overall == 'ready':
            print(f"✅ 使用缓存的环境状态: READY（跳过检查）", file=sys.stderr)
            return True
        elif overall == 'degraded':
            print(f"⚠️  使用缓存的环境状态: DEGRADED（跳过检查）", file=sys.stderr)
            return True

    return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='智能环境检查（带缓存）')
    parser.add_argument('--force', '-f', action='store_true', help='强制重新检查（忽略缓存）')
    parser.add_argument('--clear', '-c', action='store_true', help='清除缓存')
    parser.add_argument('--skip', '-s', action='store_true', help='跳过检查（使用缓存）')
    args = parser.parse_args()

    cache = EnvCheckCache()

    # 清除缓存
    if args.clear:
        cache.clear_cache()
        print("✅ 缓存已清除", file=sys.stderr)
        return

    # 强制检查
    if args.force:
        print("⚠️  强制重新检查环境...", file=sys.stderr)
        cache.clear_cache()

    # 跳过检查
    if args.skip:
        cached_status = cache.get_cached_status()
        if cached_status:
            print(json.dumps(cached_status, indent=2, ensure_ascii=False))
            return
        else:
            print("❌ 没有可用的缓存", file=sys.stderr)
            sys.exit(1)

    # 智能检查：先检查缓存
    if not args.force:
        if should_skip_check():
            cached_status = cache.get_cached_status()
            if cached_status:
                print(json.dumps(cached_status, indent=2, ensure_ascii=False))
                return

    # 缓存不存在或已过期，执行实际检查
    print("🔍 执行环境检查...", file=sys.stderr)

    try:
        result = subprocess.run(
            ['python3', 'scripts/check_env_json.py'],
            capture_output=True,
            text=True,
            timeout=30
        )

        # 直接输出原始结果（保持格式）
        print(result.stdout, end='')
        if result.stderr:
            print(result.stderr, end='', file=sys.stderr)

        # 尝试解析 JSON 并缓存
        try:
            # 提取 JSON 部分（从第一个 { 到最后一个 }）
            json_start = result.stdout.find('{')
            json_end = result.stdout.rfind('}')

            if json_start != -1 and json_end != -1:
                json_str = result.stdout[json_start:json_end + 1]
                status = json.loads(json_str)
                cache.set_cached_status(status)
                print(f"✅ 环境状态已缓存（有效期: {cache.cache_ttl}秒）", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  无法缓存环境状态: {e}", file=sys.stderr)

        if result.returncode != 0:
            sys.exit(1)

    except Exception as e:
        print(f"❌ 执行检查时出错: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    import subprocess
    main()
