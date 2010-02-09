@echo off
echo Collecting DLL information, please wait...

SETLOCAL
call setenv.bat
echo %date% %time% > dllinfo.txt
FOR /F "tokens=*" %%D IN ('DIR /B /S *.dll') DO (
    IF EXIST %WINDIR%\system32\%%~nxD (
        ECHO ******************************************************************* >> dllinfo.txt
        "%GDAL_ROOT%\bin\dllupdate" -oite "%%D" >> dllinfo.txt
    )
)
ENDLOCAL
echo Finished collecting DLL information, output is in "dllinfo.txt"
pause