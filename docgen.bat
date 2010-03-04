@echo off
setlocal
call "%~DP0setenv.bat"

call python.exe "%~DP0docgen.py"
endlocal
pause
