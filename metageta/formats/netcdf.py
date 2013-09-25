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
Metadata driver for NetCDF imagery

B{Format specification}:
    - U{http://www.unidata.ucar.edu/software/netcdf}
'''

format_regex=[r'.*\.nc$'] #NITF
'''Regular expression list of file formats'''

#import base dataset modules
import __default__

# import other modules
import sys, os, glob
from metageta import utilities, geometry

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
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __getmetadata__(self):
        '''Read Metadata for a NetCDF image (1st subdataset)'''
        f=self.fileinfo['filepath']
        if f[:4]=='/vsi':raise NotImplementedError

        nc=geometry.OpenDataset(f)
        ncmd=nc.GetMetadata()

        sds=nc.GetSubDatasets()
        if sds: #Use the SubDataset with the most cols*rows
            xy=[]
            sdo=[]
            for sd_name,sd_desc in sds:
                sd=geometry.OpenDataset(sd_name)
                xy.append(sd.RasterXSize * sd.RasterYSize)
                sdo.append([sd,sd_name,sd_desc])

            sd,sd_name,sd_desc=sdo[xy.index(max(xy))]
            try:__default__.Dataset.__getmetadata__(self, sd_name) #autopopulate basic metadata
            except NotImplementedError:
                if map(int,geometry.gdal.__version__.split('.')) < [1,8,0]:
                    raise NotImplementedError('You are using GDAL %s, versions < 1.8 do not read georeferencing information for certain NetCDF files.'%geometry.gdal.__version__)
                else:raise
            sdmd=sd.GetMetadata()
        else:
            try:__default__.Dataset.__getmetadata__(self, f) #autopopulate basic metadata
            except NotImplementedError:
                if map(int,geometry.gdal.__version__.split('.')) < [1,8,0]:
                    raise NotImplementedError('You are using GDAL %s, versions < 1.8 do not read georeferencing information for certain NetCDF files.'%geometry.gdal.__version__)
                else:raise

            sdmd={}
            sd_name,sd_desc = ['','']

        source=sdmd.get('NC_GLOBAL#source',ncmd.get('NC_GLOBAL#source',''))
        if source:source='Source:'+source
        history=sdmd.get('NC_GLOBAL#history',ncmd.get('NC_GLOBAL#history',''))
        if history:history='History:n'+history
        self.metadata['lineage'] = '\n\n'.join([source,history]).strip()
        comment=sdmd.get('NC_GLOBAL#comment',ncmd.get('NC_GLOBAL#comment',''))
        references=sdmd.get('NC_GLOBAL#references',ncmd.get('NC_GLOBAL#references',''))
        if references:references='References:n'+references
        self.metadata['abstract'] = '\n\n'.join([comment,references]).strip()
        self.metadata['title'] = ncmd.get('NC_GLOBAL#title',sdmd.get('NC_GLOBAL#title',sd_desc))
        self.metadata['useConstraints'] = ncmd.get('NC_GLOBAL#acknowledgment',sdmd.get('NC_GLOBAL#acknowledgment',''))
        pass

    def getoverview(self,outfile=None,width=800,format='JPG'):
        '''Override the default method'''

        ##Fix for Issue 18 - loop thru the bands and find the first one with valid stats
        ##Some NetCDF subdataset bands GetStatistics == [0.0, 0.0, -1.#IND, -1.#IND]
        ##GDAL error is "Failed to compute statistics, no valid pixels found in
        ##sampling".
        ##Calling GetHistogram on such bands causes gdal to segfault.

        for b in range(1,self.metadata['nbands']+1):
            band=self._gdaldataset.GetRasterBand(b)
            dfBandMin,dfBandMax,dfBandMean,dfBandStdDev = band.GetStatistics(1,1)
            if dfBandMean==dfBandMean: #NB: -1.#IND != -1.#IND
                break
            b=0
        if b==0:raise geometry.GDALError,'Unable to generate overview.'
        self._stretch=['PERCENT',[b], [2,98]]
        return __default__.Dataset.getoverview(self,outfile,width,format)

