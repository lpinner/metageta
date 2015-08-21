# MetaGETA Change Log #
## 06/08/2013 ##
MetaGETA 1.3.9 released

  * Fix GeoEye-1 bugs

## 01/08/2013 ##
MetaGETA 1.3.8 released

  * Upgrade python to 2.7, GDAL to 1.10 and ECW/JP2 SDK to 5.0
  * Fix updating existing spreadsheet when crawling zip/tar/gzip files.
  * Nicer CSS for API docs
  * Fix bugs in zip/tar archive handling
  * Fix userid/username lookup on Windows 7
  * Fix ECW crashes
  * Fix gdal version checking
  * Fix update/overwrite spreadsheet when passed in as argument
  * Fix aster row/col order bug
  * Fix ncols/nrows bug
  * Basic Pleiades HR support in dimap.py
  * Hack for SKM mosaiced datasets for SSD.
  * Deprecate the GUI progress logger. Isn't working properly with Python 2.7. Code is left in in case someone wants to use it.
  * Add L1GST hyperion support (ali\_hyperion.py)
  * Add new USGS Landsat metadata format support.
  * Add Landsat 8/LCDM support
  * Use new GDAL\_API\_PROXY (gdal 1.10+) for remote datasets in ECW/JP2 so driver crashes don't crash the python process.
  * Fix the digitalglobe regex so it doesn't pick up Landsat images.

## 16/08/2012 ##
MetaGETA 1.3.7 released

  * Update DIMAP driver to handle DCMii format.
  * Fixed the Windows installer so Metageta actually runs on Windows...
  * Remove dependency on old/unmaintained 4Suite XML library and port to the lxml library
  * Remove dependency on Tkinter/Tix so Metageta can run without requiring a GUI.
  * Add support for setting Geonetwork MEF operations privileges from the runtransform script or the metadata crawl spreadsheet
  * Add setup.py script for easier install on Linux
  * A number of minor improvements and bugfixes.

Full list of changes: [detailed changelog](ChangelogDetail.md)


## 14/03/2012 ##
MetaGETA 1.3.6 released

  * Added IKONOS/GeoEye format driver.
  * Enabled metadata extraction from zip/tar archives for generic gdal supported formats.
  * Updated GDAL to v. 1.9.0 in the Windows installer.
  * A number of minor improvements and bugfixes.

Full list of changes: [detailed changelog](ChangelogDetail.md)


## 27/07/2011 ##
MetaGETA 1.3.5 released

  * Fixed issue with runtransform not opening, for some reason the SVN repo reverted it to an earlier version and no amount of committing the updated file would change the repo.
  * Quicklooks paths are now relative to xls output - [Issue 42](http://code.google.com/p/metageta/issues/detail?id=42)

## 08/02/2011 ##
MetaGETA 1.3.4 released

A number of minor improvements and bugfixes.

Full list of changes: [detailed changelog](ChangelogDetail.md)


## 23/07/2010 ##
MetaGETA 1.3.3 released

Improvements to the Progress Logger, particularly notifying the user if the parent python process (the crawler) has crashed.
Much better colourtable handling
Support for many more image formats added.

_Bugfixes:_
A number of bugfixes, including working around a segfault crash in OGR.

Full list of changes:
http://code.google.com/p/metageta/source/list?num=54&start=456


## 07/06/2010 ##
MetaGETA 1.3.2 released

_Enhancements:_
  * Removed Quickbird driver and replaced with Digitalglobe driver to handle Worldview 1 & 2 formats in addition to Quickbird.
  * Added simple config file which allows customisation of the default metadata contact.
  * Manually adding one or more geographicIdentifier columns to the spreadsheet is now supported by the ANLIC Profile XSL stylesheet.

_Bugfixes:_
  * Removed DEWHA contact details from ANLIC Profile XSL stylesheet.

## 17/05/2010 ##
MetaGETA 1.3.1 released

_Enhancements:_
  * Enhanced the check that tests whether a dataset has been updated ([Issue 26](https://code.google.com/p/metageta/issues/detail?id=26))
  * Renabled the reading of ERS files associated with ECW datasets to extract extra metadata. This was originally disabled when MetaGETA used GDAL 1.6x and NCS`_*`.dll ECW redistributables as GDAL would segfault on certain ERS/ECW files. GDAL 1.7 with libecwj2.dll appears to be much more stable.
  * Updated README.txt

_Bugfixes:_
  * This fixes a serious bug in the installer ([Issue 27](https://code.google.com/p/metageta/issues/detail?id=27))  that would prevent the crawler from running if the PC didn't already have python installed.

## 10/05/2010 ##
MetaGETA 1.3 released

Initial public release