+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
To add support for another format:
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  * Create a new .py file. Name the .py file whatever you want as long as the filename doesn't begin with an underscore "_"
  * Define a "regular expression" string to match your formats filename
  * Create a "Dataset" class that inherits either from the base __dataset__.Dataset class or from the __default__.Dataset class
      - See class hierarchy below
      - The default Dataset class is useful if GDAL can read your format and you just need to populate some extra fields. 
  * Populate appropriate metadata and extent variables in the __init__ method of your dataset class
  * Your format will be automatically loaded when the formats module is initialised.
  * See existing examples in this directory
  * Errors get propagated back up the chain. If you can't handle a certain file and for some reason
    you don't want an error to get raised (eg. the ENVI driver (*.hdr) doesn't handle ESRI bil/flt headers (*.hdr))
    then raise NotImplementedError which will be ignored in lib.formats.Open()
  * If you want some info to get logged by the application and then continue processing (e.g the image doesn't have
    a projection defined, etc...) then use the warnings.warn("Some message") method
    Don't forget to import the warnings module!
  * Date/Time formats must follow follow AS ISO 8601-2007 (see: http://www.anzlic.org.au/metadata/guidelines/date_and_datetime.htm)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Class hierarchy

__dataset__.Dataset()

    #the metadata dictionary. You can only populate fields defined in __fields__.py
    .metadata={} #keys are immutable (values can be changed, but keys can't be added or deleted)
    
    #Extent of the four corners. May be rotated (eg. for path oriented images)
    .extent=[[x,y],[x,y],[x,y],[x,y]] #You must populate this...
                                      #coordinate order is irrelevant, as long as it doesn't create a self intersecting poly
      
    __default__.Dataset(__dataset__.Dataset)
        #populate appropriate metadata fields in the __init__ method
        .__init__(file):                  
        
        someformat.Dataset(__default__.Dataset)
            """custom format inherits from __default__.Dataset
               Use this when GDAL can read most of the images metadata, but you need to populate some other stuff as well
               If you inherit from this, don't forget to call __default__.Dataset.__init__(f) explicitly as your class will override this method
            """
            
            #populate appropriate metadata fields in the __init__ method
            .__init__(file):       

                #Don't forget to call the __default__.Dataset__init__ method explicitly as your class has overridden this method           
                __default__.Dataset.__init__(f)


    anotherformat.Dataset(__dataset__.Dataset)
        """custom format inherits from base __dataset__.Dataset
           need to populate basic metadata yourself
        """
        #populate appropriate metadata fields in the __init__ method
        .__init__(file):                  
