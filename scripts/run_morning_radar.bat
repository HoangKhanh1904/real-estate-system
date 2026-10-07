@echo off
chcp 65001 >nul
cd /d "%~dp0\.."
title BDS - Radar Tin Sang Tu Dong
echo ========================================================
echo   DANG QUET TIN NONG BDS & QUY HOACH MOI SANG...
echo ========================================================
python -m pipeline.run_pipeline --radar
if errorlevel 1 (
    echo [X] Co loi xay ra khi chay Radar.
) else (
    echo [OK] Hoan tat quet tin sang!
)
pause
