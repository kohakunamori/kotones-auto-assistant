import os
import sys
import json
import ctypes
import codecs
import locale
import logging
import subprocess
import importlib.metadata
import argparse
import tempfile
import zipfile
import shutil
from pathlib import Path
from collections import deque
from datetime import datetime
from time import sleep
from typing import Optional, Dict, Any, TypedDict, Literal, List

from request import head, HTTPError, NetworkError
from terminal import (
    Color, print_header, print_status, clear_screen, 
    get_terminal_width, get_display_width, truncate_string,
    hide_cursor, show_cursor, move_cursor_up, wait_key, get_terminal_height
)
from repo import Version

# 配置文件的类型定义
class BackendConfig(TypedDict, total=False):
    type: Literal['custom', 'mumu12', 'leidian', 'dmm']
    screenshot_impl: Literal['adb', 'adb_raw', 'uiautomator2', 'windows', 'remote_windows', 'nemu_ipc']
    
class MiscConfig(TypedDict, total=False):
    check_update: Literal['never', 'startup']
    auto_install_update: bool

class UserConfig(TypedDict, total=False):
    name: str
    id: str
    category: str
    description: str
    backend: BackendConfig
    keep_screenshots: bool
    options: Dict[str, Any]  # 这里包含 misc 等配置

class Config(TypedDict, total=False):
    version: int
    user_configs: List[UserConfig]

# 获取当前Python解释器路径
PYTHON_EXECUTABLE = sys.executable
TRUSTED_HOSTS = "pypi.org files.pythonhosted.org pypi.python.org mirrors.aliyun.com mirrors.cloud.tencent.com mirrors.tuna.tsinghua.edu.cn"

def setup_logging():
    """
    配置日志记录。
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
    log_file = log_dir / f"bootstrap-{timestamp}.log"

    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s',
        filename=log_file,
        filemode='w',
        encoding='utf-8'
    )

    # 记录未捕获的异常
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.error("未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception
    logging.info("日志记录器已初始化。")

PIP_SERVERS = [
    "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple",
    "https://mirrors.aliyun.com/pypi/simple",
    "https://mirrors.cloud.tencent.com/pypi/simple",
    "https://pypi.org/simple",
]

def is_admin() -> bool:
    """
    检查当前进程是否具有管理员权限。
    
    :return: 如果具有管理员权限返回True，否则返回False
    :rtype: bool
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def test_url_availability(url: str) -> bool:
    """
    测试URL是否可访问（返回200状态码）。
    
    :param url: 要测试的URL
    :type url: str
    :return: 如果URL可访问返回True，否则返回False
    :rtype: bool
    """
    try:
        with head(url, timeout=10) as response:
            return response.status_code == 200
    except (HTTPError, NetworkError):
        return False
    except Exception:
        return False

def get_working_pip_server() -> Optional[str]:
    """
    获取可用的pip服务器。
    
    :return: 第一个可用的pip服务器URL，如果都不可用返回None
    :rtype: Optional[str]
    """
    for server in PIP_SERVERS:
        msg = f"正在测试: {server}"
        print_status(msg, status='info', indent=1)
        logging.info(msg)
        if test_url_availability(server):
            msg = f"找到可用的pip服务器: {server}"
            print_status(msg, status='success', indent=1)
            logging.info(msg)
            return server
    msg = "所有pip服务器都不可用"
    print_status(msg, status='error')
    logging.error(msg)
    return None

def package_version(package_name: str) -> Optional[str]:
    """
    获取指定包的版本信息。
    
    :param package_name: 包名称
    :type package_name: str
    :return: 包版本字符串，如果包不存在则返回 None
    :rtype: Optional[str]
    
    :Example:
    
    .. code-block:: python
    
        >>> package_version("requests")
        '2.31.0'
        >>> package_version("nonexistent_package")
        None
    
    :raises: 无异常抛出，包不存在时返回 None
    """
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None

