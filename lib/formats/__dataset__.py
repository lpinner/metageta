'''
Base Dataset class
==================
Defines the metadata fields and populates some basic info
'''

import utilities, uuid
import os,time

#Import fieldnames
import __fields__

class Dataset(object):
    '''A base Dataset class'''
    _err=('fields','metadata') #These fields can't be deleted
    def __setattr__(self, name, value):
        #Stop the fields and metadata attributes from being changed
        if name in self._err:raise TypeError("Can't modify field names")
        else:self.__dict__[name] = value
    def __delattr__(self, name):
        #Stop the fields and metadata attributes from being deleted
        if name in self._err:raise TypeError("Can't delete %s" % name)
        else:self.__dict__[name] = value
    def __new__(self,f):
        #Initialise the object
        self=object.__new__(self)

        #Initialise the metadata
        metadata={}
        for field in __fields__.fields:metadata[field]=''
        metadata=_idict(metadata) #We don't want any fields added/deleted
        super(Dataset, self).__setattr__('fields', __fields__.fields) #required to avoid errors by
        super(Dataset, self).__setattr__('metadata', metadata)        #bypassing local __setattr__

        #Populate some basic fields
        self.metadata['filename']=os.path.basename(f)
        self.metadata['filepath']=f
        self.metadata['metadatadate']=time.strftime('%Y-%m-%d',time.localtime())
        fileinfo=utilities.FileInfo(f)
        self.metadata['ownerid']=fileinfo['OWNERID']
        self.metadata['ownername']=fileinfo['OWNERNAME']
        self.metadata['datecreated']=fileinfo['DATE_CREATED']
        #Make the guid reproducible based on filename
        #self.metadata['guid']=str(uuid.uuid4())
        self.metadata['guid']=str(uuid.uuid3(uuid.NAMESPACE_DNS,f))
        
        return self
    def __init__(self,*args,**kwargs):
        pass #just in case a subclass tries to call this method

class _idict(object):
    '''The idict class. An immutable dictionary.
       http://code.activestate.com/recipes/498072/
    '''
    def __init__(self, dict=None, **kwds):
        self.__data = {}
        if dict is not None:
            self.__data.update(dict)
        if len(kwds):
            self.__data.update(kwds)
        pass
    def __iter__(self):
        for key in self.__data.keys():yield key
    
    def __repr__(self):
        return repr(self.__data)
    
    def __cmp__(self, dict):
        if isinstance(dict, tuct):
            return cmp(self.__data, dict.__data)
        else:
            return cmp(self.__data, dict)
    
    def __len__(self):
        return len(self.__data)
    
    def __getitem__(self, key):
        return self.__data[key]

    def __setitem__(self, key, val):
        if key in self.__data.keys():
            self.__data[key]=val
        else:raise TypeError("Can't add fields")

    def __delitem__(self, key):
        raise TypeError("Can't delete fields")

    def copy(self):
        if self.__class__ is tuct:
            return tuct(self.__data.copy())
        import copy
        __data = self.__data
        try:
            self.__data = {}
            c = copy.copy(self)
        finally:
            self.__data = __data
        c.update(self)
        return c

    def pop(self, key):
        return self.__data.pop(key)
    
    def keys(self):
        return self.__data.keys()
    
    def items(self):
        return self.__data.items()
        
    def iteritems(self):
        return self.__data.iteritems()
        
    def iterkeys(self):
        return self.__data.iterkeys()
    
    def itervalues(self):
        return self.__data.itervalues()
    
    def values(self):
        return self.__data.values()
        
    def has_key(self, key):
        return self.__data.has_key(key)
    
    def get(self, key, failobj=None):
        if not self.has_key(key):
            return failobj
        return self[key]
        
    def __contains__(self, key):
        return key in self.__data

    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d
