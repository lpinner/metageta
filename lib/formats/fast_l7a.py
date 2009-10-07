'''
Metadata driver for ACRES Landsat FastL7A imagery
=================================================

@see:Format specification
    U{http://www.ga.gov.au/image_cache/GA10348.pdf}

@see:General info
    U{http://www.ga.gov.au/remote-sensing/satellites-sensors/landsat}
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
import utilities
import geometry
import spatialreferences

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
    
class Dataset(__dataset__.Dataset): 
    '''Subclass of base Dataset class'''
    def __init__(self,f):
        if not f:f=self.fileinfo['filepath']
        d=os.path.dirname(f)

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
        
        self.filelist=[f] #header
        self.filelist.extend([f for f in utilities.rglob(d,rex,regex=True, regex_flags=re.I, recurse=False)]) #bands
        pass
    def __getmetadata__(self):
        '''Read Metadata for an ACRES Landsat FastL7A format image as GDAL doesn't.
        Format description: http://www.ga.gov.au/image_cache/GA10348.pdf

        Note:
        hrf = ~30m VNIR/SWIR       (bands 1-5 & 7)
        htm = ~60m thermal         (band 6)
        hpn = ~15m pan             (band 8)
        '''
        
        hdr=self.fileinfo['filepath']
        d=os.path.dirname(hdr)
        
        md=self.metadata
        md['filesize']=sum([os.path.getsize(file) for file in self.filelist])

        err='Unable to open %s' % hdr
        
        txt=open(hdr).read()
        rex=re.compile('L7[0-9]{7,7}_[0-9]{11,11}_B[1-8][0-2]\.FST', re.I)
        bandnames=rex.findall(txt)
        
        rename=False
        bandfiles={}
        for band in bandnames:
            dat_u=os.path.join(d,band.upper())
            dat_l=os.path.join(d,band.lower())
            if dat_u in self.filelist:
                dat=dat_u
                bandfiles[dat]=dat
            elif dat_l in self.filelist:
                dat=dat_l
                bandfiles[dat]=dat
            else:#Have to rename the data files so GDAL can read them from ACRES format (band*.dat) to Fast format (l7*.fst)...
                dat=os.path.join(d,band)
                bandid=band[23:25]
                if bandid == '61':bandid='6l'
                elif bandid == '62':bandid='6h'
                else:bandid=bandid[0]

                bnd_u=os.path.join(d,'BAND%s.DAT' %bandid.upper())
                bnd_l=os.path.join(d,'band%s.dat' %bandid.lower())
                if bnd_u in self.filelist:bnd=bnd_u
                elif bnd_l in self.filelist:bnd=bnd_l
                else:raise IOError, err
                
                os.rename(bnd,dat)
                rename=True
                bandfiles[dat]=bnd

        nbands=len(bandnames)
        bandnums=[]

        md['sceneid']=os.path.basename(bandfiles.keys()[0])[3:21] #Use path/row & aquisition date as sceneid - L7f[ppprrr_rrrYYYYMMDD]_AAA.FST 
        if self._filetype=='HRF':
            md['bands']='1 (BLUE),2 (GREEN),3 (RED),4 (NIR),5 (SWIR),7 (SWIR)'
        elif self._filetype=='HTM':
            md['bands']='6L (THERMAL),6H (THERMAL)'
        elif self._filetype=='HPN':
            md['bands']='8 (PAN)'

        self._gdaldataset = geometry.OpenDataset(hdr)
        if not self._gdaldataset:
            errmsg=gdal.GetLastErrorMsg()
            gdal.ErrorReset()
            raise IOError, err+'\n'+ errmsg.strip()

        md['cols']=self._gdaldataset.RasterXSize
        md['rows']=self._gdaldataset.RasterYSize
        
        #Workaround for UTM zones as GDAL does not pick up southern hemisphere
        #as some FST headers don't include a negative zone number to indicate southern hemisphere
        #as per the FAST format definition
        utm=re.search('MAP PROJECTION\s*=\s*UTM',txt)
        if utm:
            #Workaround for GDA94 datum as GDAL only recognises "NAD27" "NAD83" "WGS84" "ELLIPSOID"
            #as per the FAST format definition
            gda=re.search('DATUM\s*=\s*GDA',txt)
            zone=re.findall('MAP ZONE\s*=\s*([0-9][0-9])',txt)[0]
            if gda:
                epsg=int('283'+zone)
            else:
                if re.findall(r'UL\s*=.*[EW]\s*[0-9]{6,6}\.[0-9]{4,4}([NS])',txt)[0]=='S':#Southern hemishpere
                    epsg=int('327'+zone) #Assume WGS84
                else:         #North
                    epsg=int('326'+zone)
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(epsg)
            md['srs']=srs.ExportToWkt()
            md['epsg']=epsg
            md['units']='m'
        else:
            md['srs']=self._gdaldataset.GetProjection()
            md['epsg'] = spatialreferences.IdentifyAusEPSG(md['srs'])
            md['units'] = spatialreferences.GetLinearUnitsName(md['srs'])
        md['filetype'] = self._gdaldataset.GetDriver().ShortName+'/'+self._gdaldataset.GetDriver().LongName
        
        rb=self._gdaldataset.GetRasterBand(1)
        md['datatype']=gdal.GetDataTypeName(rb.DataType)
        md['nbits']=gdal.GetDataTypeSize(rb.DataType)
        nodata=rb.GetNoDataValue()
        if nodata:md['nodata']=nodata
        else:
            if md['datatype'][0:4] in ['Byte','UInt']: md['nodata']=0 #Unsigned, assume 0
            else:md['nodata']=-2**(md['nbits']-1)                     #Signed, assume min value in data range
       
        geotransform=self._gdaldataset.GetGeoTransform()
        metadata=self._gdaldataset.GetMetadata()

        gcps=geometry.GeoTransformToGCPs(geotransform,md['cols'],md['rows'])

        ext=[[gcp.GCPX, gcp.GCPY] for gcp in gcps]
        ext.append([gcps[0].GCPX, gcps[0].GCPY])#Add the 1st point to close the polygon)

        #Reproject corners to lon,lat
        geom = geometry.GeomFromExtent(ext)
        src_srs=osr.SpatialReference()
        src_srs.ImportFromWkt(md['srs'])
        tgt_srs=osr.SpatialReference()
        tgt_srs.ImportFromEPSG(4326)
        geom=geometry.ReprojectGeom(geom,src_srs,tgt_srs)
        points=geom.GetBoundary()
        ext=[[points.GetX(i),points.GetY(i)] for i in range(0,points.GetPointCount())]

        md['cellx'],md['celly']=geometry.CellSize(geotransform)
        md['rotation']=geometry.Rotation(geotransform)
        md['UL']='%s,%s' % tuple(ext[0])
        md['UR']='%s,%s' % tuple(ext[1])
        md['LR']='%s,%s' % tuple(ext[2])
        md['LL']='%s,%s' % tuple(ext[3])
            
        metadata=self._gdaldataset.GetMetadata()

        md['satellite']=metadata['SATELLITE']
        md['sensor']=metadata['SENSOR']
        md['imgdate'] = time.strftime('%Y-%m-%d',time.strptime(metadata['ACQUISITION_DATE'],'%Y%m%d')) #ISO 8601 
        #md['imgdate']=metadata['ACQUISITION_DATE']
        md['nbands']=nbands
        if abs(md['rotation']) < 1.0: md['orientation']='Map oriented'
        else: md['orientation']='Path oriented'
        #md['bands'] = ','.join(bandnums)
        p=re.compile(r'RESAMPLING\s*=\s*([A-Z]{2,2})', re.IGNORECASE)
        md['resampling']=p.findall(txt)[0]
        p=re.compile(r'LOOK ANGLE\s*=\s*([0-9]{1,2}\.[0-9]{1,2})', re.IGNORECASE)
        md['viewangle']=p.findall(txt)[0]
        p=re.compile(r'SUN AZIMUTH ANGLE\s*=\s*([0-9]{1,2}\.[0-9]{1,2})', re.IGNORECASE)
        md['sunazimuth']=p.findall(txt)[0]
        p=re.compile(r'SUN ELEVATION ANGLE\s*=\s*([0-9]{1,2}\.[0-9]{1,2})', re.IGNORECASE)
        md['sunelevation']=p.findall(txt)[0]
        p=re.compile(r'TYPE OF PROCESSING\s*=\s*(SYSTEMATIC|SYSTERRAIN|PRECISION|TERRAIN)', re.IGNORECASE)
        level=p.findall(txt)[0]
        if level == 'SYSTEMATIC'  :md['level'] = '1G '
        elif level == 'SYSTERRAIN':md['level'] = '1Gt'
        elif level == 'PRECISION' :md['level'] = '1P'
        elif level == 'TERRAIN'   :md['level'] = '1T'
        md['metadata']='\n'.join(['%s: %s' %(m,metadata[m]) for m in metadata])
        md['compressionratio']=0
        md['compressiontype']='None'
        
        #Rename the data files back to what they were
        self._gdaldataset=None #Release gdal locks on the files
        rb=None
        del self._gdaldataset
        del rb
        if rename:
            for band in bandfiles:os.rename(band,bandfiles[band])

        self.extent=ext

        for m in md:self.metadata[m]=md[m]

        #Basic raw raster VRT for overview generation
        vrtbands=bandfiles.values()
        vrtbands.sort()
        self._gdaldataset=geometry.OpenDataset(geometry.CreateRawRasterVRT(vrtbands,md['cols'],md['rows'],md['datatype'],md['nbits']))