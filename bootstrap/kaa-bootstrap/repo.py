import importlib
import re
import sys
import html.parser
import urllib.parse
from typing import List
from dataclasses import dataclass
from request import get, HTTPError
from importlib.metadata import version, PackageNotFoundError

PYTHON_EXECUTABLE = sys.executable
# PEP 440 version regex (simplified from the official pattern)
VERSION_PATTERN = r"""
    v?
    (?:(?P<epoch>[0-9]+)!)?                           # epoch
    (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
    (?P<pre>                                          # pre-release
        [-_\.]?
        (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
        [-_\.]?
        (?P<pre_n>[0-9]+)?
    )?
    (?P<post>                                         # post release
        (?:-(?P<post_n1>[0-9]+))
        |
        (?:
            [-_\.]?
            (?P<post_l>post|rev|r)
            [-_\.]?
            (?P<post_n2>[0-9]+)?
        )
    )?
    (?P<dev>                                          # dev release
        [-_\.]?
        (?P<dev_l>dev)
        [-_\.]?
        (?P<dev_n>[0-9]+)?
    )?
    (?:\+[a-z0-9]+(?:[-_\.][a-z0-9]+)*)?            # local version
"""
_VERSION_REGEX = re.compile(r"^\s*(?:" + VERSION_PATTERN + r")\s*$", re.VERBOSE | re.IGNORECASE)


def _normalize_pre_label(label: str) -> str:
    label = label.lower()
    if label in {"alpha", "a"}:
        return "a"
    if label in {"beta", "b"}:
        return "b"
    if label in {"rc", "c", "pre", "preview"}:
        return "rc"
    return label