def run_command(command: str, check: bool = True, verbatim: bool = False, scroll_region_size: int = -1, log_output: bool = True) -> bool:
    """
    运行命令并实时输出，返回是否成功。
    
    :param command: 要运行的命令
    :param check: 是否检查返回码
    :param verbatim: 是否原样输出，不使用滚动UI
    :param scroll_region_size: 滚动区域的大小, -1 表示动态计算
    :param log_output: 是否将命令输出记录到日志中
    :return: 命令是否成功执行
    """
    logging.info(f"执行命令: {command}")

    # 设置环境变量以确保正确的编码处理
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    # 获取系统默认编码
    system_encoding = locale.getpreferredencoding()
    
    # 创建解码器
    def decode_output(line: bytes) -> str:
        try:
            # 首先尝试UTF-8解码
            return line.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # 如果UTF-8失败，尝试系统默认编码
                return line.decode(system_encoding)
            except UnicodeDecodeError:
                # 如果都失败了，使用'replace'策略
                return line.decode('utf-8', errors='replace')

    if verbatim:
        print(f"▶ 执行命令: {command}")
        try:
            process = subprocess.Popen(
                command, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                env=env
            )
            if process.stdout:
                for line in iter(process.stdout.readline, b''):
                    clean_line = decode_output(line).strip('\n')
                    print(clean_line)
                    if log_output:
                        logging.info(clean_line)

            returncode = process.wait()
            logging.info(f"命令执行完毕，返回码: {returncode}")
            return returncode == 0
        except FileNotFoundError:
            msg = f"命令未找到: {command.split()[0]}"
            print_status(msg, status='error', indent=1)
            logging.error(msg)
            return False
        except Exception as e:
            msg = f"命令执行时发生错误: {e}"
            print_status(msg, status='error', indent=1)
            logging.error(msg, exc_info=True)
            return False

    # --- 滚动UI模式 ---
    if scroll_region_size == -1:
        # Heuristic: leave some lines for context above and below.
        # Use at least 5 lines.
        SCROLL_REGION_SIZE = max(5, get_terminal_height() - 8)
    else:
        SCROLL_REGION_SIZE = scroll_region_size
        
    terminal_width = get_terminal_width()

    # 打印初始状态行
    prefix = "▶ "
    prefix_width = 2  # "▶ "
    available_width = terminal_width - prefix_width
    command_text = f"执行命令: {command}"
    truncated_command = truncate_string(command_text, available_width)
    padding_len = available_width - get_display_width(truncated_command)
    padding = ' ' * max(0, padding_len)
    
    print(f"{Color.GRAY}{prefix}{truncated_command}{padding}{Color.RESET}")

    process = subprocess.Popen(
        command, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        env=env
    )

    output_buffer = deque(maxlen=SCROLL_REGION_SIZE)
    lines_rendered = 0
    hide_cursor()

    try:
        if process.stdout:
            for line in iter(process.stdout.readline, b''):
                stripped_line = decode_output(line).strip()
                output_buffer.append(stripped_line)
                if log_output:
                    logging.info(stripped_line)

                # 移动光标到绘制区域顶部
                if lines_rendered > 0:
                    move_cursor_up(lines_rendered)

                lines_rendered = min(len(output_buffer), SCROLL_REGION_SIZE)
                # 重新绘制滚动区域
                lines_to_render = list(output_buffer)
                for i in range(lines_rendered):
                    line_to_print = lines_to_render[i] if i < len(lines_to_render) else ""
                    prefix = f"{Color.GRAY}|{Color.RESET} "
                    prefix_width = 2
                    
                    available_width = terminal_width - prefix_width
                    truncated = truncate_string(line_to_print, available_width)
                    padding_len = available_width - get_display_width(truncated)
                    padding = ' ' * max(0, padding_len)
                    
                    # 使用 \r 和 \n 刷新行
                    print(f"\r{prefix}{truncated}{padding}")
                

        returncode = process.wait()
        logging.info(f"命令执行完毕，返回码: {returncode}")

    finally:
        show_cursor()

    # 清理滚动区域
    if lines_rendered > 0:
        move_cursor_up(lines_rendered)
        for _ in range(lines_rendered):
            print(' ' * terminal_width)
        move_cursor_up(lines_rendered)

    # 更新最终状态行
    move_cursor_up(1)
    
    if returncode == 0:
        final_symbol = f"{Color.GREEN}✓"
        success = True
    else:
        final_symbol = f"{Color.RED}✗"
        success = False

    # 重新计算填充以确保行被完全覆盖
    final_prefix = f"{final_symbol} "
    final_prefix_width = 2 # "✓ " or "✗ "
    available_width = terminal_width - final_prefix_width
    
    final_line_text = f"执行命令: {command}"
    truncated_final_line = truncate_string(final_line_text, available_width)
    padding_len = available_width - get_display_width(truncated_final_line)
    padding = ' ' * max(0, padding_len)
    
    print(f"\r{final_prefix}{truncated_final_line}{Color.RESET}{padding}")

    if check and not success:
        msg = f"命令执行失败，返回码: {returncode}"
        print_status(msg, status='error', indent=1)
        logging.error(msg)
        return False
        
    return success

