*************
System
*************
Requires Windows XP or Vista 32 bit OS. It will be ported to Linux in the not tooo distant future.
May require administrative rights, I haven't tested on a PC using a non-admin user account.

The application contains all the required 3rd party libraries and applications required. The MrSID and ECW drivers
use proprietary SDK's. See mrsid-license.txt and ecw-license.txt in the <install>\crawler directory.

If you wish to use your own Python and GDAL/OGR installations, you will need the following libraries:
  Python 2.5 or 2.6 and the following non-standard Python libraries: (if you wish to use Python 3.0+, you will need to port the application)
    * epydoc http://epydoc.sourceforge.net
    * 4Suite XML http://4suite.org
    * xlutils (inc. xlrd & xlwt) http://pypi.python.org/pypi/xlutils
    * pywin32 http://pywin32.sourceforge.net
    * GDAL python bindings (see below)

  GDAL 1.6+ http://www.gdal.org
    On Windows, use OSGeo4W to get GDAL 1.6 and the appropriate python bindings. http://trac.osgeo.org/osgeo4w (Don't use FWTools, it only supports python 2.3.)
    On ubuntu, try the UbuntuGIS packages https://wiki.ubuntu.com/UbuntuGIS
    If you want to read ECW/JPEG2000/MrSID files, you'll need to install and link to the appropriate SDK (if building from source) 
    or the OSGeo4W plugins (http://trac.osgeo.org/osgeo4w/wiki/pkg-gdal-mrsid & http://trac.osgeo.org/osgeo4w/wiki/pkg-gdal-ecw)
  
*************
Installation
*************
Extract to a local directory (e.g. C:\Metadata_Crawler)
It will run from a network path, but is considerably slower.

*************
Running
*************
You can run the crawler by simply double clicking the runcrawler.bat file. 
Don't try to run any *.py files directly unless you have set up your environment to suit.

You can also run the crawler without the directory/files entry GUI popping up
by passing arguments to crawler.bat. 

1. Either make a shortcut to runcrawler.bat, then right click, select properties 
and change "Target:" from 
"<path>\runcrawler.bat" to 
"<path>\runcrawler.bat" -d "<some directory>" -x "<some *.xls>" -s "<some *.shp>" -l "<some *.log>" -o

OR

2. in a cmd window or another batch file:
call "<path>\runcrawler.bat" -d "<some directory>" -x "<some *.xls>" -s "<some *.shp>" -l "<some *.log>" -o

NOTE the double quotes are only required if your paths have spaces in them...

