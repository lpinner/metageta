# -*- coding: utf-8 -*-
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

'''
Metadata driver for ESRI Bil imagery

B{Format specification}:
    - U{http://webhelp.esri.com/arcgisdesktop/9.2/index.cfm?id=2527&pid=2519&topicname=BIL,_BIP,_and_BSQ_raster_files}

@todo: Generic BIL/BIP/BSQ...?

'''

format_regex=[r'\.hdr$']
'''Regular expression list of file formats'''

#import base dataset modules
import __default__

# import other modules (use "_"  prefix to import privately)
import sys, os, glob
from metageta import geometry

class Dataset(__default__.Dataset): 
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''

    def __init__(self,f):
        if not f:f=self.fileinfo['filepath']
        if f[:4]=='/vsi':raise NotImplementedError
        lin=open(f).readline().strip() #read first line
        if lin == 'ENVI':raise NotImplementedError, '%s is not an ESRI bil file.' % f

        data_formats=['','.bil','.bip','.bsq','.flt'] #added '' as TerraScan can create "bils" with no file extension
        hdr=os.path.splitext(f)[0]
        for fmt in data_formats:
            dat=hdr+fmt
            if os.path.exists(dat):break
            else: dat=False
        if dat:self._datafile=dat
        else:raise NotImplementedError, '%s is not an ESRI bil file.' % f
    def __getmetadata__(self,f=None):
        '''Read Metadata for a ESRI Bil image as GDAL doesn't work if you pass the header file...'''
        try:__default__.Dataset.__getmetadata__(self, self._datafile) #autopopulate basic metadata
        except geometry.GDALError,err:
            if 'HFAEntry' in err.errmsg:#Sometimes AUX files can cause problems. AUXs seem to be handled by the HFA (ERDAS Imagine) driver,
                                        #so deregister it and try again. We won't get as much info though :(
                try:
                    hfa=__default__.gdal.GetDriverByName('HFA') 
                    hfa.Deregister()
                finally:
                    __default__.Dataset.__getmetadata__(self, self._datafile)
                    __default__.gdal.AllRegister() 
            else:raise #Something else caused it, reraise the error
    def getoverview(self,outfile=None,width=800,format='JPG'):
        '''Override the default method if there is a .clr file'''
        from metageta import overviews
        clr=glob.glob(self.fileinfo['filepath'][:-3]+'[cC][lL][rR]')
        if clr:
            clr=overviews.ParseColourLUT(clr[0])
            self._stretch=['COLOURTABLELUT',[1],[clr]]
        return __default__.Dataset.getoverview(self,outfile,width,format)
