@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."

if exist "%REPO_ROOT%\.venv\Scripts\python.exe" (
  "%REPO_ROOT%\.venv\Scripts\python.exe" "%SCRIPT_DIR%codex-tts-wrapper.py" %*
) else (
  py -3 "%SCRIPT_DIR%codex-tts-wrapper.py" %*
)

exit /b %ERRORLEVEL%
