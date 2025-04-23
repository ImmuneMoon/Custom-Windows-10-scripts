Add-Type @"
using System;
using System.Runtime.InteropServices;

Write-Output "RUNNING minimize_xwindows.ps1"

public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
}
"@

# Array of target window titles (partial matches)
$windowTitles = @("Server", "Docker")

# Iterate over each target window title
foreach ($windowTitle in $windowTitles) {
    Get-Process | Where-Object {
        $_.MainWindowTitle -like "*$windowTitle*"
    } | ForEach-Object {
        $hwnd = $_.MainWindowHandle
        if ($hwnd -ne 0) {
            [Win32]::ShowWindowAsync($hwnd, 6)  # 6 = SW_MINIMIZE
            Write-Output "Minimized: $($_.ProcessName) [$($_.Id)]"
        }
    }
}
