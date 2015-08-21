## Changes in MetaGETA 1.3.7 ##
Add ULA and update DIMAP drivers

Add setup.py script for easier install on Linux

Fix bug with generating colour tables from raster attribute tables.

Better checks for file/dir/zip types in recursive glob.

A few tweaks to allow running without Tkinter/Tix installed.

Resolve issues 45, 46 and 47

Clean out the PATH env var to hopefully avoid more missing/extra dependencies

Fix field length

Fix bug where deleted files were not being marked as such

Fix dual inheritance issue.

ogr.Geometry.GetBoundary() requires geos, use GetGeometryRef instead so code runs on systems where gdal was built w/out geos support.

Port to lxml instead of 4suite. Add exslt format-date function as it's not available in lxml

Add file path to DigitalTransferOptions

Add support for setting Geonetwork MEF operations privileges from the runtransform script or the metadata crawl spreadsheet


## Changes in MetaGETA 1.3.6 ##
Added IKONOS/GeoEye format driver

Update ANZLIC metadata stylesheet to remove hardcoded GeographicDescription and include use one or more if defined in the crawler result spreadsheet.

Remove NoDataValue from stretched VRT as it doesn't really make a difference and can massively increase overview creation time on large tiffs with BLOCKYSIZE > 1.

Enabled metadata extraction from zip/tar archives for generic gdal supported formats. Untested on custom formats yet. No handling of errors trying to read such formats other than the usual logging.

Fix ExcelWriter not handling dict inputs, regression from adding list handling functionality.

Add license elements to ANZLIC XSLT

Don't inform user that a dataset has been marked as deleted if it was already marked as deleted in the spreadsheet.

Handle DigitalGlobe NITF format - get the geotransform and projection info from the GCPs

Fixes for PCI Geomatics ('.pix') datasets

Fix incorrect extent ordering. Better ERS checking

Fix "Failed to compute min/max, no valid pixels found in sampling" error when generating approximate statistics.

## Changes in MetaGETA 1.3.5 ##
Fixed issue with runtransform not opening, for some reason the SVN repo reverted it to an earlier version and no amount of committing the updated file would change the repo.

