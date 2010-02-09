'''
Spatial reference helper functions
==================================
'''
import os,sys
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

#==============================================================================
#Constants
#==============================================================================

SRS_UNITS_CONV={ 
    'meter':                'm',
    'metre':                'm',
    'meters':               'm',
    'metres':               'm',
    'foot (international)': 'ft',
    'foot':                 'ft',
    'feet':                 'ft',
    'u.s. foot':            'ft-us',
    'u.s. feet':            'ft-us',
    'us survey foot':       'ft-us',
    'nautical mile':        'nm',
    'nm':                   'nm',
    'degree':               'deg',
    'dd':                   'deg',
    'deg':                  'deg',
    'radian':               'rad',
    'radians':              'rad',
    'rad':                  'rad'
}
'''Convert from GDAL-OSR to ISO 19115 metadata unit of measure.

Mostly from ogr_srs_api.h (with some extras thrown in just in case...)::
  define SRS_UL_METER            "Meter"
  define SRS_UL_FOOT             "Foot (International)" /* or just "FOOT"? */
  define SRS_UL_US_FOOT          "U.S. Foot" /* or "US survey foot" */
  define SRS_UL_NAUTICAL_MILE    "Nautical Mile"
  define SRS_UA_DEGREE           "degree"
  define SRS_UA_RADIAN           "radian"
'''

#Geog/Projected EPSG codes
AUS_GEOGCS=(
    4202, #AGD66
    4203, #AGD84
    4283, #GDA94
    4326, #WGS 84
    32622  #WGS 84 / Plate Carree
)
AUS_PROJCS=(
    3032, #WGS 84 / Australian Antarctic Polar Stereographic
    3033, #WGS 84 / Australian Antarctic Lambert
    3107, #GDA94 / SA Lambert
    3110, #AGD66 / Vicgrid66
    3111, #GDA94 / Vicgrid94
    3112, #GDA94 / Geoscience Australia Lambert
    3308, #GDA94 / NSW Lambert
    3577, #GDA94 / Australian Albers
    4176, #Australian Antarctic
    20248, #AGD66 / AMG zone 48
    20249, #AGD66 / AMG zone 49
    20250, #AGD66 / AMG zone 50
    20251, #AGD66 / AMG zone 51
    20252, #AGD66 / AMG zone 52
    20253, #AGD66 / AMG zone 53
    20254, #AGD66 / AMG zone 54
    20255, #AGD66 / AMG zone 55
    20256, #AGD66 / AMG zone 56
    20257, #AGD66 / AMG zone 57
    20258, #AGD66 / AMG zone 58
    20348, #AGD84 / AMG zone 48
    20349, #AGD84 / AMG zone 49
    20350, #AGD84 / AMG zone 50
    20351, #AGD84 / AMG zone 51
    20352, #AGD84 / AMG zone 52
    20353, #AGD84 / AMG zone 53
    20354, #AGD84 / AMG zone 54
    20355, #AGD84 / AMG zone 55
    20356, #AGD84 / AMG zone 56
    20357, #AGD84 / AMG zone 57
    20358, #AGD84 / AMG zone 58
    28348, #GDA94 / MGA zone 48
    28349, #GDA94 / MGA zone 49
    28350, #GDA94 / MGA zone 50
    28351, #GDA94 / MGA zone 51
    28352, #GDA94 / MGA zone 52
    28353, #GDA94 / MGA zone 53
    28354, #GDA94 / MGA zone 54
    28355, #GDA94 / MGA zone 55
    28356, #GDA94 / MGA zone 56
    28357, #GDA94 / MGA zone 57
    28358  #GDA94 / MGA zone 58
)
#==============================================================================
#Functions
#==============================================================================
def IdentifyAusEPSG(wkt):
    
    se=osr.SpatialReference()
    sw=osr.SpatialReference(wkt)
    
    epsg=0
    if   sw.IsGeographic():epsg=sw.GetAuthorityCode('GEOGCS')
    elif sw.IsProjected():epsg=sw.GetAuthorityCode('PROJCS')
    if not epsg:
        if sw.IsGeographic():
            for ausepsg in AUS_GEOGCS:
                epsg=0 #Default return value
                se.ImportFromEPSG(ausepsg)
                if se.ExportToUSGS() == sw.ExportToUSGS():#dirty little kludge, doesn't always work...
                    epsg=ausepsg
                    break
        elif sw.IsProjected():
            for ausepsg in AUS_PROJCS:
                epsg=0 #Default return value
                se.ImportFromEPSG(ausepsg)
                if se.ExportToUSGS() == sw.ExportToUSGS():
                    epsg=ausepsg
                    break
    del se;del sw
    return int(epsg)

def GetLinearUnitsName(wkt):
    sw=osr.SpatialReference(wkt)
    name = 'Meter' #Default
    if sw.IsProjected():
        name = sw.GetAttrValue( 'PROJCS|UNIT', 0 ).lower()
    elif sw.IsLocal():
        name = sw.GetAttrValue( 'LOCAL_CS|UNIT', 0 ).lower()
    else:
        name = 'deg'

    if SRS_UNITS_CONV.has_key(name):
        return SRS_UNITS_CONV[name]
    else:
        return name