@dataclass
class Version:
    """版本信息"""
    version_str: str
    major: int = 0
    minor: int = 0
    patch: int = 0
    prerelease: str = ""
    prerelease_num: int = 0
    
    def __post_init__(self):
        """初始化后解析版本号"""
        self._parse_version()
    
    def _parse_version(self):
        """解析版本号字符串（尽量遵循 PEP 440）"""
        raw = self.version_str.strip()
        version_str = raw.lower().lstrip('v')

        # 使用 PEP 440 兼容的正则解析
        m = _VERSION_REGEX.match(version_str)
        if m:
            # 解析 release 段
            release = m.group('release')
            if release:
                parts = [int(p) for p in release.split('.')]
                self.major = parts[0] if len(parts) > 0 else 0
                self.minor = parts[1] if len(parts) > 1 else 0
                self.patch = parts[2] if len(parts) > 2 else 0

            # 处理 dev / pre / post（只保留一种标记用于比较与过滤）
            if m.group('dev') is not None:
                # 开发版视为预发布
                self.prerelease = 'dev'
                self.prerelease_num = int(m.group('dev_n') or 0)
            elif m.group('pre') is not None:
                self.prerelease = _normalize_pre_label(m.group('pre_l') or '')
                self.prerelease_num = int(m.group('pre_n') or 0)
            elif m.group('post') is not None:
                # post 版本：比正式版更高
                self.prerelease = 'post'
                # 两种 post 表达方式择其一
                post_n = m.group('post_n1') or m.group('post_n2') or 0
                self.prerelease_num = int(post_n)
            else:
                self.prerelease = ''
                self.prerelease_num = 0
            return

        # 回退：简单解析
        version_match = re.match(r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?', version_str)
        if version_match:
            self.major = int(version_match.group(1))
            self.minor = int(version_match.group(2)) if version_match.group(2) else 0
            self.patch = int(version_match.group(3)) if version_match.group(3) else 0
        
        prerelease_match = re.search(r'(a|b|c|rc|alpha|beta|pre|preview|dev|post)\s*([0-9]*)', version_str)
        if prerelease_match:
            self.prerelease = _normalize_pre_label(prerelease_match.group(1))
            self.prerelease_num = int(prerelease_match.group(2)) if prerelease_match.group(2) else 0
    
    def __lt__(self, other):
        """版本比较"""
        if not isinstance(other, Version):
            return NotImplemented
        
        # 比较主版本号
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        
        # 比较预发布/后发布顺序（dev < a < b < rc < final < post）
        prerelease_order = {'dev': 0, 'a': 1, 'b': 2, 'rc': 3, '': 4, 'post': 5}
        self_order = prerelease_order.get(self.prerelease, 4)
        other_order = prerelease_order.get(other.prerelease, 4)
        
        if self_order != other_order:
            return self_order < other_order
        
        # 同类型比较数字
        if self.prerelease == other.prerelease:
            return self.prerelease_num < other.prerelease_num
        
        return False
    
    def __eq__(self, other):
        """版本相等比较"""
        if not isinstance(other, Version):
            return NotImplemented
        
        return (self.major == other.major and 
                self.minor == other.minor and 
                self.patch == other.patch and
                self.prerelease == other.prerelease and
                self.prerelease_num == other.prerelease_num)
    
    def __repr__(self):
        return f"Version('{self.version_str}')"

    def __str__(self):
        return self.version_str

@dataclass
class PackageVersion:
    """包版本信息"""
    version: Version
    url: str


class PyPIHTMLParser(html.parser.HTMLParser):
    """解析PyPI HTML响应的解析器"""
    
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_href = None
        self.current_text = None
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            # 提取href属性
            for attr_name, attr_value in attrs:
                if attr_name == 'href':
                    self.current_href = attr_value
                    break
    
    def handle_data(self, data):
        if self.current_href:
            self.current_text = data.strip()
    
    def handle_endtag(self, tag):
        if tag == 'a' and self.current_href and self.current_text:
            self.links.append((self.current_text, self.current_href))
            self.current_href = None
            self.current_text = None


def normalize_package_name(package_name: str) -> str:
    """
    标准化包名，将 _, -, . 字符视为相等
    """
    return re.sub(r'[_.-]', '-', package_name.lower())


def extract_version_from_filename(filename: str) -> str:
    """
    从文件名中提取版本号
    
    例如: beautifulsoup4-4.13.0b2-py3-none-any.whl -> 4.13.0b2
    """
    # 匹配版本号模式
    version_pattern = r'^[^-]+-([^-]+?)(?:-py\d+)?(?:-none-any)?\.(?:whl|tar\.gz|zip)$'
    match = re.match(version_pattern, filename)
    if match:
        return match.group(1)
    
    # 备用模式：查找版本号
    version_match = re.search(r'-(\d+\.\d+(?:\.\d+)?(?:[a-zA-Z0-9]*))', filename)
    if version_match:
        return version_match.group(1)
    
    return "unknown"


def list_versions(package_name: str, *, server_url: str | None = None, include_pre_release: bool = False) -> List[PackageVersion]:
    """
    获取指定包的所有可用版本，按版本号降序排列
    
    :param package_name: 包名
    :type package_name: str
    :param server_url: 可选的服务器URL，默认为None时使用PyPI官方服务器（https://pypi.org/simple）。
    :type server_url: str | None
    :param include_pre_release: 是否包含预发布版本（alpha/beta/rc/dev/pre）。默认不包含。
    :type include_pre_release: bool
    :return: 包含版本信息的列表，按版本号降序排列
    :rtype: List[PackageVersion]
    :raises HTTPError: 当包不存在或网络错误时
    :raises NetworkError: 当网络连接错误时
    """
    # 标准化包名
    normalized_name = normalize_package_name(package_name)
    
    # 构建API URL
    if server_url is None:
        base_url = "https://pypi.org/simple"
    else:
        base_url = server_url.rstrip('/')
    
    url = f"{base_url}/{urllib.parse.quote(normalized_name)}/"
    
    # 设置请求头
    headers = {
        'Accept': 'application/vnd.pypi.simple.v1+html'
    }
    
    try:
        # 发送请求
        html_content = get(url, headers=headers).decode('utf-8')
        
        # 解析HTML
        parser = PyPIHTMLParser()
        parser.feed(html_content)
        
        # 处理链接并提取版本信息
        versions: list[PackageVersion] = []
        for filename, href in parser.links:
            # 提取版本号
            version_str = extract_version_from_filename(filename)
            
            # 创建Version对象
            version = Version(version_str)
            
            # 过滤预发布版本（当不包含预发布时）
            if not include_pre_release:
                if version.prerelease in {'a', 'b', 'rc', 'dev'}:
                    continue
            
            # 创建PackageVersion对象
            package_version = PackageVersion(
                version=version,
                url=href
            )
            versions.append(package_version)
        
        # 按版本号降序排列
        versions.sort(key=lambda x: x.version, reverse=True)
        
        return versions
        
    except HTTPError as e:
        if e.code == 404:
            raise ValueError(f"包 '{package_name}' 不存在") from e
        else:
            raise

def local_version(package_name: str) -> Version | None:
    """
    获取已安装的包的版本信息

    :return: 已安装的包的版本信息，如果包未安装则返回None
    """
    try:
        return Version(version(package_name))
    except PackageNotFoundError:
        return None

def latest_version(package_name: str, *, server_url: str | None = None, include_pre_release: bool = False) -> Version | None:
    """
    获取指定包的最新版本信息
    """
    versions = list_versions(package_name, server_url=server_url, include_pre_release=include_pre_release)
    return versions[0].version if versions else None

def main():
    """测试函数"""
    try:
        # 测试获取beautifulsoup4的版本
        print("获取 beautifulsoup4 的版本信息...")
        versions = list_versions("beautifulsoup4", include_pre_release=True)
        
        print(f"找到 {len(versions)} 个版本:")
        for i, pkg_version in enumerate(versions[:10], 1):  # 只显示前10个
            print(f"{i}. 版本: {pkg_version.version.version_str}")
            print(f"   主版本: {pkg_version.version.major}.{pkg_version.version.minor}.{pkg_version.version.patch}")
            if pkg_version.version.prerelease:
                print(f"   预发布: {pkg_version.version.prerelease}{pkg_version.version.prerelease_num}")
            print(f"   URL: {pkg_version.url}")
            print()
            
        if len(versions) > 10:
            print(f"... 还有 {len(versions) - 10} 个版本")
            
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
