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
Metadata driver for remote ECWP imagery
'''

format_regex=[r'\.url$',r'\.ecwp$']
'''Regular expression list of file formats'''

#import base dataset modules
import __default__

# import other modules (use "_"  prefix to import privately)
import sys, os

class Dataset(__default__.Dataset): 
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __init__(self,f):
        if not f:f=self.fileinfo['filepath']
        if f[:4]=='/vsi':raise NotImplementedError
        self.ecwp=open(f).read().strip()
        if self.ecwp[0:4].upper() != 'ECWP':
            raise NotImplementedError, '%s is not an ECWP file.' % f
            
        ##Update the GUID using the ecwp url instead of the file
        self.guid=utilities.uuid(self.ecwp)
        self.fileinfo['guid']=self.guid

    def __getmetadata__(self,f=None):
        '''Read Metadata for a remote ECWP image'''

        __default__.Dataset.__getmetadata__(self,self.ecwp) #autopopulate basic metadata
        self.metadata['compressionratio']=-1 #N/A for a remote raster and avoids the
                                                 #'File may be corrupt' exception
