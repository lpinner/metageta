'''
Metadata driver for ECW imagery
===============================
'''

#list of file name regular expressions
format_regex=[r'\.ecw$'] #Well duh...

#import base dataset modules
#import __dataset__
import __default__

# import other modules (use "_"  prefix to import privately)
import sys, os

class Dataset(__default__.Dataset): 
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __getmetadata__(self,f=None):
        '''Read Metadata for a ECW image as GDAL doesn't quite get it all...'''
        if not f:f=self.fileinfo['filepath']
        ers=os.path.splitext(f)[0]+'.ers'
        if os.path.exists(ers):
            try:
                __default__.Dataset.__getmetadata__(self, ers) #autopopulate basic metadata
                self.metadata['filetype']='ECW/ERMapper Compressed Wavelets'
                self.metadata['compressiontype']='ECW'
            except:__default__.Dataset.__getmetadata__(self, f)
        else:
            __default__.Dataset.__getmetadata__(self) #autopopulate basic metadata
