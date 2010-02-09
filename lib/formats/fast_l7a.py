'''
Metadata driver for ACRES Landsat FastL7A imagery
=================================================

@see:Format specification
    U{http://www.ga.gov.au/image_cache/GA10348.pdf}
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
        '''Read Metadata for an ACRES Landsat FastL7A format image as GDAL doesn't.
        Format description: http://www.ga.gov.au/image_cache/GA10348.pdf
        '''

        p=os.path.split(f)
        
        hdr=open(f).read()
        bands=re.findall('L7[0-9]{7,7}_[0-9]{11,11}_B[1-8][0-2]\.FST',hdr)

        nbands=len(bands)
        bandnums=[]
        filelist=[f]
        filelist_regex = r'header\..*$|report\..*$|readme.*$|.*\.ers$|.*\.png$|.*\.jpg$|.*\.txt$'

        for fl in utilities.rglob(p[0],filelist_regex, regex=True, regex_flags=re.I, recurse=False):
            filelist.append(fl)

        #May have to rename the data files so GDAL can read them...
        gdalDataset = geometry.OpenDataset(f)
        if gdalDataset:
            rename=False
        else:  #Couldn't open the FAST file
            rename=True
            gdalDataset=None

        #If we've renamed the files from ACRES band*.dat to proper Fast format l7*.fst
        if not gdalDataset:gdalDataset = geometry.OpenDataset(f) #Try opening the renamed file again 
        if not gdalDataset:
            errmsg=gdal.GetLastErrorMsg()
            gdal.ErrorReset()
            raise IOError, 'Unable to process '+f+'\n'+ errmsg.strip()

        self.metadata['cols']=gdalDataset.RasterXSize
        self.metadata['rows']=gdalDataset.RasterYSize
        
        #Workaround for UTM zones as GDAL does not pick up southern hemisphere
        #as some FST header don't include a negative zone number to indicate southern hemisphere
        #as per the FAST format definition
        utm=re.search('MAP PROJECTION\s*=\s*UTM',hdr)
        if utm:
            #Workaround for GDA94 datum as GDAL only recognises "NAD27" "NAD83" "WGS84" "ELLIPSOID"
            #as per the FAST format definition
            gda=re.search('DATUM\s*=\s*GDA',hdr)
            zone=re.findall('MAP ZONE\s*=\s*([0-9][0-9])',hdr)[0]
            if gda:
                epsg=int('283'+zone)
            else:
                if re.findall(r'UL\s*=.*[EW]\s*[0-9]{6,6}\.[0-9]{4,4}([NS])',hdr)[0]=='S':#Southern hemishpere
                    epsg=int('327'+zone) #Assume WGS84
                else:         #North
                    epsg=int('326'+zone)
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(epsg)
            self.metadata['srs']=srs.ExportToWkt()
            self.metadata['epsg']=epsg
            self.metadata['units']='m'
        else:
            self.metadata['srs']=gdalDataset.GetProjection()
            self.metadata['epsg'] = spatialreferences.IdentifyAusEPSG(self.metadata['srs'])
            self.metadata['units'] = spatialreferences.GetLinearUnitsName(self.metadata['srs'])
        self.metadata['filetype'] = gdalDataset.GetDriver().ShortName+'/'+gdalDataset.GetDriver().LongName
        
        for band in bands:
            if band[23]=='6':
                num=band[23:25]
                if band[24]=='1':nam='6l'
                else:nam='6h'
            else:num,nam=band[23],band[23]
            bandnums.append(num)
            if rename:
                filelist.extend(glob.glob(os.path.join(p[0],'band%s*.*' % nam)))
                if not os.path.exists(band) and os.path.exists('band%s.dat' % nam):os.rename('band%s.dat' % nam,band)
            else:
                filelist.append(os.path.join(p[0],band))
            
        rb=gdalDataset.GetRasterBand(1)
        self.metadata['datatype']=gdal.GetDataTypeName(rb.DataType)
        self.metadata['nbits']=gdal.GetDataTypeSize(rb.DataType)
        nodata=rb.GetNoDataValue()
        if nodata:self.metadata['nodata']=nodata
        else:
            if self.metadata['datatype'][0:4] in ['Byte','UInt']: self.metadata['nodata']=0 #Unsigned, assume 0
            else:self.metadata['nodata']=-2**(self.metadata['nbits']-1)                     #Signed, assume min value in data range
       
        geotransform=gdalDataset.GetGeoTransform()
        metadata=gdalDataset.GetMetadata()

        gcps=geometry.GeoTransformToGCPs(geotransform,self.metadata['cols'],self.metadata['rows'])

        ext=[[gcp.GCPX, gcp.GCPY] for gcp in gcps]
        ext.append([gcps[0].GCPX, gcps[0].GCPY])#Add the 1st point to close the polygon)

        #Reproject corners to lon,lat
        geom = geometry.GeomFromExtent(ext)
        src_srs=osr.SpatialReference()
        src_srs.ImportFromWkt(self.metadata['srs'])
        tgt_srs=osr.SpatialReference()
        tgt_srs.ImportFromEPSG(4326)
        geom=geometry.ReprojectGeom(geom,src_srs,tgt_srs)
        points=geom.GetBoundary()
        ext=[[points.GetX(i),points.GetY(i)] for i in range(0,points.GetPointCount())]

        self.metadata['cellx'],self.metadata['celly']=geometry.CellSize(geotransform)
        self.metadata['rotation']=geometry.Rotation(geotransform)
        self.metadata['UL']='%s,%s' % tuple(ext[0])
        self.metadata['UR']='%s,%s' % tuple(ext[1])
        self.metadata['LR']='%s,%s' % tuple(ext[2])
        self.metadata['LL']='%s,%s' % tuple(ext[3])
            
        metadata=gdalDataset.GetMetadata()

        self.metadata['satellite']=metadata['SATELLITE']
        self.metadata['sensor']=metadata['SENSOR']
        self.metadata['imgdate'] = time.strftime('%Y-%m-%d',time.strptime(metadata['ACQUISITION_DATE'],'%Y%m%d')) #ISO 8601 
        #self.metadata['imgdate']=metadata['ACQUISITION_DATE']
        self.metadata['nbands']=nbands
        if abs(self.metadata['rotation']) < 1.0: self.metadata['orientation']='Map oriented'
        else: self.metadata['orientation']='Path oriented'
        self.metadata['nbands'] = nbands
        self.metadata['bands'] = ','.join(bandnums)
        p=re.compile(r'RESAMPLING\s*=\s*([A-Z]{2,2})', re.IGNORECASE)
        self.metadata['resampling']=p.findall(hdr)[0]
        p=re.compile(r'LOOK ANGLE\s*=\s*([0-9]{1,2}\.[0-9]{1,2})', re.IGNORECASE)
        self.metadata['viewangle']=p.findall(hdr)[0]
        p=re.compile(r'SUN AZIMUTH ANGLE\s*=\s*([0-9]{1,2}\.[0-9]{1,2})', re.IGNORECASE)
        self.metadata['sunazimuth']=p.findall(hdr)[0]
        p=re.compile(r'SUN ELEVATION ANGLE\s*=\s*([0-9]{1,2}\.[0-9]{1,2})', re.IGNORECASE)
        self.metadata['sunelevation']=p.findall(hdr)[0]
        p=re.compile(r'TYPE OF PROCESSING\s*=\s*(SYSTEMATIC|SYSTERRAIN|PRECISION|TERRAIN)', re.IGNORECASE)
        level=p.findall(hdr)[0]
        if level == 'SYSTEMATIC'  :self.metadata['level'] = '1G '
        elif level == 'SYSTERRAIN':self.metadata['level'] = '1Gt'
        elif level == 'PRECISION' :self.metadata['level'] = '1P'
        elif level == 'TERRAIN'   :self.metadata['level'] = '1T'
        self.metadata['metadata']='\n'.join(['%s: %s' %(m,metadata[m]) for m in metadata])
        self.metadata['compressionratio']=0
        self.metadata['compressiontype']='None'
        
        #Rename the data files back to what they were
        gdalDataset=None
        rb=None
        del gdalDataset
        del rb
        for band in bands:
            if band[23:25]=='61':nam='6l'
            elif band[23:25]=='62':nam='6h'
            else:nam=band[23]
            if rename: os.rename(band,'band%s.dat' % nam)

        self.metadata['filesize']=sum([os.path.getsize(file) for file in filelist])
        self.metadata['filelist']=','.join(utilities.fixSeparators(filelist))
        self.extent=ext
