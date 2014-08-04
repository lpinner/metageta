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
Iterator for metadata crawling.

Example:
    >>> import crawler
    >>> Crawler=crawler.Crawler('Some directory to crawl')
    >>> #Loop thru dataset objects returned by Crawler
    >>> for dataset in Crawler:
    >>>     metadata=dataset.metadata

@todo:
    - Make this faster!!! It's verrry slow on large filesystems...
    - Explore removing regular expression and searching using fnmatch instead
    - Can this be rewritten to yield files as they're found instead of building a complete list of files first? Probably.
      However, the multiple loops are there to ensure certain types of files are dealt with first, but perhaps that logic
      needs to be handled by the formats library
'''

from metageta import utilities,formats
import re,os

class Crawler:
    ''' Iterator for metadata crawling'''
    def __init__(self,dir, recurse=True, archive=False):
        ''' Iterator for metadata crawling

            @type  dir: C{str}
            @param dir: The directory to start the metadata crawl.
        '''

        format_regex  = formats.format_regex
        #dir=utilities.uncpath(utilities.realpath(utilities.normcase(utilities.encode(dir))))
        dir=utilities.uncpath(utilities.realpath(utilities.encode(dir)))
        #Build a dict of matching files and regexes then sort according to the priority of the regex formats
        fileformats={}
        for f in utilities.rglob(dir,'|'.join(format_regex), True, re.IGNORECASE, recurse=recurse, archive=archive):
            #Use utf-8 encoding to fix Issue 20
            if f[:4]=='/vsi':f=utilities.encode(f)
            #else:f=utilities.realpath(utilities.normcase(utilities.encode(f)))
            else:f=utilities.realpath(utilities.encode(f))
            for r in format_regex: #This is so we always return _default_ format datasets last.
                if re.search(r,os.path.basename(f),re.IGNORECASE):
                    if fileformats.has_key(r):fileformats[r].append(f)
                    else:fileformats[r]=[f]
                    break
        files=[]
        for r in format_regex:
            if fileformats.has_key(r):files.extend(fileformats[r])

        #Class vars
        self.errors=[] #A list of files that couldn't be opened. Contains a tuple with file name, error info, debug info
        self.files=files
        self.file=''
        self.filecount=len(self.files)

    def __iter__(self):
        return self

    def next(self):
        ''' @rtype:  C{Dataset}
            @return: Return the next Dataset or raise StopIteration
        '''
        #Have we finished?
        if len(self.files) == 0:
            raise StopIteration

        #Get the first file
        self.file=self.files.pop(0)
        try:
            #Open it
            ds=formats.Open(self.file)

            #Remove any files in our filelist that occur in the dataset's filelist and decrement the filecount
            for f in ds.filelist:
                if f in self.files:
                    self.files.remove(f)
                    self.filecount-=1
            #Fin!
            return ds
        except:
            #decrement the filecount and append to the errors list
            self.filecount-=1
            self.errors.append((self.file,
                                utilities.ExceptionInfo(),
                                utilities.ExceptionInfo(10)
                        ))

            #Skip to the next file so we don't stop the iteration
            #Exceptions here will keep recursing until we find a
            #file we can open or run out of files.
            return self.next()




