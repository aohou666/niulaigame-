param(
    [switch]$BuildOnly,
    [switch]$Offline
)

$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$workspaceRoot = Split-Path $projectRoot -Parent
. (Join-Path $workspaceRoot 'tools\runtime-paths.ps1')
$jdkHome = $env:JAVA_HOME
if (-not $jdkHome) {
    $jdkHome = Join-Path $env:ProgramFiles 'Android\Android Studio\jbr'
}
$gradle = Join-Path $workspaceRoot '.tools\gradle-8.9\bin\gradle.bat'
$sdk = Find-GameAndroidSdk
$apk = Join-Path $projectRoot 'app\build\outputs\apk\debug\app-debug.apk'

if (-not (Test-Path -LiteralPath (Join-Path $jdkHome 'bin\java.exe'))) { throw '请安装 Android Studio，或将 JAVA_HOME 设置为 JDK 17 或更高版本的目录。' }
if (-not (Test-Path -LiteralPath $gradle)) {
    if ($Offline) { throw '离线模式未找到 Gradle 8.9，请先联网构建一次。' }
    $toolDir = Join-Path $workspaceRoot '.tools'
    New-Item -ItemType Directory -Path $toolDir -Force | Out-Null
    $archive = Join-Path $toolDir 'gradle-8.9-bin.zip'
    $url = 'https://services.gradle.org/distributions/gradle-8.9-bin.zip'
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $archive
    $expected = (Invoke-WebRequest -UseBasicParsing -Uri "$url.sha256").Content.Trim()
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected.ToLowerInvariant()) { throw 'Gradle 下载校验失败。' }
    Expand-Archive -LiteralPath $archive -DestinationPath $toolDir -Force
}
$env:ANDROID_HOME = $sdk
$sdkProperty = $sdk.Replace('\', '/').Replace(':', '\:')
Set-Content -LiteralPath (Join-Path $projectRoot 'local.properties') -Value "sdk.dir=$sdkProperty" -Encoding ASCII

$env:JAVA_HOME = $jdkHome
$env:Path = "$(Join-Path $jdkHome 'bin');$env:Path"
Push-Location $projectRoot
try {
    $gradleArgs = @(':app:assembleDebug')
    if ($Offline) { $gradleArgs += '--offline' }
    & $gradle @gradleArgs
    if ($LASTEXITCODE -ne 0) { throw "Gradle 构建失败，退出码 $LASTEXITCODE" }
} finally {
    Pop-Location
}

Write-Host "APK 已生成：$apk"
if ($BuildOnly) { exit 0 }

$adb = Join-Path $sdk 'platform-tools\adb.exe'

$devices = & $adb devices
$deviceLines = @($devices | Select-Object -Skip 1 | Where-Object { $_ -match "\tdevice$" })
if ($deviceLines.Count -eq 0) {
    throw "未检测到已授权的 Android 设备。请连接设备并开启 USB 调试后重新运行本脚本。"
}

& $adb reverse --remove "tcp:8787" 2>$null | Out-Null
& $adb install -r $apk
if ($LASTEXITCODE -ne 0) { throw 'APK 安装失败。' }
& $adb shell am force-stop com.local.offlinereplica
& $adb shell monkey -p com.local.offlinereplica -c android.intent.category.LAUNCHER 1
if ($LASTEXITCODE -ne 0) { throw '应用启动失败。' }

Write-Host '离线复刻测试已在设备上启动。'