def check_ksaa_update_available(pip_server: str, current_version: Version) -> tuple[bool, Version | None, Version | None]:
    """
    检查ksaa包是否有新版本可用。
    
    :param pip_server: pip服务器URL
    :type pip_server: str
    :param current_version: 当前版本
    :type current_version: Version
    :return: (是否有更新, 当前版本, 最新版本)
    :rtype: tuple[bool, Optional[Version], Optional[Version]]
    """
    try:
        # 使用repo.py中的list_versions函数和Version类获取最新版本信息
        from repo import list_versions, Version

        try:
            versions = list_versions("ksaa", server_url=pip_server)
            if versions and len(versions) > 0:
                latest_version = versions[0].version
                
                # 使用Version类的比较功能
                if latest_version > current_version:
                    return True, current_version, latest_version
        except Exception as e:
            logging.warning(f"从服务器 {pip_server} 获取版本信息失败: {e}")
            print_status(f"从服务器 {pip_server} 获取版本信息失败: {e}", status='error')
            # 如果指定服务器失败，尝试使用默认PyPI服务器
            try:
                versions = list_versions("ksaa")
                if versions and len(versions) > 0:
                    latest_version = versions[0].version
                    
                    # 使用Version类的比较功能
                    if latest_version > current_version:
                        return True, current_version, latest_version
            except Exception as e2:
                logging.warning(f"从PyPI获取版本信息也失败: {e2}")
        
        return False, current_version, latest_version if 'latest_version' in locals() else None
        
    except Exception as e:
        logging.warning(f"检查ksaa更新时发生错误: {e}")
        return False, None, None

def print_update_notice(current_version: str, latest_version: str):
    """
    打印更新提示信息。
    
    :param current_version: 当前版本
    :type current_version: str
    :param latest_version: 最新版本
    :type latest_version: str
    """
    clear_screen()
    print()
    print(f"{Color.YELLOW}{Color.BOLD}" + "=" * 60)
    print(f"{Color.YELLOW}{Color.BOLD}⚠️  发现新版本可用！")
    print(f"{Color.YELLOW}{Color.BOLD}" + "=" * 60)
    print(f"{Color.YELLOW}当前版本: {current_version}")
    print(f"{Color.YELLOW}最新版本: {latest_version}")
    print(f"{Color.YELLOW}建议开启自动更新或在设置中手动安装新版本。")
    print(f"{Color.YELLOW}5s 后继续启动")
    print(f"{Color.YELLOW}{Color.BOLD}" + "=" * 60 + f"{Color.RESET}")
    print()
    sleep(5)

def install_ksaa_version(pip_server: str, trusted_hosts: str, version: str) -> bool:
    """
    安装指定版本的ksaa包。

    :param pip_server: pip服务器URL
    :type pip_server: str
    :param trusted_hosts: 信任的主机列表
    :type trusted_hosts: str
    :param version: 要安装的版本号
    :type version: str
    :return: 安装是否成功
    :rtype: bool
    """
    print_status(f"安装琴音小助手 v{version}", status='info')
    install_command = f'"{PYTHON_EXECUTABLE}" -m pip install --index-url {pip_server} --trusted-host "{trusted_hosts}" --no-warn-script-location ksaa=={version}'
    return run_command(install_command)

