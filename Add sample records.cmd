@echo off
cd /d "%~dp0"
TechBridgeCRM.exe --sample-data --init-only
pause
