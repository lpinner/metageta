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
Metadata Fields
===============
Dictionary of field names and data types.
If a field is not to be included in the output shapefile, set type as None.
Currently supported field types are:
    - string (tuple of type name and size)
    - int
    - float
@note: Field names > 10 characters will be truncated.
       Field names can not contain spaces or special characters, except underscores.
@see: U{http://www.gdal.org/ogr/drv_shapefile.html}
@todo: We should probably have separate LLX and LLY etc... fields with 'float' type... This would also need to be changed in the transform XSL
'''

fields={'abstract'        :None,
        'bands'           :('string',50),
        'cellx'           :'float',
        'celly'           :'float',
        'units'           :None,
        'cloudcover'      :None,
        'cols'            :'int',
        'compressionratio':None,
        'compressiontype' :None,
        'datatype'        :('string',50),
        'datecreated'     :('string',25),
        'datemodified'    :('string',25),
        'demcorrection'   :None,
        'epsg'            :None,
        'filelist'        :None,
        'filename'        :('string',100),
        'filepath'        :('string',255),
        'filesize'        :'int',
        'filetype'        :('string',50),
        'guid'            :('string',36),
        'imgdate'         :('string',25),
        'license'         :None,
        'lineage'         :None,
        'level'           :None,
        'LL'              :None,
        'LR'              :None,
        'mediaid'         :None,
        'metadata'        :None,
        'metadatadate'    :None,
        'mode'            :None,
        'nbands'          :'int',
        'nbits'           :'int',
        'nodata'          :'float',
        'orbit'           :None,
        'orientation'     :None,
        'ownerid'         :('string',50),
        'ownername'       :('string',50),
        'quicklook'       :None,
        'resampling'      :None,
        'rotation'        :None,
        'rows'            :'int',
        'satellite'       :('string',50),
        'sceneid'         :('string',50),
        'sensor'          :('string',50),
        'srs'             :None,
        'sunazimuth'      :None,
        'sunelevation'    :None,
        'thumbnail'       :None,
        'title'           :None,
        'UL'              :None,
        'UR'              :None,
        'useConstraints'  :None,
        'viewangle'       :None,
        'DELETED'         :None
}
