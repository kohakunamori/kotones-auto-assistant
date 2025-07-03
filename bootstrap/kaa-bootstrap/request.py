import os
import urllib.parse
import urllib.error
import urllib.request
from typing import Dict, Any, Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from http.client import HTTPResponse


class HTTPError(Exception):
    """HTTP请求错误"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"HTTP {code}: {message}")


class NetworkError(Exception):
    """网络连接错误"""
    pass


class Response:
    """HTTP响应封装"""

    def __init__(self, http_response: "HTTPResponse"):
        self._response = http_response
        self._content: Optional[bytes] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """关闭响应和底层连接。"""
        self._response.close()

    @property
    def status_code(self) -> int:
        """响应状态码"""
        return self._response.getcode()

    @property
    def reason(self) -> str:
        """响应原因短语"""
        return self._response.reason

    @property
    def headers(self) -> Dict[str, Any]:
        """响应头"""
        return dict(self._response.headers)

    def read(self) -> bytes:
        """读取响应内容 (bytes)"""
        if self._content is None:
            self._content = self._response.read()
        return self._content

    def json(self) -> Any:
        """将响应内容解析为JSON"""
        import json
        return json.loads(self.read())


def request(
    url: str, 
    method: str = "GET", 
    headers: Optional[Dict[str, str]] = None,
    data: Optional[bytes] = None,
    timeout: Optional[float] = None
) -> Response:
    """
    发送HTTP请求
    
    :param url: 请求URL
    :type url: str
    :param method: HTTP方法，默认为GET
    :type method: str
    :param headers: 请求头
    :type headers: Optional[Dict[str, str]]
    :param data: 请求数据
    :type data: Optional[bytes]
    :param timeout: 超时时间（秒）
    :type timeout: Optional[float]
    :return: 响应对象
    :rtype: Response
    :raises HTTPError: HTTP错误
    :raises NetworkError: 网络连接错误
    """
    # 设置默认请求头
    default_headers = {
        'User-Agent': 'Python-urllib/3.10'
    }
    
    if headers:
        default_headers.update(headers)
    
    # 创建请求
    req = urllib.request.Request(url, data=data, headers=default_headers, method=method)
    
    try:
        # 发送请求
        response = urllib.request.urlopen(req, timeout=timeout)
        return Response(response)
            
    except urllib.error.HTTPError as e:
        raise HTTPError(e.code, e.reason) from e
    except urllib.error.URLError as e:
        raise NetworkError(f"网络连接错误: {e.reason}") from e


def get(url: str, headers: Optional[Dict[str, str]] = None, timeout: Optional[float] = None) -> bytes:
    """
    发送GET请求
    
    :param url: 请求URL
    :type url: str
    :param headers: 请求头
    :type headers: Optional[Dict[str, str]]
    :param timeout: 超时时间（秒）
    :type timeout: Optional[float]
    :return: 响应内容
    :rtype: bytes
    """
    with request(url, method="GET", headers=headers, timeout=timeout) as response:
        return response.read()


def head(url: str, headers: Optional[Dict[str, str]] = None, timeout: Optional[float] = None) -> Response:
    """
    发送HEAD请求
    
    :param url: 请求URL
    :type url: str
    :param headers: 请求头
    :type headers: Optional[Dict[str, str]]
    :param timeout: 超时时间（秒）
    :type timeout: Optional[float]
    :return: 响应对象
    :rtype: Response
    :raises HTTPError: HTTP错误
    :raises NetworkError: 网络连接错误
    """
    return request(url, method="HEAD", headers=headers, timeout=timeout)


def download_file(
    url: str, 
    dst_path: str, 
    *, 
    callback: Optional[Callable[[int, int], None]] = None,
    timeout: Optional[float] = None
) -> None:
    """
    下载文件
    
    :param url: 文件URL
    :type url: str
    :param dst_path: 目标路径
    :type dst_path: str
    :param callback: 进度回调函数，参数为(已下载字节数, 总字节数)
    :type callback: Optional[Callable[[int, int], None]]
    :param timeout: 超时时间（秒）
    :type timeout: Optional[float]
    :raises HTTPError: HTTP错误
    :raises NetworkError: 网络连接错误
    """
    # 设置请求头
    headers = {
        'User-Agent': 'Python-urllib/3.10'
    }
    
    # 创建请求
    req = urllib.request.Request(url, headers=headers)
    
    try:
        # 发送请求
        with urllib.request.urlopen(req, timeout=timeout) as response:
            # 获取文件大小
            content_length = response.headers.get('Content-Length')
            total_size = int(content_length) if content_length else None
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            
            # 下载文件
            downloaded_size = 0
            with open(dst_path, 'wb') as f:
                while True:
                    chunk = response.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # 调用进度回调
                    if callback and total_size:
                        callback(downloaded_size, total_size)
                    elif callback and not total_size:
                        callback(downloaded_size, -1)  # 未知总大小
                        
    except urllib.error.HTTPError as e:
        raise HTTPError(e.code, e.reason) from e
    except urllib.error.URLError as e:
        raise NetworkError(f"网络连接错误: {e.reason}") from e
    except OSError as e:
        raise NetworkError(f"文件写入错误: {e}") from e


def main():
    """测试函数"""
    try:
        # 测试GET请求
        print("测试GET请求...")
        response_bytes = get("https://httpbin.org/get")
        print(f"响应长度: {len(response_bytes)} 字节")
        
        # 测试文件下载
        print("\n测试文件下载...")
        def progress_callback(downloaded: int, total: int):
            if total > 0:
                percentage = (downloaded / total) * 100
                print(f"下载进度: {downloaded}/{total} 字节 ({percentage:.1f}%)")
            else:
                print(f"已下载: {downloaded} 字节")
        
        # 下载一个小文件进行测试
        download_file(
            "https://httpbin.org/bytes/1024", 
            "test_download.bin",
            callback=progress_callback
        )
        print("下载完成!")
        
        # 清理测试文件
        if os.path.exists("test_download.bin"):
            os.remove("test_download.bin")
            
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
