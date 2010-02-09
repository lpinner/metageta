'''
Metadata driver for JP2 imagery
===============================
'''

#list of file name regular expressions
format_regex=[r'\.jp2$'] #Well duh...

#import base dataset modules
#import __dataset__
import __default__

# import other modules (use "_"  prefix to import privately)
import sys, os

class Dataset(__default__.Dataset): 
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __init__(self,f):
        '''Read Metadata for a JP2 image'''
        ers=os.path.splitext(f)[0]+'.ers'
        if os.path.exists(ers):
            try:
                __default__.Dataset.__init__(self, ers) #autopopulate basic metadata
                self.metadata['filepath']=f
                self.metadata['filename']=os.path.split(f)[1]
                self.metadata['filetype']='JP2ECW/ERMapper JPEG2000'
                self.metadata['compressiontype']='JPEG2000'
            except:__default__.Dataset.__init__(self, f)
        else:
            __default__.Dataset.__init__(self, f) #autopopulate basic metadata
