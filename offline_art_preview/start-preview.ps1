$ErrorActionPreference = 'Stop'
. (Join-Path (Split-Path $PSScriptRoot -Parent) 'tools\runtime-paths.ps1')
$python = Find-GamePython
$adb = Join-Path (Find-GameAndroidSdk) 'platform-tools\adb.exe'
$port = 8765

$existing = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq 'python.exe' -and $_.CommandLine -like "*http.server $port*offline_art_preview*"
}
if (-not $existing) {
    Start-Process -FilePath $python -ArgumentList @('-m','http.server',"$port",'--bind','127.0.0.1','--directory',('"{0}"' -f $PSScriptRoot)) -WindowStyle Hidden
    Start-Sleep -Milliseconds 700
}
& $adb reverse "tcp:$port" "tcp:$port" | Out-Null
& $adb shell am start -a android.intent.action.VIEW -d "http://127.0.0.1:$port/index.html"
