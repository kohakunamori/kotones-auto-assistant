// kaa-wrapper.cpp : 定义应用程序的入口点。
//

#include "framework.h"
#include "kaa-wrapper.h"
#include <string>

int APIENTRY wWinMain(_In_ HINSTANCE hInstance,
                     _In_opt_ HINSTANCE hPrevInstance,
                     _In_ LPWSTR    lpCmdLine,
                     _In_ int       nCmdShow)
{
    UNREFERENCED_PARAMETER(hInstance);
    UNREFERENCED_PARAMETER(hPrevInstance);
    UNREFERENCED_PARAMETER(nCmdShow);

    // 设置当前目录为程序所在目录
    WCHAR szPath[MAX_PATH];
    if (GetModuleFileNameW(NULL, szPath, MAX_PATH) == 0) {
        MessageBoxW(NULL, L"无法获取程序所在目录", L"错误", MB_OK | MB_ICONERROR);
        return 1;
    }

    std::wstring path(szPath);
    size_t pos = path.find_last_of(L"\\");
    if (pos == std::wstring::npos) {
        MessageBoxW(NULL, L"程序路径格式错误", L"错误", MB_OK | MB_ICONERROR);
        return 1;
    }

    path = path.substr(0, pos);
    if (!SetCurrentDirectoryW(path.c_str())) {
        MessageBoxW(NULL, L"无法设置工作目录", L"错误", MB_OK | MB_ICONERROR);
        return 1;
    }

    // 检查 Python 解释器是否存在
    std::wstring pythonPath = path + L"\\WPy64-310111\\python-3.10.11.amd64\\python.exe";
    if (GetFileAttributesW(pythonPath.c_str()) == INVALID_FILE_ATTRIBUTES) {
        MessageBoxW(NULL, L"找不到 Python 解释器", L"错误", MB_OK | MB_ICONERROR);
        return 1;
    }

    // 检查 bootstrap.pyz 是否存在
    std::wstring bootstrapPath = path + L"\\bootstrap.pyz";
    if (GetFileAttributesW(bootstrapPath.c_str()) == INVALID_FILE_ATTRIBUTES) {
        MessageBoxW(NULL, L"找不到 bootstrap.pyz 文件", L"错误", MB_OK | MB_ICONERROR);
        return 1;
    }

    // 构建命令行
    std::wstring cmd = L"\"" + pythonPath + L"\" \"" + bootstrapPath + L"\"";

    // 如果有命令行参数，将其传递给 bootstrap
    if (lpCmdLine && wcslen(lpCmdLine) > 0) {
        cmd += L" ";
        cmd += lpCmdLine;
    }
    
    // 启动信息
    STARTUPINFOW si = { sizeof(si) };
    PROCESS_INFORMATION pi;
    
    // 创建进程，使用当前目录作为工作目录
    if (!CreateProcessW(NULL,
        const_cast<LPWSTR>(cmd.c_str()),
        NULL,
        NULL,
        FALSE,
        0,
        NULL,
        path.c_str(),  // 设置工作目录为当前目录
        &si,
        &pi))
    {
        DWORD error = GetLastError();
        WCHAR errorMsg[256];
        swprintf_s(errorMsg, L"无法启动程序 (错误代码: %d)", error);
        MessageBoxW(NULL, errorMsg, L"错误", MB_OK | MB_ICONERROR);
        return 1;
    }

    // 关闭进程和线程句柄
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return 0;
}
