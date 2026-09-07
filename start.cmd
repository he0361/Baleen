@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%~dp0.."
set "PYTHONUTF8=1"
set "TEXTUAL_COLOR_SYSTEM=truecolor"
set "NO_COLOR="
"%~dp0.venv\Scripts\python.exe" -P -m Baleen %*
endlocal