def install_ksaa_from_zip(zip_path: str) -> bool:
    """
    从zip文件安装ksaa包。

    :param zip_path: zip文件路径
    :type zip_path: str
    :return: 安装是否成功
    :rtype: bool
    """
    zip_file = Path(zip_path)
    if not zip_file.exists():
        msg = f"zip文件不存在: {zip_path}"
        print_status(msg, status='error')
        logging.error(msg)
        return False

    if not zip_file.suffix.lower() == '.zip':
        msg = f"文件不是zip格式: {zip_path}"
        print_status(msg, status='error')
        logging.error(msg)
        return False

    print_status(f"从zip文件安装琴音小助手: {zip_path}", status='info')

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        try:
            # 解压zip文件
            print_status("解压zip文件...", status='info', indent=1)
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(temp_path)

            # 使用pip install --find-links安装
            print_status("安装ksaa包...", status='info', indent=1)
            install_command = f'"{PYTHON_EXECUTABLE}" -m pip install --no-warn-script-location --no-cache-dir --upgrade --no-deps --force-reinstall --no-index --find-links "{temp_path.absolute()}" ksaa'
            return run_command(install_command)

        except zipfile.BadZipFile:
            msg = f"无效的zip文件: {zip_path}"
            print_status(msg, status='error')
            logging.error(msg)
            return False
        except Exception as e:
            msg = f"从zip文件安装失败: {e}"
            print_status(msg, status='error')
            logging.error(msg, exc_info=True)
            return False


def install_ksaa_from_package(package_path: str) -> bool:
    """
    从 .whl 或 .tar.gz 文件安装ksaa包。

    :param package_path: .whl或.tar.gz文件路径
    :type package_path: str
    :return: 安装是否成功
    :rtype: bool
    """
    package_file = Path(package_path)
    if not package_file.exists():
        msg = f"包文件不存在: {package_path}"
        print_status(msg, status='error')
        logging.error(msg)
        return False

    suffix = package_file.suffix.lower()
    if not (suffix == '.whl' or package_path.lower().endswith('.tar.gz')):
        msg = f"文件不是 .whl 或 .tar.gz 格式: {package_path}"
        print_status(msg, status='error')
        logging.error(msg)
        return False

    print_status(f"从包文件安装琴音小助手: {package_path}", status='info')

    install_command = f'"{PYTHON_EXECUTABLE}" -m pip install --no-warn-script-location --no-cache-dir --upgrade --no-deps --force-reinstall --no-index "{package_file.absolute()}"'
    return run_command(install_command)

def install_pip_and_ksaa(pip_server: str, check_update: bool = True, install_update: bool = True) -> bool:
    """
    安装和更新pip以及ksaa包。

    :param pip_server: pip服务器URL
    :type pip_server: str
    :param check_update: 是否检查更新
    :type check_update: bool
    :param install_update: 是否安装更新
    :type install_update: bool
    :return: 安装是否成功
    :rtype: bool
    """
    print_header("安装与更新小助手", color=Color.BLUE)

    # 升级pip
    print_status("更新 pip", status='info')
    upgrade_pip_command = f'"{PYTHON_EXECUTABLE}" -m pip install -i {pip_server} --trusted-host "{TRUSTED_HOSTS}" --upgrade pip'
    if not run_command(upgrade_pip_command):
        return False

    # 默认安装逻辑
    install_command = f'"{PYTHON_EXECUTABLE}" -m pip install --upgrade --index-url {pip_server} --trusted-host "{TRUSTED_HOSTS}" --no-warn-script-location ksaa'
    ksaa_version_str = package_version("ksaa")
    # 未安装
    if not ksaa_version_str:
        print_status("安装琴音小助手", status='info')
        return run_command(install_command)
    # 已安装，检查更新
    else:
        ksaa_version = Version(ksaa_version_str)
        if check_update:
            has_update, current_version, latest_version = check_ksaa_update_available(pip_server, ksaa_version)
            if has_update:
                if install_update:
                    print_status("更新琴音小助手", status='info')
                    return run_command(install_command)
                else:
                    print_update_notice(str(current_version), str(latest_version))
            else:
                print_status("已是最新版本", status='success')
    return True

