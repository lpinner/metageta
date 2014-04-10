@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
call "%~DP0\setenv.bat"
set PYTHONDLL=%PYTHONHOME%
set TCL_LIBRARY=%PYTHONHOME%\tcl\tcl8.5
set TK_LIBRARY=%PYTHONHOME%\tcl\tk8.5
set PYTHONPATH=%PYTHONPATH%;%PYTHONHOME%\DLLs;C:\Software\PyScripter\Lib
set PYTHONHOME=
REM start "PyScripter MetaGETA" /B "C:\Software\PyScripter\PyScripter.exe" --PYTHON27  --PYTHONDLLPATH "%PYTHONDLL%" --newinstance %1 %2 %3 %4 %5
CALL "C:\Software\PyScripter\PyScripter.exe" --PYTHON27  --PYTHONDLLPATH "%PYTHONDLL%" --newinstance %1 %2 %3 %4 %5
PAUSE
ENDLOCAL