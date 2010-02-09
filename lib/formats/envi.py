'''
Metadata driver for ENVI imagery
================================
'''

#list of file name regular expressions
format_regex=[r'\.hdr$']

#import base dataset modules
#import __dataset__
import __default__

# import other modules
import sys, os

class Dataset(__default__.Dataset): 
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __init__(self,f=None):
        if not f:f=self.fileinfo['filepath']
        hdr=open(f)
        lin=hdr.readline().strip() #read first line
        hdr.close()
        self._dat=os.path.splitext(f)[0]
        if not lin == 'ENVI' or not os.path.exists(self._dat): #is it an ENVI format hdr...?
            raise NotImplementedError #This error gets ignored in __init__.Open()
            
    def __getmetadata__(self):
        '''Read Metadata for a ENVI image as GDAL doesn't work if you pass the header file...'''
        __default__.Dataset.__getmetadata__(self, self._dat) #autopopulate basic metadata
