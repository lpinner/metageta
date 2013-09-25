# -*- coding: utf-8 -*-
# Copyright (c) 2013 Australian Government, Department of the Environment
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

'''
Default Dataset class
=====================
Metadata driver for generic imagery formats including GDAL Virtual Rasters (VRT files and xml strings)
'''

format_regex=[
    r'\.nc$',
    r'\.vrt$',
    r'\.jpg$',
    r'\.png$',
    r'\.ers$',
    r'\.img$',
    r'\.tiff$',
    r'\.tif$',        #Completely untested with following formats...
    r'.*\.asc$',      #Arc/Info ASCII Grid
    r'.*\.bag$',      #Bathymetry Attributed Grid
    r'.*\.kap$',      #BSB Nautical Chart Format
    r'.*\.bt$',       #VTP Binary Terrain Format
    r'.*\.doq$',      #First Generation/New Labelled USGS DOQ
    r'.*\.n1$',       #Envisat Image Product
    r'.*\.fits$',     #FITS
    r'.*\.grb$',      #WMO GRIB1/GRIB2
    r'.*\.mem$',      #Japanese DEM (.mem)
    r'.*\.nat$',      #EUMETSAT Archive native
    r'.*\.rik$',      #Swedish Grid RIK
    r'a\.toc$',       #Raster Product Format/RPF
    r'product\.xml$', #RadarSat2 XML
    r'.*CATD\.DDF$',  #USGS SDTS DEM
    r'.*\.ter$',      #Terragen Heightfield
    r'.*\.dem$',      #USGS ASCII DEM
    r'.*\.xpm$',      #X11 Pixmap
    r'.*\.gen$|.*\.thf$', #ADRG/ARC Digitilized Raster Graphics
    r'.*\.blx$|.*\.xlb$', #Magellan BLX Topo
    r'.*\.mpr$|.*\.mpl$', #ILWIS Raster Map
    r'.*\.LAN$|.*\.GIS$', #Erdas 7.x .LAN and .GIS
    r'.*\.ppm$|.*\.pgm$', #Netpbm
    r'.*\.rsw$|.*\.mtw$',#Raster Matrix Format
    r'.*\.dt0$|.*\.dt1$|.*\.dt2$', #Military Elevation Data
    r'.*\.grc$|.*\.grd$|.*\.tab$'  #Northwood/VerticalMapper Classified/Numeric Grid Format
]
'''Regular expression list of file formats'''

import sys, os, re, glob, time, math, string
from metageta import utilities
from metageta import geometry
from metageta import spatialreferences
import __dataset__

import warnings,logging
warnings.formatwarning=lambda *args:str(args[0])+'\n'

try:
    from osgeo import gdal
    from osgeo import gdalconst
    from osgeo import osr
    from osgeo import ogr
except ImportError:
    import gdal
    import gdalconst
    import osr
    import ogr
gdal.AllRegister()

