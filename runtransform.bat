@echo off
setlocal
call "%~DP0setenv.bat"

REM Check if the progress bar GUI will be used.
set nogui=0
set /a nargs=0
for %%a in (%*) do (
    set /a nargs+=1
    if /i "%%a"=="--nogui" set nogui=1
    if /i "%%a"=="-h" (
        set nogui=1
    )
    if /i "%%a"=="--help" (
        set nogui=1
    )
)
if %nogui%==1 (
    call python.exe "%~DP0runtransform.py" %*
) else (
    start "Crawler" /b pythonw.exe "%~DP0runtransform.py" %*
)
endlocal