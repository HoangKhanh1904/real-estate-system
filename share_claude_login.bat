@echo off
setlocal EnableExtensions
title Chia se dang nhap Claude Code (token dai han)

rem =============================================================================
rem  Cho may khac dung Claude Code bang tai khoan cua minh, LAU DAI (~1 nam).
rem
rem  Cach cu (chep .credentials.json) KHONG dung duoc lau: refresh token chi
rem  dung 1 lan, may nao gia han truoc thi token o may kia chet ngay.
rem
rem  Cach moi: "claude setup-token" tao 1 OAuth token dai han rieng, doc lap voi
rem  phien dang nhap cua may minh. May dich chi can bien moi truong
rem  CLAUDE_CODE_OAUTH_TOKEN = token do.
rem
rem  Dung 1 file .bat nay cho ca 2 dau:
rem    1) Chay tren MAY MINH, chon [1] -> dang nhap trinh duyet -> dan token
rem       -> ghi ra "claude-token.txt" nam canh file bat.
rem    2) Chep ca 2 file (bat + txt) sang may cu em, chay lai .bat -> cai token.
rem       (Hoac gui token qua kenh kin, ben kia chay .bat chon [2] roi dan vao.)
rem
rem  CANH BAO: token = chia khoa tai khoan Claude cua ban, song ~1 nam.
rem            Gui qua kenh kin, cai xong thi xoa file di.
rem            Muon thu hoi: claude.ai > Settings > Claude Code / Connected apps.
rem =============================================================================

set "PKG=%~dp0claude-token.txt"
set "TOKEN="

echo ======================================================================
echo    CHIA SE DANG NHAP CLAUDE CODE      %COMPUTERNAME% / %USERNAME%
echo ======================================================================
echo.

if not exist "%PKG%" goto :menu_new

echo Tim thay file token canh .bat:
echo    %PKG%
echo.
echo   [1] Cai token trong file vao MAY NAY  ^(lam o may cu em^)   ^<- Enter
echo   [2] Tao token moi tu may nay          ^(ghi de file tren^)
echo.
set "ANS="
set /p "ANS=Chon 1 hoac 2: "
if "%ANS%"=="2" goto :export
goto :import_file

:menu_new
echo   [1] Tao token dai han  ^(lam o MAY MINH - may da dang nhap Claude^)
echo   [2] Dan token vao may nay  ^(lam o may cu em^)
echo.
set "ANS="
set /p "ANS=Chon 1 hoac 2: "
if "%ANS%"=="1" goto :export
if "%ANS%"=="2" goto :paste
echo [X] Chon khong hop le.
goto :fail

rem -----------------------------------------------------------------------------
:export
where claude >nul 2>&1
if errorlevel 1 (
  echo [X] May nay chua cai Claude Code - khong tao token duoc.
  goto :fail
)
echo.
echo [*] Chay "claude setup-token": trinh duyet se mo de xac nhan tai khoan.
echo     Xong, cua so se in ra token dang  sk-ant-oat01-....
echo     Boi den, copy nguyen dong token do.
echo.
call claude setup-token
echo.
set "TOKEN="
set /p "TOKEN=Dan token vua copy vao day roi Enter: "
call :check_token || goto :fail
powershell -NoProfile -ExecutionPolicy Bypass -Command "[System.IO.File]::WriteAllText($env:PKG, $env:TOKEN.Trim(), (New-Object System.Text.UTF8Encoding($false)))"
if errorlevel 1 goto :fail
echo     OK -^> %PKG%
echo.
echo Buoc tiep theo:
echo   1. Chep 2 file nay sang may cu em (cung 1 thu muc):
echo        share_claude_login.bat
echo        claude-token.txt
echo   2. Ben do chay share_claude_login.bat, chon [1].
echo   3. Cai xong thi XOA claude-token.txt o ca 2 may.
echo   Token dung duoc cho nhieu may, khong may nao da may nao.
goto :end

rem -----------------------------------------------------------------------------
:paste
set "TOKEN="
set /p "TOKEN=Dan token (sk-ant-oat01-...) roi Enter: "
call :check_token || goto :fail
goto :install