class Dataset(__dataset__.Dataset):
    '''Default Dataset class.
    For generic imagery formats that gdal can read.'''
    def __init__(self,f):
        pass
    def __getmetadata__(self,f=None):
        '''
        Generate metadata for generic imagery

        @type  f: string
        @param f: a filepath to the dataset or a VRT XML string
        @return:  None

        @todo: We force a NoData value. This is not ideal, but it makes for better overview images.
        '''
        if not f:f=self.fileinfo['filepath']
        try:
            cwd=os.path.abspath(os.curdir)
            if os.path.exists(f) and os.path.dirname(f):
                p=os.path.split(f)[0]
                os.chdir(p)
            if not self._gdaldataset:self._gdaldataset= geometry.OpenDataset(f) #in case we're subclassed and there's already a dataset open
            if self._gdaldataset:
                driver=self._gdaldataset.GetDriver().ShortName
                if driver[0:3]=='HDF':raise NotImplementedError, 'HDF files are not yet implemented except by custom formats'
                self.metadata['filetype'] = driver+'/'+self._gdaldataset.GetDriver().LongName
                self.metadata['cols'] = self._gdaldataset.RasterXSize
                self.metadata['rows'] = self._gdaldataset.RasterYSize
                self.metadata['nbands'] = self._gdaldataset.RasterCount

                self.metadata['srs']= self._gdaldataset.GetProjection()
                if not self.metadata['srs'] and self._gdaldataset.GetGCPCount() > 0:
                    self.metadata['srs'] = self._gdaldataset.GetGCPProjection()
                self.metadata['epsg'] = spatialreferences.IdentifyAusEPSG(self.metadata['srs'])
                self.metadata['units'] = spatialreferences.GetLinearUnitsName(self.metadata['srs'])

                geotransform = self._gdaldataset.GetGeoTransform()
                if geotransform == (0, 1, 0, 0, 0, 1):
                    if self._gdaldataset.GetGCPCount() > 0:
                        gcps=self._gdaldataset.GetGCPs()
                        geotransform=gdal.GCPsToGeoTransform(gcps)
                        gcps=geometry.GeoTransformToGCPs(geotransform,self.metadata['cols'],self.metadata['rows']) #Just get the 4 corner GCP's
                    else:
                        raise NotImplementedError, 'Dataset is not georeferenced'
                else:
                    gcps=geometry.GeoTransformToGCPs(geotransform,self.metadata['cols'],self.metadata['rows'])

                ext=[[gcp.GCPX, gcp.GCPY] for gcp in gcps]
                ext.append([gcps[0].GCPX, gcps[0].GCPY])#Add the 1st point to close the polygon)

                #Reproject corners to lon,lat
                geom = geometry.GeomFromExtent(ext)
                src_srs=osr.SpatialReference()
                src_srs.ImportFromWkt(self.metadata['srs'])
                tgt_srs=osr.SpatialReference()
                tgt_srs.ImportFromEPSG(4326)
                geom=geometry.ReprojectGeom(geom,src_srs,tgt_srs)
                points=geom.GetGeometryRef(0) #geom.GetBoundary()
                ext=[[points.GetX(i),points.GetY(i)] for i in range(0,points.GetPointCount())]

                self.metadata['cellx'],self.metadata['celly']=geometry.CellSize(geotransform)
                self.metadata['rotation']=geometry.Rotation(geotransform)
                if abs(self.metadata['rotation']) < 1.0:
                    self.metadata['orientation']='Map oriented'
                    self.metadata['rotation']=0.0
                else: self.metadata['orientation']='Path oriented'
                self.metadata['UL']='%s,%s' % tuple(ext[0])
                self.metadata['LL']='%s,%s' % tuple(ext[1])
                self.metadata['LR']='%s,%s' % tuple(ext[2])
                self.metadata['UR']='%s,%s' % tuple(ext[3])

                rb=self._gdaldataset.GetRasterBand(1)
                if rb:
                    self.metadata['datatype']=gdal.GetDataTypeName(rb.DataType)
                    self.metadata['nbits']=gdal.GetDataTypeSize(rb.DataType)
                    nodata=rb.GetNoDataValue()
                    if nodata is not None:self.metadata['nodata']=str(nodata)
                    else:
                        ct = rb.GetColorTable() #Fix for Issue 31
                        if ct is None:
                            if self.metadata['datatype'][0:4] in ['Byte','UInt']: nodata=0 #Unsigned, assume 0
                            else:nodata=-2**(self.metadata['nbits']-1)                     #Signed, assume min value in data range
                            self.metadata['nodata']=str(nodata)
                            #Fix for Issue 17
                            for i in range(1,self._gdaldataset.RasterCount+1):
                                self._gdaldataset.GetRasterBand(i).SetNoDataValue(nodata)
                else:raise IOError,'No valid rasterbands found.'

                metadata=self._gdaldataset.GetMetadata()
                self.metadata['metadata']='\n'.join(['%s: %s' %(m,metadata[m]) for m in metadata])
                self.metadata['filesize']=sum([os.path.getsize(tmp) for tmp in self.filelist])
                if self.metadata['filesize']>0:self.metadata['compressionratio']=int((self.metadata['nbands']*self.metadata['cols']*self.metadata['rows']*(self.metadata['nbits']/8.0))/self.metadata['filesize'])
                if self.metadata['compressionratio'] > 0:
                    try:
                        if driver[0:3]=='JP2':
                            self.metadata['compressiontype']="JPEG2000"
                        elif driver[0:3]=='ECW':
                            self.metadata['compressiontype']="ECW"
                        else:
                            mdis=self._gdaldataset.GetMetadata('IMAGE_STRUCTURE')
                            #self.metadata['compressiontype']=mdis['IMAGE_STRUCTURE']
                            self.metadata['compressiontype']=mdis['COMPRESSION']
                    except: self.metadata['compressiontype']='Unknown'
                else: self.metadata['compressiontype']='None'
                self.extent=ext
            else:
                errmsg=gdal.GetLastErrorMsg()
                raise IOError, 'Unable to open %s\n%s' % (f,errmsg.strip())

        finally: #Cleanup
            gdal.ErrorReset()
            os.chdir(cwd)

