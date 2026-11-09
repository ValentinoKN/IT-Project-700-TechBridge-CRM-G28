@echo off
cd /d "%~dp0"
set /p "backupfile=Paste the full backup file path here (without quotes): "
TechBridgeCRM.exe --restore "%backupfile%"
pause
