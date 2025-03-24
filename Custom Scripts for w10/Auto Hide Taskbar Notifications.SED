[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=0
HideExtractAnimation=0
UseLongFileName=0
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=I
InstallPrompt=%InstallPrompt%
DisplayLicense=%DisplayLicense%
FinishMessage=%FinishMessage%
TargetName=%TargetName%
FriendlyName=%FriendlyName%
AppLaunched=%AppLaunched%
PostInstallCmd=%PostInstallCmd%
AdminQuietInstCmd=%AdminQuietInstCmd%
UserQuietInstCmd=%UserQuietInstCmd%
SourceFiles=SourceFiles
[Strings]
InstallPrompt=Do you want to continue?
DisplayLicense=
FinishMessage=Complete!
TargetName=E:\Files\Custom Scripts for w10\Auto Hide Taskbar Notifications.EXE
FriendlyName=Auto Hide Taskbar Notification
AppLaunched=powershell.exe
PostInstallCmd=-File AutoHideTaskbar.ps1
AdminQuietInstCmd=
UserQuietInstCmd=
FILE0="AutoHideTaskbar.ps1"
[SourceFiles]
SourceFiles0=E:\Files\Custom Scripts for w10\scripts\
[SourceFiles0]
%FILE0%=
