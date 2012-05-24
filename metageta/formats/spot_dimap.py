# -*- coding: utf-8 -*-
# Copyright (c) 2011 Australian Government, Department of Sustainability, Environment, Water, Population and Communities
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
Metadata driver for SPOT DIMAP imagery

B{Format specification}:
    - U{http://www.spotimage.fr/dimap/spec/documentation/refdoc.htm}

@todo: GDALINFO is pretty slow (4+ sec), check that this driver is not that slow...
'''

format_regex=[r'metadata\.dim$'] #SPOT DIMAP
'''Regular expression list of file formats'''

#import base dataset modules
#import __dataset__
import __default__

# import other modules
import sys, os, re, glob, time, math, string
from metageta import utilities, geometry
from lxml import etree

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
        '''Open the dataset'''
        if not f:f=self.fileinfo['filepath']
        self.filelist=[r for r in glob.glob('%s/*'%os.path.dirname(f))]
    def __getmetadata__(self,f=None):
        '''Read Metadata for a SPOT DIMAP image as GDAL doesn't quite get it all...'''
        if not f:f=self.fileinfo['filepath']
        #dom=etree.parse(f) #Takes tooo long to parse the whole file, so just read as far as we need...
        strxml=''
        for line in open(f, 'r'):
            if line.upper().strip()=='<DATA_STRIP>':break
            else: strxml+=line
        if not '</Dimap_Document>' in strxml:strxml+='</Dimap_Document>'
        dom=etree.fromstring(strxml)
        #self.metadata['sceneid'] = dom.documentElement.getElementsByTagName('DATASET_NAME')[0].childNodes[0].data
        #bands=dom.documentElement.getElementsByTagName('BAND_DESCRIPTION')
        #self.metadata['bands']=','.join([band.childNodes[0].data for band in bands])
        self.metadata['sceneid'] = dom.xpath('string(/Dimap_Document/Dataset_Id/DATASET_NAME)')
        bands=dom.xpath('/Dimap_Document/Spectral_Band_Info/BAND_DESCRIPTION')
        self.metadata['bands']=','.join([band.xpath('string(.)') for band in bands])

        try:__default__.Dataset.__getmetadata__(self, f) #autopopulate basic metadata
        except geometry.GDALError,err: #Work around reading images with lowercase filenames when
                                       #the DATA_FILE_PATH is uppercase
                                       # - eg samba filesystems which get converted to lowercase

            dfp=dom.xpath('/Dimap_Document/Data_Access/Data_File/DATA_FILE_PATH')[0]
            fn=utilities.encode(dfp.xpath('string(@href)')) #XML is unicode, gdal.Open doesn't like unicode
            if not os.path.dirname(fn):fn=os.path.join(os.path.dirname(f),fn)
            exists,img=utilities.exists(fn,True)
            if exists and not os.path.exists(fn):
                import tempfile
                tmpfd,tmpfn=tempfile.mkstemp(suffix='.dim',prefix='metadata')
                dfp.set('href',img)
                tmpfo=os.fdopen(tmpfd,'w')
                tmpfo.write(etree.tostring(dom))
                tmpfo.flush()
                tmpfo.close()
                cwd=os.path.abspath(os.curdir)
                tmp=os.path.split(tmpfn)
                os.chdir(tmp[0]) #CD to the tmp dir so __default__.Dataset.__getmetadata__ doesn't
                __default__.Dataset.__getmetadata__(self, tmp[1])
                gdalmd=self._gdaldataset.GetMetadata()
                self._gdaldataset=geometry.OpenDataset(img)
                self._gdaldataset.SetMetadata(gdalmd)
                os.unlink(tmpfn)
                os.chdir(cwd)
            else:raise
        dates={}
        for src in dom.xpath('//Scene_Source'):
            datetime='%sT%s'%(src.xpath('string(IMAGING_DATE)'),src.xpath('string(IMAGING_TIME)'))
            dts=time.mktime(time.strptime(datetime,utilities.datetimeformat))#ISO 8601
            dates[dts]=datetime

        self.metadata['imgdate']='%s/%s'%(dates[min(dates.keys())],dates[max(dates.keys())])

        gdalmd=self._gdaldataset.GetMetadata()
        self.metadata['satellite']='%s %s' % (gdalmd['MISSION'],gdalmd['MISSION_INDEX'])
        self.metadata['sensor']='%s %s' % (gdalmd['INSTRUMENT'],gdalmd['INSTRUMENT_INDEX'])
        try:self.metadata['sunelevation'] = float(gdalmd['SUN_ELEVATION'])
        except:pass
        try:self.metadata['sunazimuth'] = float(gdalmd['SUN_AZIMUTH'])
        except:pass
        try:self.metadata['level'] = gdalmd['PROCESSING_LEVEL']
        except:pass
        self.metadata['viewangle'] = gdalmd.get('VIEWING_ANGLE',gdalmd.get('INCIDENCE_ANGLE',''))

    def getoverview(self,outfile=None,width=800,format='JPG'):
        '''
        Generate overviews for SPOT imagery

        @type  outfile: str
        @param outfile: a filepath to the output overview image. If supplied, format is determined from the file extension
        @type  width:   int
        @param width:   image width
        @type  format:  str
        @param format:  format to generate overview image, one of ['JPG','PNG','GIF','BMP','TIF']. Not required if outfile is supplied.
        @rtype:         str
        @return:        filepath (if outfile is supplied)/binary image data (if outfile is not supplied)
        '''
        from metageta import overviews

        #First check for a browse graphic, no point re-inventing the wheel...
        f=self.fileinfo['filepath']
        browse=os.path.join(os.path.dirname(f),'PREVIEW.JPG')
        if os.path.exists(browse):

            try:return overviews.resize(browse,outfile,width)
            except:return __default__.Dataset.getoverview(self,outfile,width,format) #Try it the slow way...

        else: return __default__.Dataset.getoverview(self,outfile,width,format)#Do it the slow way...
