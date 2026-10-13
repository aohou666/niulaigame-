function Find-GamePython {
    $candidates = @(
        (Join-Path $PSScriptRoot '..\.tools\python\python.exe'),
        (Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) { return (Resolve-Path -LiteralPath $candidate).Path }
    }
    $command = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($command -and $command.Source -notlike '*WindowsApps*') { return $command.Source }
    throw '未找到 Python。请安装 Python 3.10 或更高版本并添加到 PATH，或解压完整迁移包。'
}

function Find-GameAndroidSdk {
    foreach ($candidate in @($env:ANDROID_HOME, $env:ANDROID_SDK_ROOT, (Join-Path $env:LOCALAPPDATA 'Android\Sdk'))) {
        if ($candidate -and (Test-Path -LiteralPath (Join-Path $candidate 'platform-tools\adb.exe'))) { return $candidate }
    }
    throw '未找到 Android SDK。请通过 Android Studio 安装 SDK，并设置 ANDROID_HOME。'
}
