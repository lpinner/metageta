@echo off
setlocal ENABLEDELAYEDEXPANSION
call "%~DP0setenv.bat"
call python.exe "%~DP0runtransform.py" %*
pause

endlocal
