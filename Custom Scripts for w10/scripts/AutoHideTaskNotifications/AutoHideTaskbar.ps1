function Hide-Taskbar { 
    Add-Type -TypeDefinition @" 
	using System; 
	using System.Runtime.InteropServices; 

	public class Taskbar { 
		[DllImport("user32.dll")] 
		public static extern int FindWindow(string className, string windowText); 
		[DllImport("user32.dll")] public static extern int ShowWindow(int hwnd, int nCmdShow); 
		public const int SW_HIDE = 0; 
		public const int SW_SHOW = 5; 
		public static void Hide() { 
			int hwnd = FindWindow("Shell_TrayWnd", ""); 
			ShowWindow(hwnd, SW_HIDE); 
		} 
		public static void Show() { 
			int hwnd = FindWindow("Shell_TrayWnd", ""); 
			ShowWindow(hwnd, SW_SHOW); 
		} 
	} 
"@ 
    [Taskbar]::Hide() 
    Start-Sleep -Seconds 5 # Adjust the delay as needed 
    [Taskbar]::Show()
}

# Loop to check for notifications 
while ($true) { 
    $notificationCount = Get-Process | Where-Object { $_.MainWindowTitle -like "*Notification*" } 
    if ($notificationCount) { 
        Hide-Taskbar
    } 
    Start-Sleep -Seconds 10 # Adjust the check interval as needed
}