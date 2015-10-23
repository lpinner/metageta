# MetaGETA

Search for, extract and transform metadata from spatial imagery data.

## Introduction
MetaGETA is a python application for discovering and extracting metadata from spatial raster datasets (metadata crawler) and transforming it into xml (metadata transformation). A number of generic and specialised imagery formats are supported. The format support has a plugin architecture and more formats can easily be added.

## News
06 August 2013 - MetaGETA 1.3.9 has been released! See the Changelog for details.

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
User installation:
 ```pip install --user metageta``` 
 ```pip install --user <path_to_downloaded_metageta>.whl```


System wide installation (requires root/admin/elevated privileges):
 ```pip install metageta``` 
 ```pip install <path_to_downloaded_metageta>.whl```

### Requirements
Python 2.7 and the following 3rd party Python libraries: 

 - lxml
 - openpyxl
 - pypiwin32 (obviously only on Windows)
 - gdal>=1.7

### Notes for Windows users: 
PyWin32, GDAL and lxml are binary extensions.  While [PyPi](https://pypi.python.org) has prebuilt wheels for PyWin32 (pypiwin32) and lxml, there are none (in PyPi) for GDAL.  We recommend Windows users install it from Christoph Gohlke's [Unofficial Windows Binaries for Python Extension Packages](http://www.lfd.uci.edu/~gohlke/pythonlibs).  Download the appropriate GDAL wheel for your Python architecture (either 32 or 64 bit) and install, e.g:
 ```pip install GDAL-1.11.3-cp27-none-win32.whl``` 
 or  
 ```pip install GDAL-1.11.3-cp27-none-win_amd64.whl```

I

## Usage
To use MetaGETA as provided, the first step is to crawl the filesystem to locate imagery and extract metadata to a spreadsheet. Writing to a spreadsheet allows for quality control, such as removal of records, checking for duplicates, bulk updates, etc. It also allows the addition of extra metadata fields such as contacts, use and access constraints etc. Information on additional metadata fields can be found [here](https://htmlpreview.github.io/?https://github.com/lpinner/metageta/blob/master/doc/files/metageta.transforms-module.html).

If you don't like spreadsheets, it's quite simple to roll your own script that writes straight to XML, database, etc... Check out the [API documentation](https://htmlpreview.github.io/?https://github.com/lpinner/metageta/blob/master/doc/index.html) for more info.

You can run the crawler and transform applications by simply double clicking or calling the runcrawler/runtransform executables (on Windows, you may need to add your install path to your PATH environment variable).

    usage: runcrawler [arguments]
    Run the metadata crawler. If no arguments are passed, a dialog box pops up.
    Options: 
	    -h, --help show this help message and exit 
	    -m media CD/DVD ID 
	    -x xlsx Output metadata spreadsheet 
            -o, --overviews Generate overview images 
            --debug Turn debug output on
            --keep-alive Reopen the dialog box after the crawl

The information extracted can then be transformed into XML. Currently only the ANZLIC Profile (ISO 19139) metadata schema is implemented for XML transformation, however more stylesheets can be added (PR welcome).

    Usage: runtransform [arguments]
    Transform metadata to XML. If no arguments are passed, a dialog box pops up.
    Options: 
	    -h, --help show this help message and exit 
	    -x xlsx Excel spreadsheet to read metadata from 
	    -t xsl XSL transform {.xsl|"ANZLIC Profile"} 
	    -m Create Metadata Exchange Format (MEF) file 
	    --debug Turn debug output on


