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
Metadata driver for JPEG2000 imagery
'''

format_regex=[r'\.jp2$'] #Well duh...
'''Regular expression list of file formats'''

#import base dataset modules
#import __dataset__
import __default__

# import other modules (use "_"  prefix to import privately)
import sys, os
from osgeo import gdal

class Dataset(__default__.Dataset):
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __getmetadata__(self,f=None):
        '''Read Metadata for a JP2 image'''
        if not f:f=self.fileinfo['filepath']
        ers=os.path.splitext(f)[0]+'.ers'
        if os.path.exists(ers):
            try:
                self._gdaldataset= self.open_exec(ers)
                __default__.Dataset.__getmetadata__(self, ers) #autopopulate basic metadata
                self.metadata['filetype']='JP2/JPEG2000'
                self.metadata['compressiontype']='JPEG2000'
                self._gdaldataset= self.open_exec(f)
            except:
                self._gdaldataset= self.open_exec(f)
                __default__.Dataset.__getmetadata__(self, f)
        else:
            __default__.Dataset.__getmetadata__(self, f) #autopopulate basic metadata

    def getoverview(self,*args,**kwargs):
        '''Check for possibly corrupt files that can crash GDAL and therefore python...'''
        if self.metadata['compressionratio'] > 10000:
            raise RuntimeError, 'Unable to generate overview image from %s\nFile may be corrupt' % self.fileinfo['filepath']
        else:
            try:
                return __default__.Dataset.getoverview(self,*args,**kwargs)
            except:
                do=self._gdaldataset.GetDriver()
                skip=os.environ.get('GDAL_SKIP','').split()
                os.environ['GDAL_SKIP']=' '.join([do.GetDescription()]+skip)
                do.Deregister()
                ov=self.open_exec(self.fileinfo['filepath'],__default__.Dataset.getoverview, self,*args,**kwargs)
                do.Register()
                os.environ['GDAL_SKIP']=' '.join(skip)
                if ov:return ov
                else:raise RuntimeError, 'Unable to generate overview image from %s\nFile may be corrupt' % self.fileinfo['filepath']

    def open_exec(self,f,func=None,*args,**kwargs):
        self._gdaldataset=None
        result=None
        skip=os.environ.get('GDAL_SKIP','').split()
        drivers=filter(None,[gdal.GetDriverByName(d) for d in ['JP2MrSID','JP2ECW','JP2KAK'] if not d  in skip])
        drivers=zip([d.ShortName for d in drivers]+[''],drivers+[None]) #Filter the list to only installed drivers
        for dn,do in drivers:
            try:
                self._gdaldataset=gdal.Open(f) #Some jp2s crash on open
                if func:result=func(*args,**kwargs)
                break
            except:
                if do:
                    os.environ['GDAL_SKIP']=' '.join([dn]+skip)
                    do.Deregister()

        for dn,do in drivers:
            if do:do.Register()

        #gdal.AllRegister()
        os.environ['GDAL_SKIP']=' '.join(skip)
        if func:return result
        else:return self._gdaldataset
