@echo off
setlocal
cd /d "%~dp0"
set SENIORCONNECT_OPEN_BROWSER=1
echo Starting SeniorConnect. Keep this window open while using the software.
echo If startup fails, check seniorconnect-error.log in this folder.
SeniorConnectServer.exe
echo.
echo SeniorConnect stopped. Press any key to close this window.
pause >nul
