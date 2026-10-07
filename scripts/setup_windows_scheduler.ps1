# ==============================================================================
# Script dang ky Windows Task Scheduler tu dong chay Radar luc 06:30 sang moi ngay
# ==============================================================================

$projectDir = (Get-Item $PSScriptRoot).Parent.FullName
$actionScript = Join-Path $PSScriptRoot "run_morning_radar.bat"

# Kiem tra xem file bat co ton tai khong
if (-not (Test-Path $actionScript)) {
    Write-Host "[X] Khong tim thay file $actionScript" -ForegroundColor Red
    exit 1
}

# Hanh dong can thuc hien
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$actionScript`"" -WorkingDirectory "$projectDir"

# Thoi gian kich hoat: 06:30 sang moi ngay
$trigger = New-ScheduledTaskTrigger -Daily -At "06:30AM"

# Thiet lap tuy chon (chay bat ke nguon pin hay sac)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Dang ky Task vao Windows
try {
    # Neu da ton tai thi xoa de tao lai
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Tu dong quet tin nong BDS luc 6h30 sang cho kenh"
    Write-Host "[OK] Da dang ky thanh cong Windows Task Scheduler!" -ForegroundColor Green
    Write-Host "     Task Name: $taskName" -ForegroundColor Cyan
    Write-Host "     Lich chay: 06:30 AM moi ngay" -ForegroundColor Cyan
} catch {
    Write-Host "[X] Loi khi dang ky Task: $_" -ForegroundColor Red
    Write-Host "    (Luu y: Can chay PowerShell voi quyen Administrator neu gap loi phan quyen)" -ForegroundColor Yellow
}
