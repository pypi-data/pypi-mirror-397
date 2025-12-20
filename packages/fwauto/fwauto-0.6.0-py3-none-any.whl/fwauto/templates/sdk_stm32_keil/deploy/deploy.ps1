# FWAuto Deploy Script - ST-LINK Utility
# PowerShell 版本

param(
    [string]$ProjectRoot = "../..",
    [string]$HexFile = "",
    [string]$StLinkCli = "C:\Program Files (x86)\STMicroelectronics\STM32 ST-LINK Utility\ST-LINK Utility\ST-LINK_CLI.exe"
)

# 函數：顯示錯誤訊息並退出
function Exit-WithError {
    param([string]$Message)
    Write-Host "ERROR: $Message" -ForegroundColor Red
    exit 1
}

# 開始部署
Write-Host "=== Deploying firmware ===" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"

# 取得專案根目錄絕對路徑
$ProjectRootPath = Resolve-Path $ProjectRoot -ErrorAction SilentlyContinue
if (-not $ProjectRootPath) {
    Exit-WithError "Cannot resolve project root: $ProjectRoot"
}

# 設定 HEX 檔案路徑
if ([string]::IsNullOrEmpty($HexFile)) {
    $HexFile = Join-Path $ProjectRootPath "OBJ\Template.hex"
}

Write-Host "Hex file: $HexFile"
Write-Host ""

# 檢查 HEX 檔案是否存在
if (-not (Test-Path $HexFile)) {
    Exit-WithError "Hex file not found: $HexFile"
}

# 檢查 ST-LINK CLI 是否存在
if (-not (Test-Path $StLinkCli)) {
    Exit-WithError "ST-LINK CLI not found: $StLinkCli"
}

# 執行部署
Write-Host "🔥 Deploying with ST-LINK..." -ForegroundColor Yellow
$DeployProcess = Start-Process -FilePath $StLinkCli `
    -ArgumentList "-c SWD -P `"$HexFile`" -V -Rst" `
    -Wait -PassThru -NoNewWindow

$DeployExitCode = $DeployProcess.ExitCode

Write-Host ""
if ($DeployExitCode -eq 0) {
    Write-Host "✅ Deploy complete!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ Deploy failed with exit code $DeployExitCode" -ForegroundColor Red
    exit 1
}
