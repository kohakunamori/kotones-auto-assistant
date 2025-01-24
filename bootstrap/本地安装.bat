@echo off
call WPy64-310111\scripts\env.bat
if errorlevel 1 (
    goto ERROR
)

if "%~1"=="" (
    echo 请将 whl 文件拖到此脚本上
    pause
    exit /b 1
)

echo 卸载原有包...
pip uninstall -y ksaa
if errorlevel 1 (
    goto ERROR
)

echo 正在安装 %~1 ...
pip install "%~1"
if errorlevel 1 (
    goto ERROR
)

echo 安装完成
pause
exit /b 0

:ERROR
echo 发生错误，程序退出
pause
exit /b 1