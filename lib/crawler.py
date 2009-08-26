'''
Iterator for metadata crawling
==============================

Example:

>>> import crawler
>>> Crawler=crawler.Crawler('Some directory to crawl')
>>> #Loop thru dataset objects returned by Crawler
>>> for dataset in Crawler:
>>>     metadata=dataset.metadata

'''

import utilities
import formats
import re

debug=False
'''Default debug option'''

class Crawler:
    "Iterator for metadata crawling"
    def __init__(self,dir):
        format_regex  = formats.format_regex

        #Build a dict of matching files and regexes then sort according to the priority of the regex formats 
        fileformats={}
        for f in utilities.rglob(dir,'|'.join(format_regex), True, re.IGNORECASE):
            for r in format_regex:
                if re.search(r,f,re.IGNORECASE):
                    if fileformats.has_key(r):fileformats[r].append(f)
                    else:fileformats[r]=[f]
                    break
        files=[]
        for r in format_regex:
            if fileformats.has_key(r):files.extend(fileformats[r])

        #Class vars
        self.errors=[] #A list of files that couldn't be opened. Contains a tuple with file name, error info, debug info
        self.files=utilities.fixSeparators(files)
        self.file=''
        self.filecount=len(self.files)

    def __iter__(self):
        return self

    def next(self):
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
            



