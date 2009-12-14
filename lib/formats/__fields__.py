'''
Metadata Fields
===============
Dictionary of field names and data types
'''

# Copyright (c) 2009 Australian Government, Department of Environment, Heritage, Water and the Arts
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

fields={'abstract'        :'no fieldtype required as this is not included in the shapefile...',
        'bands'           :('string',50),
        'cellx'           :'float',
        'celly'           :'float',
        'units'           :('string',25),
        'cloudcover'      :('string',50),
        'cols'            :'int',
        'compressionratio':'int',
        'compressiontype' :('string',50),
        'datatype'        :('string',50),
        'datecreated'     :('string',25),
        'datemodified'    :('string',25),
        'demcorrection'   :('string',50),
        'epsg'            :('string',4),
        'filelist'        :('string',255),
        'filename'        :('string',50),
        'filepath'        :('string',255),
        'filesize'        :'int',
        'filetype'        :('string',50),
        'guid'            :('string',36),
        'imgdate'         :('string',25),
        'lineage'         :'no fieldtype required as this is not included in the shapefile...',
        'level'           :('string',50),
        'LL'              :('string',25),#should probably be separate LLX and LLY etc... fields with 'float' type...
        'LR'              :('string',25),
        'metadata'        :'no fieldtype required as this is not included in the shapefile...',
        'metadatadate'    :('string',25),
        'mode'            :('string',50),
        'nbands'          :'int',
        'nbits'           :'int',
        'nodata'          :'float',
        'orbit'           :('string',50),
        'orientation'     :('string',50),
        'ownerid'         :('string',50),
        'ownername'       :('string',50),
        'quicklook'       :('string',50),
        'resampling'      :('string',50),
        'rotation'        :'float',
        'rows'            :'int',
        'satellite'       :('string',50),
        'sceneid'         :('string',50),
        'sensor'          :('string',50),
        'srs'             :'no fieldtype required as this is not included in the shapefile...',
        'sunazimuth'      :'float',
        'sunelevation'    :'float',
        'thumbnail'       :('string',50),
        'title'           :'no fieldtype required as this is not included in the shapefile...',
        'UL'              :('string',25),
        'UR'              :('string',25), 
        'useConstraints'  :'no fieldtype required as this is not included in the shapefile...',
        'viewangle'       :'float'
}
