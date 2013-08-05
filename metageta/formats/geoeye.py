# -*- coding: utf-8 -*-
# Copyright (c) 2013 Australian Government, Department of Sustainability, Environment, Water, Population and Communities
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
Metadata driver for Ikonos and GeoEye (1) imagery

B{Format specification}: Not Available.
'''

format_regex=[r'^.*_metadata\.txt$']
'''Regular expression list of file formats'''

#import base dataset modules
import __dataset__
import __default__

# import other modules (use "_"  prefix to import privately)
import sys, os, re, glob, time, math, string, fnmatch
from metageta import utilities,geometry

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
        self.mdtxt=open(f).read()
        if 'Source Image Metadata' not in self.mdtxt:raise NotImplementedError

        self.filelist=glob.glob(os.path.join(os.path.dirname(f),'*'))

    def __getmetadata__(self):
        '''Read Metadata for a GeoEye format image (IKONOS, GeoEye-1)

        '''
        md=self.__parsemetadata__()
        ds,nbands,bandnames,f=self.__opendataset__()
        __default__.Dataset.__getmetadata__(self, f) #autopopulate basic metadata

        for m in md:self.metadata[m]=md[m]
        self._gdaldataset=ds
        self.metadata['nbands']=nbands
        self.metadata['bands']=bandnames
        self.metadata['filelist']=self.filelist

    def __parsemetadata__(self):
        md={}
        md['metadata']=self.mdtxt
        f=self.fileinfo['filepath']

        #The GeoEye metadata file can contain info for more than one scene if there are
        #multiple scenes in a product. Each scene is in it's own directory but the
        #metadata file in that directory will be identical to that in any other
        #scene directories in theproduct.
        #  i.e:
        #  +---somedirectory
        #    |   \---123456                  <---Product directory
        #    |       +---po_123456_0000000   <--- Scene ("component") directory (Doesn't always match this pattern...)
        #    |       +---po_123456_0010000   <--- Scene ("component") directory
        #    |       \---po_123456_0020000   <--- Scene ("component") directory

        for fl in self.filelist:
            while os.path.basename(fl)!=os.path.splitext(os.path.basename(fl))[0]:
                fl=os.path.splitext(os.path.basename(fl))[0]

            if fnmatch.fnmatch(fl,'po_[0-9]*_*_[0-9]*'):
                component=fl.split('_') #i.e. ['po','123456',pan,'0020000']
                break
        component_id=component[3]         #i.e. 0020000
        #image_id=component_id.rstrip('0') #i.e. 002
        image_id=component_id[:3]
        if not image_id:image_id='000'
        image_start = self.mdtxt.find(r'Product Image ID: %s'%image_id)
        component_start = self.mdtxt.find(r'Component ID: %s'%component_id,image_start)

        try:
            mat=re.search(r'^\s*License Type:\s*(?P<license>.+$)',self.mdtxt, re.I+re.M)
            md['license']=mat.groupdict()['license']
            mat=re.search(r'^\s*License Option\s*[0-9]*:\s*(?P<md>.+$)',self.mdtxt, re.I+re.M)
            md['license']+='\n'+mat.groupdict()['md']
        except:pass
        try:
            mat=re.search(r'^\s*Sensor Name:\s*(?P<md>.+$)',self.mdtxt, re.I+re.M)
            md['satellite']=mat.groupdict()['md']
        except:pass
        try:
            mat=re.search(r'^\s*Sensor:\s*(?P<md>.+$)',self.mdtxt, re.I+re.M)
            md['satellite']=mat.groupdict()['md']
        except:pass
        try:
            mat=re.search(r'^\s*Image Type:\s*(?P<md>.+$)',self.mdtxt, re.I+re.M)
            md['sensor']=mat.groupdict()['md']
        except:pass
        try:
            mat=re.search(r'^\s*Processing Level:\s*(?P<md>.+$)',self.mdtxt, re.I+re.M)
            md['level']=mat.groupdict()['md']
        except:pass
        try:
            mat=re.search(r'^\s*Interpolation Method:\s*(?P<md>.+$)',self.mdtxt, re.I+re.M)
            md['resampling']=mat.groupdict()['md']
        except:pass

        #Need to access individual scene metadata via component/image IDs
        #Source Image Metadata
        try:
            mat=re.search(r'^\s*Source Image ID:\s*(?P<md>\d+%s)'%(int(image_id)+1),self.mdtxt, re.I+re.M)
            md['sceneid']=mat.groupdict()['md']
        except:pass
        try:
            mat=re.search(r'^\s*Nominal Collection Elevation:\s*(?P<md>[+-]?((\d+(\.\d*)?)|\.\d+)([eE][+-]?[0-9]+)?)',self.mdtxt[image_start:], re.I+re.M)
            md['viewangle']=float(mat.groupdict()['md'])
        except:pass
        try:
            mat=re.search(r'^\s*Sun Angle Azimuth:\s*(?P<md>[+-]?((\d+(\.\d*)?)|\.\d+)([eE][+-]?[0-9]+)?)',self.mdtxt[image_start:], re.I+re.M)
            md['sunazimuth']=float(mat.groupdict()['md'])
        except:pass
        try:
            mat=re.search(r'^\s*Sun Angle Elevation:\s*(?P<md>[+-]?((\d+(\.\d*)?)|\.\d+)([eE][+-]?[0-9]+)?)',self.mdtxt[image_start:], re.I+re.M)
            md['sunelevation']=float(mat.groupdict()['md'])
        except:pass
        try:
            mat=re.search(r'^\s*Acquisition Date/Time:\s*(?P<md>.+$)',self.mdtxt[image_start:], re.I+re.M)
            md['imgdate']='T'.join(mat.groupdict()['md'].split()[0:2])+'Z'
        except:pass
        try:
            mat=re.search(r'^\s*Percent Cloud Cover:\s*(?P<md>\d+$)',self.mdtxt[image_start:], re.I+re.M)
            md['cloudcover']=float(mat.groupdict()['md'])
        except:pass

        #Product Component Metadata
        try:
            mat=re.search(r'^\s*Component File Name: \s*(?P<md>.+$)',self.mdtxt[component_start:], re.I+re.M)
            self._datafiles=mat.groupdict()['md'].split()
        except:self._datafiles=None
        try:
            mat=re.search(r'^\s*Thumbnail File Name:\s*(?P<md>.+$)',self.mdtxt[component_start:], re.I+re.M)
            self._overview=os.path.join(os.path.dirname(f),mat.groupdict()['md'])
        except:self._overview=None

        return md

    def __opendataset__(self):

        bandlookup={'pan':['pan'],
                    'blu':['blu'],'grn':['grn'],
                    'red':['red'],'nir':['nir'],
                    'bgrn':['blu','grn','red','nir'],
                    'bgr':['blu','grn','red'],
                    'rgb':['red','grn','blu']
                    }
        bandfiles={}
        bandnames=[]
        for d in self._datafiles:
            band=d.split('_')[2]
            bands=bandlookup.get(band,band)
            for band in bands:
                bandfiles[band]=os.path.join(os.path.dirname(self.fileinfo['filepath']),d)
                bandnames+=[band]

        try:
            f=bandfiles['red']
            rgb=True
        except:
            f=bandfiles['pan']
            rgb=False

        ds=geometry.OpenDataset(f)
        rb=ds.GetRasterBand(1)
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        datatype =gdal.GetDataTypeName(rb.DataType)
        nbits=gdal.GetDataTypeSize(rb.DataType)
        nbands=len(bandnames)
        bandnames=','.join(bandnames)

        if rgb and bandfiles['red']!=bandfiles['blu']:
            ds=geometry.OpenDataset(
                    geometry.CreateSimpleVRT(
                        [bandfiles['red'],bandfiles['grn'],bandfiles['blu']],
                        cols,rows,datatype
                    )
                )

        return ds,nbands,bandnames,f


    def getoverview(self,outfile=None,width=800,format='JPG'):
        '''
        Generate overviews for GeoEye imagery

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
        try:return overviews.resize(self._overview,outfile,width)
        except:return __default__.Dataset.getoverview(self,outfile,width,format) #Try it the slow way...

