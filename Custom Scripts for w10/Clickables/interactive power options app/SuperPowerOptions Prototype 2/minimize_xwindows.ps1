Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public class Win32 {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern int GetWindowTextLength(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
}
"@

# Target keywords in window titles
$targets = @("Docker", "VcXsrv", "xming")

# Define the enumeration callback
$windows = @()
$enumFunc = [Win32+EnumWindowsProc]{
    param($hWnd, $lParam)

    if (-not [Win32]::IsWindowVisible($hWnd)) { return $true }

    $length = [Win32]::GetWindowTextLength($hWnd)
    if ($length -eq 0) { return $true }

    $builder = New-Object System.Text.StringBuilder $length
    [Win32]::GetWindowText($hWnd, $builder, $length + 1)
    $title = $builder.ToString()

    foreach ($target in $targets) {
        if ($title -like "*$target*") {
            [Win32]::ShowWindowAsync($hWnd, 6)  # Minimize
            Write-Output "Minimized: $title"
        }
    }

    return $true
}

# Execute enumeration
[Win32]::EnumWindows($enumFunc, [IntPtr]::Zero)
