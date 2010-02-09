'''
Metadata driver for generic imagery
===================================
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
        try:
            cwd=os.curdir
            p=os.path.split(f)[0]
            os.chdir(p)
            filelist = utilities.GetFileList(f)
            self._gdalDataset= geometry.OpenDataset(f)
            if self._gdalDataset:
                driver=self._gdalDataset.GetDriver().ShortName
                self.metadata['filetype'] = driver+'/'+self._gdalDataset.GetDriver().LongName
                self.metadata['cols'] = self._gdalDataset.RasterXSize
                self.metadata['rows'] = self._gdalDataset.RasterYSize
                self.metadata['nbands'] = self._gdalDataset.RasterCount

                self.metadata['srs']= self._gdalDataset.GetProjection()
                if not self.metadata['srs'] and self._gdalDataset.GetGCPCount() > 0:
                    self.metadata['srs'] = self._gdalDataset.GetGCPProjection()
                self.metadata['epsg'] = spatialreferences.IdentifyAusEPSG(self.metadata['srs'])
                self.metadata['units'] = spatialreferences.GetLinearUnitsName(self.metadata['srs'])
                
                geotransform = self._gdalDataset.GetGeoTransform()
                if geotransform == (0, 1, 0, 0, 0, 1) and self._gdalDataset.GetGCPCount() > 0:
                    gcps=self._gdalDataset.GetGCPs()
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

                rb=self._gdalDataset.GetRasterBand(1)
                self.metadata['datatype']=gdal.GetDataTypeName(rb.DataType)
                self.metadata['nbits']=gdal.GetDataTypeSize(rb.DataType)
                nodata=rb.GetNoDataValue()
                if nodata:self.metadata['nodata']=nodata
                else:
                    if self.metadata['datatype'][0:4] in ['Byte','UInt']: self.metadata['nodata']=0 #Unsigned, assume 0
                    else:self.metadata['nodata']=-2**(self.metadata['nbits']-1)                     #Signed, assume min value in data range
                metadata=self._gdalDataset.GetMetadata()
                self.metadata['metadata']='\n'.join(['%s: %s' %(m,metadata[m]) for m in metadata])
                self.metadata['filesize']=sum([os.path.getsize(file) for file in filelist])
                self.metadata['filelist']=','.join(utilities.fixSeparators(filelist))
                self.metadata['compressionratio']=int((self.metadata['nbands']*self.metadata['cols']*self.metadata['rows']*(self.metadata['nbits']/8.0))/self.metadata['filesize'])
                if self.metadata['compressionratio'] > 0:
                    try:
                        if driver[0:3]=='JP2':
                            self.metadata['compressiontype']="JPEG2000"
                        elif driver[0:3]=='ECW':
                            self.metadata['compressiontype']="ECW"
                        else:
                            mdis=self._gdalDataset.GetMetadata('IMAGE_STRUCTURE')
                            self.metadata['compressiontype']=mdis['IMAGE_STRUCTURE']
                    except: self.metadata['compressiontype']='Unknown'
                else: self.metadata['compressiontype']='None'
                self.extent=ext
            else:
                errmsg=gdal.GetLastErrorMsg()
                raise IOError, 'Unable to open %s\n%s' % (f,errmsg.strip())

        finally: #Cleanup
            gdal.ErrorReset()
            os.chdir(cwd)