def load_config() -> Optional[Config]:
    """
    加载config.json配置文件。
    
    :return: 配置字典，如果加载失败返回None
    :rtype: Optional[Config]
    """
    config_path = Path("./config.json")
    if not config_path.exists():
        msg = "配置文件 config.json 不存在，跳过配置加载"
        print_status(msg, status='warning')
        logging.warning(msg)
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        msg = "成功加载配置文件"
        print_status(msg, status='success')
        logging.info(msg)
        return config
    except Exception as e:
        msg = f"加载配置文件失败: {e}"
        print_status(msg, status='error')
        logging.error(msg, exc_info=True)
        return None

def get_update_settings(config: Config) -> tuple[bool, bool]:
    """
    从配置中获取更新设置。
    
    :param config: 配置字典
    :type config: Config
    :return: (是否检查更新, 是否自动安装更新)
    :rtype: tuple[bool, bool]
    """
    # 默认值
    check_update = True
    auto_install_update = True
    
    # 检查是否有用户配置
    user_configs = config.get("user_configs", [])
    if user_configs:
        first_config = user_configs[0]
        options = first_config.get("options", {})
        misc = options.get("misc", {})
        
        # 获取检查更新设置
        check_update_setting = misc.get("check_update", "startup")
        check_update = check_update_setting == "startup"
        
        # 获取自动安装更新设置
        auto_install_update = misc.get("auto_install_update", True)
        
        msg = f"更新设置: 检查更新={check_update}, 自动安装={auto_install_update}"
        logging.info(msg)
    
    return check_update, auto_install_update

def restart_as_admin() -> None:
    """
    以管理员身份重启程序。
    """
    if is_admin():
        return

    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{item}"' for item in sys.argv[1:]])
    
    try:
        # 使用 ShellExecute 以管理员身份启动程序
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", PYTHON_EXECUTABLE, f'"{script}" {params}', None, 1
        )
        if ret > 32:  # 返回值大于32表示成功
            msg = "正在以管理员身份重启程序..."
            print_status(msg, status='info')
            logging.info(msg)
            os._exit(0)
        else:
            msg = f"以管理员身份重启失败，错误码: {ret}"
            print_status(msg, status='error')
            logging.error(msg)
            return
    except Exception as e:
        msg = f"以管理员身份重启时发生错误: {e}"
        print_status(msg, status='error')
        logging.error(msg, exc_info=True)
        return

def check_admin(config: Config) -> bool:
    """
    检查Windows截图权限（管理员权限）。
    
    :param config: 配置字典
    :type config: Config
    :return: 权限检查是否通过
    :rtype: bool
    """
    # 检查是否有用户配置
    user_configs = config.get("user_configs", [])
    if not user_configs:
        msg = "配置文件中没有用户配置"
        print_status(msg, status='warning')
        logging.warning(msg)
        return True # Not a fatal error, allow to continue
    
    # 检查第一个用户配置的截图方式
    first_config = user_configs[0]
    backend = first_config.get("backend", {})
    screenshot_impl = backend.get("screenshot_impl")
    
    if screenshot_impl == "windows":
        msg = "检测到Windows截图模式，检查管理员权限..."
        print_status(msg, status='info')
        logging.info(msg)
        if not is_admin():
            msg1 = "需要管理员权限才能使用Windows截图模式"
            print_status(msg1, status='error')
            logging.error(msg1)
            
            # 尝试以管理员身份重启
            msg2 = "正在尝试以管理员身份重启..."
            print_status(msg2, status='info', indent=1)
            logging.info(msg2)
            restart_as_admin()
            return False
        else:
            msg = "管理员权限检查通过"
            print_status(msg, status='success')
            logging.info(msg)
    
    return True

def run_kaa(args: list[str]) -> bool:
    """
    运行琴音小助手。
    
    :return: 运行是否成功
    :rtype: bool
    """
    print_header("运行琴音小助手", color=Color.GREEN)
    clear_screen()
    
    # 设置环境变量
    os.environ["no_proxy"] = "localhost, 127.0.0.1, ::1"
    
    # 运行kaa命令
    if not run_command(f'"{PYTHON_EXECUTABLE}" -m kotonebot.kaa.main.cli {" ".join(args)}', verbatim=True, log_output=False):
        return False
    
    print_header("运行结束", color=Color.GREEN)
    return True


