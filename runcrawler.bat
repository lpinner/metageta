@echo off
setlocal ENABLEDELAYEDEXPANSION
call "%~DP0setenv.bat"
call python.exe "%~DP0runcrawler.py" --nogui %*
pause

REM Check if the progress bar GUI will be used.
REM set nogui=0
REM set /a nargs=0
REM for %%a in (%*) do (
REM     set /a nargs+=1
REM     if /i "%%a"=="--nogui" set nogui=1
REM     if /i "%%a"=="-h" (
REM         set nogui=1
REM     )
REM     if /i "%%a"=="--help" (
REM         set nogui=1
REM     )
REM )
REM if %nogui%==1 (
REM    call python.exe "%~DP0runcrawler.py" %*
REM    pause
REM ) else (
REM     start "Crawler" /b pythonw.exe "%~DP0runcrawler.py" %*
REM )
endlocal