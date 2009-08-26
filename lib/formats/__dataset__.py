'''
Base Dataset class
==================
Defines the metadata fields and populates some basic info
'''

import os,time,sys,glob,time
import UserDict 
import utilities, uuid

#Import fieldnames
import __fields__

class Dataset(object):
    '''A base Dataset class'''
    def __new__(self,f):
        ##Initialise the class object
        self=object.__new__(self)
        
        self._gdaldataset=None
        self._metadata={}
        self._extent=[]
        self._filelist=[]
        
        ##Populate some basic info
        self.fileinfo=utilities.FileInfo(f)
        #self.guid=str(uuid.uuid4())
        #Make the guid reproducible based on filename
        self.guid=str(uuid.uuid3(uuid.NAMESPACE_DNS,f))
        self.fileinfo['filename']=os.path.basename(f)
        self.fileinfo['filepath']=f
        self.fileinfo['guid']=self.guid
        self.fileinfo['metadatadate']=time.strftime(utilities.dateformat+utilities.timeformat,time.localtime())

        ##Initialise the fields
        self.fields=idict(__fields__.fields)#We don't want any fields added/deleted

        return self

    # ============= #
    # Class Methods
    # ============= #
    def __getmetadata__(self,*args,**kwargs):
        '''In case subclasses don't override...'''
        pass

    def __getfilelist__(self,*args,**kwargs):
        '''Get all files that have the same name (sans .ext), or are related according to gdalinfo
            special cases may be handled separately in their respective format drivers'''
        f=self.fileinfo['filepath']
        files=glob.glob(os.path.splitext(f)[0]+'.*')
        if os.path.exists(os.path.splitext(f)[0]):files.append(os.path.splitext(f)[0])
        hdr_dir=os.path.join(os.path.split(f)[0], 'headers') #Cause ACRES creates a 'headers' directory
        if os.path.exists(hdr_dir):
            files.extend(glob.glob(os.path.join(hdr_dir,'*')))

        if self._gdaldataset:
            files.extend(self._gdaldataset.GetFileList())

        self._filelist=list(set(utilities.fixSeparators(files))) #list(set([])) filters out duplicates
        
    def __init__(self,*args,**kwargs):
        pass #just in case a subclass tries to call this method

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
