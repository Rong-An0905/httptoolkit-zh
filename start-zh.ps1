# 启动汉化版 HTTP Toolkit：先确保本地 UI 服务在跑，再带上 APP_URL 启动桌面端
$Root   = $PSScriptRoot
$Port   = 8899
$Exe    = 'D:\HTTP Toolkit\HTTP Toolkit.exe'
$Python = 'D:\Program Files\python\python.exe'

if (-not (Test-Path $Exe)) {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show("未找到 HTTP Toolkit：$Exe`n请先在设置里修改本脚本中的安装路径。", '启动失败')
    exit 1
}

$running = Get-Process | Where-Object { $_.ProcessName -like '*HTTP Toolkit*' -and $_.MainWindowTitle }
if ($running) {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show('检测到 HTTP Toolkit 已在运行。' + "`n请先完全退出它，再用本启动器启动汉化版。", '已有一个实例在运行')
    exit 1
}

if (-not (Test-NetConnection -ComputerName 127.0.0.1 -Port $Port -InformationLevel Quiet)) {
    Start-Process -FilePath $Python -ArgumentList "`"$Root\serve.py`"", "$Port" -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

$env:APP_URL = "http://127.0.0.1:$Port"
Start-Process -FilePath $Exe
