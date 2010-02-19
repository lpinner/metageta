@echo off
setlocal
call "%~DP0setenv.bat"

call python.exe "%~DP0runtransform.py" %*
pause

REM TODO... plug in the GUI progress logger...

REM Check if the progress bar GUI will be used.
REM GUI=0
REM FOR %%A IN (%*) DO (
REM       IF /I "%%A"=="--gui" SET GUI=1
REM )

REM IF /I "%GUI%"=="0" (
REM call python.exe runtransform.py %*
REM pause
REM ) ELSE (
REM start "Crawler" /B pythonw.exe runtransform.py %*
REM )
endlocal
