*************
License
*************
See <install>/MetaGeta/license.txt

*************
System
*************
Runs on Windows XP or Vista (only tested on 32 bit OS).

It has also been tested and mostly runs on 64 bit Linux (Ubuntu 9.04). However, there are issues with segfaults and read errors on HDF and NetCDF files on Ubuntu <=9.10. This is a GDAL/HDF4/NetCDF incompatibility - the UbuntuGIS gdal packages are built against a HDF4 library (libhdf4g) which includes an implementation of the netcdf api that is incompatible with the NetCDF library. See http://trac.osgeo.org/gdal/wiki/HDF for more info. The only way around it (currently) is to build your own HDF4 library from source and then link to that when building gdal from source. This should not be a problem on current versions of Debian or Ubuntu > 10.04 (lucid lynx) where gdal is/will be built against the new libhdf4-alt library 

*************
Installation
*************
*Windows*:

Download [http://code.google.com/p/metageta/downloads/list] the setup zipfile and extract and run the installer.  The application contains all the 3rd party libraries and applications required. The MrSID, JPEG2000 and ECW drivers use proprietary SDK's, to add support for these formats, download the plugins setup zipfile and extract and run the installer. 

*Linux (or Windows where you wish to use your own Python and GDAL/OGR installations)*:

Download [http://code.google.com/p/metageta/downloads/list] the source package or checkout [http://code.google.com/p/metageta/source/checkout] a copy of the source code, extract somewhere and see below:

You will need the following libraries:

  * Python 2.5 or 2.6 and the following non-standard Python libraries: (if you wish to use Python 3.0+, you will need to port the application)
    * epydoc [http://epydoc.sourceforge.net]
    * 4Suite XML [http://4suite.org]
    * xlutils 1.41+ [http://pypi.python.org/pypi/xlutils ]
    * xlrd 0.71+ [http://pypi.python.org/pypi/xlrd]
    * xlwt 0.72+ [http://pypi.python.org/pypi/xlwt]
    * pywin32 [http://pywin32.sourceforge.net] (obviously only on Windows)
    * GDAL python bindings (see below)

  * GDAL 1.6+ http://www.gdal.org
    * On Windows, use OSGeo4W [http://trac.osgeo.org/osgeo4w] or the prebuilt binaries at http://vbkto.dyndns.org/sdk to get GDAL 1.6+ and the appropriate python bindings (Don't use FWTools, it only supports python 2.3.)
    * On Ubuntu, try the UbuntuGIS [https://wiki.ubuntu.com/UbuntuGIS] packages (or build from source if you prefer)
    * If you want to read ECW/JPEG2000/MrSID files, you'll need to install and link to the appropriate SDK (if building from source) or the OSGeo4W plugins gdal-mrsid [http://trac.osgeo.org/osgeo4w/wiki/pkg-gdal-mrsid] & gdal-ecw [http://trac.osgeo.org/osgeo4w/wiki/pkg-gdal-ecw]) or the see the UbuntuGIS scripts - gdal-mrsid-build gdal-ecw-build (located in /usr/bin by default if installed from the repos) and see - http://lists.osgeo.org/pipermail/ubuntu/2009-June/000054.html and http://trac.osgeo.org/ubuntugis/wiki/TutorialMrSid
    * You will also have to download and build appropriate libraries for other non-standard GDAL formats. 
    * See http://trac.osgeo.org/gdal/wiki/BuildHints for more info

*************
Usage
*************
To use MetaGeta as provided, the first step is to crawl the filesystem to locate imagery and extract metadata to a spreadsheet. Writing to a spreadsheet allows for quality control, such as removal of records, checking for duplicates, bulk updates, etc. It also allows the addition of extra metadata fields such as contacts, use and access constraints etc. Information on additional metadata fields can be found here.

If you don't like spreadsheets, it's quite simple to roll your own script that writes straight to XML, database, etc... Check out the API documentation for more info.

You can run the crawler and transform applications by simply double clicking the runcrawler/runtransform.[bat|sh] files. Don't try to run any .py files directly unless you have set up your environment to suit.

You can also run the crawler and transform applications without the directory/files entry GUI popping up by passing arguments to runcrawler/runtransform.[bat|sh].

Usage: runcrawler.bat/sh arguments

Run the metadata crawler. If no arguments are passed, a dialog box pops up.

Options: -h, --help show this help message and exit -d dir The directory to crawl -m media CD/DVD ID -x xls Output metadata spreadsheet -u, --update Update existing crawl results -o, --overviews Generate overview images --debug Turn debug output on --nogui Don't show the GUI progress dialog --keep-alive Keep this dialog box open

The information extracted can then be transformed into XML. Currently only the ANZLIC Profile (ISO 19139) metadata schema is implemented for XML transformation, however more stylesheets can be added easily.

Usage: runtransform.bat/sh arguments 

Transform metadata to XML. If no arguments are passed, a dialog box pops up.

Options: -h, --help show this help message and exit -d dir The directory to output metadata XML to -x xls Excel spreadsheet to read metadata from -t xsl XSL transform {.xsl|"ANZLIC Profile"} -m Create Metadata Exchange Format (MEF) file --debug Turn debug output on

Basic API documentation may be found here: http://metageta.googlecode.com/svn/trunk/doc/index.html