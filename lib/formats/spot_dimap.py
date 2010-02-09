'''
Metadata driver for SPOT DIMAP imagery
======================================
@see:Format specification
    U{http://www.spotimage.fr/dimap/spec/documentation/refdoc.htm}
@todo: GDALINFO is pretty slow (4+ sec), check that this driver is not that slow...
'''

#Regular expression list of file formats
format_regex=[r'metadata\.dim$'] #SPOT DIMAP
    
#import base dataset modules
#import __dataset__
import __default__

# import other modules
import sys, os, re, glob, time, math, string
import utilities
import geometry
import xml.dom.minidom as _xmldom

try:
    from osgeo import gdal
    from osgeo import gdalconst
    from osgeo import osr
    from osgeo import ogr
except ImportError:
    import gdal
    import gdalconst
    import osr
    import ogr
    
class Dataset(__default__.Dataset): 
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __init__(self,f):
        if not f:f=self.fileinfo['filepath']
        self.filelist=[r for r in glob.glob('%s/*'%os.path.dirname(f))]
    def __getmetadata__(self,f=None):
        '''Read Metadata for a SPOT DIMAP image as GDAL doesn't quite get it all...'''
        if not f:f=self.fileinfo['filepath']
        __default__.Dataset.__getmetadata__(self, f) #autopopulate basic metadata
        #include every file in the current and upper level directory
        gdalmd=self._gdaldataset.GetMetadata()
        self.metadata['imgdate']=gdalmd['IMAGING_DATE']#ISO 8601 
        self.metadata['satellite']='%s %s' % (gdalmd['MISSION'],gdalmd['MISSION_INDEX'])
        self.metadata['sensor']='%s %s' % (gdalmd['INSTRUMENT'],gdalmd['INSTRUMENT_INDEX'])
        self.metadata['sunelevation'] = float(gdalmd['SUN_ELEVATION'])
        self.metadata['sunazimuth'] = float(gdalmd['SUN_AZIMUTH'])
        self.metadata['level'] = gdalmd['PROCESSING_LEVEL']
        self.metadata['viewangle'] = gdalmd['VIEWING_ANGLE']
        #dom=__xmldom.parse(f) #Takes tooo long to parse the whole damn file, so just read as far as we need...
        strxml=''
        for line in open(f, 'r'):
            if line.upper().strip()=='<DATA_STRIP>':break
            else: strxml+=line
        strxml+='</Dimap_Document>'
        dom=_xmldom.parseString(strxml)
        self.metadata['sceneid'] = dom.documentElement.getElementsByTagName('DATASET_NAME')[0].childNodes[0].data
        bands=dom.documentElement.getElementsByTagName('BAND_DESCRIPTION')
        self.metadata['bands']=','.join([band.childNodes[0].data for band in bands])
