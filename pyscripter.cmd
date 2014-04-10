@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
call "%~DP0\setenv.bat"
set PYTHONDLL=%PYTHONHOME%
set PYTHONHOME=
set PYTHONPATH=%PYTHONPATH%;C:\Software\PyScripter\Lib
REM start "PyScripter MetaGETA" /B "C:\Software\PyScripter\PyScripter.exe" --PYTHON27  --PYTHONDLLPATH "%PYTHONDLL%" --newinstance %1 %2 %3 %4 %5
CALL "C:\Software\PyScripter\PyScripter.exe" --PYTHON27  --PYTHONDLLPATH "%PYTHONDLL%" --newinstance %1 %2 %3 %4 %5
PAUSE
ENDLOCAL