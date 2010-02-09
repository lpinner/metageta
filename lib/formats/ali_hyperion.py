'''
Metadata driver for EO1 ALI (L1G & L1R) & Hyperion (L1R) images
===============================================================
@see:Format specifications

  HDF format:U{http://www.gdal.org/frmt_hdf4.html}

  Hyperion/ALI format:U{http://eo1.usgs.gov/userGuide/index.php}

@todo: extract stuff from FDGC metadata?
'''
#Regular expression list of file formats
format_regex=[r'eo1.*\.[lm]1r$',     #EO1 ALI (L1R) & Hyperion
              r'eo1.*_hdf\.l1g$',    #EO1 ALI (L1G) HDF
              r'eo1.*_mtl\.tif$']    #EO1 ALI (L1G) TIFF

#import base dataset module
import __dataset__

# import other modules (use "_"  prefix to import privately)
import sys, os, re, glob, time, math, string
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
    
class Dataset(__dataset__.Dataset):
    '''Subclass of base Dataset class'''
    def __init__(self,f):
        '''Read Metadata for recognised EO1 ALI (L1G & L1R) & Hyperion (L1R) images as GDAL doesn't'''

        self.metadata['satellite']='E01'
        
        if re.search(r'\.m[1-4]r$', f):
            self.metadata['level']='L1R'
            self.metadata['sensor']='ALI'

            gdalDataset = geometry.OpenDataset(f)
            if not gdalDataset:
                errmsg=gdal.GetLastErrorMsg()
                raise IOError, 'Unable to open %s\n%s' % (f,errmsg.strip())

            self.metadata['filetype'] = '%s/%s (%s %s)' % (gdalDataset.GetDriver().ShortName,
                                                           gdalDataset.GetDriver().LongName,
                                                           self.metadata['sensor'],
                                                           self.metadata['level'])

            filelist=glob.glob(os.path.splitext(f)[0]+'.*')
            filelist.extend(glob.glob('%s\\%s_%s_*.hdf' % (os.path.dirname(f),os.path.basename(f)[10:14],os.path.basename(f)[14:17])))

            srs=osr.SpatialReference()
            srs.ImportFromEPSG(4326)
            self.metadata['srs']= srs.ExportToWkt()
            self.metadata['epsg']= 4326
            self.metadata['units']= 'deg'

            hdf_sd=gdalDataset.GetSubDatasets()
            hdf_md=gdalDataset.GetMetadata()
            sd,sz = hdf_sd[0]
            sd=geometry.OpenDataset(sd)
            sd_md=sd.GetMetadata()
            nbands=sd.RasterCount
            ncols=str(sd.RasterXSize*4-30) #Account for the four SCA strips and the overlap between SCA strips
            nrows=sd_md['Number of along track pixels'] #sd.RasterYSize is incorrect
            if len(hdf_sd) == 6:#Includes pan band (3 sds each)
                sd,sz = hdf_sd[3]
                sd=geometry.OpenDataset(sd)
                sd_md=sd.GetMetadata()
                #Make a csv list of cols, bands
                ncols=[ncols for i in range(0,nbands)]
                nrows=[nrows for i in range(0,nbands)]
                #nbands='%s,%s' % (nbands, sd_md['Number of bands'])
                nbands=nbands+int(sd_md['Number of bands'])
                cols=str(int(sd_md['Number of cross track pixels'])*4-30)#Account for the four SCA strips and the overlap between SCA strips
                rows=sd_md['Number of along track pixels']
                ncols.extend([cols for i in range(0,sd.RasterCount)]) 
                nrows.extend([rows for i in range(0,sd.RasterCount)])
                ncols=','.join(ncols)
                nrows=','.join(nrows)

            met=os.path.splitext(f)[0]+'.met'
            for line in open(met, 'r').readlines():
                if line[0:16]=='Scene Request ID':
                    line=line.strip().split()
                    self.metadata['sceneid']=line[3]
                if line[0:14]=='ALI Start Time':
                    line=line.strip().split()
                    hdf_md['ImageStartTime']=line[3]+line[4]
                if line[0:8]=='PRODUCT_':
                    line=line.strip()
                    line=map(string.strip, line.split('='))
                    if line[0]=='PRODUCT_UL_CORNER_LAT':uly=float(line[1])
                    if line[0]=='PRODUCT_UL_CORNER_LON':ulx=float(line[1])
                    if line[0]=='PRODUCT_UR_CORNER_LAT':ury=float(line[1])
                    if line[0]=='PRODUCT_UR_CORNER_LON':urx=float(line[1])
                    if line[0]=='PRODUCT_LR_CORNER_LAT':lry=float(line[1])
                    if line[0]=='PRODUCT_LR_CORNER_LON':lrx=float(line[1])
                    if line[0]=='PRODUCT_LL_CORNER_LAT':lly=float(line[1])
                    if line[0]=='PRODUCT_LL_CORNER_LON':llx=float(line[1])
            geoext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]
            prjext=geoext
        elif re.search(r'eo1.*_mtl\.tif$', f):
            self.metadata['level']='L1G'
            self.metadata['sensor']='ALI'
            self.metadata['sceneid']=self.metadata['filename'].split('_')[0]
            self.metadata['filetype'] = 'GTiff/GeoTIFF (%s %s)' % (self.metadata['sensor'],self.metadata['level'])

            filelist=glob.glob(os.path.dirname(f)+'/*')
            ncols=[]
            nrows=[]
            nbands=0
            for band in glob.glob(os.path.dirname(f)+'/eo1*_b*.tif'):
                band=geometry.OpenDataset(band)
                ncols.append(str(band.RasterXSize))
                nrows.append(str(band.RasterYSize))
                nbands+=1
                #rb=sd.GetRasterBand(1)
            ncols=','.join(ncols)
            nrows=','.join(nrows)
            met=f
            md={}
            for line in open(met, 'r'):
                line=line.replace('"','')
                line=[l.strip() for l in line.split('=')]
                if line[0]=='END':         #end of the metadata file
                    break
                elif line[0]=='GROUP':     #start of a metadata group
                    if line[1]!='L1_METADATA_FILE':
                        group = line[1]
                        md[group]={}
                elif line[0]=='END_GROUP': #end of a metadata group
                    pass
                else:                     #metadata value
                    md[group][line[0]]=line[1]

            uly=float(md['PRODUCT_METADATA']['PRODUCT_UL_CORNER_LAT'])
            ulx=float(md['PRODUCT_METADATA']['PRODUCT_UL_CORNER_LON'])
            ury=float(md['PRODUCT_METADATA']['PRODUCT_UR_CORNER_LAT'])
            urx=float(md['PRODUCT_METADATA']['PRODUCT_UR_CORNER_LON'])
            lry=float(md['PRODUCT_METADATA']['PRODUCT_LR_CORNER_LAT'])
            lrx=float(md['PRODUCT_METADATA']['PRODUCT_LR_CORNER_LON'])
            lly=float(md['PRODUCT_METADATA']['PRODUCT_LL_CORNER_LAT'])
            llx=float(md['PRODUCT_METADATA']['PRODUCT_LL_CORNER_LON'])
            geoext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]

            uly=float(md['PRODUCT_METADATA']['PRODUCT_UL_CORNER_MAPY'])
            ulx=float(md['PRODUCT_METADATA']['PRODUCT_UL_CORNER_MAPX'])
            ury=float(md['PRODUCT_METADATA']['PRODUCT_UR_CORNER_MAPY'])
            urx=float(md['PRODUCT_METADATA']['PRODUCT_UR_CORNER_MAPX'])
            lry=float(md['PRODUCT_METADATA']['PRODUCT_LR_CORNER_MAPY'])
            lrx=float(md['PRODUCT_METADATA']['PRODUCT_LR_CORNER_MAPX'])
            lly=float(md['PRODUCT_METADATA']['PRODUCT_LL_CORNER_MAPY'])
            llx=float(md['PRODUCT_METADATA']['PRODUCT_LL_CORNER_MAPX'])
            prjext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]
            
            self.metadata['imgdate']=md['PRODUCT_METADATA']['ACQUISITION_DATE']
            self.metadata['resampling']=md['PROJECTION_PARAMETERS']['RESAMPLING_OPTION']
            try:self.metadata['viewangle']=float(md['PRODUCT_PARAMETERS']['SENSOR_LOOK_ANGLE'])
            except:pass #Exception raised if value == 'UNAVAILABLE'
            try:self.metadata['sunazimuth']=float(md['PRODUCT_PARAMETERS']['SUN_AZIMUTH'])
            except:pass #Exception raised if value == 'UNAVAILABLE'
            try:self.metadata['sunelevation']=float(md['PRODUCT_PARAMETERS']['SUN_ELEVATION'])
            except:pass #Exception raised if value == 'UNAVAILABLE'

            #EPSG:32601: WGS 84 / UTM zone 1N
            #EPSG:32701: WGS 84 / UTM zone 1S
            srs=osr.SpatialReference()
            zone=int(md['UTM_PARAMETERS']['ZONE_NUMBER'])
            if zone > 0:epsg=32600 + zone #North
            else:       epsg=32700 - zone #South
            srs.ImportFromEPSG(epsg)
            self.metadata['units']= 'm'
            self.metadata['srs']= srs.ExportToWkt()
            self.metadata['epsg']= str(epsg)
            
        elif re.search(r'eo1.*_hdf\.l1g$', f):
            self.metadata['level']='L1G'
            self.metadata['sensor']='ALI'
            self.metadata['sceneid']=self.metadata['filename'].split('_')[0]
            filelist=glob.glob(os.path.dirname(f)+'/*')

            gdalDataset = geometry.OpenDataset(f)
            if not gdalDataset:
                errmsg=gdal.GetLastErrorMsg()
                raise IOError, 'Unable to open %s\n%s' % (f,errmsg.strip())

                self.metadata['filetype'] = '%s/%s (%s %s)' % (gdalDataset.GetDriver().ShortName,
                                                           gdalDataset.GetDriver().LongName,
                                                           self.metadata['sensor'],
                                                           self.metadata['level'])

            hdf_sd=gdalDataset.GetSubDatasets()
            hdf_md=gdalDataset.GetMetadata()
            sd,sz = hdf_sd[0]
            sd=geometry.OpenDataset(sd)
            sd_md=sd.GetMetadata()
            ncols=[]
            nrows=[]
            nbands=0
            for sd,sz in hdf_sd:
                sd=geometry.OpenDataset(sd)
                ncols.append(str(sd.RasterXSize))
                nrows.append(str(sd.RasterYSize))
                nbands+=1
            ncols=','.join(ncols)
            nrows=','.join(nrows)
            met=f.lower().replace('_hdf.l1g','_mtl.l1g')
            md={}
            for line in open(met, 'r'):
                line=line.replace('"','')
                line=[l.strip() for l in line.split('=')]
                if line[0]=='END':         #end of the metadata file
                    break
                elif line[0]=='GROUP':     #start of a metadata group
                    if line[1]!='L1_METADATA_FILE':
                        group = line[1]
                        md[group]={}
                elif line[0]=='END_GROUP': #end of a metadata group
                    pass
                else:                     #metadata value
                    md[group][line[0]]=line[1]

            uly=float(md['PRODUCT_METADATA']['PRODUCT_UL_CORNER_LAT'])
            ulx=float(md['PRODUCT_METADATA']['PRODUCT_UL_CORNER_LON'])
            ury=float(md['PRODUCT_METADATA']['PRODUCT_UR_CORNER_LAT'])
            urx=float(md['PRODUCT_METADATA']['PRODUCT_UR_CORNER_LON'])
            lry=float(md['PRODUCT_METADATA']['PRODUCT_LR_CORNER_LAT'])
            lrx=float(md['PRODUCT_METADATA']['PRODUCT_LR_CORNER_LON'])
            lly=float(md['PRODUCT_METADATA']['PRODUCT_LL_CORNER_LAT'])
            llx=float(md['PRODUCT_METADATA']['PRODUCT_LL_CORNER_LON'])
            geoext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]
            prjext=geoext
            
            self.metadata['imgdate']=md['PRODUCT_METADATA']['ACQUISITION_DATE']
            self.metadata['resampling']=md['PROJECTION_PARAMETERS']['RESAMPLING_OPTION']
            try:self.metadata['viewangle']=float(md['PRODUCT_PARAMETERS']['SENSOR_LOOK_ANGLE'])
            except:pass #Exception raised if value == 'UNAVAILABLE'
            try:self.metadata['sunazimuth']=float(md['PRODUCT_PARAMETERS']['SUN_AZIMUTH'])
            except:pass #Exception raised if value == 'UNAVAILABLE'
            try:self.metadata['sunelevation']=float(md['PRODUCT_PARAMETERS']['SUN_ELEVATION'])
            except:pass #Exception raised if value == 'UNAVAILABLE'

            #EPSG:32601: WGS 84 / UTM zone 1N
            #EPSG:32701: WGS 84 / UTM zone 1S
            srs=osr.SpatialReference()
            zone=int(md['UTM_PARAMETERS']['ZONE_NUMBER'])
            if zone > 0:epsg=32600 + zone #North
            else:       epsg=32700 - zone #South
            srs.ImportFromEPSG(epsg)
            self.metadata['units']= 'm'
            self.metadata['srs']= srs.ExportToWkt()
            self.metadata['epsg']= str(epsg)
            
        else:
            self.metadata['level']='L1R'
            self.metadata['sensor']='HYPERION'
            filelist=glob.glob(os.path.splitext(f)[0]+'.*')
            filelist.extend(glob.glob('%s\\%s_%s_*.hdf' % (os.path.dirname(f),os.path.basename(f)[10:14],os.path.basename(f)[14:17])))

            gdalDataset = geometry.OpenDataset(f)
            if not gdalDataset:
                errmsg=gdal.GetLastErrorMsg()
                raise IOError, 'Unable to open %s\n%s' % (f,errmsg.strip())

            self.metadata['filetype'] = '%s/%s (%s %s)' % (gdalDataset.GetDriver().ShortName,
                                                           gdalDataset.GetDriver().LongName,
                                                           self.metadata['sensor'],
                                                           self.metadata['level'])
            srs=osr.SpatialReference()
            srs.ImportFromEPSG(4326)
            self.metadata['srs']= srs.ExportToWkt()
            self.metadata['epsg']= 4326
            self.metadata['units']= 'deg'

            hdf_sd=gdalDataset.GetSubDatasets()
            hdf_md=gdalDataset.GetMetadata()
            sd,sz = hdf_sd[0]
            sd=geometry.OpenDataset(sd)
            sd_md=sd.GetMetadata()
            nbands=sd.RasterCount
            ncols=sd.RasterXSize
            nrows=sd.RasterYSize
            met=os.path.splitext(f)[0]+'.met'
            for line in open(met, 'r').readlines():
                if line[0:16]=='Scene Request ID':
                    line=line.strip().split()
                    self.metadata['sceneid']=line[3]
                if line[0:14]=='HYP Start Time':
                    line=line.strip().split()
                    imgdate=time.strptime(line[3]+line[4], '%Y%j')
                    self.metadata['imgdate']=time.strftime('%Y-%m-%d',imgdate)#ISO 8601 
                if line[0:8]=='PRODUCT_':
                    line=line.strip()
                    line=map(string.strip, line.split('='))
                    if line[0]=='PRODUCT_UL_CORNER_LAT':uly=float(line[1])
                    if line[0]=='PRODUCT_UL_CORNER_LON':ulx=float(line[1])
                    if line[0]=='PRODUCT_UR_CORNER_LAT':ury=float(line[1])
                    if line[0]=='PRODUCT_UR_CORNER_LON':urx=float(line[1])
                    if line[0]=='PRODUCT_LR_CORNER_LAT':lry=float(line[1])
                    if line[0]=='PRODUCT_LR_CORNER_LON':lrx=float(line[1])
                    if line[0]=='PRODUCT_LL_CORNER_LAT':lly=float(line[1])
                    if line[0]=='PRODUCT_LL_CORNER_LON':llx=float(line[1])
            geoext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]
            prjext=geoext

        self.metadata['cols'] = ncols
        self.metadata['rows'] = nrows
        self.metadata['nbands'] = nbands
        self.metadata['nbits'] = 16
        self.metadata['datatype']='Int16'
        self.metadata['nodata']=0

        #Geotransform
        ncols=map(int, str(ncols).split(','))
        nrows=map(int, str(nrows).split(','))
        cellx,celly=[],[]
        j=0
        while j < len(ncols):
            gcps=[];i=0
            lr=[[0,0],[ncols[j],0],[ncols[j],nrows[j]],[0,nrows[j]]]
            while i < len(prjext)-1: #don't need the last xy pair
                gcp=gdal.GCP()
                gcp.GCPPixel,gcp.GCPLine=lr[i]
                gcp.GCPX,gcp.GCPY=prjext[i]
                gcp.Id=str(i)
                gcps.append(gcp)
                i+=1
            j+=1
            geotransform = gdal.GCPsToGeoTransform(gcps)
            x,y=geometry.CellSize(geotransform)
            cellx.append(str(x))
            celly.append(str(abs(y)))
        
        self.metadata['cellx']=','.join(cellx)
        self.metadata['celly']=','.join(celly)

        self.metadata['UL']='%s,%s' % tuple(geoext[0])
        self.metadata['UR']='%s,%s' % tuple(geoext[1])
        self.metadata['LR']='%s,%s' % tuple(geoext[2])
        self.metadata['LL']='%s,%s' % tuple(geoext[3])
        
        self.metadata['rotation']=geometry.Rotation(geotransform)
        if abs(self.metadata['rotation']) < 1.0:
            self.metadata['orientation']='Map oriented'
            self.metadata['rotation']=0.0
        else:self.metadata['orientation']='Path oriented'

        self.metadata['filesize']=sum([os.path.getsize(file) for file in filelist])
        self.metadata['filelist']=','.join(utilities.fixSeparators(filelist))
        self.metadata['compressionratio']=0
        self.metadata['compressiontype']='None'
        self.extent=geoext
