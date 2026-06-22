@echo off
setlocal
cd /d "%~dp0"
set SENIORCONNECT_OPEN_BROWSER=1
start "SeniorConnect Server" SeniorConnectServer.exe
