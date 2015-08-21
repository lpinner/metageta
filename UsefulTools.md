# Introduction #

This page contains a few useful related tools that are not really part of MetaGETA.


# Details #

## [Batch Upload MEF](http://code.google.com/p/metageta/source/browse/tools/batchuploadmef.py) ##
This script can be used to batch upload MEF (Metadata Exchange Format) files to GeoNetwork. It works around some of the [issues](http://trac.osgeo.org/geonetwork/ticket/169) in the GAST (import actions and error handling) and Web interface (local files only) batch upload functions. It requires the poster library - http://atlee.ca/software/poster (not included here). For users not experienced in installing python modules: 1. download and unzip the tar.gz. and 2. copy/move the poster folder (not the poster-0.8.x folder)to your python installation directory - C:\PythonX\Lib\site\_packages or the directory from which you run the batchuploadmef.py script.  See also other [methods](http://docs.python.org/install/index.html#the-new-standard-distutils).

## [GeoNetwork Windows Service](http://code.google.com/p/metageta/source/browse/tools/geonetwork-service) ##
This script can be used to set up GeoNetwork as a Windows Service while still using the default Jetty servlet engine, rather than running under a Tomcat service.  It does not use the Windows Resource Kit "srvany.exe" as that doesn't gracefully shutdown GeoNetwork when stopping the service.  It requires Python 2.5-2.7 and PyWin32.