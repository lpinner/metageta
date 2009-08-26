'''
Metadata driver for ESRI GRIDs
==============================
@see:Format specification
    U{http://home.gdal.org/projects/aigrid/aigrid_format.html}
'''
#list of file name regular expressions
format_regex=[r'hdr\.adf$']

#import base dataset modules
import __default__

# import other modules (use "_"  prefix to import privately)
import sys, os,glob

class Dataset(__default__.Dataset): 
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __init__(self,f):
        ''' Set the filename from <path>\hdr.adf to <path>'''
        grddir=os.path.dirname(f)
        self.fileinfo['filepath']=grddir
        self.fileinfo['filename']=os.path.basename(grddir)
        self.filelist=glob.glob(grddir+'*')
        self.filelist.extend(glob.glob(grddir+'/*'))
    def __getmetadata__(self):
        '''Read Metadata for a ESRI GRID dataset'''
        __default__.Dataset.__getmetadata__(self, self.fileinfo['filepath']) #autopopulate basic metadata
        if self.metadata['compressiontype']=='Unknown':self.metadata['compressiontype']='RLE'
