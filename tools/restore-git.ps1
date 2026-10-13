$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $root
if (Test-Path -LiteralPath '.git') { Write-Host 'Git 仓库已存在。'; return }
git init
if ($LASTEXITCODE) { throw '请先安装 Git。' }
git fetch (Join-Path $root 'game-history.bundle') main
if ($LASTEXITCODE) { throw '无法读取 Git 历史包。' }
git reset --mixed FETCH_HEAD
if ($LASTEXITCODE) { throw '无法恢复 Git 分支。' }
git branch -M main
git remote add origin https://github.com/houguangdong104-beep/-.git
Write-Host '已恢复 main 分支和 GitHub 地址。首次推送时请登录自己的 GitHub 账号。'
