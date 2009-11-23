*************
License
*************
See <install>/crawler/license.txt

*************
System
*************
Requires Windows XP or Vista (only tested on 32 bit OS). 
May require administrative rights, I haven't tested on a PC using a non-admin user account.

It has also been tested and mostly runs on 64 bit Linux (Ubuntu 9.04). 
There are issues with segfaults and read errors on HDF and NetCDF files. This is a GDAL/HDF/NetCDF issue.

The application contains all the 3rd party libraries and applications required. The MrSID and ECW drivers
use proprietary SDK's. See mrsid-eula.txt and ecw-eula.txt in the <install>\crawler directory.

If you wish to use your own Python and GDAL/OGR installations, you will need the following libraries:
  Python 2.5 or 2.6 and the following non-standard Python libraries: (if you wish to use Python 3.0+, you will need to port the application)
    * epydoc http://epydoc.sourceforge.net
    * 4Suite XML http://4suite.org
    * xlutils (inc. xlrd & xlwt) http://pypi.python.org/pypi/xlutils
    * pywin32 http://pywin32.sourceforge.net
    * GDAL python bindings (see below)

  GDAL 1.6+ http://www.gdal.org
    On Windows, use OSGeo4W to get GDAL 1.6 and the appropriate python bindings. http://trac.osgeo.org/osgeo4w (Don't use FWTools, it only supports python 2.3.)
    On ubuntu, try the UbuntuGIS packages https://wiki.ubuntu.com/UbuntuGIS (or build from source if you prefer)
    If you want to read ECW/JPEG2000/MrSID files, you'll need to install and link to the appropriate SDK (if building from source)
    or the OSGeo4W plugins (http://trac.osgeo.org/osgeo4w/wiki/pkg-gdal-mrsid & http://trac.osgeo.org/osgeo4w/wiki/pkg-gdal-ecw)
    or the see the UbuntuGIS scripts - gdal-mrsid-build gdal-ecw-build (located in /usr/bin by default if installed from the repos) and see - 
    http://lists.osgeo.org/pipermail/ubuntu/2009-June/000054.html and http://trac.osgeo.org/ubuntugis/wiki/TutorialMrSid
  
*************
Installation
*************
Windows:
Extract to a local directory (e.g. C:\Metadata_Crawler)
It will run from a network path, but is considerably slower.

Linux: extract the crawler directory somewhere

*************
Running
*************
You can run the crawler by simply double clicking the runcrawler.[bat|sh] file. 
Don't try to run any *.py files directly unless you have set up your environment to suit.

You can also run the crawler without the directory/files entry GUI popping up
by passing arguments to runcrawler.[bat|sh]. 

1. Either make a shortcut to runcrawler.bat, then right click, select properties 
and change "Target:" from 
"<path>\runcrawler.bat" to 
"<path>\runcrawler.bat" -d "<some directory>" -x "<some *.xls>" -s "<some *.shp>" -l "<some *.log>" -o

OR

2. in a cmd window or another batch file:
"<path>\runcrawler.[bat|sh]" -d "<some directory>" -x "<some *.xls>" -s "<some *.shp>" -l "<some *.log>" -o

NOTE the double quotes are only required if your paths have spaces in them...

*************
Support
*************
No support is available.