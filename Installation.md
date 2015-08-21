# System #
Runs on Windows XP, Vista and Windows 7 (only tested on 32 bit OS).

It has also been tested and mostly runs on 64 bit Linux (Ubuntu 9.04).
However, there are issues with segfaults and read errors on HDF and NetCDF files on Ubuntu <=9.10. This is a GDAL/HDF4/NetCDF incompatibility - the UbuntuGIS gdal packages are built against a HDF4 library (libhdf4g) which includes an implementation of the netcdf api that is incompatible with the NetCDF library. See http://trac.osgeo.org/gdal/wiki/HDF for more info. The only way around it (currently) is to build your own HDF4 library from source and then link to that when building gdal from source. This should not be a problem on current versions of Debian or Ubuntu > 10.04 (lucid lynx) where gdal is/will be built against the new libhdf4-alt library

# Installation #
**Windows**:

[Download](http://code.google.com/p/metageta/downloads/list) the setup zipfile and extract and run the installer.  The application contains all the 3rd party libraries and applications required. The MrSID, JPEG2000 and ECW drivers use proprietary SDK's, to add support for these formats, download the plugins setup zipfile and extract and run the installer.


**Linux (or Windows where you wish to use your own Python and GDAL/OGR installations)**:

[Download](http://code.google.com/p/metageta/downloads/list) the source package or [checkout](http://code.google.com/p/metageta/source/checkout) a copy of the source code, extract somewhere and see below:

You will need the following libraries:

  * Python 2.5 or 2.6 and the following non-standard Python libraries: (if you wish to use Python 3.0+, you will need to port the application)
    * [lxml](http://lxml.de) ([4Suite XML](http://4suite.org) for MetaGETA <= 1.3.6)
    * [xlutils](http://pypi.python.org/pypi/xlutils) 1.41+
    * [xlrd](http://pypi.python.org/pypi/xlrd) 0.71+
    * [xlwt](http://pypi.python.org/pypi/xlwt) 0.72+
    * [pywin32](http://pywin32.sourceforge.net) (obviously only on Windows)
    * [epydoc](http://epydoc.sourceforge.net)
    * [Tix](http://tix.sourceforge.net) (only if you wish to use a GUI, not required on 1.3.7+)
    * GDAL python bindings (see below)

  * GDAL 1.6+ http://www.gdal.org
    * On Windows, use [OSGeo4W](http://trac.osgeo.org/osgeo4w) or the prebuilt binaries at http://www.gisinternals.com/sdk to get GDAL 1.6+ and the appropriate python bindings (Don't use FWTools, it only supports python 2.3.)
    * On Ubuntu, try the [UbuntuGIS](https://wiki.ubuntu.com/UbuntuGIS) packages (or build from source if you prefer).
    * On Debian, try the [wiki.debian.org/DebianGis DebianGIS] packages (or build from source if you prefer).
    * On RHEL/CentOS, try the [ELGIS](http://elgis.argeo.org/) packages (or build from source if you prefer).
    * On OSX, try the [KyngChaos](http://www.kyngchaos.com/software/frameworks) Framework.
    * If you want to read ECW/JPEG2000/MrSID files, you'll need to install and link to the appropriate SDK (if building from source) or the OSGeo4W plugins [gdal-mrsid](http://trac.osgeo.org/osgeo4w/wiki/pkg-gdal-mrsid) & [gdal-ecw](http://trac.osgeo.org/osgeo4w/wiki/pkg-gdal-ecw)) or the see the UbuntuGIS scripts - gdal-mrsid-build gdal-ecw-build (located in /usr/bin by default if installed from the repos) and see - http://lists.osgeo.org/pipermail/ubuntu/2009-June/000054.html and http://trac.osgeo.org/ubuntugis/wiki/TutorialMrSid
    * You will also have to download and build appropriate libraries for other non-standard GDAL formats.
    * See http://trac.osgeo.org/gdal/wiki/BuildHints for more info


**Step by step on Ubuntu 10.04 32 bit**:
  * Installed the following packages from the repositories:
    * libgdal1-1.6.0
    * gdal-bin
    * python-gdal # NB I didn't mess around trying to get the latest gdal version from source/ubuntugis etc, nor did I install ECW/JP2 support.
    * libproj0
    * proj-data
    * python-pip
    * tix
    * python-4suite-xml
    * Made a sym link (ln -s) from /usr/lib/libproj.so.0.6.6 named /usr/lib/libproj.so
      * NB there is a symlink named /usr/lib/libproj.so.0 created during install, but gdal was complaining it couldn't find "libproj.so"
    * Used python-pip (you can also use easy\_install) to install the following packages from http://pypi.python.org (NB python-pip executable is called "pip" e.g. sudo pip install somepackagename
      * xlutils
      * xlrd
      * xlwt
    * unzipped the metageta-1.N.N.zip
    * Set GDAL\_DATA, GEOTIFF\_CSV and LD\_LIBRARY\_PATH env vars to appropriate locations (in my case /usr/share/gdal16 and /usr/lib). I did this in my bash profile so I could use the gdal utilities on their own. I could  have edited "setenv.sh" in the metageta dir instead.
    * Made runcrawler.sh and runtransform.sh executable (chmod +x etc.)

  * Update: the Tix ComboBox no worky in Ubuntu 9.04-10.04, https://bugs.launchpad.net/ubuntu/+source/tix/+bug/371720. The workaround is to install Tix 8.4.3 from https://launchpad.net/~portis25/+archive/science

