@echo off
setlocal ENABLEDELAYEDEXPANSION
call "%~DP0setenv.bat"
call python.exe "%~DP0runcrawler.py" %*
pause
endlocal