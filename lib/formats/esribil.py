'''
Metadata driver for ESRI Bil imagery
====================================
@see:Format specification
    U{http://webhelp.esri.com/arcgisdesktop/9.2/index.cfm?id=2527&pid=2519&topicname=BIL,_BIP,_and_BSQ_raster_files}
@todo: Generic BIL/BIP/BSQ...?

'''
#list of file name regular expressions
format_regex=[r'\.hdr$']

#import base dataset modules
import __default__

# import other modules (use "_"  prefix to import privately)
import sys, os

class Dataset(__default__.Dataset): 
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''

    def __init__(self,f):
        if not f:f=self.fileinfo['filepath']

        data_formats=['bil','bip','bsq','flt']
        hdr=os.path.splitext(f)[0]
        for fmt in data_formats:
            dat='%s.%s' % (hdr,fmt)
            if os.path.exists(dat):break
            else: dat=False
        if dat:self._datafile=dat
        else:raise NotImplementedError, '%s is not an ESRI bil file.' % f
    def __getmetadata__(self,f=None):
        '''Read Metadata for a ESRI Bil image as GDAL doesn't work if you pass the header file...'''
        __default__.Dataset.__getmetadata__(self, self._datafile) #autopopulate basic metadata
        
