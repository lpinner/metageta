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
Metadata driver for "scene01/*.tif" GA imagery

B{Format specification}:
    - U{http://www.ga.gov.au}

B{General info}:
    - U{http://www.ga.gov.au/earth-observation.html}
'''

format_regex=[r'scene01(\\|/).*\.tif$']
'''Regular expression list of file formats'''

#import base dataset module
import __default__

# import other modules
import sys, os, re, glob, time, math, string
from metageta import utilities, geometry, spatialreferences
import alos,landsat_mtl

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

class Dataset(__default__.Dataset):
    '''Subclass of base Dataset class'''
    def __init__(self,f):
        if not f:f=self.fileinfo['filepath']
        if f[:4]=='/vsi':raise NotImplementedError
        d=os.path.dirname(f)
        self.filelist=glob.glob(os.path.join(d,'*'))

        #exclude stuff handled by specialist drivers
        fr='|'.join(alos.format_regex+landsat_mtl.format_regex)
        rx=re.compile(fr, re.IGNORECASE)
        for fi in self.filelist:
            if rx.search(f):raise NotImplementedError

    def __getmetadata__(self):
        '''Read Metadata for a "scene01/*.tif" (possibly) multiband image'''

        f=self.fileinfo['filepath']
        d=os.path.dirname(f)
        bands=sorted([t for t in self.filelist if t[-4:].lower()=='.tif'])
        ds=geometry.OpenDataset(f)
        
        vrt = geometry.CreateSimpleVRT(bands,ds.RasterXSize,ds.RasterYSize,
                                       gdal.GetDataTypeName(ds.GetRasterBand(1).DataType),
                                       relativeToVRT=0)
        vrtds=geometry.OpenDataset(vrt,gdalconst.GA_Update)
        vrtds.SetGeoTransform(ds.GetGeoTransform())
        vrtds.SetProjection(ds.GetProjection())
        vrtds.SetGCPs(ds.GetGCPs(),ds.GetProjection())
        vrtds.SetMetadata(ds.GetMetadata())

        #Kludge... the drivers are designed to "open" strings, i.e. filenames and vrt xml
        #(maybe look at allowing GdalDataset objects in future) 
        vrtds=geometry.CreateVRTCopy(vrtds) #This updates the Description property to include all the
        vrtxml= vrtds.GetDescription()      #SRS/GCP/GT info we just added.
                                            #GetDescription() is the only way I know of to get at the
                                            #underlying XML string.
        
        #Autopopulate metadata
        __default__.Dataset.__getmetadata__(self, vrtxml)
        self.metadata['filetype'] = 'GTiff/GeoTIFF'