def parse_arguments():
    """
    解析命令行参数。

    :return: 解析后的参数
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description='琴音小助手启动器')
    parser.add_argument('package_file', nargs='?', help='要安装的包文件路径（.whl, .tar.gz, .zip）')
    parser.add_argument('--install-version', type=str, help='安装指定版本的 ksaa (例如: --install-version=1.2.3)')
    parser.add_argument('--install-from-zip', type=str, help='从 zip 文件安装 ksaa (例如: --install-from-zip=/path/to/file.zip)')
    parser.add_argument('--install-from-package', type=str, help='从 .whl 或 .tar.gz 文件安装 ksaa')

    args, extra_args = parser.parse_known_args()
    args.extra_args = extra_args

    return args

def main_launch():
    """
    主启动函数，执行完整的安装和启动流程。
    """
    # 解析命令行参数
    args = parse_arguments()

    # 处理位置参数
    if args.package_file:
        lower_path = args.package_file.lower()
        if lower_path.endswith('.zip'):
            if not args.install_from_zip:
                args.install_from_zip = args.package_file
        elif lower_path.endswith('.whl') or lower_path.endswith('.tar.gz'):
            if not args.install_from_package:
                args.install_from_package = args.package_file
        else:
            raise ValueError(f"不支持的文件类型: {args.package_file}")

    setup_logging()
    run_command("title 琴音小助手（运行时请勿关闭此窗口）", verbatim=True, log_output=False)
    clear_screen()
    print_header("琴音小助手启动器")
    logging.info("启动器已启动。")

    try:
        # 1. 加载配置文件（提前加载以获取更新设置）
        print_header("加载配置", color=Color.BLUE)
        logging.info("加载配置。")
        config = load_config()

        # 2. 获取更新设置
        check_update, auto_install_update = get_update_settings(config if config else {"version": 5, "user_configs": []})

        # 3. 如果指定了特殊安装参数，跳过更新检查
        if args.install_version or args.install_from_zip or args.install_from_package:
            check_update = False
            auto_install_update = False

        # 4. 根据配置决定是否检查更新
        print_status("正在寻找最快的 PyPI 镜像源...", status='info')
        logging.info("正在寻找最快的 PyPI 镜像源...")
        pip_server = get_working_pip_server()
        if not pip_server:
            raise RuntimeError("没有找到可用的pip服务器，请检查网络连接。")

        # 5. 处理特殊安装情况
        if args.install_from_zip:
            # 从zip文件安装
            print_header("安装补丁", color=Color.BLUE)
            if not install_ksaa_from_zip(args.install_from_zip):
                raise RuntimeError("从zip文件安装失败，请检查上面的错误日志。")
        elif args.install_from_package:
            # 从包文件安装
            print_header("安装补丁", color=Color.BLUE)
            if not install_ksaa_from_package(args.install_from_package):
                raise RuntimeError("从包文件安装失败，请检查上面的错误日志。")
        elif args.install_version:
            # 安装指定版本
            print_header("安装指定版本", color=Color.BLUE)
            if not install_ksaa_version(pip_server, TRUSTED_HOSTS, args.install_version):
                raise RuntimeError("安装指定版本失败，请检查上面的错误日志。")
        else:
            # 默认安装和更新逻辑
            if not install_pip_and_ksaa(pip_server, check_update, auto_install_update):
                raise RuntimeError("依赖安装失败，请检查上面的错误日志。")

        # 6. 检查Windows截图权限
        if config:
            if not check_admin(config):
                raise RuntimeError("权限检查失败。")

        # 7. 运行琴音小助手
        if not run_kaa(args.extra_args):
            raise RuntimeError("琴音小助手主程序运行失败。")

        msg = "琴音小助手已退出。"
        print_status(msg, status='success')
        logging.info(msg)

    except Exception as e:
        msg = f"发生致命错误: {e}"
        print_status(msg, status='error')
        print_status("压缩 kaa 目录下的 logs 文件夹并给此窗口截图后一并发送给开发者", status='error')
        logging.critical(msg, exc_info=True)

    finally:
        logging.info("启动器运行结束。")
        wait_key("\n按任意键退出...")

if __name__ == "__main__":
    try:
        main_launch()
    except KeyboardInterrupt:
        print_status("运行结束。现在可以安全关闭此窗口。", status='info')