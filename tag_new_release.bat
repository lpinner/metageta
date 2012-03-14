@echo off
SET CURDIR=%CD%

Set /P version=Enter release version number (e.g. 1.2.3):
If "%version%"=="" goto :err
goto:noerr

:err
echo No release version entered
goto:end

:noerr
SET SRC=https://metageta.googlecode.com/svn/trunk
SET DST=https://metageta.googlecode.com/svn/tags/%version%

svn copy %SRC% %DST% -m "Tagging version %version%"
svn checkout --depth=empty %DST% %TEMP%\metageta-%version%
cd %TEMP%\metageta-%version%
svn propset displayversion %version% .
svn propset version %version%.$Revision$ .
svn commit -m "Updating version properties %version%"
cd %CURDIR%
del /f /q %TEMP%\metageta-%version%

:end
pause