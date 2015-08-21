# MetaGETA (Metadata Gathering, Extraction and Transformation Application) #
Search for, extract and transform metadata from spatial imagery data.

## Introduction ##
MetaGETA is a python application for discovering and extracting metadata from spatial raster datasets (metadata crawler) and transforming it into xml (metadata transformation). A number of generic and specialised imagery formats are [supported](http://metageta.googlecode.com/svn/trunk/doc/files/metageta.formats-module.htmlformats-module.html#section-Submodules). The format support has a plugin architecture and more formats can easily be added.

## News ##
06 August 2013 - MetaGETA 1.3.9 has been released!
See the [Changelog](http://code.google.com/p/metageta/wiki/Changelog) for details.

## Features ##
  * Search for supported data [formats](http://metageta.googlecode.com/svn/trunk/doc/files/metageta.formats-module.html#section-Submodules) on your local or network file system
  * Automatically extract file and format specific metadata
  * Automatically populate an MS Excel file with the metadata
  * Automatically generate quicklooks and thumbnails for each metadata record
  * Manually supplement metadata records with additional metadata [fields](http://metageta.googlecode.com/svn/trunk/doc/files/metageta.transforms-module.html)
  * Transform the MS Excel file to [ANZLIC profile](http://www.anzlic.org.au/metadata/guidelines/Index.html) ISO19115/19139 xml as a bundled (includes quicklooks and thumbnails) [MEF](http://apps.who.int/geonetwork/docs/ch17.html) suitable for upload to [Geonetwork](http://geonetwork-opensource.org/).
    * Note: You can [write your own](http://metageta.googlecode.com/svn/trunk/doc/files/metageta.transforms-module.html) translation stylesheet to meet the requirements of your target profile
  * Subsequent metadata crawls may be used to update records when data is added to or removed from the file system
  * Enables flagging of records in MS Excel that should not be included in the transformed xml i.e. maintains a record of but does not create xml metadata for redundant or irrelevant datasets

## Links ##
  * [Downloads](http://code.google.com/p/metageta/downloads/list)
  * [Installation](Installation.md)
  * [Usage](Usage.md)
    * [Advanced usage (API Documentation)](http://metageta.googlecode.com/svn/trunk/doc/index.html)
  * [UsefulTools](UsefulTools.md)
    * [(Batch upload and Windows Service Tool for Geonetwork)](http://code.google.com/p/metageta/wiki/UsefulTools)