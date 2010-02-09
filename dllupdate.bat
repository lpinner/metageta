@echo off
echo Updating DLLs, please wait...

SETLOCAL
call setenv.bat
echo %date% %time% > dllupdate.txt
FOR /F "tokens=*" %%D IN ('DIR /B /S *.dll') DO (
    IF EXIST %WINDIR%\system32\%%~nxD (
        ECHO ******************************************************************* >> dllupdate.txt
        "%GDAL_ROOT%\bin\dllupdate" -oite -copy "%%D" >> dllupdate.txt
    )
)
ENDLOCAL
echo Finished updating DLLs, output is in "dllupdate.txt"
pause