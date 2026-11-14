/* Native Windows entry point; /MT keeps the compiler runtime inside this EXE. */
#define UNICODE
#define _UNICODE
#include <windows.h>
#include <wchar.h>

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previous, PWSTR args, int show) {
    wchar_t root[32768], python[32768], command[32768];
    STARTUPINFOW startup = { sizeof(startup) };
    PROCESS_INFORMATION process;
    DWORD result;
    (void)instance; (void)previous; (void)show;
    if (!GetModuleFileNameW(NULL, root, 32768)) return 1;
    wchar_t *separator = wcsrchr(root, L'\\');
    if (!separator) return 1;
    *separator = 0;
    if (swprintf_s(python, 32768, L"%s\\pythonw.exe", root) < 0 ||
        swprintf_s(command, 32768, L"\"%s\" -I \"%s\\app\\src\\launch.py\" %s", python, root, args) < 0) return 1;
    /* -I ignores user Python packages and PYTHONPATH. launch.py adds its own source path. */
    if (!CreateProcessW(python, command, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, root, &startup, &process)) {
        MessageBoxW(NULL, L"The application could not start. Please reinstall VocaListener Modern.", L"VocaListener Modern", MB_OK | MB_ICONERROR);
        return 1;
    }
    WaitForSingleObject(process.hProcess, INFINITE);
    GetExitCodeProcess(process.hProcess, &result);
    CloseHandle(process.hProcess);
    CloseHandle(process.hThread);
    return (int)result;
}
