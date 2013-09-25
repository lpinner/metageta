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
Spatial reference helper functions
'''

import os,sys,math
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

Mostly from ogr_srs_api.h (with some extras thrown in just in case...)'''

##Copyright notice from ogr_srs_api.h as required by the MIT license
##/******************************************************************************
## * $Id$
## *
## * Project:  OpenGIS Simple Features Reference Implementation
## * Purpose:  C API and constant declarations for OGR Spatial References.
## * Author:   Frank Warmerdam, warmerdam@pobox.com
## *
## ******************************************************************************
## * Copyright (c) 2000, Frank Warmerdam
## *
## * Permission is hereby granted, free of charge, to any person obtaining a
## * copy of this software and associated documentation files (the "Software"),
## * to deal in the Software without restriction, including without limitation
## * the rights to use, copy, modify, merge, publish, distribute, sublicense,
## * and/or sell copies of the Software, and to permit persons to whom the
## * Software is furnished to do so, subject to the following conditions:
## *
## * The above copyright notice and this permission notice shall be included
## * in all copies or substantial portions of the Software.
## *
## * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
## * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
## * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
## * DEALINGS IN THE SOFTWARE.
## ****************************************************************************/

AUS_GEOGCS=(
    4202, #AGD66
    4203, #AGD84
    4283, #GDA94
    4326, #WGS 84
    32622 #WGS 84 / Plate Carree
)
'''Geographic EPSG codes'''

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
'''Projected EPSG codes'''

#************************************************************************#
#*  GCTP projection codes.                                              *#
#************************************************************************#
GCTP_PROJECTIONS={'GEO':      0, ## Geographic
                  'UTM':      1, ## Universal Transverse Mercator (UTM)
                  'SPCS':     2, ## State Plane Coordinates
                  'ALBERS':   3, ## Albers Conical Equal Area
                  'LAMCC':    4, ## Lambert Conformal Conic
                  'MERCAT':   5, ## Mercator
                  'PS':       6, ## Polar Stereographic
                  'POLYC':    7, ## Polyconic
                  'EQUIDC':   8, ## Equidistant Conic
                  'TM':       9, ## Transverse Mercator
                  'STEREO':  10, ## Stereographic
                  'LAMAZ':   11, ## Lambert Azimuthal Equal Area
                  'AZMEQD':  12, ## Azimuthal Equidistant
                  'GNOMON':  13, ## Gnomonic
                  'ORTHO':   14, ## Orthographic
                  'GVNSP':   15, ## General Vertical Near-Side Perspective
                  'SNSOID':  16, ## Sinusiodal
                  'EQRECT':  17, ## Equirectangular
                  'MILLER':  18, ## Miller Cylindrical
                  'VGRINT':  19, ## Van der Grinten
                  'HOM':     20, ## (Hotine) Oblique Mercator 
                  'ROBIN':   21, ## Robinson
                  'SOM':     22, ## Space Oblique Mercator (SOM)
                  'ALASKA':  23, ## Alaska Conformal
                  'GOODE':   24, ## Interrupted Goode Homolosine 
                  'MOLL':    25, ## Mollweide
                  'IMOLL':   26, ## Interrupted Mollweide
                  'HAMMER':  27, ## Hammer
                  'WAGIV':   28, ## Wagner IV
                  'WAGVII':  29, ## Wagner VII
                  'OBEQA':   30, ## Oblated Equal Area
                  'ISINUS1': 31, ## Integerized Sinusoidal Grid (the same as 99)
                  'CEA':     97, ## Cylindrical Equal Area (Grid corners set in meters for EASE grid) 
                  'BCEA':    98, ## Cylindrical Equal Area (Grid corners set in DMS degs for EASE grid) 
                  'ISINUS':  99  ## Integerized Sinusoidal Grid (added by Raj Gejjagaraguppe ARC for MODIS) 
}
'''USGS projection codes ported from ogr_srs_usgs.cpp'''

#************************************************************************#
#*  GCTP ellipsoid codes.                                               *#
#************************************************************************#
GCTP_ELLIPSOIDS={'CLARKE1866'         : 0,
                 'CLARKE1880'         : 1,
                 'BESSEL'             : 2,
                 'INTERNATIONAL1967'  : 3,
                 'INTERNATIONAL1909'  : 4,
                 'WGS72'              : 5,
                 'EVEREST'            : 6,
                 'WGS66 '             : 7,
                 'GRS1980'            : 8,
                 'GRS80'              : 8,
                 'AIRY  '             : 9,
                 'MODIFIED_EVEREST'   :10,
                 'MODIFIED_AIRY'      :11,
                 'WGS84'              :12,
                 'SOUTHEAST_ASIA'     :13,
                 'AUSTRALIAN_NATIONAL':14,
                 'KRASSOVSKY'         :15,
                 'HOUGH'              :16,
                 'MERCURY1960'        :17,
                 'MODIFIED_MERCURY'   :18,
                 'SPHERE'             :19
}
'''USGS ellipsoid codes ported from ogr_srs_usgs.cpp'''

##Copyright notice from ogr_srs_api.h as required by the MIT license
##/******************************************************************************
## * $Id$
## *
## * Project:  OpenGIS Simple Features Reference Implementation
## * Purpose:  OGRSpatialReference translation to/from USGS georeferencing
## *           information (used in GCTP package).
## * Author:   Andrey Kiselev, dron@ak4719.spb.edu
## *
## ******************************************************************************
## * Copyright (c) 2004, Andrey Kiselev <dron@ak4719.spb.edu>
## *
## * Permission is hereby granted, free of charge, to any person obtaining a
## * copy of this software and associated documentation files (the "Software"),
## * to deal in the Software without restriction, including without limitation
## * the rights to use, copy, modify, merge, publish, distribute, sublicense,
## * and/or sell copies of the Software, and to permit persons to whom the
## * Software is furnished to do so, subject to the following conditions:
## *
## * The above copyright notice and this permission notice shall be included
## * in all copies or substantial portions of the Software.
## *
## * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
## * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
## * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
## * DEALINGS IN THE SOFTWARE.
## ****************************************************************************/


#==============================================================================
#Functions
#==============================================================================
def IdentifyAusEPSG(wkt):
    '''Identify common EPSG codes used in Australia from OGC WKT
    
        @type wkt:  C{str}
        @param wkt: WKT SRS string
        @rtype:     C{int}
        @return:    EPSG code
    '''

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
    ''' Identify linear units
        @type wkt:  C{str}
        @param wkt: WKT SRS string
        @rtype:     C{str}
        @return:    Linear unit code (m,ft,dd, etc.)
    '''

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
def lon2utmzone(lon):
    ''' Calculate UTM Zone number from a Longitude
        
        @type  lon: C{float}
        @param lon: Longitude
        @rtype:     C{int}
        @return:    UTM Zone
    '''
    return int(math.floor((lon - (-180.0)) / 6.0) + 1)
