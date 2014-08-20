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
Metadata driver for EO1 ALI (L1G & L1R) & Hyperion (L1R) images

@see:Format specifications

  HDF format:U{http://www.gdal.org/frmt_hdf4.html}

  Hyperion/ALI format:U{http://eo1.usgs.gov/userGuide/index.php}

@todo: extract stuff from FDGC metadata?
'''


format_regex=[r'eo1[ah].*\.[lm]1r$',     #EO1 ALI (L1R) & Hyperion
              r'eo1.*_hdf\.l1g$',    #EO1 ALI (L1G) HDF
              r'eo1.*_mtl\.tif$',    #EO1 ALI (L1G) TIFF
              r'eo1.*_mtl_.*\.l1t$'] #EO1 ALI & Hyperion (L1T) TIFF
'''Regular expression list of file formats'''

#import base dataset module
import __dataset__

# import other modules (use "_"  prefix to import privately)
import sys, os, re, glob, time, math, string
from metageta import utilities, geometry
from landsat_mtl import parseheader

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
        if f[:4]=='/vsi':raise NotImplementedError
        self.filelist=glob.glob(os.path.dirname(f)+'/*') #Assume raw data - all files in current dir belong to this dataset.
        #filelist=glob.glob(os.path.splitext(f)[0]+'.*')
        #filelist.extend(glob.glob('%s\\%s_%s_*.hdf' % (os.path.dirname(f),os.path.basename(f)[10:14],os.path.basename(f)[14:17])))
    def __getmetadata__(self):
        '''Read Metadata for recognised EO1 ALI (L1G & L1R) & Hyperion (L1R) images as GDAL doesn't'''

        f=self.fileinfo['filepath']
        self.metadata['satellite']='E01'
        self.metadata['nbits'] = 16
        self.metadata['datatype']='Int16'
        self.metadata['nodata']=0
        if re.search(r'eo1a.*\.m[1-4]r$', f, re.I):
            self.ali_l1r(f)
        elif re.search(r'eo1.*_mtl\.tif$', f):
            self.ali_l1g_tiff(f)
        elif re.search(r'eo1.*_hdf\.l1g$', f):
            self.ali_l1g_hdf(f)
        elif re.search(r'eo1h.*\.l[1-4]r$', f):
            self.hyp_l1r(f)
        elif re.search(r'eo1.*_mtl_.*\.l1t$', f, re.I):
            self.hyp_l1t(f)

        self.metadata['cols'] = self.ncols
        self.metadata['rows'] = self.nrows
        self.metadata['nbands'] = self.nbands

        #Geotransform
        ncols=map(int, str(self.ncols).split(','))
        nrows=map(int, str(self.nrows).split(','))
        cellx,celly=[],[]
        j=0
        while j < len(ncols):
            gcps=[];i=0
            lr=[[0,0],[ncols[j],0],[ncols[j],nrows[j]],[0,nrows[j]]]
            while i < len(self.prjext)-1: #don't need the last xy pair
                gcp=gdal.GCP()
                gcp.GCPPixel,gcp.GCPLine=lr[i]
                gcp.GCPX,gcp.GCPY=self.prjext[i]
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

        self.metadata['UL']='%s,%s' % tuple(self.geoext[0])
        self.metadata['UR']='%s,%s' % tuple(self.geoext[1])
        self.metadata['LR']='%s,%s' % tuple(self.geoext[2])
        self.metadata['LL']='%s,%s' % tuple(self.geoext[3])

        self.metadata['rotation']=geometry.Rotation(geotransform)
        if abs(self.metadata['rotation']) < 1.0:
            self.metadata['orientation']='Map oriented'
            self.metadata['rotation']=0.0
        else:self.metadata['orientation']='Path oriented'

        self.metadata['filesize']=sum([os.path.getsize(tmp) for tmp in self.filelist])
        self.metadata['compressionratio']=0
        self.metadata['compressiontype']='None'
        self.extent=self.geoext

    def ali_l1r(self,f):
            self.metadata['level']='L1R'
            self.metadata['sensor']='ALI'

            gdalDataset = geometry.OpenDataset(f)
            #if not gdalDataset: #Error now raised in geometry.OpenDataset
            #    errmsg=gdal.GetLastErrorMsg()
            #    raise IOError, 'Unable to open %s\n%s' % (f,errmsg.strip())

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
            self.nbands=sd.RasterCount
            self.ncols=str(sd.RasterXSize*4-30) #Account for the four SCA strips and the overlap between SCA strips
            self.nrows=sd_md['Number of along track pixels'] #sd.RasterYSize is incorrect
            if len(hdf_sd) == 6:#Includes pan band (3 sds each)
                sd,sz = hdf_sd[3]
                sd=geometry.OpenDataset(sd)
                sd_md=sd.GetMetadata()
                cols=str(int(sd_md['Number of cross track pixels'])*4-30)#Account for the four SCA strips and the overlap between SCA strips
                rows=sd_md['Number of along track pixels']

                #set up to create multispectral only self._gdaldatset for overview generation
                if self.nbands==1:
                    multi=3
                    multibands=sd_md['Number of bands']
                    multicols=cols
                    multirows=rows
                else:
                    multi=0
                    multibands=self.nbands
                    multicols=self.ncols
                    multirows=self.nrows
                multibands=range(1,int(multibands)+1)

                #Make a csv list of cols, bands
                self.ncols=[self.ncols for i in range(0,self.nbands)]
                self.nrows=[self.nrows for i in range(0,self.nbands)]
                self.ncols.extend([cols for i in range(0,sd.RasterCount)])
                self.nrows.extend([rows for i in range(0,sd.RasterCount)])
                #nbands='%s,%s' % (nbands, sd_md['Number of bands'])
                self.nbands=self.nbands+int(sd_md['Number of bands'])
                self.ncols=','.join(self.ncols)
                self.nrows=','.join(self.nrows)

            else:
                #set up to create multispectral only _gdaldatset for overview generation
                multi=0
                multibands=range(1,self.nbands+1)
                multicols=self.ncols
                multirows=self.nrows

            #create multispectral only _gdaldatset for overview generation
            #Get all the data files and mosaic the strips
            #strips=[s for s in utilities.rglob(os.path.dirname(f),r'\.m[1-4]r$',True,re.I,False)]
            strips=glob.glob(os.path.join(os.path.dirname(f),'*.m[1-4]r'))
            strips.sort();strips.reverse() #west->east = *.m4r-m1
            scols=(int(multicols)+30)/4 # +30 handles the 10 pixel overlap
            xoff=10
            yoff=400
            srows=int(multirows)-yoff
            srcrects=[[0,yoff,scols,srows]]*4
            dstrects=[]
            srcrect=[0,yoff,scols,srows]
            #dstrect=[None,0,scols,srows]
            files=[]
            sd,sz = hdf_sd[multi]
            vrt_opts=[]
            indatasetlist=[]
            for i in range(0,4):
                files.append(sd.replace(f,strips[i]))
                dstrects.append([i*(scols-xoff),0,scols,srows])
            self._gdaldataset=geometry.OpenDataset(geometry.CreateMosaicedVRT(files,multibands,srcrects,dstrects,multicols,srows,'Int16'))
            self._gdaldataset.GetRasterBand(2).SetNoDataValue(0)
            self._gdaldataset.GetRasterBand(3).SetNoDataValue(0)
            self._gdaldataset.GetRasterBand(4).SetNoDataValue(0)
            self._stretch=('STDDEV',(4,3,2),[2])

            #Extract other metadata
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
            self.geoext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]
            self.prjext=self.geoext

    def hyp_l1r(self,f):
        self.metadata['level']='L1R'
        self.metadata['sensor']='HYPERION'

        gdalDataset = geometry.OpenDataset(f)
        #if not gdalDataset: #Error now raised in geometry.OpenDataset
        #    errmsg=gdal.GetLastErrorMsg()
        #    raise IOError, 'Unable to open %s\n%s' % (f,errmsg.strip())

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
        if hdf_sd: #gdal <=1.10.x
            sd,sz = hdf_sd[0]
            sd=geometry.OpenDataset(sd)
            sd_md=sd.GetMetadata()
        else: #gdal >=1.11.0
            sd=gdalDataset
            sd_md=hdf_md
        self.nbands=sd.RasterCount
        self.ncols=sd.RasterXSize
        self.nrows=sd.RasterYSize
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
        self.geoext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]
        self.prjext=self.geoext

        #########################################################################################################
        ##set self._gdaldataset for use in overview generation
        ##we'll use bands 21, 30 & 43 for RGB (http://edcsns17.cr.usgs.gov/eo1/Hyperion_Spectral_Coverage.htm)
        ##as they're near the center of the equivalent ALI bands

        ##This generates verrrryyy looong overviews cos hyperion data is one long thin strip eg. 256*3000 etc...
        #self._gdaldataset = geometry.CreateVRTCopy(sd)
        ##Instead we can clip out some of the centre rows
        #vrtcols=ncols
        #vrtrows=int(ncols*1.5)
        #srcrect=[0, int(nrows/2-vrtrows/2),ncols,vrtrows]
        #dstrect=[0, 0,ncols,vrtrows]
        ##Or we can fill out the ncols with nodata
        vrtcols=int(self.nrows/1.5)
        vrtrows=self.nrows
        srcrect=[0, 0,self.ncols,self.nrows]
        dstrect=[int(self.nrows/2.5-self.ncols), 0,self.ncols,self.nrows]
        vrt=geometry.CreateMosaicedVRT([sd.GetDescription()],[43,30,21],[srcrect],[dstrect],vrtcols,vrtrows,self.metadata['datatype'])
        self._gdaldataset=geometry.OpenDataset(vrt)
        self._gdaldataset.GetRasterBand(3).SetNoDataValue(0)
        self._gdaldataset.GetRasterBand(2).SetNoDataValue(0)
        self._gdaldataset.GetRasterBand(1).SetNoDataValue(0)
        self._stretch=('STDDEV',(1,2,3),[2])


    def ali_l1g_hdf(self,f):
            self.metadata['level']='L1G'
            self.metadata['sensor']='ALI'
            self.metadata['sceneid']=self.metadata['filename'].split('_')[0]

            gdalDataset = geometry.OpenDataset(f)
            #if not gdalDataset: #Error now raised in geometry.OpenDataset
            #    errmsg=gdal.GetLastErrorMsg()
            #    raise IOError, 'Unable to open %s\n%s' % (f,errmsg.strip())

            self.metadata['filetype'] = '%s/%s (%s %s)' % (gdalDataset.GetDriver().ShortName,
                                                       gdalDataset.GetDriver().LongName,
                                                       self.metadata['sensor'],
                                                       self.metadata['level'])

            hdf_sd=gdalDataset.GetSubDatasets()
            hdf_md=gdalDataset.GetMetadata()
            sd,sz = hdf_sd[0]
            sd=geometry.OpenDataset(sd)
            sd_md=sd.GetMetadata()
            self.ncols=[]
            self.nrows=[]
            self.nbands=0
            bands=[]
            for sd,sz in hdf_sd:
                bands.append(sd)
                ds=geometry.OpenDataset(sd)
                self.ncols.append(str(ds.RasterXSize))
                self.nrows.append(str(ds.RasterYSize))
                self.nbands+=1

            #get all multi bands for use in overview generation
            pancols = max(self.ncols)
            panindex = ncols.index(pancols)
            multibands=bands
            multincols=self.ncols
            multinrows=self.nrows
            if pancols > min(self.ncols):#there is a pan band
                multibands.pop(panindex)
                multincols.pop(panindex)
                multinrows.pop(panindex)
            multibands.sort()
            self._gdaldataset = geometry.OpenDataset(geometry.CreateSimpleVRT(multibands,multincols[0],multinrows[0],'Int16'))
            self._gdaldataset.GetRasterBand(2).SetNoDataValue(0)
            self._gdaldataset.GetRasterBand(3).SetNoDataValue(0)
            self._gdaldataset.GetRasterBand(4).SetNoDataValue(0)
            self._stretch=('STDDEV',(4,3,2),[2])

            self.ncols=','.join(self.ncols)
            self.nrows=','.join(self.nrows)

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
            self.geoext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]
            self.prjext=self.geoext

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

    def ali_l1g_tiff(self,f):
            self.metadata['level']='L1G'
            self.metadata['sensor']='ALI'
            self.metadata['sceneid']=self.metadata['filename'].split('_')[0]
            self.metadata['filetype'] = 'GTiff/GeoTIFF'

            ncols=[]
            nrows=[]
            nbands=0
            bands=glob.glob(os.path.join(os.path.dirname(f),'eo1*_b*.tif'))
            for band in bands:
                band=geometry.OpenDataset(band)
                ncols.append(str(band.RasterXSize))
                nrows.append(str(band.RasterYSize))
                nbands+=1
                #rb=sd.GetRasterBand(1)

            #get all multi bands for use in overview generation
            pancols = max(ncols)
            panindex = ncols.index(pancols)
            multibands=bands
            multincols=ncols
            multinrows=nrows
            if pancols > min(ncols):#there is a pan band
                multibands.pop(panindex)
                multincols.pop(panindex)
                multinrows.pop(panindex)
            multibands.sort()
            self._gdaldataset = geometry.OpenDataset(geometry.CreateSimpleVRT(multibands,multincols[0],multinrows[0],'Int16'))
            self._gdaldataset.GetRasterBand(2).SetNoDataValue(0)
            self._gdaldataset.GetRasterBand(3).SetNoDataValue(0)
            self._gdaldataset.GetRasterBand(4).SetNoDataValue(0)
            self._stretch=('STDDEV',(4,3,2),[2])


            self.ncols=','.join(ncols)
            self.nrows=','.join(nrows)
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
            self.geoext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]

            uly=float(md['PRODUCT_METADATA']['PRODUCT_UL_CORNER_MAPY'])
            ulx=float(md['PRODUCT_METADATA']['PRODUCT_UL_CORNER_MAPX'])
            ury=float(md['PRODUCT_METADATA']['PRODUCT_UR_CORNER_MAPY'])
            urx=float(md['PRODUCT_METADATA']['PRODUCT_UR_CORNER_MAPX'])
            lry=float(md['PRODUCT_METADATA']['PRODUCT_LR_CORNER_MAPY'])
            lrx=float(md['PRODUCT_METADATA']['PRODUCT_LR_CORNER_MAPX'])
            lly=float(md['PRODUCT_METADATA']['PRODUCT_LL_CORNER_MAPY'])
            llx=float(md['PRODUCT_METADATA']['PRODUCT_LL_CORNER_MAPX'])
            self.prjext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]

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

    def hyp_l1t(self,f):
        md = parseheader(f)

        self.metadata['level']=md['PRODUCT_METADATA']['PRODUCT_TYPE']
        self.metadata['sceneid']=self.metadata['filename'].split('_')[0].upper()
        self.metadata['filetype'] = 'GTiff/GeoTIFF'
        self.metadata['satellite']= 'EO1'
        self.metadata['sensor']= md['PRODUCT_METADATA']['SENSOR_ID']

        bands=glob.glob(os.path.join(os.path.dirname(f),'eo1*_b*.tif'))
        band=geometry.OpenDataset(bands[0])
        self.ncols=band.RasterXSize
        self.nrows=band.RasterYSize
        self.nbands=len(bands)

        uly=float(md['PRODUCT_METADATA']['PRODUCT_UL_CORNER_LAT'])
        ulx=float(md['PRODUCT_METADATA']['PRODUCT_UL_CORNER_LON'])
        ury=float(md['PRODUCT_METADATA']['PRODUCT_UR_CORNER_LAT'])
        urx=float(md['PRODUCT_METADATA']['PRODUCT_UR_CORNER_LON'])
        lry=float(md['PRODUCT_METADATA']['PRODUCT_LR_CORNER_LAT'])
        lrx=float(md['PRODUCT_METADATA']['PRODUCT_LR_CORNER_LON'])
        lly=float(md['PRODUCT_METADATA']['PRODUCT_LL_CORNER_LAT'])
        llx=float(md['PRODUCT_METADATA']['PRODUCT_LL_CORNER_LON'])
        self.geoext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]

        uly=float(md['PRODUCT_METADATA']['PRODUCT_UL_CORNER_MAPY'])
        ulx=float(md['PRODUCT_METADATA']['PRODUCT_UL_CORNER_MAPX'])
        ury=float(md['PRODUCT_METADATA']['PRODUCT_UR_CORNER_MAPY'])
        urx=float(md['PRODUCT_METADATA']['PRODUCT_UR_CORNER_MAPX'])
        lry=float(md['PRODUCT_METADATA']['PRODUCT_LR_CORNER_MAPY'])
        lrx=float(md['PRODUCT_METADATA']['PRODUCT_LR_CORNER_MAPX'])
        lly=float(md['PRODUCT_METADATA']['PRODUCT_LL_CORNER_MAPY'])
        llx=float(md['PRODUCT_METADATA']['PRODUCT_LL_CORNER_MAPX'])
        self.prjext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]

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

        #########################################################################################################
        ##set self._gdaldataset for use in overview generation
        ##we'll use bands 21, 30 & 43 for RGB (http://edcsns17.cr.usgs.gov/eo1/Hyperion_Spectral_Coverage.htm)
        ##as they're near the center of the equivalent ALI bands
        self._gdaldataset = geometry.OpenDataset(geometry.CreateSimpleVRT([bands[43],bands[30],bands[21]],self.ncols,self.nrows,'Int16'))
        self._gdaldataset.GetRasterBand(1).SetNoDataValue(0)
        self._gdaldataset.GetRasterBand(2).SetNoDataValue(0)
        self._gdaldataset.GetRasterBand(3).SetNoDataValue(0)
        #self._stretch=('STDDEV',(1,2,3),[2])
        self._stretch=('PERCENT',(1,2,3),[2,98])

