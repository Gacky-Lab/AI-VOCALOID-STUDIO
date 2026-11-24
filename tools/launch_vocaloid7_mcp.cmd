@echo off
rem Keep protocol stdout clean. Resolve all paths from this script, not the caller's CWD.
set "BRIDGE=%~dp0..\private\vocaloid_bridge"
set "VOCALOID_WORKSPACE=%BRIDGE%"
set "PYTHONPATH=%BRIDGE%"
set "PYTHONUTF8=1"
if not exist "%BRIDGE%\.venv\Scripts\python.exe" (
  >&2 echo VOCALOID7 MCP not installed. Run tools\setup_vocaloid7_mcp.ps1 -Action Install first.
  exit /b 1
)
"%BRIDGE%\.venv\Scripts\python.exe" -m vocaloid_bridge
exit /b %ERRORLEVEL%
