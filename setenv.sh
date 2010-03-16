#!/bin/bash
export CURDIR=$(cd "$(dirname "$0")"; pwd)
#export GDAL_DATA=$CURDIR/../gdal_data
export GDAL_DATA=/usr/share/gdal16
export GEOTIFF_CSV=$GDAL_DATA
export PYTHONPATH=$CURDIR/lib:$PYTHONPATH

