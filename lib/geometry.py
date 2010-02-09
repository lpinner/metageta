'''
Geometry and dataset helper functions
=====================================
'''
import os,math,warnings,tempfile


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

#========================================================================================================
#Dataset Utilities
#========================================================================================================
def OpenDataset(f,mode=gdalconst.GA_ReadOnly):
    '''Open & return a gdalDataset object'''
    gdal.ErrorReset()
    gdal.PushErrorHandler( 'CPLQuietErrorHandler' )
    gdalDataset = gdal.Open(f, mode)
    gdal.PopErrorHandler()
    return gdalDataset
    
#========================================================================================================
#Geometry Utilities
#========================================================================================================
def Rotation(gt):   
    '''
    Get rotation angle from a geotransform
    @param gt: geotransform
    '''
    try:return math.degrees(math.tanh(gt[2]/gt[5]))
    except:return 0

def CellSize(gt):   
    '''
    Get cell size from a geotransform
    @param gt: geotransform
    '''
    cellx=round(math.hypot(gt[1],gt[4]),7)
    celly=round(math.hypot(gt[2],gt[5]),7)
    return (cellx,celly)

def SceneCentre(gt,cols,rows):
    '''
    Get scene centre from a geotransform.
    
    @param gt: geotransform
    @param cols: number of columns in the dataset
    @param rows: number of rows in the dataset
    '''
    px = cols/2
    py = rows/2
    x=gt[0]+(px*gt[1])+(py*gt[2])
    y=gt[3]+(px*gt[4])+(py*gt[5])
    return x,y

def GeoTransformToGCPs(gt,cols,rows):
    ''' 
    Form a gcp list from a geotransform using the 4 corners.

    This function is meant to be used to convert a geotransform
    to gcp's so that the geocoded information can be reprojected.

    @param gt: geotransform to convert to gcps
    @param cols: number of columns in the dataset
    @param rows: number of rows in the dataset
    '''
    
    gcp_list=[]
    parr=[0,cols]
    larr=[0,rows]
    id=0
    for px in parr:
        for py in larr:
            cgcp=gdal.GCP()
            cgcp.Id=str(id)
            cgcp.GCPX=gt[0]+(px*gt[1])+(py*gt[2])
            cgcp.GCPY=gt[3]+(px*gt[4])+(py*gt[5])
            cgcp.GCPZ=0.0
            cgcp.GCPPixel=px
            cgcp.GCPLine=py
            id+=1
            gcp_list.append(cgcp)
        larr.reverse()
    return gcp_list

def GeomFromExtent(ext,srs=None,srs_wkt=None):
    if type(ext[0]) is list or type(ext[0]) is tuple: #is it a list of xy pairs
        wkt = 'POLYGON ((%s))' % ','.join(map(' '.join, [map(str, i) for i in ext]))
    else: #it's a list of xy values
        xmin,ymin,xmax,ymax=ext
        template = 'POLYGON ((%(minx)f %(miny)f, %(minx)f %(maxy)f, %(maxx)f %(maxy)f, %(maxx)f %(miny)f, %(minx)f %(miny)f))'
        r1 = {'minx': xmin, 'miny': ymin, 'maxx':xmax, 'maxy':ymax}
        wkt = template % r1
    if srs_wkt is not None:srs=osr.SpatialReference(wkt=srs_wkt)
    geom = ogr.CreateGeometryFromWkt(wkt,srs)
    return geom

def ReprojectGeom(geom,src_srs,tgt_srs):
    ''' 
    Reproject a geometry object.

    @param geom: GDAL geometry object
    @param src_srs: GDAL (OSR) SpatialReference object
    @param tgt_srs: GDAL (OSR) SpatialReference object
    '''
    gdal.ErrorReset()
    gdal.PushErrorHandler( 'CPLQuietErrorHandler' )
    geom.AssignSpatialReference(src_srs)
    geom.TransformTo(tgt_srs)
    err = gdal.GetLastErrorMsg()
    if err:warnings.warn(err.replace('\n',' '))
    gdal.PopErrorHandler()
    gdal.ErrorReset()
    return geom

#========================================================================================================
#VRT Utilities
#========================================================================================================
def CreateVRTCopy(ds):
    try:
        vrtdrv=gdal.GetDriverByName('VRT')
        vrtds=vrtdrv.CreateCopy('',ds)
        return vrtds
    except:
        return None

def CreateMosaicedVRT(files,bands,srcrects,dstrects,cols,rows,datatype,relativeToVRT=0):
    try:
        vrt=[]
        for i,band in enumerate(bands):
            vrt.append('  <VRTRasterBand dataType="%s" band="%s">' % (datatype, i+1))
            for j,f in enumerate(files):
                vrt.append('    <SimpleSource>')
                vrt.append('      <SourceFilename relativeToVRT="%s">%s</SourceFilename>' % (relativeToVRT,f))
                vrt.append('      <SourceProperties RasterXSize="%s" RasterYSize="%s" DataType="%s"/>' % (dstrects[j][2],dstrects[j][3],datatype))
                vrt.append('      <SourceBand>%s</SourceBand>' % band)
                vrt.append('      <SrcRect xOff="%s" yOff="%s" xSize="%s" ySize="%s"/>' % (srcrects[j][0],srcrects[j][1],srcrects[j][2],srcrects[j][3]))
                vrt.append('      <DstRect xOff="%s" yOff="%s" xSize="%s" ySize="%s"/>' % (dstrects[j][0],dstrects[j][1],dstrects[j][2],dstrects[j][3]))
                vrt.append('    </SimpleSource>')
                
            vrt.append('  </VRTRasterBand>')
        return CreateCustomVRT('\n'.join(vrt),cols,rows)
    except:
        raise #return None

