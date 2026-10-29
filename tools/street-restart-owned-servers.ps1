param([string]$Version = '0.42.0')
$taskTag = 'v' + $Version.Split('.')[1]
$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath '.').Path
$taskPython = Join-Path $taskRoot '.tools/python/python.exe'
$taskServer = Join-Path $taskRoot 'local_game/offline_server.py'
$taskLogDir = Join-Path $taskRoot 'outputs/street-reskin/servers'
New-Item -ItemType Directory -Path $taskLogDir -Force | Out-Null
$taskSaves = @{
 8787='pc_server_data/offline-replica-save.json';8791='outputs/street-reskin/effect-test-save.json';
 8792='outputs/street-reskin/stress/8792-save.json';8793='outputs/street-reskin/stress/8793-save.json';
 8794='outputs/street-reskin/stress/8794-save.json';8795='outputs/street-reskin/stress/8795-save.json'
}
$taskRows = @()
foreach ($taskPort in ($taskSaves.Keys | Sort-Object)) {
 $taskSave = Join-Path $taskRoot $taskSaves[$taskPort]
 $taskHash = (Get-FileHash -LiteralPath $taskSave -Algorithm SHA256).Hash
 $taskListener = Get-NetTCPConnection -State Listen -LocalPort $taskPort
 $taskProcess = Get-CimInstance Win32_Process -Filter ('ProcessId=' + $taskListener.OwningProcess)
 if (-not $taskProcess.CommandLine.Contains($taskRoot) -or -not $taskProcess.CommandLine.Contains('offline_server.py')) { throw "Port $taskPort is not this workspace server" }
 $taskRows += [pscustomobject]@{port=$taskPort;oldPid=$taskListener.OwningProcess;save=$taskSave;shaBefore=$taskHash}
}
foreach ($taskRow in $taskRows) { Stop-Process -Id $taskRow.oldPid }
foreach ($taskRow in $taskRows) {
 $taskArguments = @(('"'+$taskServer+'"'),'--port',[string]$taskRow.port,'--save',('"'+$taskRow.save+'"'))
 $taskNew = Start-Process -FilePath $taskPython -ArgumentList $taskArguments -WorkingDirectory $taskRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $taskLogDir ($taskTag+'-'+$taskRow.port+'.log')) -RedirectStandardError (Join-Path $taskLogDir ($taskTag+'-'+$taskRow.port+'-error.log'))
 $taskRow | Add-Member -NotePropertyName newPid -NotePropertyValue $taskNew.Id
}
foreach ($taskRow in $taskRows) {
 $taskReady = $false
 for ($taskAttempt=0;$taskAttempt -lt 30;$taskAttempt++) {
  try { $taskResponse = Invoke-WebRequest -UseBasicParsing -Uri ('http://127.0.0.1:'+$taskRow.port+'/offline-launcher.html') -TimeoutSec 3; if ($taskResponse.StatusCode -eq 200) { $taskReady=$true;break } } catch { Start-Sleep -Milliseconds 100 }
 }
 if (-not $taskReady) { throw "Server $($taskRow.port) did not start" }
 $taskAfter = (Get-FileHash -LiteralPath $taskRow.save -Algorithm SHA256).Hash
 if ($taskAfter -ne $taskRow.shaBefore) { throw "Save changed on restart $($taskRow.port)" }
 $taskRow | Add-Member -NotePropertyName savePreserved -NotePropertyValue $true
}
$taskRows | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path ('art-migration/versions/'+$Version) 'server-restart.json')
$taskRows | Select-Object port,newPid,savePreserved | ConvertTo-Json
