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
Base Dataset class
==================
Defines the metadata fields and populates some basic info

@todo: implement ESRI PGDB rasters (depends on GDAL)
'''

import os,time,sys,glob,time,math, uuid
import UserDict
from metageta import utilities, geometry, overviews


#Import fieldnames
import __fields__

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

class Dataset(object):
    '''A base Dataset class'''
    def __new__(self,f):
        ##Initialise the class object
        self=object.__new__(self)

        #Little kludge to avoid ESRI GDB rasters for now
        d=os.path.abspath(os.path.dirname(f))
        if d[-4:].lower() == '.gdb': raise Exception, 'Unable to open rasters stored in an ESRI GDB %s'%f

        self._gdaldataset=None
        self._metadata={}
        self._extent=[]
        self._filelist=[]
        self._stretch=None
        ''' self._stretch allows subclasses to control overview generation somewhat
            self._stretch = (stretch_type,rgb_bands,stretch_args)
            See L{overviews.getoverview} for appropriate values.
        '''

        ##Populate some basic info
        self.__setfileinfo__(f)

        ##Initialise the fields
        self.fields=idict(__fields__.fields)#We don't want any fields added/deleted

        return self

    # ==================== #
    # Public Class Methods
    # ==================== #
    def getoverview(self,outfile=None,width=800,format='JPG'):
        '''
        Generate overviews for generic imagery

        @requires:exposing a gdal.Dataset object as self._gdaldataset

        @note: There are a number of ways of controlling the generation of overview images:
            - Overriding this class method and writing your own.
            - Setting self._stretch to the appropriate (stretch_type,rgb_bands,stretch_args) values. See L{overviews.getoverview}.
            - Customising self._gdaldataset using a VRT, for example: setting red, green and blue color interpretations for selected bands

        @type  outfile: string
        @param outfile: a filepath to the output overview image. If supplied, format is determined from the file extension
        @type  width:   integer
        @param width:   image width
        @type  format:  string
        @param format:  format to generate overview image, one of ['JPG','PNG','GIF','BMP','TIF']. Not required if outfile is supplied.

        @return:
            - B{filepath} (if outfile is supplied) B{OR}
            - B{binary image data} (if outfile is not supplied)
        '''

        md=self.metadata
        ds=self._gdaldataset
        if not ds:raise AttributeError, 'No GDALDataset object available, overview image can not be generated'

        #Don't rely on the metadata as self._gdaldataset might be a custom VRT
        ##nbands=md['nbands']
        ##cols=md['cols']
        ##rows=md['rows']
        ##nbits=md['nbits']
        rb=ds.GetRasterBand(1)
        nbands=ds.RasterCount
        cols=ds.RasterXSize
        rows=ds.RasterYSize
        nbits=gdal.GetDataTypeSize(rb.DataType)
        datatype=gdal.GetDataTypeName(rb.DataType)
        stretch_type=None
        stretch_args=None
        rgb_bands = {}

        #Check for pre-defined stretch
        if self._stretch:
            stretch_type,rgb_bands,stretch_args=self._stretch
        else:
            #Check for pre-defined rgb bands, if 8 bit - assume they don't need stretching
            for i in range(1,nbands+1):
                gci=ds.GetRasterBand(i).GetRasterColorInterpretation()
                if   gci == gdal.GCI_RedBand:
                    rgb_bands[0]=i
                elif gci == gdal.GCI_GreenBand:
                    rgb_bands[1]=i
                elif gci == gdal.GCI_BlueBand:
                    rgb_bands[2]=i
                if len(rgb_bands)==3:
                    rgb_bands=rgb_bands[0],rgb_bands[1],rgb_bands[2] #Make a list from the dict
                    if nbits == 8:
                        stretch_type='NONE'
                        stretch_args=[]
                    else:
                        stretch_type='STDDEV'
                        stretch_args=[2]
                    break

        #Set some defaults
        if stretch_type is None or stretch_args is None:
            if nbands < 3:
                #Default - assume greyscale
                #stretch_type='PERCENT'
                #stretch_args=[2,98]
                stretch_type='STDDEV'
                stretch_args=[2]
                rgb_bands=[1]
                #But check if there's an attribute table or colour table
                #and change the stretch type to colour table
                if datatype in ['Byte', 'Int16', 'UInt16']:
                    ct=rb.GetColorTable()
                    at=rb.GetDefaultRAT()
                    min,max=rb.ComputeRasterMinMax()
                    if ct and ct.GetCount() > 0 and min>=0: #GDAL doesn't like colourtables with negative values
                            stretch_type='COLOURTABLE'
                            stretch_args=[]
                    elif at and at.GetRowCount() > 0 and at.GetRowCount() < 256:
                        stretch_type='RANDOM'
                        stretch_args=[]

            elif nbands == 3:
                #Assume RGB
                if nbits > 8:
                    stretch_type='PERCENT'
                    stretch_args=[2,98]
                else:
                    stretch_type='NONE'
                    stretch_args=[]
                if len(rgb_bands) < 3:rgb_bands=[1,2,3]
            elif nbands >= 4:
                stretch_type='PERCENT'
                stretch_args=[2,98]
                #stretch_type='STDDEV'
                #stretch_args=[2]
                if len(rgb_bands) < 3:rgb_bands=[3,2,1]
        if not rgb_bands:rgb_bands=[1]
        return overviews.getoverview(ds,outfile,width,format,rgb_bands,stretch_type,*stretch_args)

    # ===================== #
    # Private Class Methods
    # ===================== #
    def __setfileinfo__(self,f):
        self.fileinfo=utilities.FileInfo(f)
        self.guid=self.fileinfo['guid']
        #self.fileinfo['metadatadate']=time.strftime(utilities.dateformat,time.localtime())  #Just use yyy-mm-dd
        self.fileinfo['metadatadate']=time.strftime(utilities.datetimeformat,time.localtime())  #Use yyy-mm-ddThh:mm:ss

    def __getfilelist__(self,*args,**kwargs):
        '''Get all files that have the same name (sans .ext), or are related according to gdalinfo.
            Special cases may be handled separately in their respective format drivers.'''
        f=self.fileinfo['filepath']
        files=[]
        try:
            files=glob.glob(os.path.splitext(f)[0]+'.*')
            if os.path.exists(os.path.splitext(f)[0]):files.append(os.path.splitext(f)[0])
            hdr_dir=os.path.join(os.path.split(f)[0], 'headers') #Cause ACRES creates a 'headers' directory
            if os.path.exists(hdr_dir):
                files.extend(glob.glob(os.path.join(hdr_dir,'*')))
        except:pass # Need to handle errors when dealing with an VRT XML string better...

        if self._gdaldataset:
            #try:files.extend(self._gdaldataset.GetFileList()) #GetFileList can return files that don't exist... - e.g. the aux.xml in a read-only directory
            try:files.extend([os.path.abspath(f) for f in self._gdaldataset.GetFileList() if os.path.exists(f)])
            except:pass

        #self._filelist=list(set(utilities.normcase(files))) #list(set([])) filters out duplicates
        self._filelist=list(set(files)) #list(set([])) filters out duplicates

    def __getmetadata__(self,*args,**kwargs):
        '''In case subclasses don't override...'''
        pass
    def __init__(self,*args,**kwargs):
        '''In case subclasses don't override...'''
        pass


    # ================ #
    # Class Properties
    # ================ #
    def __classproperty__(fcn):
        '''The class property decorator function'''
        try:return property( **fcn() )
        except TypeError,e:
            raise TypeError('"%s" is a property, you can only get and set its value.'%fcn.__name__)

    @__classproperty__
    def metadata():
        '''The metadata property.'''

        def fget(self):
            if not self._metadata:
                #Initialise the metadata idict
                for field in self.fields:
                    if field in self.fileinfo:self._metadata[field]=self.fileinfo[field]
                    else:self._metadata[field]=''
                self._metadata=idict(self._metadata) #We don't want any fields added/deleted
                self.__getmetadata__()
                #Pretty print the SRS
                srs=osr.SpatialReference(self._metadata['srs'])
                self._metadata['srs']=srs.ExportToPrettyWkt()
                #if self._metadata['compressionratio'] > 10000 and self._metadata['filetype'] != 'VRT/Virtual Raster': #Possibly a dodgy JP2 that will grash GDAL and therefore python...
                #    raise IOError, 'Unable to extract metadata from %s\nFile may be corrupt' % self.fileinfo['filepath']

            return self._metadata

        def fset(self, *args, **kwargs):
            if len(args) == 1:raise AttributeError('Can\'t overwrite metadata property')
            elif len(args) == 2:self._metadata[args[0]] = args[1]

        def fdel(self):pass #raise AttributeError('Can\'t delete metadata property')???????

        return locals()

    @__classproperty__
    def extent():
        '''The extent property.'''

        def fget(self, *args, **kwargs):
            if not self._extent:self.__getmetadata__() #extent gets set during metadata extraction
            return self._extent

        def fset(self, *args, **kwargs):
            if len(args) == 1:self._extent = args[0]
            elif len(args) == 2:self._extent[args[0]] = args[1]

        def fdel(self, *args, **kwargs):pass

        return locals()

    @__classproperty__
    def filelist():
        '''The filelist property.'''
        def fget(self):
            if not self._filelist:self.__getfilelist__()
            #return self._filelist
            #Just in case the metadata xml generated by runtransform gets picked up...
            return [f for f in self._filelist if self.guid not in f]
        def fset(self, *args, **kwargs):
            #if len(args) == 1:self._filelist = utilities.normcase(args[0])
            #elif len(args) == 2:self._filelist[args[0]] = utilities.normcase(args[1])
            if len(args) == 1:self._filelist = args[0]
            elif len(args) == 2:self._filelist[args[0]] = args[1]

        def fdel(self):pass

        return locals()

class idict(UserDict.IterableUserDict):
    '''An immutable dictionary.
       Modified from http://code.activestate.com/recipes/498072/
       to inherit UserDict.IterableUserDict
    '''
    def __setitem__(self, key, val):
        if key in self.data.keys():
            self.data[key]=val
        else:raise KeyError("Can't add keys")

    def __delitem__(self, key):
        raise KeyError("Can't delete keys")

    def pop(self, key):
        raise KeyError("Can't delete keys")

    def popitem(self):
        raise KeyError("Can't delete keys")
