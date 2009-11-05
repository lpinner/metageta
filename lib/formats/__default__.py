'''
Metadata driver for generic imagery formats including GDAL Virtual Rasters (VRT files and xml strings)
=======================================================================================================
'''

format_regex=[
    r'\.ers$',
    r'\.img$',
    r'\.ecw$',
    r'\.sid$',
    r'\.jp2$',
    r'\.tif$'
]

import sys, os, re, glob, time, math, string
import utilities
import geometry
import spatialreferences
import __dataset__

import warnings,logging
warnings.formatwarning=lambda *args:str(args[0])+'\n'

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
    '''Default Dataset class.
    For generic imagery formats that gdal can read.'''
    def __init__(self,f):
        pass
    def __getmetadata__(self,f=None): 
        '''
        Generate metadata for generic imagery

        @type  f: string
        @param f: a filepath to the dataset or a VRT XML string
        @return:  None
        '''
        if not f:f=self.fileinfo['filepath']
        try:
            cwd=os.path.abspath(os.curdir)
            if os.path.exists(f):
                p=os.path.split(f)[0]
                os.chdir(p)
            self._gdaldataset= geometry.OpenDataset(f)
            if self._gdaldataset:
                driver=self._gdaldataset.GetDriver().ShortName
                self.metadata['filetype'] = driver+'/'+self._gdaldataset.GetDriver().LongName
                self.metadata['cols'] = self._gdaldataset.RasterXSize
                self.metadata['rows'] = self._gdaldataset.RasterYSize
                self.metadata['nbands'] = self._gdaldataset.RasterCount

                self.metadata['srs']= self._gdaldataset.GetProjection()
                if not self.metadata['srs'] and self._gdaldataset.GetGCPCount() > 0:
                    self.metadata['srs'] = self._gdaldataset.GetGCPProjection()
                self.metadata['epsg'] = spatialreferences.IdentifyAusEPSG(self.metadata['srs'])
                self.metadata['units'] = spatialreferences.GetLinearUnitsName(self.metadata['srs'])
                
                geotransform = self._gdaldataset.GetGeoTransform()
                if geotransform == (0, 1, 0, 0, 0, 1) and self._gdaldataset.GetGCPCount() > 0:
                    gcps=self._gdaldataset.GetGCPs()
                    geotransform=gdal.GCPsToGeoTransform(gcps)
                    gcps=geometry.GeoTransformToGCPs(geotransform,self.metadata['cols'],self.metadata['rows']) #Just get the 4 corner GCP's
                else:
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
                if abs(self.metadata['rotation']) < 1.0:
                    self.metadata['orientation']='Map oriented'
                    self.metadata['rotation']=0.0
                else: self.metadata['orientation']='Path oriented'
                self.metadata['UL']='%s,%s' % tuple(ext[0])
                self.metadata['UR']='%s,%s' % tuple(ext[1])
                self.metadata['LR']='%s,%s' % tuple(ext[2])
                self.metadata['LL']='%s,%s' % tuple(ext[3])

                rb=self._gdaldataset.GetRasterBand(1)
                self.metadata['datatype']=gdal.GetDataTypeName(rb.DataType)
                self.metadata['nbits']=gdal.GetDataTypeSize(rb.DataType)
                nodata=rb.GetNoDataValue()
                if nodata:self.metadata['nodata']=nodata
                else:
                    if self.metadata['datatype'][0:4] in ['Byte','UInt']: self.metadata['nodata']=0 #Unsigned, assume 0
                    else:self.metadata['nodata']=-2**(self.metadata['nbits']-1)                     #Signed, assume min value in data range
                metadata=self._gdaldataset.GetMetadata()
                self.metadata['metadata']='\n'.join(['%s: %s' %(m,metadata[m]) for m in metadata])
                self.metadata['filesize']=sum([os.path.getsize(tmp) for tmp in self.filelist])
                #self.metadata['filelist']=','.join(self.filelist)
                if self.metadata['filesize']>0:self.metadata['compressionratio']=int((self.metadata['nbands']*self.metadata['cols']*self.metadata['rows']*(self.metadata['nbits']/8.0))/self.metadata['filesize'])
                if self.metadata['compressionratio'] > 0:
                    try:
                        if driver[0:3]=='JP2':
                            self.metadata['compressiontype']="JPEG2000"
                        elif driver[0:3]=='ECW':
                            self.metadata['compressiontype']="ECW"
                        else:
                            mdis=self._gdaldataset.GetMetadata('IMAGE_STRUCTURE')
                            #self.metadata['compressiontype']=mdis['IMAGE_STRUCTURE']
                            self.metadata['compressiontype']=mdis['COMPRESSION']
                    except: self.metadata['compressiontype']='Unknown'
                else: self.metadata['compressiontype']='None'
                self.extent=ext
            else:
                errmsg=gdal.GetLastErrorMsg()
                raise IOError, 'Unable to open %s\n%s' % (f,errmsg.strip())

        finally: #Cleanup
            gdal.ErrorReset()
            os.chdir(cwd)

