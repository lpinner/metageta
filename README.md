# MetaGETA

Search for, extract and transform metadata from spatial imagery data.

## Introduction
MetaGETA is a python application for discovering and extracting metadata from spatial raster datasets (metadata crawler) and transforming it into xml (metadata transformation). A number of generic and specialised imagery formats are supported. The format support has a plugin architecture and more formats can easily be added.

## News
**Coming soon**

## Features
 - Search for supported data formats on your local or network file system;
 - Automatically extract file and format specific metadata;
 - Automatically populate an MS Excel (.xlsx) file with the metadata;
 - Automatically generate quicklooks and thumbnails for each metadata record;
 - Manually supplement metadata records with additional metadata fields;
 - Transform the MS Excel file to ANZLIC profile ISO19115/19139 xml as a bundled (includes quicklooks and thumbnails) MEF suitable for upload to Geonetwork;
   - Note: You can write your own translation stylesheet to meet the requirements of your target profile.
 - Subsequent metadata crawls may be used to update records when data is added to or removed from the file system;
 - Enables flagging of records in MS Excel that should not be included in the transformed xml i.e. maintains a record of but does not create xml metadata for redundant or irrelevant datasets.

## Installation
**Coming soon**
<!--
User installation:

    pip install --user metageta
    pip install --user <path_to_downloaded_metageta>.whl


System wide installation (requires root/admin/elevated privileges):
 ```pip install metageta``` 
 ```pip install <path_to_downloaded_metageta>.whl```

-->

### Requirements
Python 2.7 and the following 3rd party Python libraries: 

 - lxml
 - openpyxl
 - pypiwin32 (obviously only on Windows)
 - gdal>=1.7

### Notes for Windows users: 
PyWin32, GDAL and lxml are binary extensions.  While [PyPi](https://pypi.python.org) has prebuilt
wheels for PyWin32 (pypiwin32) and lxml, there are none (in PyPi) for GDAL.

We recommend Windows users install GDAL from either
Christoph Gohlke's [Unofficial Windows Binaries for Python Extension Packages](http://www.lfd.uci.edu/~gohlke/pythonlibs)
(built against numpy 1.9) or the the [GIS Internals](http://www.gisinternals.com) MSVC 2008 installers
which are built against numpy 1.7.  Download the appropriate GDAL wheel/msi for your Python architecture
(either 32 or 64 bit) and install.

For ease of installing both the GDAL python bindings and the ECW/MrSID plugins, we have repackaged the above
 wheels/installers into pip installable wheels complete with the plugins.

If you have numpy 1.7 installed (i.e an ArcGIS 10.1 or 10.2 python installation):

    pip install --user -i https://pypi.anaconda.org/luke/channel/np17/simple gdal

If you have numpy 1.9 installed:

    pip install --user -i https://pypi.anaconda.org/luke/channel/np19/simple gdal

If you don't have numpy installed, use either method, metageta will still run, but if you use GDAL for anything else,
you won't be able to import the ```gdal_array``` module or call the ```ReadAsArray``` functions.`


## Usage
To use MetaGETA as provided, the first step is to crawl the filesystem to locate imagery and extract metadata to a
spreadsheet. Writing to a spreadsheet allows for quality control, such as removal of records, checking for duplicates, bulk updates, etc. It also allows the addition of extra metadata fields such as contacts, use and access constraints etc. Information on additional metadata fields can be found [here](https://htmlpreview.github.io/?https://github.com/lpinner/metageta/blob/master/doc/files/metageta.transforms-module.html).

If you don't like spreadsheets, it's quite simple to roll your own script that writes straight to XML, database,
etc... Check out the [API documentation](https://htmlpreview.github.io/?https://github.com/lpinner/metageta/blob/master/doc/index.html) for more info.

You can run the crawler and transform applications by simply double clicking or calling the runcrawler/runtransform
executables (on Windows, you may need to add your install path to your PATH environment variable).

    usage: runcrawler [arguments]
    Run the metadata crawler. If no arguments are passed, a dialog box pops up.
    Options: 
	    -h, --help show this help message and exit 
	    -m media CD/DVD ID 
	    -x xlsx Output metadata spreadsheet 
            -o, --overviews Generate overview images 
            --debug Turn debug output on
            --keep-alive Reopen the dialog box after the crawl

The information extracted can then be transformed into XML. Currently only the ANZLIC Profile (ISO 19139)
metadata schema is implemented for XML transformation, however more stylesheets can be added (PR welcome).

    Usage: runtransform [arguments]
    Transform metadata to XML. If no arguments are passed, a dialog box pops up.
    Options: 
	    -h, --help show this help message and exit 
	    -x xlsx Excel spreadsheet to read metadata from 
	    -t xsl XSL transform {.xsl|"ANZLIC Profile"} 
	    -m Create Metadata Exchange Format (MEF) file 
	    --debug Turn debug output on


The metadata transform relies on a (per user) xml config file ([defaults](https://github.com/lpinner/metageta/blob/master/metageta/config/config.xml))
which can be edited using the ```metagetaconfig``` command.