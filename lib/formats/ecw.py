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
    def __init__(self,f):
        '''Read Metadata for a ECW image as GDAL doesn't quite get it all...'''
        ers=os.path.splitext(f)[0]+'.ers'
        if os.path.exists(ers):
            try:
                __default__.Dataset.__init__(self, ers) #autopopulate basic metadata
                self.metadata['filepath']=f
                self.metadata['filename']=os.path.split(f)[1]
                self.metadata['filetype']='ECW/ERMapper Compressed Wavelets'
                self.metadata['compressiontype']='ECW'
            except:__default__.Dataset.__init__(self, f)
        else:
            __default__.Dataset.__init__(self, f) #autopopulate basic metadata
        path=os.environ['PATH']
        os.environ['PATH'] = '%s\\bin_ecw;%s' %(os.path.dirname(__file__), os.environ['PATH'])
        stdin,stdout,stderr=os.popen3('ecw_report.exe "%s"' % f)
        os.environ['PATH']=path
        stdout=stdout.readlines()
        for line in stdout:
            line=[part.strip() for part in line.split(':')]
            if line[0].upper() == 'TARGET RATIO':
                self.metadata['targetratio']=line[1]
                break