:import_file
for /f "usebackq delims=" %%T in ("%PKG%") do set "TOKEN=%%T"
call :check_token || goto :fail
goto :install

rem -----------------------------------------------------------------------------
:install
echo.
echo [*] Cai token vao may nay...

rem --- Claude Code da co chua? ---
where claude >nul 2>&1
if errorlevel 1 (
  echo [!] May nay chua cai Claude Code.
  set "ANS="
  set /p "ANS=    Cai bang trinh cai chinh chu ngay bay gio? (Y/n): "
  call :maybe_install
)

rem Ghi bien moi truong User (vinh vien) + bo qua man hinh onboarding.
rem Sao luu va go claudeAiOauth cu (token chep kieu cu, da chet) de khong bi hoi dang nhap.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $t=$env:TOKEN.Trim(); [Environment]::SetEnvironmentVariable('CLAUDE_CODE_OAUTH_TOKEN', $t, 'User'); Write-Host '    OK - da ghi bien CLAUDE_CODE_OAUTH_TOKEN (User)'; $utf8=New-Object System.Text.UTF8Encoding($false); $dir=Join-Path $env:USERPROFILE '.claude'; $cred=Join-Path $dir '.credentials.json'; if(Test-Path $cred){$c=Get-Content $cred -Raw | ConvertFrom-Json; if($c.claudeAiOauth){$bak=$cred + '.bak-' + (Get-Date -Format 'yyyyMMdd-HHmmss'); Copy-Item $cred $bak -Force; $c.PSObject.Properties.Remove('claudeAiOauth'); [System.IO.File]::WriteAllText($cred, ($c | ConvertTo-Json -Depth 20), $utf8); Write-Host ('    da go token kieu cu, sao luu -> ' + $bak)}}; $cj=Join-Path $env:USERPROFILE '.claude.json'; $j=if(Test-Path $cj){Get-Content $cj -Raw | ConvertFrom-Json}else{[pscustomobject]@{}}; $j | Add-Member -NotePropertyName hasCompletedOnboarding -NotePropertyValue $true -Force; [System.IO.File]::WriteAllText($cj, ($j | ConvertTo-Json -Depth 100), $utf8); foreach($v in 'ANTHROPIC_API_KEY','ANTHROPIC_AUTH_TOKEN'){ if([Environment]::GetEnvironmentVariable($v,'User') -or [Environment]::GetEnvironmentVariable($v,'Machine')){Write-Host ('[!] May nay co bien ' + $v + ' - no duoc uu tien hon token, hay xoa di.') -ForegroundColor Yellow}}"
if errorlevel 1 goto :fail

echo.
echo XONG. Dong het cua so Terminal/CMD/VS Code dang mo, mo cua so MOI roi go:  claude
echo       (bien moi truong chi co hieu luc o cua so mo SAU khi cai)
if exist "%PKG%" (
  echo.
  echo Nho xoa file token sau khi cai:
  echo       del "%PKG%"
)
goto :end

rem -----------------------------------------------------------------------------
:check_token
if not defined TOKEN (
  echo [X] Chua co token.
  exit /b 1
)
echo %TOKEN%| findstr /b "sk-ant-oat" >nul
if errorlevel 1 (
  echo [X] Token khong dung dang sk-ant-oat01-... - copy lai nguyen dong token.
  exit /b 1
)
exit /b 0

rem -----------------------------------------------------------------------------
:maybe_install
if /i "%ANS%"=="n" (
  echo     Bo qua. Cai tay:  irm https://claude.ai/install.ps1 ^| iex
  exit /b 0
)
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://claude.ai/install.ps1 | iex"
if errorlevel 1 (
  echo [!] Cai that bai - van se ghi token, cai Claude Code sau cung duoc.
)
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
exit /b 0

rem -----------------------------------------------------------------------------
:fail
echo.
echo *** Dung lai vi loi o tren. ***
pause
endlocal
exit /b 1

:end
echo.
pause
endlocal
exit /b 0
