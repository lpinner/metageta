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
Metadata driver for Landsat geotiff imagery

B{General info}:
    - U{http://www.ga.gov.au/remote-sensing/satellites-sensors/landsat}
'''

format_regex=[r'L.*\_MTL\.txt$']#  - Standard file names
'''Regular expression list of file formats'''

#import base dataset module
import __default__

# import other modules (use "_"  prefix to import privately)
import sys, os, re, glob, time, math, string
from metageta import utilities, geometry, spatialreferences

try:
    from collections import OrderedDict
except:
    from metageta.ordereddict import OrderedDict

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
        self.filelist = glob.glob(os.path.dirname(f)+'/*')
    def __getmetadata__(self):
        '''Read Metadata for a Landsat Geotiff with Level 1 Metadata format image as GDAL doesn't get it all.'''
        f=self.fileinfo['filepath']
        d=os.path.dirname(f)
        hdr=parseheader(f)

        if hdr['L1_METADATA_FILE'].get('LANDSAT_SCENE_ID'):self.__getnewmetadata__(f,d,hdr)
        else:self.__getoldmetadata__(f,d,hdr)

        md=self.metadata
        vrtxml=geometry.CreateSimpleVRT(self.bandfiles,md['cols'],md['rows'], md['datatype'])
        self._gdaldataset = geometry.OpenDataset(vrtxml)
        for i in range(self._gdaldataset.RasterCount):
            self._gdaldataset.GetRasterBand(i+1).SetNoDataValue(0)

        #Fix quicklook stretch for Landsat 8 data
        if md['satellite']=='LANDSAT_8':
            self._stretch=['PERCENT',[4,3,2],[1,99]]
        else:
            self._stretch=['PERCENT',[3,2,1], [2,98]]

    def __getnewmetadata__(self,f,d,hdr):
        '''Read Metadata for a Landsat Geotiff with new (>2012) Level 1 Metadata.'''

        #bands=[''.join(fnb.split('_')[3:]).replace('VCID','') for fnb in sorted(hdr['PRODUCT_METADATA'].keys()) if fnb.startswith('FILE_NAME_BAND')]
        #self.bandfiles=[os.path.join(d,hdr['PRODUCT_METADATA'][fnb]) for fnb in sorted(hdr['PRODUCT_METADATA'].keys()) if fnb.startswith('FILE_NAME_BAND')]
        bands=[''.join(fnb.split('_')[3:]).replace('VCID','') for fnb in hdr['PRODUCT_METADATA'].keys() if fnb.startswith('FILE_NAME_BAND')]
        self.bandfiles=[os.path.join(d,hdr['PRODUCT_METADATA'][fnb]) for fnb in hdr['PRODUCT_METADATA'].keys() if fnb.startswith('FILE_NAME_BAND')]

        __default__.Dataset.__getmetadata__(self, self.bandfiles[0])

        md=self.metadata
        md['metadata']=open(f).read().replace('\x00','')
        md['sceneid']=hdr['L1_METADATA_FILE']['LANDSAT_SCENE_ID']
        md['filetype'] = 'GTIFF/Landsat MTL Geotiff'

        md['bands']=','.join(bands)
        md['nbands']=len(bands)
        md['level']=hdr['PRODUCT_METADATA']['DATA_TYPE']
        md['imgdate']='%sT%s'%(hdr['PRODUCT_METADATA']['DATE_ACQUIRED'],hdr['PRODUCT_METADATA']['SCENE_CENTER_TIME'][0:8]) #ISO 8601 format, strip off the milliseconds
        md['satellite']=hdr['PRODUCT_METADATA']['SPACECRAFT_ID']
        md['sensor']=hdr['PRODUCT_METADATA']['SENSOR_ID']
        md['demcorrection']=hdr['PRODUCT_METADATA'].get('ELEVATION_SOURCE','') #Level 1G isn't terrain corrected
        md['resampling']=hdr['PROJECTION_PARAMETERS']['RESAMPLING_OPTION']
        md['sunazimuth']=hdr['IMAGE_ATTRIBUTES']['SUN_AZIMUTH']
        md['sunelevation']=hdr['IMAGE_ATTRIBUTES']['SUN_ELEVATION']
        md['cloudcover']=hdr['IMAGE_ATTRIBUTES']['CLOUD_COVER']

    def __getoldmetadata__(self,f,d,hdr):
        '''Read Metadata for a Landsat Geotiff with ol (pre 2012) Level 1 Metadata.'''

        bands=sorted([i for i in hdr['PRODUCT_METADATA']['BAND_COMBINATION']])
        if hdr['PRODUCT_METADATA']['SENSOR_ID']=='ETM+': #Landsat 7 has 2 data files for thermal band 6
            #Format=123456678
            bands[5]=bands[5].replace('6','61')
            bands[6]=bands[6].replace('6','62')

        self.bandfiles=[os.path.join(d,hdr['PRODUCT_METADATA']['BAND%s_FILE_NAME'%b]) for b in bands]

        __default__.Dataset.__getmetadata__(self, self.bandfiles[0])

        md=self.metadata
        md['metadata']=open(f).read().replace('\x00','')
        md['sceneid']=os.path.basename(d)
        md['filetype'] = 'GTIFF/Landsat MTL Geotiff'

        md['bands']=','.join(bands)
        md['nbands']=len(bands)
        md['level']=hdr['PRODUCT_METADATA']['PRODUCT_TYPE']
        md['imgdate']='%sT%s'%(hdr['PRODUCT_METADATA']['ACQUISITION_DATE'],hdr['PRODUCT_METADATA']['SCENE_CENTER_SCAN_TIME'][0:8]) #ISO 8601 format, strip off the milliseconds
        md['satellite']=hdr['PRODUCT_METADATA']['SPACECRAFT_ID']
        md['sensor']=hdr['PRODUCT_METADATA']['SENSOR_ID']
        md['demcorrection']=hdr['PRODUCT_METADATA'].get('ELEVATION_SOURCE','') #Level 1G isn't terrain corrected
        md['resampling']=hdr['PROJECTION_PARAMETERS']['RESAMPLING_OPTION']
        md['sunazimuth']=hdr['PRODUCT_PARAMETERS']['SUN_AZIMUTH']
        md['sunelevation']=hdr['PRODUCT_PARAMETERS']['SUN_ELEVATION']

def parseheader(f):
    ''' A simple header parser.

        @type    f: C{str}
        @param   f: Path to header file
        @rtype:   C{dict}
        @return:  Dictionary

        @todo:This function works for both landsat MTL and Digitalglobe IMD metadata
              files. Need to fix duplication - digitalglobe driver will need tweaking
              as it's version of the parser extracts band information.
    '''
    lines=iter(open(f).readlines())

    hdrdata=OrderedDict({})
    line=lines.next()
    while line:
        line=[item.strip() for item in line.replace('"','').split('=')]
        group=line[0].upper()
        if group in ['END;','END']:break
        value=line[1]
        if group in ['END_GROUP']:pass
        elif group in ['BEGIN_GROUP','GROUP']:
            group=value
            subdata=OrderedDict({})
            while line:
                line=lines.next()
                line = [l.replace('"','').strip() for l in line.split('=')]
                subgroup=line[0]
                subvalue=line[1]
                if subgroup == 'END_GROUP':
                    break
                elif line[1] == '(':
                    while line:
                        line=lines.next()
                        line = line.replace('"','').strip()
                        subvalue+=line
                        if line[-1:]==';':
                            subvalue=eval(subvalue.strip(';'))
                            break
                else:subvalue=subvalue.strip(';')
                subdata[subgroup]=subvalue
            hdrdata[group]=subdata
        else: hdrdata[group]=value.strip(');')
        line=lines.next()
    return hdrdata


