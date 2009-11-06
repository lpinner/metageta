'''
Metadata driver for NITF imagery
======================================
@see:Format specification
    U{http://www.gwg.nga.mil/ntb/baseline/documents.html}

@todo:GDAL upscales non standard bit depths. e.g 11 bit data is treated as 16 bit.
Currently the NITF driver reports the upscaled bit depth.
The actual bit depth can be extracted using the  NITF_ABPP metadata item.
Should this be reported instead of the upscaled bit depth...?

@todo:support NITF with subdatasets

'''

#Regular expression list of file formats
format_regex=[r'.*\.ntf$'] #NITF
    
#import base dataset modules
import __default__

# import other modules
import sys, os, glob
import utilities
import geometry

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
        if glob.glob(os.path.splitext(f)[0]+'.[iI][mM][dD]'): #if an imd file exists
            raise NotImplementedError #Let the quickbird driver handle it, this error gets ignored in __init__.Open()
    def __getmetadata__(self):
        '''Read Metadata for a NITF image'''
        f=self.fileinfo['filepath']
        __default__.Dataset.__getmetadata__(self, f) #autopopulate basic metadata
        gdalmd=self._gdaldataset.GetMetadata()
        self.metadata['title']=gdalmd.get('NITF_FTITLE','')
        self.metadata['imgdate']=gdalmd.get('NITF_STDIDC_ACQUISITION_DATE','')[0:8]
        if 'NITF_USE00A_SUN_EL' in gdalmd:self.metadata['sunelevation']=float(gdalmd['NITF_USE00A_SUN_EL'])
        if 'NITF_USE00A_SUN_AZ' in gdalmd:self.metadata['sunazimuth']=float(gdalmd['NITF_USE00A_SUN_AZ'])
        self.metadata['satellite']=gdalmd.get('NITF_STDIDC_MISSION','')
        self.metadata['sensor']=gdalmd.get('NITF_IREP','')
        self.metadata['sceneid'] = gdalmd.get('NITF_IID1','')
        self.metadata['viewangle'] = gdalmd.get('NITF_USE00A_OBL_ANG','')