def CreateSimpleVRT(bands,cols,rows,datatype,relativeToVRT=0):
    try:
        vrt=[]
        for i,band in enumerate(bands):
            vrt.append('  <VRTRasterBand dataType="%s" band="%s">' % (datatype, i+1))
            vrt.append('    <SimpleSource>')
            vrt.append('      <SourceFilename relativeToVRT="%s">%s</SourceFilename>' % (relativeToVRT,band))
            vrt.append('      <SourceBand>1</SourceBand>')
            vrt.append('    </SimpleSource>')
            vrt.append('  </VRTRasterBand>')
        return CreateCustomVRT('\n'.join(vrt),cols,rows)
    except:
        return None

def CreateRawRasterVRT(bands,cols,rows,datatype,nbits,headeroffset=0,byteorder=None,relativeToVRT=0):
    '''Create RawRaster VRT from one or more _single_ band files'''
    try:
        vrt=[]
        for i,band in enumerate(bands):
            vrt.append('  <VRTRasterBand dataType="%s" band="%s" subClass="VRTRawRasterBand">' % (datatype, i+1))
            vrt.append('    <SourceFilename relativeToVRT="%s">%s</SourceFilename>' % (relativeToVRT,band))
            vrt.append('    <ImageOffset>%s</ImageOffset>' % (headeroffset))
            vrt.append('    <PixelOffset>%s</PixelOffset>' % (nbits/8))
            vrt.append('    <LineOffset>%s</LineOffset>' % (nbits/8 * cols))
            if byteorder:vrt.append('    <ByteOrder>%s</ByteOrder>' % (byteorder))
            vrt.append('  </VRTRasterBand>')
        return CreateCustomVRT('\n'.join(vrt),cols,rows)
    except:
        return None
    return '\n'.join(vrt)

def CreateCustomVRT(vrtxml,vrtcols,vrtrows):
    try:
        vrt=[]
        vrt.append('<VRTDataset rasterXSize="%s" rasterYSize="%s">' % (vrtcols,vrtrows))
        vrt.append('%s' % vrtxml)
        vrt.append('</VRTDataset>')
        return '\n'.join(vrt)
    except:
        return None
    

#========================================================================================================
#Shapefile Writer
#========================================================================================================
class ShapeWriter:
    '''A class for writing geometry and fields to ESRI shapefile format'''
    def __init__(self,shapefile,fields,srs_wkt=None,overwrite=True):
        '''Open the shapefile for writing or appending'''
        try:
            gdal.ErrorReset()
            self._srs=osr.SpatialReference()
            self.fields=[]
            if srs_wkt:self._srs.ImportFromWkt(srs_wkt)
            else:self._srs.ImportFromEPSG(4283) #default=GDA94 Geographic
            self._shape=self.OpenShapefile(shapefile,fields,overwrite)
        except Exception, err:
            self.__error__(err)

    def __del__(self):
        '''Shutdown and release the lock on the shapefile'''
        gdal.ErrorReset()
        self._shape.Release()

    def __error__(self, err):
        gdalerr=gdal.GetLastErrorMsg();gdal.ErrorReset()
        errmsg = str(err)
        if gdalerr:errmsg += '\n%s' % gdalerr
        raise err.__class__, errmsg
        
    def WriteRecord(self,extent,attributes):
        '''Write record'''
        try:
            geom=GeomFromExtent(extent,self._srs)
            if self._srs.IsGeographic(): #basic coordinate bounds test. Can't do for projected though
                srs=osr.SpatialReference()
                srs.ImportFromEPSG(4283)#4326)
                valid = GeomFromExtent([-180,-90,180,90], srs=srs)
                if not valid.Contains(geom): raise ValueError, 'Invalid extent coordinates'

            lyr=self._shape.GetLayer(0)
            
            feat = ogr.Feature(lyr.GetLayerDefn())
            for a in attributes:
                if a in self.fields:feat.SetField(a, attributes[a])
            feat.SetGeometryDirectly(geom)
            lyr.CreateFeature(feat)

        except Exception, err:
            self.__error__(err)

    def OpenShapefile(self, shapefile,fields,overwrite):
        '''Open the shapefile for writing or appending'''
        try:
            driver = ogr.GetDriverByName('ESRI Shapefile')
            if os.path.exists(shapefile):
                if overwrite:
                    driver.DeleteDataSource(shapefile)
                else:
                    shp=driver.Open(shapefile,update=1)
                    lyr=shp.GetLayer(0)
                    self._srs=lyr.GetSpatialRef()
                    return shp

            shp = driver.CreateDataSource(shapefile)
            lyr=os.path.splitext(os.path.split(shapefile)[1])[0]
            lyr = shp.CreateLayer(lyr,geom_type=ogr.wkbPolygon,srs=self._srs)
            for f in fields:
                #Get field types
                if type(fields[f]) in [list,tuple]:
                    ftype=fields[f][0]
                    fwidth=fields[f][1]
                else:
                    ftype=fields[f]
                    fwidth=0
                if ftype.upper()=='STRING':
                    fld = ogr.FieldDefn(f, ogr.OFTString)
                    fld.SetWidth(fwidth)
                    lyr.CreateField(fld)
                    self.fields.append(f)
                elif ftype.upper()=='INT':
                    fld = ogr.FieldDefn(f, ogr.OFTInteger)
                    lyr.CreateField(fld)
                    self.fields.append(f)
                elif ftype.upper()=='FLOAT':
                    fld = ogr.FieldDefn(f, ogr.OFTReal)
                    lyr.CreateField(fld)
                    self.fields.append(f)
                else:pass
                    #raise AttributeError, 'Invalid field definition'

            return shp

        except Exception, err:
            self.__error__(err)