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
    def __init__(self,f):
        '''Read Metadata for a ENVI image as GDAL doesn't work if you pass the header file...'''
        hdr=open(f)
        try:
            if hdr.readline().strip() == 'ENVI': #is it an ENVI hdr file...?
                dat=os.path.splitext(f)[0] #Get the data file
                if os.path.exists(dat):
                    __default__.Dataset.__init__(self, dat) #autopopulate basic metadata
                else:
                    raise NotImplementedError, 'No data file exists for ENVI header file %s.' % f
                #self.metadata['filename']=os.path.basename(f)
                #self.metadata['filepath']=f
            else:raise NotImplementedError #This error gets ignored in __init__.Open()
        finally:
            hdr.close()