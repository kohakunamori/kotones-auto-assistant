@echo off
call WPy64-310111\scripts\env.bat
if errorlevel 1 (
    goto ERROR
)

if "%~1"=="" (
    echo 请将 Python 包文件拖到此脚本上
    pause
    exit /b 1
)

echo =========== 卸载原有包 ===========
pip uninstall -y ksaa
pip uninstall -y ksaa_res
if errorlevel 1 (
    goto ERROR
)

:INSTALL_LOOP
if "%~1"=="" goto INSTALL_DONE

echo =========== 安装 %~1 ===========
pip install "%~1"
if errorlevel 1 (
    goto ERROR
)

shift
goto INSTALL_LOOP

:INSTALL_DONE
echo =========== 安装完成 ===========
pause
exit /b 0

:ERROR
echo 发生错误，程序退出
pause
exit /b 1