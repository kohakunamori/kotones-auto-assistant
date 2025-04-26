import sys
import logging
import argparse
import importlib.metadata
import runpy

from .kaa import Kaa
from kotonebot.backend.context import tasks_from_id, task_registry

version = importlib.metadata.version('ksaa')

# 主命令
psr = argparse.ArgumentParser(description='Command-line interface for Kotone\'s Auto Assistant')
psr.add_argument('-v', '--version', action='version', version='kaa v' + version)
# psr.add_argument('-c', '--config', required=False, help='Path to the configuration file. Default: ./config.json')

# 子命令
subparsers = psr.add_subparsers(dest='subcommands')

# task 子命令
task_psr = subparsers.add_parser('task', help='Task related commands')
task_subparsers = task_psr.add_subparsers(dest='task_command', required=True)

# task invoke 子命令
invoke_psr = task_subparsers.add_parser('invoke', help='Invoke a task or many tasks')
invoke_psr.add_argument('task_ids', nargs='*', help='Tasks to invoke')

# task list 子命令
list_psr = task_subparsers.add_parser('list', help='List all available tasks')

# remote-server 子命令
remote_server_psr = subparsers.add_parser('remote-server', help='Start the remote Windows server')
remote_server_psr.add_argument('--host', default='0.0.0.0', help='Host to bind to')
remote_server_psr.add_argument('--port', type=int, default=8000, help='Port to bind to')

_kaa: Kaa | None = None
def kaa() -> Kaa:
    global _kaa
    if _kaa is None:
        _kaa = Kaa()
        _kaa.initialize()
    return _kaa

def task_invoke() -> int:
    tasks_args = psr.parse_args().task_ids
    if not tasks_args:
        print('No tasks specified.')
        return -1
    kaa().set_log_level(logging.DEBUG)
    print(tasks_args)
    if len(tasks_args) == 1 and tasks_args[0] == '*':
        kaa().run_all()
    else:
        kaa().run(tasks_from_id(tasks_args))
    return 0

def task_list() -> int:
    # 确保任务已加载
    kaa()

    if not task_registry:
        print('No tasks available.')
        return 0

    print('Available tasks:')
    for task in task_registry.values():
        print(f'  * {task.id}: {task.name}\n    {task.description.strip()}')
    return 0

def remote_server() -> int:
    args = psr.parse_args()
    try:
        # 使用runpy运行remote_windows.py模块
        sys.argv = ['remote_windows.py', f'--host={args.host}', f'--port={args.port}']
        runpy.run_module('kotonebot.client.implements.remote_windows', run_name='__main__')
        return 0
    except Exception as e:
        print(f'Error starting remote server: {e}')
        return -1

def main():
    args = psr.parse_args()
    if args.subcommands == 'task':
        if args.task_command == 'invoke':
            sys.exit(task_invoke())
        elif args.task_command == 'list':
            sys.exit(task_list())
    elif args.subcommands == 'remote-server':
        sys.exit(remote_server())
    elif args.subcommands is None:
        kaa().set_log_level(logging.DEBUG)
        from .gr import main as gr_main
        gr_main(kaa())

if __name__ == '__main__':
    main()