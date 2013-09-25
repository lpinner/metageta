# -*- coding: utf-8 -*-
'''
Metadata driver for ESRI GRIDs

B{Format specification}:
    - U{http://home.gdal.org/projects/aigrid/aigrid_format.html}
'''

# Copyright (c) 2013 Australian Government, Department of the Environment
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
import sys, os,glob
from metageta import geometry,utilities,overviews

class Dataset(__default__.Dataset):
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __init__(self,f):
        ''' Set the filename from <path>\hdr.adf to <path>'''
        self._adf=f
        f=os.path.dirname(f)
        self.__setfileinfo__(f)
        #self.fileinfo['filepath']=f
        #self.fileinfo['filename']=os.path.basename(f)
        filelist=glob.glob(f+'.*')
        filelist.extend(glob.glob(f+'/*'))
        self.filelist=filelist #Resolves Issue 41 - self.filelist is a property, we can only get or set it, not extend it.

    def __getmetadata__(self):
        '''Read Metadata for a ESRI GRID dataset'''
        #__default__.Dataset.__getmetadata__(self, self.fileinfo['filepath']) #autopopulate basic metadata

        try:__default__.Dataset.__getmetadata__(self, self.fileinfo['filepath'])
        except:self.__aux_workaround__(__default__.Dataset.__getmetadata__, self,self.fileinfo['filepath'])
        if self.metadata['compressiontype']=='Unknown':self.metadata['compressiontype']='RLE'

    def getoverview(self,outfile=None,width=800,format='JPG'):
        '''Override the default method if there is a clr file or the attribute table contains RGB values'''

        #Check for clr file first
        clr=[self.fileinfo['filepath']+'.[cC][lL][rR]',os.path.join(self.fileinfo['filepath'],'[cC][lL][rR].[aA][dD][fF]')]
        for c in clr:
            c=glob.glob(c)
            if c:
                clr=overviews.ParseColourLUT(c[0])
                self._stretch=['COLOURTABLELUT',[1],[clr]]
                break
        #Check for attribute table with RGB values
        if not self._stretch:
            rat=self._gdaldataset.GetRasterBand(1).GetDefaultRAT()
            if rat:
                clr = overviews.RATtoLUT(rat)
                if clr:self._stretch=['COLOURTABLELUT',[1],[clr]]

        try:return __default__.Dataset.getoverview(self,outfile,width,format)
        except:return self.__aux_workaround__(__default__.Dataset.getoverview, self,outfile,width,format)
    def __aux_workaround__(self, func,*args,**kwargs):
        ##  Sometimes AUX files can cause problems, this is related to the HFA driver,
        ##  One workaround is to cd to the grid dir and open the hdr.adf file.
        ##  This sometimes causes issue with statistics calculations
        ##  Deregistering the HFA driver results in another error:
        ##    Unable to open <somegrid>
        ##   '<somegrid>.aux' not recognised as a supported file format
        ##  Workaround, disable PAM, reload gdal, disable Erdas Imagine (HFA) driver,
        ##  which is what opens aux files
        GDAL_PAM_ENABLED=os.environ.get('GDAL_PAM_ENABLED',None)
        os.environ['GDAL_PAM_ENABLED']='NO'
        reload(__default__.gdal)
        hfa=__default__.gdal.GetDriverByName('HFA')
        if hfa:hfa.Deregister()
        retval=func(*args,**kwargs)
        if GDAL_PAM_ENABLED:os.environ['GDAL_PAM_ENABLED']=GDAL_PAM_ENABLED
        else:os.environ.pop('GDAL_PAM_ENABLED')
        reload(__default__.gdal)
        if hfa:hfa.Register()
        return retval


