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
Metadata driver for ECW imagery
'''

format_regex=[r'\.ecw$'] #Well duh...
'''Regular expression list of file formats'''

#import base dataset modules
#import __dataset__
import __default__

# import other modules (use "_"  prefix to import privately)
import sys, os
from metageta import geometry

class Dataset(__default__.Dataset):
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __getmetadata__(self,f=None):
        '''Read Metadata for a ECW image as GDAL doesn't quite get it all...'''
        if not f:f=self.fileinfo['filepath']
        #Originally we used the ERS to get metadata as they sometimes hold more info than the ECW
        #however, this caused segfaults under certain circumstances which were unable to be tracked down.
        #These circumstances were very repeatable and only occurred when the Crawler iterator returned a
        #certain ECW dataset, not when it was opened, when metadata was extracted nor even when overviews were generated.
        #Got me stumped!
        ers=os.path.splitext(f)[0]+'.ers'
        if os.path.exists(ers) and os.path.basename(f) in open(ers).read():
            try:
                __default__.Dataset.__getmetadata__(self, ers) #autopopulate basic metadata
                self.metadata['filetype']='ECW/ERMapper Compressed Wavelets'
                self.metadata['compressiontype']='ECW'
                self.metadata['filepath']=f
                self.metadata['filename']=os.path.basename(f)
                self._gdaldataset=geometry.OpenDataset(f) #ERS may not get handed off to gdal proxy and segfault
            except:__default__.Dataset.__getmetadata__(self, f)
        else:
            __default__.Dataset.__getmetadata__(self) #autopopulate basic metadata
        #Leave the ECW driver in place even though all it does is call the default class.
        #This is so ECWs get processed before any ERSs (which could cause a segfault)
        ##__default__.Dataset.__getmetadata__(self) #autopopulate basic metadata


    def getoverview(self,*args,**kwargs):
        '''Check for possibly corrupt files that can crash GDAL and therefore python...'''
        if self.metadata['compressionratio'] > 10000:
            raise IOError, 'Unable to generate overview image from %s\nFile may be corrupt' % self.fileinfo['filepath']
        else:return __default__.Dataset.getoverview(self,*args,**kwargs)
