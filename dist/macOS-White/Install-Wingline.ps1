$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms

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
        $matches = Get-ChildItem -LiteralPath $PSScriptRoot -File |
            Where-Object { $_.Name -like ($themeKey + "-" + $entry.Value + ".*") } |
            Select-Object -First 1
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

if (-not ("WinglineCursor.NativeMethods" -as [type])) {
    Add-Type -Namespace WinglineCursor -Name NativeMethods -MemberDefinition '
        [System.Runtime.InteropServices.DllImport("user32.dll", SetLastError=true)]
        public static extern bool SystemParametersInfo(uint action, uint param, System.IntPtr value, uint flags);
    '
}
if (-not [WinglineCursor.NativeMethods]::SystemParametersInfo(0x0057, 0, [IntPtr]::Zero, 0)) {
    throw "Windows saved the theme but could not reload the cursor settings."
}
[System.Windows.Forms.MessageBox]::Show("$schemeName was reapplied and is active.", "Wingline Cursor Pack") | Out-Null
