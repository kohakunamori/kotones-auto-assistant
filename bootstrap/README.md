# bootstrap
此文件夹下存放的是为了简化分发而编写的启动器代码。

## bootstrap/kaa-bootstrap
启动器本体，由 Python 编写。负责：
1. 寻找最快的 PyPI 镜像源
2. 安装与更新 pip 和 kaa 本体
3. 读入配置文件，检查是否需要管理员权限
4. 启动 kaa

打包产物：bootstrap.pyz

## bootstrap/kaa-wrapper
启动器包装器，由 C++ 编写，用于调用 Python 启动 kaa-bootstrap。

打包产物：kaa.exe