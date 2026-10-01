# 恢复 APK 历史归档

下载四个 `part-001` 至 `part-004` 分卷并放在同一目录，然后在 PowerShell 中运行：

```powershell
$parts = Get-ChildItem 'apk-history-v0.1-v0.17.tar.zst.part-*' | Sort-Object Name
$output = [IO.File]::Create('apk-history-v0.1-v0.17.tar.zst')
try {
  foreach ($part in $parts) {
    $input = [IO.File]::OpenRead($part.FullName)
    try { $input.CopyTo($output) } finally { $input.Dispose() }
  }
} finally { $output.Dispose() }

zstd -d --long=30 apk-history-v0.1-v0.17.tar.zst -o apk-history-v0.1-v0.17.tar
tar -xf apk-history-v0.1-v0.17.tar
```

完整归档 SHA-256：

```text
13bb74460ecf51735d40677fa0dc228adeef855749ad804dbbedab89d491c158
```

解压后应得到 15 个 APK。逐文件校验值见 `apk-sha256.csv`。
