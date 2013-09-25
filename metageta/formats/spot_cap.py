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
Metadata driver for SPOT 1-4 imagery

B{Format specification}:
    - U{http://www.spotimage.com/automne_modules_files/standard/public/p555_fileLINKEDFILE1_cap.pdf}

@todo: Level 1A - is not geometrically corrected, so cell size isn't really appropriate, however we
       calculate it from the geographic corner coords.
       Perhaps it would be better to just assign default values depending on whether the imagery is
       Multispectral, Pan or Merged Multi/Pan...?
'''

format_regex=[r'imag_[0-9]*\.dat$']#Landsat 5/SPOT 1-4 CCRS
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

class Dataset(__dataset__.Dataset): #Subclass of base Dataset class
    def __init__(self,f=None):
        '''Open the dataset'''
        if not f:f=self.fileinfo['filepath']
        if f[:4]=='/vsi':raise NotImplementedError

        led=glob.glob(os.path.dirname(f) + '/[Ll][Ee][Aa][Dd]*')[0] #volume file
        meta = open(led,'rb').read()

        #Record 2 - Scene header record
        record=2
        recordlength=3960 #SPOT recordlength=3960 
        satellite=utilities.readbinary(meta,(record-1)*recordlength,613,628)
        if not satellite[0:4] == 'SPOT':
            raise NotImplementedError #This error gets ignored in __init__.Open()
        self.filelist=[r for r in utilities.rglob(os.path.dirname(f))] #everything in this dir and below.

    def __getmetadata__(self,f=None):
        '''Populate metadata'''
        if not f:f=self.fileinfo['filepath']
        self._gdaldataset = geometry.OpenDataset(f)

        led=glob.glob(os.path.dirname(f) + '/[Ll][Ee][Aa][Dd]*')[0] #volume file
        meta = open(led,'rb').read()

        ######################
        # Scene header record
        ######################
        record=2
        recordlength=3960 #SPOT recordlength=3960

        ##################
        #SCENE PARAMETERS
        ##################
        sceneid=utilities.readbinary(meta,(record-1)*recordlength,37,52)

        cy=geometry.DMS2DD(utilities.readbinary(meta,(record-1)*recordlength,85,100),'HDDDMMSS') #Latitude of the Scene Centre
        cx=geometry.DMS2DD(utilities.readbinary(meta,(record-1)*recordlength,101,116),'HDDDMMSS') #Longitude of the Scene Centre
        uly=geometry.DMS2DD(utilities.readbinary(meta,(record-1)*recordlength,149,164),'HDDDMMSS')
        ulx=geometry.DMS2DD(utilities.readbinary(meta,(record-1)*recordlength,165,180),'HDDDMMSS')
        ury=geometry.DMS2DD(utilities.readbinary(meta,(record-1)*recordlength,213,228),'HDDDMMSS')
        urx=geometry.DMS2DD(utilities.readbinary(meta,(record-1)*recordlength,229,244),'HDDDMMSS')
        lly=geometry.DMS2DD(utilities.readbinary(meta,(record-1)*recordlength,277,292),'HDDDMMSS')
        llx=geometry.DMS2DD(utilities.readbinary(meta,(record-1)*recordlength,293,308),'HDDDMMSS')
        lry=geometry.DMS2DD(utilities.readbinary(meta,(record-1)*recordlength,341,356),'HDDDMMSS')
        lrx=geometry.DMS2DD(utilities.readbinary(meta,(record-1)*recordlength,357,372),'HDDDMMSS')
        ext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]

        ######################
        #IMAGING PARAMETERS
        ######################
        self.metadata['rotation']=float(utilities.readbinary(meta,(record-1)*recordlength,437,452))
        if abs(self.metadata['rotation']) < 1:
            self.metadata['orientation']='Map oriented'
            self.metadata['rotation']=0.0
        else:self.metadata['orientation']='Path oriented'
        self.metadata['sunazimuth']=float(utilities.readbinary(meta,(record-1)*recordlength,469,484))
        self.metadata['sunelevation']=float(utilities.readbinary(meta,(record-1)*recordlength,485,500))
        imgdate=utilities.readbinary(meta,(record-1)*recordlength,581,612)
        #self.metadata['imgdate']=time.strftime(utilities.dateformat,time.strptime(imgdate[0:8],'%Y%m%d')) #ISO 8601 
        self.metadata['imgdate']=time.strftime(utilities.datetimeformat,time.strptime(imgdate[0:14],'%Y%m%d%H%M%S')) #ISO 8601 
        satellite=utilities.readbinary(meta,(record-1)*recordlength,613,628)
        sensor=utilities.readbinary(meta,(record-1)*recordlength,629,644)
        mode=utilities.readbinary(meta,(record-1)*recordlength,645,660)

        ######################
        #IMAGE PARAMETERS
        ######################
        ncols=int(utilities.readbinary(meta,(record-1)*recordlength,997,1012))
        nrows=int(utilities.readbinary(meta,(record-1)*recordlength,1013,1028))
        nbands=int(utilities.readbinary(meta,(record-1)*recordlength,1045,1060))
        bands=utilities.readbinary(meta,(record-1)*recordlength,1061,1316).replace(' ',',')
        self.metadata['level']=utilities.readbinary(meta,(record-1)*recordlength,1317,1332)
        self.metadata['resampling']=utilities.readbinary(meta,(record-1)*recordlength,1365,1380)
        if self.metadata['level']=='1A': #Not geometrically corrected. Cell size isn't really appropriate
            gcps=geometry.ExtentToGCPs(ext,ncols,nrows)
            gt=gdal.GCPsToGeoTransform(gcps)
            cellx,celly=geometry.CellSize(gt)
        else:
            cellx=float(utilities.readbinary(meta,(record-1)*recordlength,1381,1396))
            celly=float(utilities.readbinary(meta,(record-1)*recordlength,1397,1412))

        #################################################
        #Ancillary "Ephemeris / Attitude" record,
        #################################################
        record=3
        viewangle=float(utilities.readbinary(meta,(record-1)*recordlength,3065,3076))
        
        #################################################
        #Map projection (scene-related) ancillary record
        #################################################
        record=26
        projection = utilities.readbinary(meta,(record-1)*recordlength,21,52).replace('\x00','')
        ellipsoid = utilities.readbinary(meta,(record-1)*recordlength,57,88).replace('\x00','')
        datum = utilities.readbinary(meta,(record-1)*recordlength,101,132).replace('\x00','')

        if 'UTM' in projection:
            # UTM
            type='UTM'
            units='m'
            zone=projection[3:-1]
            if not zone:
                zone=str(spatialreferences.lon2utmzone(cx))
            if   'GDA' in datum: epsg=int('283'+zone)
            elif 'AGD' in datum: epsg=int('202'+zone)
            elif 'WGS' in datum: epsg=int('327'+zone) if projection[-1] =='S' else int('326'+zone)
            
        else: #Assume
            type='GEO'
            units='deg'
            if datum=='GDA94':epsg=4283
            else:epsg=4326 #Assume WGS84
            if   'GDA' in datum: epsg=4283
            elif 'AGD' in datum: epsg=202
            else:                epsg=4326 #Assume WGS84'

            #cell sizes are reported in metres even for geo projections
            gcps=[];i=0
            lr=[[0,0],[ncols,0],[ncols,nrows],[0,nrows]]
            while i < len(ext)-1: #don't need the last xy pair
                gcp=gdal.GCP()
                gcp.GCPPixel,gcp.GCPLine=lr[i]
                gcp.GCPX,gcp.GCPY=ext[i]
                gcp.Id=str(i)
                gcps.append(gcp)
                i+=1
            geotransform = gdal.GCPsToGeoTransform(gcps)
            cellx,celly=geometry.CellSize(geotransform)
            rotation=geometry.Rotation(geotransform)

        srs = osr.SpatialReference()
        srs.ImportFromEPSG(epsg)
        srs=srs.ExportToWkt()

        self.metadata['satellite']=satellite
        self.metadata['sensor']=sensor
        self.metadata['filetype'] ='CEOS/SPOT CCT Format'
        self.metadata['filesize']=sum([os.path.getsize(file) for file in self.filelist])
        self.metadata['sceneid'] = sceneid
        self.metadata['srs'] = srs
        self.metadata['epsg'] = epsg
        self.metadata['units'] = units
        self.metadata['cols'] = ncols
        self.metadata['rows'] = nrows
        self.metadata['nbands'] = nbands
        self.metadata['bands'] = bands
        self.metadata['nbits'] = 8
        self.metadata['datatype'] = 'Byte'
        self.metadata['nodata'] = 0
        self.metadata['mode'] = mode
        self.metadata['cellx'],self.metadata['celly']=map(float,[cellx,celly])
        self.metadata['UL']='%s,%s' % tuple(ext[0])
        self.metadata['UR']='%s,%s' % tuple(ext[1])
        self.metadata['LR']='%s,%s' % tuple(ext[2])
        self.metadata['LL']='%s,%s' % tuple(ext[3])
        metadata=self._gdaldataset.GetMetadata()
        self.metadata['metadata']='\n'.join(['%s: %s' %(m,hdf_self.metadata[m]) for m in metadata])
        self.metadata['compressionratio']=0
        self.metadata['compressiontype']='None'
        self.extent=ext
