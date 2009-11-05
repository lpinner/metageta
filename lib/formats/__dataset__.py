'''
Base Dataset class
==================
Defines the metadata fields and populates some basic info
'''

import os,time,sys,glob,time,math
import UserDict 
import utilities, geometry, uuid

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
class Dataset(object):
    '''A base Dataset class'''
    def __new__(self,f):
        ##Initialise the class object
        self=object.__new__(self)
        
        self._gdaldataset=None
        self._metadata={}
        self._extent=[]
        self._filelist=[]
        self._stretch=None
        
        ##Populate some basic info
        self.__setfileinfo__(f)

        ##Initialise the fields
        self.fields=idict(__fields__.fields)#We don't want any fields added/deleted

        return self

    # ==================== #
    # Public Class Methods
    # ==================== #
    #def getoverview(self,*args,**kwargs):
    #    '''In case subclasses don't override...'''
    #    pass
    def getoverview(self,outfile=None,width=800,format='JPG'): 
        '''
        Generate overviews for generic imagery

        Override this class if you like, otherwise simply expose a GDALDataset object as self._gdaldataset_

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
        import overviews

        md=self.metadata
        ds=self._gdaldataset
        if not ds:raise AttributeError, 'No GDALDataset object available, overview image can not be generated'

        #Don't rely on the metadata as self._gdaldataset might be a custom VRT
        ##nbands=md['nbands']
        ##cols=md['cols']
        ##rows=md['rows']
        ##nbits=md['nbits']
        nbands=ds.RasterCount
        cols=ds.RasterXSize
        rows=ds.RasterYSize
        nbits=gdal.GetDataTypeSize(ds.GetRasterBand(1).DataType)

        stretch_type=None
        stretch_args=None
        rgb_bands = {}

        #Check for pre-defined stretch
        if self._stretch:
            stretch_type,stretch_args=self._stretch

        #Check for pre-defined rgb bands
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

        #Set some defaults
        if not stretch_type and not stretch_args:
            if nbands < 3:
                #Assume greyscale
                stretch_type='PERCENT'
                stretch_args=[2,98]
                rgb_bands=[1]
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

        return overviews.getoverview(ds,outfile,width,format,rgb_bands,stretch_type,*stretch_args)

    # ===================== #
    # Private Class Methods
    # ===================== #
    def __setfileinfo__(self,f):
        self.fileinfo=utilities.FileInfo(f)
        #self.guid=str(uuid.uuid4())
        #Make the guid reproducible based on filename
        self.guid=str(uuid.uuid3(uuid.NAMESPACE_DNS,f))
        self.fileinfo['filename']=os.path.basename(f)
        self.fileinfo['filepath']=f
        self.fileinfo['guid']=self.guid
        #self.fileinfo['metadatadate']=time.strftime(utilities.datetimeformat,time.localtime()) #Geonetwork is baulking at the yyy-mm-ddThh:mm:ss format
        self.fileinfo['metadatadate']=time.strftime(utilities.dateformat,time.localtime())  #Just use yyy-mm-dd
    def __getfilelist__(self,*args,**kwargs):
        '''Get all files that have the same name (sans .ext), or are related according to gdalinfo
            special cases may be handled separately in their respective format drivers'''
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
            try:files.extend(self._gdaldataset.GetFileList())
            except:pass

        self._filelist=list(set(utilities.fixSeparators(files))) #list(set([])) filters out duplicates
        
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
        except:pass

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
            return self._filelist

        def fset(self, *args, **kwargs):
            if len(args) == 1:self._filelist = args[0]
            elif len(args) == 2:self._filelist[args[0]] = args[1]

        def fdel(self):pass

        return locals()

class idict(UserDict.IterableUserDict):
    '''The idict class. An immutable dictionary.
       modified from http://code.activestate.com/recipes/498072/
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
