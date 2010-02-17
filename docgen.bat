@echo off
call "%~DP0setenv.bat"

call python.exe "%~DP0docgen.py"
pause
