param(
    [ValidateSet('launcher', 'map', 'heroes', 'fight', 'demo')]
    [string]$Mode = 'launcher'
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'tools\runtime-paths.ps1')
$sdk = Find-GameAndroidSdk
$adb = Join-Path $sdk 'platform-tools\adb.exe'
$emulator = Join-Path $sdk 'emulator\emulator.exe'
$avdName = 'OfflineReplica_API35'
$apk = Join-Path $PSScriptRoot 'android_offline_shell\app\build\outputs\apk\debug\app-debug.apk'
$launcher = Join-Path $PSScriptRoot 'local_game\start-local-game.ps1'

if (-not (Test-Path $emulator)) { throw '未安装 Android Emulator。' }
if (-not (Test-Path $apk)) { throw '未找到测试 APK，请先构建。' }

$serial = (& $adb devices | Where-Object { $_ -match '^emulator-\d+\s+device$' } | Select-Object -First 1) -replace '\s+device$', ''
if (-not $serial) {
    Start-Process -FilePath $emulator -ArgumentList @('-avd', $avdName, '-gpu', 'auto', '-memory', '6144') -WindowStyle Hidden
    $deadline = (Get-Date).AddMinutes(4)
    do {
        Start-Sleep -Seconds 3
        $serial = (& $adb devices | Where-Object { $_ -match '^emulator-\d+\s+device$' } | Select-Object -First 1) -replace '\s+device$', ''
    } until ($serial -or (Get-Date) -gt $deadline)
}
if (-not $serial) { throw '虚拟机未在 4 分钟内连接 ADB。' }

$deadline = (Get-Date).AddMinutes(4)
do {
    Start-Sleep -Seconds 2
    $boot = (& $adb -s $serial shell getprop sys.boot_completed 2>$null).Trim()
} until ($boot -eq '1' -or (Get-Date) -gt $deadline)
if ($boot -ne '1') { throw '虚拟机未完成启动。' }

$installed = & $adb -s $serial shell dumpsys package com.local.offlinereplica 2>$null
$installedText = $installed -join "`n"
$buildConfig = Get-Content (Join-Path $PSScriptRoot 'android_offline_shell\app\build.gradle') -Raw
$versionCode = [regex]::Match($buildConfig, 'versionCode\s+(\d+)').Groups[1].Value
if ($installedText -notmatch "versionCode=$versionCode(?:\s|$)") {
    & $adb -s $serial install -r $apk
    if ($LASTEXITCODE -ne 0) { throw '虚拟机安装 APK 失败。' }
}

& $launcher -Mode $Mode -Serial $serial
