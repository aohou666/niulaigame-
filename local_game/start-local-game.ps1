param(
    [ValidateSet('launcher', 'main', 'map', 'heroes', 'fight', 'demo', 'tower', 'train', 'admin')]
    [string]$Mode = 'main',
    [string]$Serial = '',
    [int]$ServerPort = 8787,
    [int]$DevicePort = 8788,
    [switch]$BrowserOnly,
    [switch]$Desktop
)
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path $PSScriptRoot -Parent
. (Join-Path $workspaceRoot 'tools\runtime-paths.ps1')
$python = Find-GamePython
$serverScript = Join-Path $PSScriptRoot 'offline_server.py'
$workspaceRoot = Split-Path $PSScriptRoot -Parent
$dataRoot = Join-Path $workspaceRoot 'pc_server_data'
$savePath = Join-Path $dataRoot 'offline-replica-save.json'

$existing = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq 'python.exe' -and $_.CommandLine -like "*offline_server.py*--port $ServerPort*"
}
if (-not $existing) {
    $logDir = $dataRoot
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    Start-Process -FilePath $python -ArgumentList @(
        ('"{0}"' -f $serverScript), '--host', '127.0.0.1', '--port', "$ServerPort", '--save', ('"{0}"' -f $savePath)
    ) -RedirectStandardOutput (Join-Path $logDir 'server.log') -RedirectStandardError (Join-Path $logDir 'server-error.log') -WindowStyle Hidden
    Start-Sleep -Milliseconds 800
}

$healthUrl = "http://127.0.0.1:$ServerPort/api/save"
Invoke-WebRequest -UseBasicParsing -Uri $healthUrl -TimeoutSec 5 | Out-Null

if ($Mode -eq 'admin') {
    $adminUrl = "http://127.0.0.1:$ServerPort/admin.html"
    Start-Process $adminUrl
    Write-Host "可视化后台：$adminUrl"
    Write-Host "电脑端存档：$savePath"
    return
}

if ($Desktop) {
    $path = if ($Mode -eq 'launcher') { 'offline-launcher.html' } else { "index_bh_lite3zbtest_andr.html?mode=$Mode" }
    Start-Process "http://127.0.0.1:$ServerPort/$path"
    Write-Host "电脑端存档：$savePath"
    return
}

$adb = Join-Path (Find-GameAndroidSdk) 'platform-tools\adb.exe'

$deviceLines = @(& $adb devices | Select-Object -Skip 1 | Where-Object { $_ -match "\tdevice$" })
if (-not $Serial) {
    $emulator = $deviceLines | Where-Object { $_ -match '^emulator-' } | Select-Object -First 1
    $selected = if ($emulator) { $emulator } else { $deviceLines | Select-Object -First 1 }
    if ($selected) { $Serial = ($selected -split "\s+")[0] }
}
if (-not $Serial) { throw '未检测到 Android 虚拟机或设备。请先启动虚拟机。' }

$adbArgs = @('-s', $Serial)
& $adb @adbArgs reverse "tcp:$DevicePort" "tcp:$ServerPort" | Out-Null
$path = if ($Mode -eq 'launcher') { 'offline-launcher.html' } else { "index_bh_lite3zbtest_andr.html?mode=$Mode" }
$url = "http://127.0.0.1:$DevicePort/$path"

if ($BrowserOnly) {
    & $adb @adbArgs shell am start -a android.intent.action.VIEW -d $url | Out-Null
} else {
    & $adb @adbArgs shell am force-stop com.local.offlinereplica
    & $adb @adbArgs shell am start -n com.local.offlinereplica/.MainActivity --es startUrl $url | Out-Null
}

Write-Host "电脑端网站：http://127.0.0.1:$ServerPort/offline-launcher.html"
Write-Host "电脑端存档：$savePath"
Write-Host "测试设备：$Serial"
Write-Host "设备入口：$url"
