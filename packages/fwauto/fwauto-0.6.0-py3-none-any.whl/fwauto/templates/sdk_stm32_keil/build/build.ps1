# FWAuto Build Script - Keil uVision
# PowerShell 版本

param(
    [string]$ProjectRoot = "../..",
    [string]$KeilUV4 = "C:\Keil_v5\UV4\UV4.exe"
)

# 函數：顯示錯誤訊息並退出
function Exit-WithError {
    param([string]$Message)
    Write-Host "ERROR: $Message" -ForegroundColor Red
    exit 1
}

# 開始建置
Write-Host "=== Building firmware ===" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"
Write-Host ""

# 取得專案根目錄絕對路徑
$ProjectRootPath = Resolve-Path $ProjectRoot -ErrorAction SilentlyContinue
if (-not $ProjectRootPath) {
    Exit-WithError "Cannot resolve project root: $ProjectRoot"
}

# 設定路徑
$OutputDir = Join-Path $ProjectRootPath "OBJ"
$LogsDir = Join-Path $ProjectRootPath ".fwauto\logs"
$UserDir = Join-Path $ProjectRootPath "USER"

# 建立 logs 目錄
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

# 尋找專案檔案
$ProjectFile = Get-ChildItem -Path $UserDir -Filter "*.uvprojx" -File | Select-Object -First 1
if (-not $ProjectFile) {
    Exit-WithError "Cannot find .uvprojx file in $UserDir"
}

$ProjectFilePath = $ProjectFile.FullName
Write-Host "Project file: $ProjectFilePath"

# 設定 log 檔案路徑
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogsDir "build_$Timestamp.log"
$KeilLogFile = Join-Path $LogsDir "build.log"

Write-Host "Log file: $LogFile"
Write-Host ""

# 執行 Keil 建置
Write-Host "🔨 Compiling with Keil..." -ForegroundColor Yellow
Write-Host "---> Log File: $LogFile"
Write-Host "🔨 Command: $KeilUV4 -r `"$ProjectFilePath`" -j0 -o `"$KeilLogFile`""

$BuildProcess = Start-Process -FilePath $KeilUV4 `
    -ArgumentList "-r `"$ProjectFilePath`" -j0 -o `"$KeilLogFile`"" `
    -Wait -PassThru -NoNewWindow

$BuildExitCode = $BuildProcess.ExitCode
Write-Host "🔨 Build exit code: $BuildExitCode" -ForegroundColor $(if ($BuildExitCode -eq 0) { "Green" } else { "Red" })

# 等待 log 檔案生成
Start-Sleep -Milliseconds 500

# 顯示建置 log
Write-Host ""
Write-Host "=== Build Log ===" -ForegroundColor Cyan

if (Test-Path $KeilLogFile) {
    Get-Content $KeilLogFile | Write-Host

    # 複製 log 到時間戳記檔案
    Copy-Item $KeilLogFile -Destination $LogFile -Force
} else {
    Write-Host "Warning: Log file not found at $KeilLogFile" -ForegroundColor Yellow
}

Write-Host "=================" -ForegroundColor Cyan
Write-Host ""

# 檢查建置結果
if ($BuildExitCode -eq 0) {
    Write-Host "✅ Build complete!" -ForegroundColor Green
    Write-Host "Log saved to: $LogFile"
    exit 0
} else {
    Write-Host "❌ Build failed with exit code $BuildExitCode" -ForegroundColor Red
    Write-Host "Log saved to: $LogFile"
    exit 1
}
