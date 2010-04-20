@echo off
setlocal
call "%~DP0setenv.bat"

REM Check if the progress bar GUI will be used.
set nogui=0
set nopause=0
set /a nargs=0
for %%a in (%*) do (
    set /a nargs+=1
    if /i "%%a"=="--nogui" set nogui=1
    if /i "%%a"=="-h" (
        set nogui=1
        set nopause=1
    )
    if /i "%%a"=="--help" (
        set nogui=1
        set nopause=1
    )
)
if %nogui%==1 (
    call python.exe "%~DP0runcrawler.py" %*
    if %nopause%==0 pause
) else (
    REM Not using the GUI until I sort out the disconnection bug
    REM call python.exe  "%~DP0runcrawler.py" %* 
    REM pause
    start "Crawler" /b pythonw.exe "%~DP0runcrawler.py" %*
)
endlocal
