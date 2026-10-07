$ErrorActionPreference = "Stop"
$tokens = $null
$errors = $null
$source = Join-Path $PSScriptRoot "installer/Install-Wingline.ps1"
$ast = [System.Management.Automation.Language.Parser]::ParseFile($source, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw ($errors | Out-String) }
$selector = $ast.Find({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq "Get-WinglineAnimationSuffix" }, $true)
if (-not $selector) { throw "Animation size selector is missing." }
Invoke-Expression $selector.Extent.Text
foreach ($size in @(32, 48, 64)) {
    if ((Get-WinglineAnimationSuffix $size) -ne ".ani") { throw "Normal cursor size $size selects an oversized animation." }
}
foreach ($size in @(0, 96, 128, 192, 256)) {
    if ((Get-WinglineAnimationSuffix $size) -ne "-large.ani") { throw "Large/unknown cursor size $size loses its high-resolution fallback." }
}
$forbidden = @("Start-Job", "New-Service", "Register-ScheduledTask", "Register-ObjectEvent", "Start-ThreadJob")
foreach ($command in $ast.FindAll({ param($node) $node -is [System.Management.Automation.Language.CommandAst] }, $true)) {
    if ($command.GetCommandName() -in $forbidden) { throw "Installer starts background work: $($command.GetCommandName())" }
}
Write-Output "Installer syntax, size selection and absence of resident background work verified."
