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
Metadata driver for Digital Globe imagery

B{Format specification}:
    - U{http://www.digitalglobe.com/downloads/Imagery_Support_Data_Documentation.pdf}
'''

format_regex=[r'[0-9][0-9][A-Z]{3,3}.*\.imd$']
'''Regular expression list of file formats'''

#import base dataset modules
import __dataset__
import __default__

# import other modules (use "_"  prefix to import privately)
import sys, os, re, glob, time, math, string, fnmatch
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
        dirname,basename=os.path.split(f)
        rootname,ext=os.path.splitext(basename)
        self.filelist=[f for f in utilities.rglob(dirname, pattern=rootname+".*", regex=True, regex_flags=re.I, recurse=False)]
        self.exts={'.tif':'GTiff/GeoTIFF',
              '.img':'HFA/Erdas Imagine Images (.img)',
              '.ntf':'NITF/National Imagery Transmission Format (.ntf)',
              '.pix':'PCI Geomatics Database File (.pix)'}
        self.img=False
        for ext in self.exts:
            imgs=[i for i in self.filelist if i[-4:] in [ext,ext.upper()]]
            if imgs:
                self.img=imgs[0]
                break

        if not self.img:raise NotImplementedError, 'Matching DigitalGlobe imagery file not found:\n'

    def __getmetadata__(self):
        '''Read Metadata for an SKM modified Digital Globe format image as GDAL doesn't quite get it all...'''
        f=self.fileinfo['filepath']
        imddata=self.__getimddata__(f)
        __default__.Dataset.__getmetadata__(self, self.img)

        self.metadata['metadata']=open(f).read()

        if imddata.has_key('IMAGE_1'):imgkey='IMAGE_1'
        else:imgkey='SINGLE_IMAGE_PRODUCT'
        if imddata.has_key('MAP_PROJECTED_PRODUCT'):
            imgdate1=imddata['MAP_PROJECTED_PRODUCT']['earliestAcqTime'][0:19]#Already in ISO 8601 format, just strip off millisecs
            imgdate2=imddata['MAP_PROJECTED_PRODUCT']['latestAcqTime'][0:19]
            if imgdate1==imgdate2:self.metadata['imgdate']='%s'%(imgdate1)
            else:self.metadata['imgdate']='%s/%s'%(imgdate1,imgdate2)
        elif imddata[imgkey].has_key('firstLineTime'):
            self.metadata['imgdate']=imddata[imgkey]['firstLineTime'][0:19] #Already in ISO 8601 format, just strip off millisecs
        if imddata[imgkey]['satId']=='QB02':
            self.metadata['satellite']='Quickbird (QB02)'
        elif imddata[imgkey]['satId']=='WV01':
            self.metadata['satellite']='Worldview-1 (WV01)'
        elif imddata[imgkey]['satId']=='WV02':
            self.metadata['satellite']='Worldview-2 (WV02)'
        else:
            self.metadata['satellite']=imddata[imgkey]['satId']
        if imddata['bandId'] == 'P':self.metadata['sensor']='PANCHROMATIC'
        else:
            if imddata['panSharpenAlgorithm']== 'None':self.metadata['sensor']='MULTISPECTRAL'
            else:self.metadata['sensor']='MULTI/PAN'
        #if imddata['bandId']=='Multi':
        #    if imddata['nbands'] == 3:self.metadata['bands'] = 'B,G,R'
        #    elif imddata['nbands'] == 4:self.metadata['bands'] = 'B,G,R,N'
        #else: #'BGRN','RGB','P'
        #    self.metadata['bands'] = ','.join([l for l in imddata['bandId']])
        self.metadata['bands'] = ','.join([b.split('_')[1] for b in imddata.keys() if b[0:5]=='BAND_'])
        if imddata[imgkey].has_key('meanSatEl'):
            self.metadata['satelevation'] = imddata[imgkey]['meanSatEl']
            self.metadata['satazimuth'] = imddata[imgkey]['meanSatAz']
        elif imddata[imgkey].has_key('satEl'):
            self.metadata['satelevation'] = imddata[imgkey]['satEl']
            self.metadata['satazimuth'] = imddata[imgkey]['satAz']
        if imddata[imgkey].has_key('meanSunEl'):
            self.metadata['sunelevation'] = imddata[imgkey]['meanSunEl']
            self.metadata['sunazimuth'] = imddata[imgkey]['meanSunAz']
        elif imddata[imgkey].has_key('sunEl'):
            self.metadata['sunelevation'] = imddata[imgkey]['sunEl']
            self.metadata['sunazimuth'] = imddata[imgkey]['sunAz']
        self.metadata['level'] = imddata['productLevel']
        if imddata[imgkey].has_key('cloudCover'):
            self.metadata['cloudcover'] = imddata[imgkey]['cloudCover']
        elif imddata[imgkey].has_key('manualCloudCover'):
            self.metadata['cloudcover'] = max([0, imddata[imgkey]['manualCloudCover']]) #hack for -999 cloud cover
        elif imddata[imgkey].has_key('autoCloudCover'):
            self.metadata['cloudcover'] = max([0, imddata[imgkey]['autoCloudCover']])
        if imddata[imgkey].has_key('offNadirViewAngle'):
            self.metadata['viewangle'] = imddata[imgkey]['offNadirViewAngle']
        elif imddata[imgkey].has_key('meanOffNadirViewAngle'):
            self.metadata['viewangle'] = imddata[imgkey]['meanOffNadirViewAngle']
        if imddata[imgkey].has_key('CatId'):
            self.metadata['sceneid'] = imddata[imgkey]['CatId']
        if imddata[imgkey].has_key('resamplingKernel'):
            self.metadata['resampling'] = imddata[imgkey]['resamplingKernel']
        elif imddata.has_key('MAP_PROJECTED_PRODUCT') and imddata['MAP_PROJECTED_PRODUCT'].has_key('resamplingKernel'):
            self.metadata['resampling'] = imddata['MAP_PROJECTED_PRODUCT']['resamplingKernel']
        if imddata.has_key('MAP_PROJECTED_PRODUCT') and imddata['MAP_PROJECTED_PRODUCT'].has_key('DEMCorrection'):
            self.metadata['demcorrection'] = imddata['MAP_PROJECTED_PRODUCT']['DEMCorrection']
        #self.extent is set in __default__.Dataset.__getmetadata__()

    def __getimddata__(self,f):
        #Loop thru and parse the IMD file.
        #would be easier to walk the nodes in the XML files, but not all of our QB imagery has this
        #perhaps someone deleted them...?
        lines=iter(open(f).readlines())
        imddata={}
        bands=[]
        line=lines.next()
        while line:
            line=[item.strip() for item in line.replace('"','').split('=')]
            #line = map(string.strip, lines[i].split('='))
            group=line[0]
            if group == 'END;':break
            value=line[1]
            if group == 'BEGIN_GROUP':
                group=value
                subdata={}
                if 'BAND_' in group:bands.append(group)
                while line:
                    line=lines.next()
                    line = [l.replace('"','').strip() for l in line.split('=')]
                    subgroup=line[0]
                    subvalue=line[1]
                    if subgroup == 'END_GROUP':break
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
                imddata[group]=subdata
            else: imddata[group]=value.strip(');')
            line=lines.next()
        imddata['bands']=bands
        imddata['nbands']=len(bands)
        return imddata
