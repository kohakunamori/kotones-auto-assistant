@echo off
cd /D %~dp0

REM https://superuser.com/questions/788924/is-it-possible-to-automatically-run-a-batch-file-as-administrator
REM  --> Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo 需要以管理员身份运行。右键此脚本，选择“以管理员身份运行”。
    pause
    exit /b 1
)

call WPy64-310111\scripts\env.bat
if errorlevel 1 (
    goto ERROR
)
set PIP_EXTRA_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple/ http://mirrors.aliyun.com/pypi/simple/

echo =========== 安装与更新 KAA ===========
:INSTALL
echo 检查 pip
python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
if errorlevel 1 (
    goto ERROR
)
pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org mirrors.aliyun.com mirrors.cloud.tencent.com mirrors.tuna.tsinghua.edu.cn"
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
echo 安装 ksaa
pip install --upgrade ksaa
if errorlevel 1 (
    goto ERROR
)

echo =========== 当前版本 ===========
pip show ksaa

echo =========== 运行 KAA ===========
:RUN
kaa
if errorlevel 1 (
    goto ERROR
)

echo =========== 运行结束 ===========
pause
exit /b 0

:ERROR
echo 发生错误，程序退出
pause
exit /b 1