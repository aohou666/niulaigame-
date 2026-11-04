param([string]$OutputDir = 'outputs\reskin-v020\build')
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
. (Join-Path $PSScriptRoot 'runtime-paths.ps1')
$taskSdk=Find-GameAndroidSdk
$taskJdk=Join-Path $env:ProgramFiles 'Android\Android Studio\jbr'
$env:JAVA_HOME=$taskJdk
$env:Path="$(Join-Path $taskJdk 'bin');$env:Path"
$taskBuild=Join-Path $env:TEMP 'codex-reskin-v020-01a1354a'
$taskTools=Join-Path $taskSdk 'build-tools\35.0.0'
$taskAndroid=Join-Path $taskSdk 'platforms\android-35\android.jar'
@('classes','generated','dex') | ForEach-Object {New-Item -ItemType Directory -Path (Join-Path $taskBuild $_) -Force | Out-Null}
Copy-Item -LiteralPath (Join-Path $taskRoot 'android_offline_shell\app\src\main\res') -Destination (Join-Path $taskBuild 'res') -Recurse -Force
New-Item -ItemType Directory -Path (Join-Path $taskBuild 'src') -Force | Out-Null
Get-ChildItem -LiteralPath (Join-Path $taskRoot 'android_offline_shell\app\src\main\java\com\local\offlinereplica') -Filter '*.java' | ForEach-Object {Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $taskBuild 'src') -Force}
$taskManifest=[xml](Get-Content -Raw -LiteralPath (Join-Path $taskRoot 'android_offline_shell\app\src\main\AndroidManifest.xml'))
$taskManifest.manifest.SetAttribute('package','com.local.offlinereplica')
$taskManifest.Save((Join-Path $taskBuild 'AndroidManifest.xml'))
& (Join-Path $taskTools 'aapt2.exe') compile --dir (Join-Path $taskBuild 'res') -o (Join-Path $taskBuild 'resources.zip')
if ($LASTEXITCODE -ne 0) {throw '资源编译失败'}
& (Join-Path $taskTools 'aapt2.exe') link -o (Join-Path $taskBuild 'shell.apk') -I $taskAndroid --manifest (Join-Path $taskBuild 'AndroidManifest.xml') --java (Join-Path $taskBuild 'generated') --version-code 20 --version-name '0.20.0' --min-sdk-version 23 --target-sdk-version 35 --debug-mode (Join-Path $taskBuild 'resources.zip')
if ($LASTEXITCODE -ne 0) {throw '资源链接失败'}
$taskJavaSources=Get-ChildItem -LiteralPath (Join-Path $taskBuild 'src') -Filter '*.java' | Select-Object -ExpandProperty FullName
& (Join-Path $taskJdk 'bin\javac.exe') -encoding UTF-8 -source 17 -target 17 -classpath $taskAndroid -d (Join-Path $taskBuild 'classes') @taskJavaSources
if ($LASTEXITCODE -ne 0) {throw 'Java 编译失败'}
& (Join-Path $taskJdk 'bin\jar.exe') --create --file (Join-Path $taskBuild 'shell.jar') -C (Join-Path $taskBuild 'classes') .
& (Join-Path $taskTools 'd8.bat') --lib $taskAndroid --min-api 23 --output (Join-Path $taskBuild 'dex') (Join-Path $taskBuild 'shell.jar')
if ($LASTEXITCODE -ne 0) {throw 'DEX 编译失败'}
& (Find-GamePython) (Join-Path $PSScriptRoot 'package-reskin-apk.py') --build-dir $taskBuild
if ($LASTEXITCODE -ne 0) {throw 'APK 资源打包失败'}
& (Join-Path $taskTools 'zipalign.exe') -p -f 4 (Join-Path $taskBuild 'unsigned.apk') (Join-Path $taskBuild 'aligned.apk')
if ($LASTEXITCODE -ne 0) {throw 'APK 对齐失败'}
$taskApk=Join-Path $taskBuild 'reskin-preview-v020.apk'
& (Join-Path $taskTools 'apksigner.bat') sign --ks (Join-Path $env:USERPROFILE '.android\debug.keystore') --ks-key-alias androiddebugkey --ks-pass 'pass:android' --key-pass 'pass:android' --out $taskApk (Join-Path $taskBuild 'aligned.apk')
if ($LASTEXITCODE -ne 0) {throw 'APK 签名失败'}
& (Join-Path $taskTools 'apksigner.bat') verify $taskApk
if ($LASTEXITCODE -ne 0) {throw 'APK 签名验证失败'}
Write-Host "APK_BUILD_OK $taskApk"
Copy-Item -LiteralPath $taskApk -Destination (Join-Path $taskRoot 'outputs\reskin-v020\原创角色换皮-v0.20-预览测试版.apk') -Force
