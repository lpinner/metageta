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
Metadata driver for NITF imagery

B{Format specification}:
    - U{http://www.gwg.nga.mil/ntb/baseline/documents.html}

@todo:GDAL upscales non standard bit depths. e.g 11 bit data is treated as 16 bit.
Currently the NITF driver reports the upscaled bit depth.
The actual bit depth can be extracted using the  NITF_ABPP metadata item.
Should this be reported instead of the upscaled bit depth...?

@todo:support NITF with subdatasets
'''

format_regex=[r'.*\.ntf$'] #NITF
'''Regular expression list of file formats'''

#import base dataset modules
import __default__

# import other modules
import sys, os, glob,time
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
    def __init__(self,f):
        if f[:4]=='/vsi':raise NotImplementedError
        if glob.glob(os.path.splitext(f)[0]+'.[iI][mM][dD]'): #if an imd file exists
            raise NotImplementedError #Let the Digitalglobe driver handle it, this error gets ignored in __init__.Open()
    def __getmetadata__(self):
        '''Read Metadata for a NITF image'''
        f=self.fileinfo['filepath']
        __default__.Dataset.__getmetadata__(self, f) #autopopulate basic metadata
        gdalmd=self._gdaldataset.GetMetadata()
        self.metadata['title']=gdalmd.get('NITF_FTITLE','')
        if 'NITF_STDIDC_ACQUISITION_DATE' in gdalmd:self.metadata['imgdate']=time.strftime('%Y-%m-%d',time.strptime(gdalmd.get('NITF_STDIDC_ACQUISITION_DATE','')[0:8],'%Y%m%d')) #ISO 8601 
        if 'NITF_USE00A_SUN_EL' in gdalmd:self.metadata['sunelevation']=float(gdalmd['NITF_USE00A_SUN_EL'])
        if 'NITF_USE00A_SUN_AZ' in gdalmd:self.metadata['sunazimuth']=float(gdalmd['NITF_USE00A_SUN_AZ'])
        self.metadata['satellite']=gdalmd.get('NITF_STDIDC_MISSION','')
        self.metadata['sensor']=gdalmd.get('NITF_IREP','')
        self.metadata['sceneid'] = gdalmd.get('NITF_IID1','')
        self.metadata['viewangle'] = gdalmd.get('NITF_USE00A_OBL_ANG','')
