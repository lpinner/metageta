'''
Image Metadata drivers
======================

Example:

>>> import formats
>>> dataset = formats.open(somefile)
>>> print dataset.extent
[[139.214834,-20.155611],[139.28967,-20.170712],[139.403241,-19.311661],[139.47766,-19.326724]]
>>> print dataset.metadata['filetype']
CEOS/Landsat CCRS Format
>>> print dataset.metadata['datatype']
Int16

To add support for another format:
==================================
-	Create a new .py file. Name the .py file whatever you want as long as the filename doesn't begin with an underscore "_"
-	Define one or more "regular expression" strings to match your formats filename
-	Create a "Dataset" class that inherits either from the base __dataset__.Dataset class or from the __default__.Dataset class (See class hierarchy below)
-	The default Dataset class is useful if GDAL can read your format and you just need to populate some extra fields. 
-	Populate appropriate filelist & fileinfo in the __init__ method of your dataset class (if required), do not populate the metadata dict!
-	Populate appropriate metadata and extent variables in the __getmetadata__ method of your dataset class
-	Your format will be automatically loaded when the formats module is initialised.
-	Errors should be propagated back up the chain. If you can't handle a certain file and for some reason you don't want an error to get raised (eg. the ENVI driver (*.hdr) doesn't handle ESRI bil/flt headers (*.hdr)) then raise NotImplementedError which will be ignored in lib.formats.Open()
-	If you want some info to get logged by the application and then continue processing (e.g the image doesn't have a projection defined, etc...) then use the warnings.warn("Some message") method - don't forget to import the warnings module!
-	Date/Time formats must follow follow AS ISO 8601-2007 (see: U{http://www.anzlic.org.au/metadata/guidelines/Index.html?date_and_datetime.htm})

Class hierarchy::
    __dataset__.Dataset():
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
    |----__new__(file):
    |    #Initialise the class object and populate fileinfo
    |
    |----__getfilelist__():
    |    #populate fileelist
    |
    |----__default__.Dataset(__dataset__.Dataset)
    |   | #Default Dataset class
    |   |
    |   |----__getmetadata__(file):                  
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
    |       |----__init__(file):
    |           | #Populate/update filelist, fileinfo if required
    |           |
    |       |----__getmetadata__(file):
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
        |__init__(file):                  
        |  #Populate/update filelist, fileinfo if required
        |
        |__getmetadata__(file):                  
        |  #Populate appropriate fields in the metadata dictionary
        |  #Populate extent list

@todo: Need to pass back info about import errors - warnings.warn perhaps?
@todo: More info re. geometric, radiometric corrections where available (ccrs,...)
@todo: __dataset__.__getfilelist__() does not handle different file formats with the same basename
       eg. dir/abc.jp2,dir/abc.j2i,dir/abc.tif,dir/abc.tfw
       This could be handled with a bit of kludgery, but should it...? Can we assume that abc.jp2
       is the compressed version of abc.tif and should all be lumped together (as currently happens)?
'''