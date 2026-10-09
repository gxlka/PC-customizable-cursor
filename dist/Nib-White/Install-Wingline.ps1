$ErrorActionPreference = "Stop"
function Get-WinglineAnimationSuffix([int]$RequiredSize) {
    if ($RequiredSize -gt 0 -and $RequiredSize -le 64) { return ".ani" }
    return "-large.ani"
}
Add-Type -AssemblyName System.Windows.Forms
if (-not ("WinglineCursor.NativeMethods" -as [type])) {
    Add-Type -Namespace WinglineCursor -Name NativeMethods -MemberDefinition '
        [System.Runtime.InteropServices.DllImport("user32.dll", SetLastError=true)]
        public static extern bool SystemParametersInfo(uint action, uint param, System.IntPtr value, uint flags);
        [System.Runtime.InteropServices.DllImport("user32.dll")]
        public static extern System.IntPtr SetThreadDpiAwarenessContext(System.IntPtr context);
        [System.Runtime.InteropServices.DllImport("user32.dll")]
        public static extern uint GetDpiForSystem();
        [System.Runtime.InteropServices.DllImport("user32.dll")]
        public static extern int GetSystemMetricsForDpi(int metric, uint dpi);
        [System.Runtime.InteropServices.DllImport("user32.dll")]
        public static extern System.IntPtr GetForegroundWindow();
        [System.Runtime.InteropServices.DllImport("user32.dll")]
        public static extern uint GetDpiForWindow(System.IntPtr window);
    '
}

# Select a smaller source animation for normal cursor sizes, once at install.
# Unknown/old Windows APIs conservatively select the high-resolution fallback.
$requiredSize = 256
$previousDpiContext = [IntPtr]::Zero
try {
    $previousDpiContext = [WinglineCursor.NativeMethods]::SetThreadDpiAwarenessContext([IntPtr](-4))
    $dpi = [Math]::Max([WinglineCursor.NativeMethods]::GetDpiForSystem(), [WinglineCursor.NativeMethods]::GetDpiForWindow([WinglineCursor.NativeMethods]::GetForegroundWindow()))
    $baseSize = [int](Get-ItemPropertyValue -Path 'HKCU:\Control Panel\Cursors' -Name CursorBaseSize -ErrorAction SilentlyContinue)
    if ($baseSize -le 0) { $baseSize = 32 }
    $requiredSize = [Math]::Max([WinglineCursor.NativeMethods]::GetSystemMetricsForDpi(13, $dpi), [Math]::Ceiling($baseSize * $dpi / 96))
    if ($requiredSize -le 0) { $requiredSize = 256 }
} catch { $requiredSize = 256 }
finally {
    if ($previousDpiContext -ne [IntPtr]::Zero) { [void][WinglineCursor.NativeMethods]::SetThreadDpiAwarenessContext($previousDpiContext) }
}


$infFiles = @(Get-ChildItem -LiteralPath $PSScriptRoot -Filter "*.inf" -File)
if ($infFiles.Count -ne 1) { throw "Expected exactly one theme INF beside this installer; found $($infFiles.Count)." }
$inf = $infFiles[0]
$themeKey = [IO.Path]::GetFileNameWithoutExtension($inf.Name)
$schemeName = $themeKey.Replace("-", " ")
$target = Join-Path $env:LOCALAPPDATA ("WinglineCursorPack\" + $themeKey)
New-Item -ItemType Directory -Path $target -Force | Out-Null

$roles = [ordered]@{
    Arrow="arrow"; Help="help"; AppStarting="appstarting"; Wait="wait"
    Crosshair="crosshair"; IBeam="ibeam"; NWPen="nwpen"; No="no"
    SizeNS="sizens"; SizeWE="sizewe"; SizeNWSE="sizenwse"; SizeNESW="sizenesw"
    SizeAll="sizeall"; UpArrow="uparrow"; Hand="hand"; Pin="pin"; Person="person"
}
$schemePaths = @()
$cursorKey = [Microsoft.Win32.Registry]::CurrentUser.CreateSubKey("Control Panel\Cursors")
try {
    foreach ($entry in $roles.GetEnumerator()) {
        $suffix = if ($themeKey -like "Nib-*" -and $entry.Value -notin @("wait", "appstarting")) { ".cur" } else { Get-WinglineAnimationSuffix $requiredSize }
        $matches = Get-Item -LiteralPath (Join-Path $PSScriptRoot ($themeKey + "-" + $entry.Value + $suffix)) -ErrorAction SilentlyContinue
        if (-not $matches) { throw ("Missing cursor for role " + $entry.Key) }
        $destination = Join-Path $target $matches.Name
        Copy-Item -LiteralPath $matches.FullName -Destination $destination -Force
        $cursorKey.SetValue($entry.Key, $destination, [Microsoft.Win32.RegistryValueKind]::String)
        $schemePaths += $destination
    }
    $cursorKey.SetValue("", $schemeName, [Microsoft.Win32.RegistryValueKind]::String)
    $cursorKey.SetValue("Scheme Source", 1, [Microsoft.Win32.RegistryValueKind]::DWord)
}
finally { $cursorKey.Dispose() }

$schemesKey = [Microsoft.Win32.Registry]::CurrentUser.CreateSubKey("Control Panel\Cursors\Schemes")
try {
    $schemesKey.SetValue($schemeName, ($schemePaths -join ","), [Microsoft.Win32.RegistryValueKind]::String)
}
finally { $schemesKey.Dispose() }


if (-not [WinglineCursor.NativeMethods]::SystemParametersInfo(0x0057, 0, [IntPtr]::Zero, 0)) {
    throw "Windows saved the theme but could not reload the cursor settings."
}
[System.Windows.Forms.MessageBox]::Show("$schemeName was reapplied and is active. The cursor set is now active. Sites and games that supply their own cursors may override this scheme.", "curs0r pack") | Out-Null
