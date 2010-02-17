@echo off
call %~DP0\setenv.bat

call python.exe docgen.py
pause
