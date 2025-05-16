import sys
import runpy
import logging
import argparse
import importlib.metadata
from datetime import datetime

from .kaa import Kaa
from kotonebot.backend.context import tasks_from_id, task_registry

version = importlib.metadata.version('ksaa')

# 主命令
psr = argparse.ArgumentParser(description='Command-line interface for Kotone\'s Auto Assistant')
psr.add_argument('-v', '--version', action='version', version='kaa v' + version)
psr.add_argument('-c', '--config', default='./config.json', help='Path to the configuration file. Default: ./config.json')
psr.add_argument('-lp', '--log-path', default=None, help='Path to the log file. Does not log to file if not specified. Default: None')
psr.add_argument('-ll', '--log-level', default='DEBUG', help='Log level. Default: DEBUG')

# 子命令
subparsers = psr.add_subparsers(dest='subcommands', title='Subcommands')

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
        _kaa = Kaa(psr.parse_args().config)
        _kaa.initialize()
    return _kaa

def task_invoke() -> int:
    tasks_args = psr.parse_args().task_ids
    assert isinstance(tasks_args, list)
    if not tasks_args:
        print('No tasks specified.')
        return -1
    # 设置日志
    log_level = getattr(logging, psr.parse_args().log_level, None)
    if log_level is None:
        raise ValueError(f'Invalid log level: {psr.parse_args().log_level}')
    kaa().set_log_level(log_level)
    if psr.parse_args().log_path is not None:
        kaa().add_file_logger(psr.parse_args().log_path)
    # 执行任务
    print(tasks_args)
    if '*' in tasks_args:
        if len(tasks_args) > 1:
            raise ValueError('Cannot specify other tasks when using wildcard.')
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
        else:
            raise ValueError(f'Unknown task command: {args.task_command}')
    elif args.subcommands == 'remote-server':
        sys.exit(remote_server())
    elif args.subcommands is None:
        log_filename = datetime.now().strftime('logs/%y-%m-%d-%H-%M-%S.log')
        kaa().set_log_level(logging.DEBUG)
        kaa().add_file_logger(log_filename)
        from .gr import main as gr_main
        gr_main(kaa())

if __name__ == '__main__':
    main()