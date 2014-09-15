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
Image Metadata drivers
======================
Generic and custom image format drivers

B{Example}:
    >>> import metageta.formats
    >>> dataset = metageta.formats.open(somefile)
    >>> print dataset.extent
    [[139.214834,-20.155611],[139.28967,-20.170712],[139.403241,-19.311661],[139.47766,-19.326724]]
    >>> print dataset.metadata['filetype']
    CEOS/Landsat CCRS Format
    >>> print dataset.metadata['datatype']
    Int16


B{Adding support for another format}:
    - Create a new .py file. Name the .py file whatever you want as long as the filename doesn't begin with an underscore "_"
    - Define one or more "regular expression" strings to match your formats filename
    - Create a "Dataset" class that inherits either from the base __dataset__.Dataset class or from the __default__.Dataset class (See class hierarchy below)
    - The default Dataset class is useful if GDAL can read your format and you just need to populate some extra fields.
    - Populate appropriate filelist & fileinfo in the __init__ method of your dataset class (if required), do not populate the metadata dict!
    - Populate appropriate metadata and extent variables in the __getmetadata__ method of your dataset class
    - Your format will be automatically loaded when the formats module is initialised.
    - Errors should be propagated back up the chain. If you can't handle a certain file and for some reason you don't want an error to get raised (eg. the ENVI driver (*.hdr) doesn't handle ESRI bil/flt headers (*.hdr)) then raise NotImplementedError which will be ignored in lib.formats.Open()
    - If you want some info to get logged by the application and then continue processing (e.g the image doesn't have a projection defined, etc...) then use the warnings.warn("Some message") method - don't forget to import the warnings module!
    - Date/Time formats must follow follow AS ISO 8601-2007 (see: U{http://www.anzlic.org.au/metadata/guidelines/Index.html?date_and_datetime.htm})

B{Class hierarchy}::

    __dataset__.Dataset()
        | #Base Dataset class
        |
        |----.metadata={} #the metadata dictionary.
        |                 #the metadata dictionary.
        |                 #You can only populate fields defined in __fields__.py
        |                 #keys are immutable (values can be changed, but keys can't be
        |                 #added or deleted)
        |
        |----.filelist=[] #the list of related files
        |
        |----.fileinfo={      #file information
        |         'size':..., #doesn't included size of related files... TODO?
        |         'filename':...,
        |         'filepath':...,
        |         'guid':...,
        |         'metadatadate':...,
        |         'datemodified':...,
        |         'datecreated':...,
        |         'dateaccessed':...,
        |         'ownerid':...,
        |         'ownername':...
        |    }
        |
        |----.extent=[[x,y],[x,y],[x,y],[x,y]]
        |     #Extent of the four corners in geographic (lon,lat) coordinates.
        |     #May be rotated (eg. for path oriented images). Coordinate order
        |     #is irrelevant, as long as it doesn't create a self-intersecting
        |     #polygon.
        |
        |----getoverview(outfile=None,width=800,format='JPG'))
        |    #generate thumbnails and quicklooks
        |
        |----__new__(file)
        |    #Initialise the class object and populate fileinfo
        |
        |----__getfilelist__()
        |    #populate filelist
        |
        |----__default__.Dataset(__dataset__.Dataset)
        |   | #Default Dataset class
        |   |
        |   |----__getmetadata__(file)
        |   |     #Populate appropriate fields in the metadata dictionary
        |   |     #Populate extent list
        |   |
        |   |----someformat.Dataset(__default__.Dataset)
        |       | #Custom format inherits from subclass __default__.Dataset.
        |       |
        |       | #Use this when GDAL can read most of the images metadata,
        |       | #but you need to populate some other stuff as well
        |       | #If you inherit from this, don't forget to call
        |       | #__default__.Dataset.__getmetadata__(file) explicitly
        |       | #as your class will override this method
        |       |
        |       |----__init__(file)
        |           | #Populate/update filelist, fileinfo if required
        |           |
        |       |----__getmetadata__(file)
        |           | #Populate appropriate fields in the metadata dictionary
        |           | #Populate extent list
        |           |
        |           |----__default__.Dataset.__getmetadata__(file)
        |                #Call superclass init explicitly
        |
        |----anotherformat.Dataset(__dataset__.Dataset)
            | #Custom format inherits from base class - __dataset__.Dataset
            |
            | #You need to populate basic metadata yourself.
            |
            |__init__(file)
            |  #Populate/update filelist, fileinfo if required
            |
            |__getmetadata__(file)
            |  #Populate appropriate fields in the metadata dictionary
            |  #Populate extent list

@todo: Need to pass back info about import errors - warnings.warn perhaps?
@todo: More info re. geometric, radiometric corrections where available (ccrs,...)
@todo: __dataset__.__getfilelist__() does not handle different file formats with the same basename
       eg. dir/abc.jp2,dir/abc.j2i,dir/abc.tif,dir/abc.tfw
       This could be handled with a bit of kludgery, but should it...? Can we assume that abc.jp2
       is the compressed version of abc.tif and should all be lumped together (as currently happens)?
'''

from glob import glob as _glob
import os.path as _path, re as _re, sys as _sys, imp as _imp, warnings as _warn
import __fields__
from metageta import utilities

#Private
__formats__={}

#Public
format_regex=[]
'''List of file path regular expressions defined by format drivers'''
fields=__fields__.fields
'''List of metadata fields that can be populated'''

debug=False
#Dynamically load all formats
for _lib in sorted(_glob(_path.join(__path__[0],'[a-z]*.py'))):
    _lib=_path.splitext(_path.basename(_lib))[0]
    try:
        #import custom format and add to the list of formats
        __formats__[_lib]=__import__('%s.%s'%(__name__,_lib), fromlist=[__name__])

        #append module _format_regex & fields to lists
        format_regex.extend([r for r in __formats__[_lib].format_regex if not r in format_regex])
    #except:pass
    except:
        _warn.showwarning=_warn._show_warning #Fix Ft overwrite
        _warn.warn('Unable to import %s\n%s' % (_lib, utilities.ExceptionInfo()))

#import generic formats (eg. GeoTiff, JP2, etc...)
import __default__
#append module _format_regex to list of format regexes
format_regex.extend([_r for _r in __default__.format_regex if not _r in format_regex])

def Open(f):
    ''' Open an image with the appropriate driver.

        @type  f: C{str}
        @param f: a filepath to the dataset to open.

        @rtype:   C{formats.Dataset}
        @return:  L{formats.Dataset<formats.__dataset__.Dataset>} object

        @todo: perhaps log the entire error stack if a file couldn't be opened?
    '''
    errors=[] #error stack
    f=utilities.encode(f) #Issue 20
    #f=utilities.normcase(utilities.uncpath(utilities.realpath(f)))

    #Try custom formats
    for lib in __formats__:
        fr='|'.join(__formats__[lib].format_regex)
        rx=_re.compile(fr, _re.IGNORECASE)
        if rx.search(f):
            try:
                ds=__formats__[lib].Dataset(f)
                return ds
            except NotImplementedError:
                pass #Used when a format driver can't open a file, but doesn't want to raise an error
            except Exception as err:
                if debug:
                    errinfo=utilities.FormatTraceback(_sys.exc_info()[2],10)
                    errargs=[arg for arg in err.args]
                    errargs.append(errinfo)
                    err.args=tuple(errargs)
                errors.append(err)

    #Try default formats
    try:
        fr='|'.join(__default__.format_regex)
        rx=_re.compile(fr, _re.IGNORECASE)
        if rx.search(f):
            ds=__default__.Dataset(f)
            return ds
    except NotImplementedError:
        pass #Used when a format driver can't open a file, but doesn't want to raise an error
    except Exception as err:
        if debug:
            errinfo=utilities.FormatTraceback(_sys.exc_info()[2],10)
            errargs=[arg for arg in err.args]
            errargs.append(errinfo)
            err.args=tuple(errargs)
        errors.append(err)

    #Couldn't open file, raise the last error in the stack
    #if len(errors) > 0: raise errors[-1].__class__,'\n'.join(errors[-1].args) #Updated for Python 2.6, not all args are strings...
    if len(errors) > 0: raise errors[-1].__class__(*errors[-1].args)
    else:raise Exception('Unable to open %s' % f)
    '''@todo: perhaps log the entire error stack if a file couldn't be opened?'''
