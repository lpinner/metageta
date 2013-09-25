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
Metadata driver for ACRES Landsat FastL7A imagery

B{Format specification}:
    - U{http://www.ga.gov.au/image_cache/GA10348.pdf}

B{General info}:
    - U{http://www.ga.gov.au/remote-sensing/satellites-sensors/landsat}
'''

format_regex=[                                       #Landsat 7 FastL7A - Multispectral, Pan & Thermal
    r'header\.h(rf|pn|tm)$',                         #  - GA file names
    r'l7[0-9]{7,7}\_[0-9]{11,11}\_h(rf|pn|tm).fst$', #  - Standard file names
]
'''Regular expression list of file formats'''

#import base dataset module
import __dataset__

# import other modules (use "_"  prefix to import privately)
import sys, os, re, glob, time, math, string
from metageta import utilities, geometry, spatialreferences

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
gdal.AllRegister()

class Dataset(__dataset__.Dataset): 
    '''Subclass of base Dataset class'''
    def __init__(self,f):
        if not f:f=self.fileinfo['filepath']
        if f[:4]=='/vsi':raise NotImplementedError
        d=os.path.dirname(f)

        if open(f).read(1024).strip()[0]=='<':#HTML file, ignore it.
            raise NotImplementedError
        
        if 'HRF' in f.upper():
            self._filetype='HRF'
            #rex='BAND[1-57]\.dat|L7[0-9]{7,7}_[0-9]{11,11}_B[1-57]0\.FST' #not picking up the ACRES .ers files
            rex='BAND[1-57].*|L7[0-9]{7,7}_[0-9]{11,11}_B[1-57]0\.FST'
        elif 'HTM' in f.upper():
            self._filetype='HTM'
            #rex='BAND6[LH]\.dat|L7[0-9]{7,7}_[0-9]{11,11}_B6[1-2]\.FST' #not picking up the ACRES .ers files
            rex='BAND6[LH].*|L7[0-9]{7,7}_[0-9]{11,11}_B6[1-2]\.FST'
        elif 'HPN' in f.upper():
            self._filetype='HPN'
            #rex='BAND8\.dat|L7[0-9]{7,7}_[0-9]{11,11}_B80\.FST' #not picking up the ACRES .ers files
            rex='BAND8.*|L7[0-9]{7,7}_[0-9]{11,11}_B80\.FST'
        
        filelist=[f] #header
        filelist.extend([f for f in utilities.rglob(d,rex,regex=True, regex_flags=re.I, recurse=False)]) #bands
        self.filelist=filelist #"self.filelist" is a property, not a list, we can only 'get' or 'set' it.
    def __getmetadata__(self):
        '''Read Metadata for an ACRES Landsat FastL7A format image as GDAL doesn't get it all.
        Format description: http://www.ga.gov.au/image_cache/GA10348.pdf

        Note:
        hrf = ~30m VNIR/SWIR       (bands 1-5 & 7)
        htm = ~60m thermal         (band 6)
        hpn = ~15m pan             (band 8)
        '''
        
        f=self.fileinfo['filepath']
        d=os.path.dirname(f)
        hdr=open(f).read()
        err='Unable to open %s' % f

        md=self.metadata
        md['filesize']=sum([os.path.getsize(file) for file in self.filelist])
        md['filetype'] = 'FAST/EOSAT FAST Format'
        
        rl=1536#recordlength

        ######################################
        ##Record 1 - administrative
        ######################################
        rec=1

        req_id=utilities.readascii(hdr,(rec-1)*rl,9,28)
        loc=utilities.readascii(hdr,(rec-1)*rl,35,51)
        acquisition_date=utilities.readascii(hdr,(rec-1)*rl,71,78)
        md['imgdate']='%s-%s-%s'%(acquisition_date[:4],acquisition_date[4:6],acquisition_date[6:])
        md['satellite']=utilities.readascii(hdr,(rec-1)*rl,92,101)
        md['sensor']=utilities.readascii(hdr,(rec-1)*rl,111,120)
        md['mode']=utilities.readascii(hdr,(rec-1)*rl,135,140)
        md['viewangle']=float(utilities.readascii(hdr,(rec-1)*rl,154,159))
        product_type=utilities.readascii(hdr,(rec-1)*rl,655,672)
        product_size=utilities.readascii(hdr,(rec-1)*rl,688,697)
        level=utilities.readascii(hdr,(rec-1)*rl,741,751)
        md['resampling']=utilities.readascii(hdr,(rec-1)*rl,765,766)
        md['cols']=int(utilities.readascii(hdr,(rec-1)*rl,843,847))
        md['rows']=int(utilities.readascii(hdr,(rec-1)*rl,865,869))
        md['cellx']=float(utilities.readascii(hdr,(rec-1)*rl,954,959))
        md['celly']=md['cellx']
        md['nbits']=8         #int(utilities.readascii(hdr,(rec-1)*rl,984,985)) always 8 bit
        md['datatype']='Byte' 
        md['nodata']='0' 
        bands_present=utilities.readascii(hdr,(rec-1)*rl,1056,1087)

        bandindices=[[1131,1159],[1170,1198],[1211,1239],[1250,1278],[1291,1319],[1330,1358]]
        bandfiles={}
        for i in bandindices:
            band=utilities.readascii(hdr,(rec-1)*rl,i[0],i[1])
            if band:
                exists,path=utilities.exists(os.path.join(d,band), True)
                if exists:bandfiles[band]=path
                else:#Assume ACRES format (band*.dat) instead Fast format (l7*.fst)...
                    bandid=band[23:25]
                    if bandid == '61':bandid='6l'
                    elif bandid == '62':bandid='6h'
                    else:bandid=bandid[0]
                    exists,path=utilities.exists(os.path.join(d,'band%s.dat'%bandid), True)
                    if not exists:raise RuntimeError, 'Unable to open band data files.'
                    bandfiles[band]=path
            else:break
        md['nbands']=len(bandfiles)

        md['sceneid']=os.path.basename(bandfiles.keys()[0])[3:21] #Use path/row & aquisition date as sceneid - L7f[ppprrr_rrrYYYYMMDD]_AAA.FST 
        if self._filetype=='HRF':
            md['bands']='1 (BLUE),2 (GREEN),3 (RED),4 (NIR),5 (SWIR),7 (SWIR)'
        elif self._filetype=='HTM':
            md['bands']='6L (THERMAL),6H (THERMAL)'
        elif self._filetype=='HPN':
            md['bands']='8 (PAN)'

        ######################################
        ##Record 2 - radiometric
        ######################################
        #Move along, nothing to see here...

        ######################################
        ##Record 3 - geometric
        ######################################
        rec=3
        map_projection=utilities.readascii(hdr,(rec-1)*rl,32,35)
        prjcode=spatialreferences.GCTP_PROJECTIONS.get(map_projection,0)
        ellipsoid=utilities.readascii(hdr,(rec-1)*rl,48,65)
        ellcode=spatialreferences.GCTP_ELLIPSOIDS.get(ellipsoid,0)
        datum=utilities.readascii(hdr,(rec-1)*rl,74,79)
        zone=utilities.readascii(hdr,(rec-1)*rl,521,526)

        #Workaround for UTM zones as GDAL does not pick up southern hemisphere
        #as some FST headers don't include a negative zone number to indicate southern hemisphere
        #as per the FAST format definition
        zone=int(zone) if zone else 0

        usgs_indices = ((110,133),#Semi-major axis
                        (135,158),#Semi-minor axis
                        (161,184),
                        (186,209),
                        (211,234),
                        (241,264),
                        (266,289),
                        (291,314),
                        (321,344),
                        (346,369),
                        (371,394),
                        (401,424),
                        (426,449),
                        (451,474),
                        (481,504))
        usgs_params=[]
        for i in usgs_indices:
            p=utilities.readascii(hdr,(rec-1)*rl,i[0],i[1])
            if p:usgs_params.append(float(p))
            else:usgs_params.append(0.0)

        ulx=geometry.DMS2DD(utilities.readascii(hdr,(rec-1)*rl,566,578), 'DDDMMSSSSSSSH')
        uly=geometry.DMS2DD(utilities.readascii(hdr,(rec-1)*rl,580,591),  'DDMMSSSSSSSH')
        urx=geometry.DMS2DD(utilities.readascii(hdr,(rec-1)*rl,646,658), 'DDDMMSSSSSSSH')
        ury=geometry.DMS2DD(utilities.readascii(hdr,(rec-1)*rl,660,671),  'DDMMSSSSSSSH')
        lrx=geometry.DMS2DD(utilities.readascii(hdr,(rec-1)*rl,726,738), 'DDDMMSSSSSSSH')
        lry=geometry.DMS2DD(utilities.readascii(hdr,(rec-1)*rl,740,751),  'DDMMSSSSSSSH')
        llx=geometry.DMS2DD(utilities.readascii(hdr,(rec-1)*rl,806,818), 'DDDMMSSSSSSSH')
        lly=geometry.DMS2DD(utilities.readascii(hdr,(rec-1)*rl,820,831),  'DDMMSSSSSSSH')
        ext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]
        
        md['UL']='%s,%s' % tuple(ext[0])
        md['UR']='%s,%s' % tuple(ext[1])
        md['LR']='%s,%s' % tuple(ext[2])
        md['LL']='%s,%s' % tuple(ext[3])

        if zone > 0 and uly < 0:zone*=-1
        srs=osr.SpatialReference()
        srs.ImportFromUSGS(prjcode,zone,usgs_params,ellcode)
        if datum=='GDA':#Workaround for GDA94 datum as GDAL does not recognise it
                       #as per the FAST format definition
            if map_projection=='UTM':
                epsg=28300+abs(zone)
                srs.ImportFromEPSG(epsg)
                md['srs']=srs.ExportToWkt()
                md['epsg']=epsg
                md['units']='m'
            else:
                srs.SetGeogCS('GDA94','Geocentric_Datum_of_Australia_1994','GRS 1980', usgs_params[0], 298.257)
                md['srs']=srs.ExportToWkt()
                md['epsg'] = spatialreferences.IdentifyAusEPSG(md['srs'])
                md['units'] = spatialreferences.GetLinearUnitsName(md['srs'])
        else:
            md['srs']=srs.ExportToWkt()
            md['epsg'] = spatialreferences.IdentifyAusEPSG(md['srs'])
            md['units'] = spatialreferences.GetLinearUnitsName(md['srs'])

        md['rotation']=float(utilities.readascii(hdr,(rec-1)*rl,995,1000))
        if abs(md['rotation']) < 1:
            md['orientation']='Map oriented'
            md['rotation']=0.0
        else:md['orientation']='Path oriented'
        md['sunelevation']=utilities.readascii(hdr,(rec-1)*rl,1062,1065)
        md['sunazimuth']=utilities.readascii(hdr,(rec-1)*rl,1086,1090)

        
        try:##Open dataset 
            self._gdaldataset = geometry.OpenDataset(f)
            metadata=self._gdaldataset.GetMetadata()
            md['metadata']='\n'.join(['%s: %s' %(m,metadata[m]) for m in metadata])
            #Fix for Issue 17
            for i in range(1,self._gdaldataset.RasterCount+1):
                self._gdaldataset.GetRasterBand(i).SetNoDataValue(float(md['nodata']))
            
        except:#build a VRT dataset - if we want to use this for anything other than overview generation, should probably fill out the geotransform, srs, metadata etc...
            bands=bandfiles.values()
            bands.sort()
            #vrtxml=geometry.CreateRawRasterVRT(bands,md['cols'],md['rows'], md['datatype']) #Fix for Issue 17
            vrtxml=geometry.CreateRawRasterVRT(bands,md['cols'],md['rows'], md['datatype'],nodata=md['nodata'])
            self._gdaldataset = geometry.OpenDataset(vrtxml)
            md['metadata']=hdr

        if self._filetype=='HRF':
            self._gdaldataset.GetRasterBand(4).SetRasterColorInterpretation(gdal.GCI_BlueBand)
            self._gdaldataset.GetRasterBand(3).SetRasterColorInterpretation(gdal.GCI_GreenBand)
            self._gdaldataset.GetRasterBand(2).SetRasterColorInterpretation(gdal.GCI_RedBand)

        if level == 'SYSTEMATIC'  :md['level'] = '1G '
        elif level == 'SYSTERRAIN':md['level'] = '1Gt'
        elif level == 'PRECISION' :md['level'] = '1P'
        elif level == 'TERRAIN'   :md['level'] = '1T'

        md['compressionratio']=0
        md['compressiontype']='None'
        
        self.extent=ext

        for m in md:self.metadata[m]=md[m]
