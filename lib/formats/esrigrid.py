# -*- coding: latin-1 -*-
'''
Metadata driver for ESRI GRIDs

B{Format specification}:
    - U{http://home.gdal.org/projects/aigrid/aigrid_format.html}
'''

# Copyright (c) 2009 Australian Government, Department of Environment, Heritage, Water and the Arts
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

format_regex=[r'hdr\.adf$']
'''Regular expression list of file formats'''

#import base dataset modules
import __default__

# import other modules (use "_"  prefix to import privately)
import sys, os,glob,geometry,utilities

class Dataset(__default__.Dataset): 
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __init__(self,f):
        ''' Set the filename from <path>\hdr.adf to <path>'''
        self._adf=f
        self.fileinfo['filepath']=os.path.dirname(f)
        self.fileinfo['filename']=os.path.basename(self.fileinfo['filepath'])
        self.filelist=glob.glob(self.fileinfo['filepath']+'.*')
        self.filelist.extend(glob.glob(self.fileinfo['filepath']+'/*'))
    def __getmetadata__(self):
        '''Read Metadata for a ESRI GRID dataset'''
        #__default__.Dataset.__getmetadata__(self, self.fileinfo['filepath']) #autopopulate basic metadata
        try:__default__.Dataset.__getmetadata__(self,  self.fileinfo['filepath']) #autopopulate basic metadata
        except geometry.GDALError,err:
            if 'aux' in err.errmsg.lower():#Sometimes AUX files can cause problems, workaround, cd to the grid dir.
                curdir = os.path.abspath(os.path.curdir)
                os.chdir(self.fileinfo['filepath'])
                __default__.Dataset.__getmetadata__(self,  os.path.basename(self._adf))
                self._gdaldataset.SetDescription(self._adf)
                os.chdir(curdir)
            else:raise #Something else caused it, reraise the error
        if self.metadata['compressiontype']=='Unknown':self.metadata['compressiontype']='RLE'

    def getoverview(self,outfile=None,width=800,format='JPG'):
        '''Override the default method if there is a .clr file'''
        clr=glob.glob(self.fileinfo['filepath']+'.[cC][lL][rR]')
        if clr:
            clr=clr[0]
            self._stretch=['COLOURTABLELUT',[1],[clr]]
        return __default__.Dataset.getoverview(self,outfile,width,format)
