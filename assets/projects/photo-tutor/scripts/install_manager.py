#!/usr/bin/env python3
"""
后台依赖安装管理器
支持异步安装、进度监控、状态检查
"""

import sys
import os
import subprocess
import json
import time
import signal
from pathlib import Path
from typing import Dict, Any, Optional


class InstallManager:
    """依赖安装管理器"""

    def __init__(self, log_file: str = "install_progress.log"):
        self.log_file = log_file
        self.pid_file = "install.pid"
        self.status_file = "install_status.json"

    def is_installing(self) -> bool:
        """检查是否正在安装"""
        if not os.path.exists(self.pid_file):
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # 检查进程是否还在运行
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                # 进程不存在，清理pid文件
                os.remove(self.pid_file)
                return False
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        """获取安装状态"""
        if not os.path.exists(self.status_file):
            return {
                'status': 'not_started',
                'progress': 0,
                'message': '未开始安装'
            }

        try:
            with open(self.status_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {
                'status': 'unknown',
                'progress': 0,
                'message': '无法读取状态'
            }

    def start_install(self, background: bool = True) -> Dict[str, Any]:
        """开始安装依赖"""
        if self.is_installing():
            return {
                'success': False,
                'message': '已有安装进程在运行',
                'status': self.get_status()
            }

        # 清理旧的状态文件
        for f in [self.log_file, self.status_file, self.pid_file]:
            if os.path.exists(f):
                os.remove(f)

        if background:
            # 后台安装
            pid = self._run_background()
            if pid > 0:
                with open(self.pid_file, 'w') as f:
                    f.write(str(pid))

                return {
                    'success': True,
                    'message': '后台安装已启动',
                    'pid': pid,
                    'status': {
                        'status': 'running',
                        'progress': 0,
                        'message': '正在安装依赖，请稍候...'
                    }
                }
            else:
                return {
                    'success': False,
                    'message': '后台安装启动失败'
                }
        else:
            # 同步安装（用于测试）
            return self._run_install()

    def _run_background(self) -> int:
        """后台运行安装脚本"""
        try:
            # 使用 nohup 和 & 实现后台运行
            cmd = f"nohup bash scripts/install_dependencies.sh > {self.log_file} 2>&1 &"
            subprocess.run(cmd, shell=True, check=True)

            # 获取后台进程的 PID
            time.sleep(1)  # 等待进程启动
            result = subprocess.run(
                "pgrep -f 'install_dependencies.sh' | head -1",
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip())
            else:
                return -1

        except Exception as e:
            print(f"启动后台安装失败: {e}", file=sys.stderr)
            return -1

    def _run_install(self) -> Dict[str, Any]:
        """同步运行安装（测试用）"""
        try:
            result = subprocess.run(
                ['bash', 'scripts/install_dependencies.sh'],
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )

            status = {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'progress': 100 if result.returncode == 0 else 0,
                'message': '安装完成' if result.returncode == 0 else '安装失败',
                'output': result.stdout,
                'error': result.stderr
            }

            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)

            return {
                'success': result.returncode == 0,
                'message': status['message'],
                'status': status
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': '安装超时（10分钟）',
                'status': {
                    'status': 'timeout',
                    'progress': 0,
                    'message': '安装超时'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'安装出错: {str(e)}',
                'status': {
                    'status': 'error',
                    'progress': 0,
                    'message': str(e)
                }
            }

    def cancel_install(self) -> bool:
        """取消安装"""
        if not os.path.exists(self.pid_file):
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            os.kill(pid, signal.SIGTERM)

            # 清理文件
            for f in [self.log_file, self.status_file, self.pid_file]:
                if os.path.exists(f):
                    os.remove(f)

            return True

        except Exception as e:
            print(f"取消安装失败: {e}", file=sys.stderr)
            return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='依赖安装管理器')
    parser.add_argument('--start', action='store_true', help='开始安装')
    parser.add_argument('--check', action='store_true', help='检查状态')
    parser.add_argument('--cancel', action='store_true', help='取消安装')
    parser.add_argument('--background', action='store_true', help='后台运行')
    parser.add_argument('--sync', action='store_true', help='同步运行（测试用）')

    args = parser.parse_args()

    manager = InstallManager()

    if args.check:
        # 检查状态
        if manager.is_installing():
            status = manager.get_status()
            print(json.dumps({
                'installing': True,
                'status': status
            }, indent=2))
        else:
            # 检查是否已经安装成功
            result = subprocess.run(
                ['python3', 'scripts/check_env_json.py'],
                capture_output=True,
                text=True
            )

            try:
                env_status = json.loads(result.stdout)
                summary = env_status.get('summary', {})
                overall = summary.get('overall', 'unknown')

                if overall == 'ready':
                    print(json.dumps({
                        'installing': False,
                        'status': {
                            'status': 'completed',
                            'progress': 100,
                            'message': '依赖已安装完成'
                        },
                        'environment': summary
                    }, indent=2))
                else:
                    print(json.dumps({
                        'installing': False,
                        'status': {
                            'status': 'not_started',
                            'progress': 0,
                            'message': f'依赖未完全安装（状态: {overall}）'
                        },
                        'environment': summary
                    }, indent=2))
            except Exception:
                print(json.dumps({
                    'installing': False,
                    'status': {
                        'status': 'unknown',
                        'progress': 0,
                        'message': '无法获取环境状态'
                    }
                }, indent=2))

    elif args.cancel:
        # 取消安装
        if manager.cancel_install():
            print(json.dumps({
                'success': True,
                'message': '安装已取消'
            }, indent=2))
        else:
            print(json.dumps({
                'success': False,
                'message': '没有正在进行的安装'
            }, indent=2))

    elif args.start:
        # 开始安装
        if args.sync:
            result = manager._run_install()
            print(json.dumps(result, indent=2))
        else:
            result = manager.start_install(background=True)
            print(json.dumps(result, indent=2))

    else:
        # 默认：检查状态
        if manager.is_installing():
            print("安装正在进行中...")
            status = manager.get_status()
            print(f"状态: {status.get('status', 'unknown')}")
            print(f"进度: {status.get('progress', 0)}%")
            print(f"消息: {status.get('message', '')}")
        else:
            print("没有正在进行的安装")


if __name__ == '__main__':
    main()
