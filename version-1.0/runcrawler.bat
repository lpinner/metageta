@echo off
call setenv.bat

REM Check if the progress bar GUI will be used.
set gui=0
set /a nargs=0
for %%a in (%*) do (
    set /a nargs+=1
    if /i "%%a"=="--gui" set gui=1
)
if %nargs%==0 set gui=1
if /i "%gui%"=="0" (
    call python.exe runcrawler.py %*
    pause
) else (
    call python.exe runcrawler.py %*
    pause
rem    start "Crawler" /b pythonw.exe runcrawler.py %*
)