Quicklooks paths are now relative to xls output - [Issue 42](http://code.google.com/p/metageta/issues/detail?id=42)

## Changes in MetaGETA 1.3.4 ##
Fixed bug which causes Python to hang  on exit.

Resolved [Issue 41](http://code.google.com/p/metageta/issues/detail?id=41)

Log the number of records to transform.

Plugging the progresslogger GUI into runtransform.

Resolved [Issue 40](http://code.google.com/p/metageta/issues/detail?id=40)

Update copyright statement to current Department name

Added MEF and category option to runtransform gui

Added multiselect functionality to getargs.ComboBoxArg

Remove hardcoded category & siteid in transforms/init.py

Updated config.xml to suit.

Removed splash screen, updated docs.

Added option to not recursively crawl selected directory

More GeoNetwork validation fixes

Extra check so existing spreadsheets don't get overwritten by accident - disable the "update" checkbox in GetArgs dialog, check for xls file existence in xlsarg callback, if True then enable the update checkbox and set it to True so the user has to explicitly uncheck it to overwrite the xls file.  This looks better than simply setting the update checkbox to True by default which might be confusing if the user isn't expecting the xls file to already exist.

Add support for Wideband ALOS PRISM

Fixed regression that stops the python/pythonw process from exiting properly which was introduced during some debugging.

Fixed regression created by [r517](https://code.google.com/p/metageta/source/detail?r=517)

Fixed error handling level in ALOS driver

Use browse jpeg for overview generation if it exists.

Fix "level" for orthocorrected imagery

Update ALOS format to handle ACRES orthocorrected GeoTIFF product

Add "source" element to LI\_Lineage, update doc string

Fixes to dataquality date handling and default email address to pass validation.

Resolved [Issue 37](http://code.google.com/p/metageta/issues/detail?id=37)

Add support for Landsat MTL Geotiffs

Check file basename against regex

Handle ENVI datafiles that can have any extension, or none at all.

Provide a little more info about why we can't handle certain NetCDF files

Change from yyyy-mm-dd date format to yyyy-mm-ddThh:mm:ss date time format for forward compatibility (still ISO 8601).

Create date ranges (date/date format) where possible (i.e. spotview)

Bugfix in fast\_l7a format, not setting filelist property correctly

Modify dataset.classproperty decorator to raise Typerror if properties are not get/set correctly

Handle date ranges in stylesheet transform (but strip off time as ISO 19139 uses date only)

Fix anzlic\_iso19139.xsl so it validates correctly in Geonetwork 2.6+

Generate MEF even if overviews don't exist

Handle "spotview" profile DIMAPs.

Check if a dataset has been deleted, don't output any XML if so and mark existing xml/mef files as ".deleted"

Resolved [Issue 35](http://code.google.com/p/metageta/issues/detail?id=35)

Removed debugging code

pickle doesn't like unicode, so use cPickle instead.

Resolved [Issue 34.](http://code.google.com/p/metageta/issues/detail?id=34)

Centre ProgressLoggerGUI and adjust height/width to screen size

Fixed bug with not being able to generate overviews from highly compressed ESRI grids. Moved compression ratio test out of dataset.py and into the JP@ & ECW drivers.

Added some exception handling for aux driver workaround.

geometry.py - Pixel to Map (& vice-versa) functions return floats, no rounding.

formats/default.py - add support for JPEG, PNG and TIFFs with a ".tiff " extension, ".tif" was already supported.

> - raise exception if file is not georeferenced.

Fix bug where the the metadata xml generated by runtransform gets included in the dataset filelist

Handle empty shapefiles/spreadsheets

Use tkFileDialog.askopenfilename as well as tkFileDialog.asksaveasfilename

Fix bug where the the metadata xml generated by runtransform gets included in the dataset filelist



## Changes in 1.3.3 ##

Handle empty shapefiles/spreadsheets

Use tkFileDialog.askopenfilename as well as tkFileDialog.asksaveasfilename

Fix bug when running via pythonw.exe - no console, so trying to close the console logging handler caused an exception.

Fix bug with spaces introduced when progresslogger.py was modified to use optparse

Icon updated

Fix filelist delimeter. Filepaths can have commas...

Make same fix as [r432](https://code.google.com/p/metageta/source/detail?r=432) to UpdateRecord.

Fixed segfault crash with non-ascii fillepaths

Fixed bug where ESRI grids were not identified as having already had metadata extracted previously as the GUID was generated from the <grid dir>/hdr.adf file, but the guid used to check with was generated from the <grid dir>.

Fixed bug where images were identified as modified if they did not have a quicklook generated previously.

Resolved [Issue 28](http://code.google.com/p/metageta/issues/detail?id=28)

Improvements to the ProgressLogger.

MetaGETA GUI titlebar icon is now a class

isrunning(processid) added to utilities.py

Docstring updates

lib/progresslogger.py - The ProgressLoggerGUI now checks whether the parent process is still running.

runcrawler.py - changed application name to MetaGETA Crawler

getargs.py - make sure GetArgs() returns None if the window is closed as well as pressing the cancel button

runcrawler.py - move progresslogger handling out of main()

> - Resolved [Issue 29](http://code.google.com/p/metageta/issues/detail?id=29)

progresslogger.py - make  ProgressLogger a new style class so it can has properties

> - add a logfile property

Fixes to colourtable handling.

Fixes to colourtable handling.

formats.dataset.py and overviews.py - fixes to overview generation for byte and int images with attribute tables, now uses a 2 stddev greyscale stretch instead of random colours where attribute table row count < 256

runcrawler.py - add check for existence of quicklook file to determine whether a dataset is modified.

Bugfix in overview generation for singleband rasters with colourtable.

Resolved [Issue 31](http://code.google.com/p/metageta/issues/detail?id=31).

Added regexes for most common GDAL supported formats to the default driver. Very little testing except on rasters in the GDAL autotest suite.

Upped field length to 100 for "filename" field as it was getting truncated sometimes in the shapefile.

Fixes for geometry.MapToPixel and geometry.PixelToMap as per as per http://lists.osgeo.org/pipermail/gdal-dev/2010-June/024956.html.

spot\_dimap driver was failing with an xml parse error as the closing tag '

Unknown end tag for </Dimap\_Document>

' was sometimes appended twice.

Added more "known" extensions for envi binary raster filename ['bil','bip','bsq','envi','dat','raw'].

Only attempt to open a file with the default driver, if that filename matches the default regex.