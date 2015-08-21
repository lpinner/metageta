# Introduction #

OSGeo4W is the easiest gdal distribution to incorporate into MetaGETA, unfortunately it contains libraries that (according to legal advice) we may not redistribute. To get around this, we could use the prebuilt binaries at http://www.gisinternals.com/sdk, unfortunately this build does not include HDF4 support. So we must build from source to get HDF4 support.   Unfortunately, the HDF4 prebuilt binaries are linked against szip, a not completely open source library.  So we must also build HDF4 from source and remove szip completely.

That's 3 unfortunatelys...

Note: Make that 4, cos unfortunately this process is a pain in the proverbial.


# Details #
> ## INSTALL ##
> Microsoft Visual C++ 2008 Express Edition
> http://www.microsoft.com/express/Downloads/#2008-Visual-CPP

> Microsoft Platform SDK for Windows Server 2003 [R2](https://code.google.com/p/metageta/source/detail?r=2)
> http://www.microsoft.com/downloads/details.aspx?displaylang=en&FamilyID=0baf2b35-c656-4969-ace8-e4c0c0716adb
> Note: I couldn't get the Web Install ^ to work, probably a proxy issue. I had to do the "Full Download"
> and download alk 17 CAB files individually... (unfortunately...)
> http://www.microsoft.com/downloads/details.aspx?FamilyId=484269E2-3B89-47E3-8EB7-1F2BE6D7123A&displaylang=en

> ## DOWNLOAD ##
> HDF 4.X, ZLIB and JPEG SOURCE ARCHIVES
> http://www.hdfgroup.org/release4/obtain.html

> GDAL MSVC2008 (Win32) SDK
> http://www.gisinternals.com/sdk/release-1500-dev.zip

## BUILD ##
> ### HDF ###
> Unpack the source archive and follow the detailed instructions in <unpacked hdf dir>\release\_notes\INSTALL\_WINDOWS.txt.
> Follow the steps in this order:
    * Preconditions
      * Note: Ignore Fortran and SZIP related notes in this section
    * Section VII. Disable Szip Compression Feature inside HDF4
      * Option 1: Remove Szip compression completely
        * Note: Section VII. refers to "H4config.h" in <unpacked hdf dir>\hdf\src. This is incorrect, it should be <unpacked hdf dir>\windows\hdf\src
        * Note: Section VII. Option 1 refers to #define HAVE\_SZIP\_ENCODER 1. This is incorrect, it should be #define H4\_HAVE\_SZIP\_ENCODER 1
    * Section I: Build and Test HDF4 Libraries and Utilities
      * Step 1: Build HDF4 Libraries and Utilities
        * Note: You can ignore the debug build.
    * Step 4:  Install HDF4 Library
      * Note: Don't run installhdf4lib.BAT directly, open a command prompt and CD to <unpacked hdf dir> then type the following command as the relative paths in the batch file are (unfortunately) incorrect. windows\installhdf4lib.BAT

> Note: If you want to try building the HDF libraries from the command line (Section IX. Build and Test HDF4 Library on the Command Line), unfortunately VC Express doesn't include DEVENV.EXE which is referred to in hdf4build.bat. You'll need to modify this bat file to work with msbuild OR vcbuild (I haven't tried).

> ### GDAL ###
> Unpack the source archive. Edit <unpacked gdal dir>\gdal\nmake.opt and change:
```
    # Uncomment the following and update to enable NCSA HDF Release 4 support.
    #HDF4_PLUGIN = NO
    #HDF4_DIR =	<some path etc...>
    #HDF4_LIB =	/LIBPATH:$(HDF4_DIR)\lib Ws2_32.lib
```
> to:
```
    # Uncomment the following and update to enable NCSA HDF Release 4 support.
    HDF4_PLUGIN = NO
    HDF4_DIR =	<unpacked hdf dir>\hdf4lib\release
    HDF4_LIB =	$(HDF4_DIR)\dll\hm425m.lib $(HDF4_DIR)\dll\hd425m.lib Ws2_32.lib
```

  * Open a Visual Studio 2008 Command Prompt (in Start->All Programs->Microsoft Visual C++ 2008 Express Edition->Visual Studio Tools)
  * CD to <unpacked gdal dir> and type:
> > nmake gdal

  * Make an application dir somewhere and copy the appropriate files:
> > e.g.
```
        SET GDALDIR=<unpacked gdal dir>
        SET HDFDIR=<unpacked hdf dir>
        SET APPDIR=<some directory>\bin\gdal
        IF exist %APPDIR% RMDIR /S /Q %APPDIR%
        MKDIR %APPDIR%

        ECHO ftgl.dll>%GDALDIR%\excludes.txt
        ECHO fribidi.dll>>%GDALDIR%\excludes.txt
        ECHO libfcgi.dll>>%GDALDIR%\excludes.txt
        ECHO pdflib.dll>>%GDALDIR%\excludes.txt
        ECHO libmap.dll>>%GDALDIR%\excludes.txt
        ECHO cairo.dll>>%GDALDIR%\excludes.txt        ECHO cfitsio.dll>>%GDALDIR%\excludes.txt
        XCOPY /EXCLUDE:%GDALDIR%\excludes.txt /I /Y %GDALDIR%\release-1500\bin\*.dll %APPDIR%\bin
        XCOPY /I /Y %GDALDIR%\release-1500\bin\gdal\apps\*info.exe %APPDIR%\bin
        ECHO gdal_FITS.dll>%GDALDIR%\excludes.txt
        XCOPY /EXCLUDE:%GDALDIR%\excludes.txt /I /Y %GDALDIR%\release-1500\bin\gdal\plugins\gdal_*.dll %APPDIR%\bin\plugins
        XCOPY /I /Y /S %GDALDIR%\release-1500\bin\gdal\python\* %APPDIR%\lib
        XCOPY /I /Y %GDALDIR%\release-1500\bin\gdal-data\* %APPDIR%\share\gdal-data
        XCOPY /I /Y %GDALDIR%\release-1500\bin\proj\share %APPDIR%\share\proj
        XCOPY /I /Y %HDFDIR%\hdf4lib\release\dll\*.dll %APPDIR%\bin
        DEL %GDALDIR%\excludes.txt
```

  * Finally, edit %APPDIR%\bin\gdal\share\gdal-data\ecw\_cs.wkt (ecw\_cs.dat no longer seems to be in GDAL trunk...) and append the contents of the custom [ecw\_cs.wkt](http://code.google.com/p/metageta/source/browse/build/gdal/gdal_data/ecw_cs.wkt)