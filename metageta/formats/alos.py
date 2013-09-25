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
Metadata driver for ACRES ALOS AVNIR-2/PRISM/PALSAR imagery

B{Supports}:
    - ALOS AVNIR2/PRISM
    - ALOS PALSAR (Level 1.5 only, Level 1.0 not (yet?) implemented)

B{Format specifications}:
    - PALSAR Level 1.0: U{http://www.ga.gov.au/servlet/BigObjFileManager?bigobjid=GA10287}
    - PALSAR Level 1.1/1.5: U{http://www.eorc.jaxa.jp/ALOS/doc/fdata/PALSAR_x_Format_EK.pdf}
    - ALOS AVNIR2/PRISM: U{http://www.ga.gov.au/servlet/BigObjFileManager?bigobjid=GA10285}
'''
format_regex=[
      r'LED-ALAV.*_U$',            #ALOS AVNIR-2 leader file
      r'LED-ALAV.*___$',           #ALOS AVNIR-2 leader file
      r'LED-ALPSR.*UD$',           #ALOS PALSAR
      r'LED-ALPSM.*\_U[BFNW]$'     #ALOS PRISM
      ]
'''Regular expression list of file formats'''

#import base dataset module
import __default__

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

class Dataset(__default__.Dataset): 
    '''Subclass of default Dataset class'''

    def __init__(self,f=None):
        if not f:f=self.fileinfo['filepath']
        if f[:4]=='/vsi':raise NotImplementedError
        self.filelist=[r for r in utilities.rglob(os.path.dirname(f))]
        self._led=f
        try:self._vol=glob.glob(os.path.dirname(f) + '/[Vv][Oo][Ll]*')[0] #volume file
        except:self._vol=False

        img_regex=[
              r'IMG-0[1-4]-ALAV.*_U$',     #ALOS AVNIR-2 img file
              r'.*\.tif$',                 #ALOS AVNIR-2 ACRES orthocorrected tif file
              r'IMG-[HV][HV]-ALPSR.*UD$',  #ALOS PALSAR
              r'IMG-ALPSM.*\_U[BFNW]$'     #ALOS PRISM
        ]
        self._imgs=[i for i in utilities.rglob(os.path.dirname(f),'|'.join(img_regex),True,re.I, False)]
        
        self.fileinfo['filepath']=self._led #change filename to leader file
        self.fileinfo['filename']=os.path.basename(self._led)
    def __getmetadata__(self,f=None):
        '''Read Metadata for an ACRES ALOS AVNIR-2/PRISM/PALSAR format image as GDAL doesn't'''

        #Local copies for brevity
        vol=self._vol
        led=self._led

        if 'led-alpsr' in led.lower():driver='SAR_CEOS'
        else:driver='CEOS'

        extra_md={} #for holding any extra metadata which gets stuffed into self.metadata['metadata'] later on

        self.metadata['satellite']='ALOS'
        nodata = 0

        #ACRES ortho product is in GTIFF format
        tif=False

        if driver=='SAR_CEOS':  #PALSAR - assumes Level 1.5, Level 1.0 not implemented
            #Format Description
            #Level 1.0     - http://www.ga.gov.au/servlet/BigObjFileManager?bigobjid=GA10287
            #Level 1.1/1.5 - http://www.eorc.jaxa.jp/ALOS/doc/fdata/PALSAR_x_Format_EK.pdf
            
            self.metadata['sensor']='PALSAR'
            self.metadata['filetype'] ='CEOS/ALOS PALSAR CEOS Format'
            
            '''
            volume file has 3-6 records, 360 bytes length:
            Record            Length
            =========================
            1 File descriptor 360 
            2 File pointer    360 (3-6 records = N+2 where N is number of polarization)
            3 Text            360
            '''
            meta = open(vol,'rb').read()

            #File descriptor record
            offset = 0

            #Number of file pointers        
            npointers=int(utilities.readbinary(meta,offset,161,164))

            #Text record
            offset = 360*(npointers+1)

            #Product type specifier
            start,stop = 17,56
            prodspec = utilities.readbinary(meta,offset,start,stop)[8:] #Strip of the "'PRODUCT:" string
            if prodspec[1:4] != '1.5':raise Exception, 'ALOS PALSAR Level %s not yet implemented' % level
            if prodspec[0]=='H':self.metadata['mode']='Fine (high resolution) mode'
            elif prodspec[0]=='W':self.metadata['mode']='ScanSAR (wide observation) mode'
            elif prodspec[0]=='D':self.metadata['mode']='Direct Downlink mode'
            elif prodspec[0]=='P':self.metadata['mode']='Polarimetry mode'
            elif prodspec[0]=='C':self.metadata['mode']='Calibration mode'
            level=prodspec[1:5]
            orient=prodspec[4]
            if orient=='G':self.metadata['orientation']='Map oriented'
            else: self.metadata['orientation']='Path oriented'
            orbit=prodspec[6]
            
            '''
            leader file has >9 records of variable length:
            Record                    Length
            ============================================
            1 File descriptor         720 
            2 Data set summary        4096
            3 Map projection data     1620
            4 Platform position data  4680
            5 Attitude data           8192
            6 Radiometric data        9860
            7 Data quality summary    1620
            8 Calibration data        13212
            9 Facility related        Variable
            '''
            meta = open(led,'rb').read()

            #File descriptor
            offset = 0
            
            #Data set summary
            offset = 720
            #Scene ID
            start,stop = 21,52
            sceneid = utilities.readbinary(meta,offset,start,stop)
            #Image date
            start,stop = 69,100
            #imgdate=utilities.readbinary(meta,offset,start,stop)[0:14]#Strip off time
            #self.metadata['imgdate'] = time.strftime(utilities.dateformat,time.strptime(imgdate,'%Y%m%d')) #ISO 8601
            imgdate=utilities.readbinary(meta,offset,start,stop)[0:14] #Keep time, strip off milliseconds
            self.metadata['imgdate'] = time.strftime(utilities.datetimeformat,time.strptime(imgdate,'%Y%m%d%H%M%S'))            #SAR Channels
            start,stop = 389,392
            nbands = int(utilities.readbinary(meta,offset,start,stop))
            
            #Radar wavelength
            start,stop = 501,516
            wavelen = utilities.readbinary(meta,offset,start,stop)
            extra_md['wavelength']=wavelen
            
            #Nominal offnadir angle
            start,stop = 1839,1854
            self.metadata['viewangle'] = utilities.readbinary(meta,offset,start,stop)

            #Map projection data
            offset += 4096
            #Cols & rows
            start,stop = 61,76
            ncols = int(utilities.readbinary(meta,offset,start,stop))
            start,stop = 77,92
            nrows = int(utilities.readbinary(meta,offset,start,stop))
            #cell sizes (metres)
            start,stop = 93,124
            ypix,xpix = map(float,utilities.readbinary(meta,offset,start,stop).split())


            #Orientation at output scene centre
            start,stop = 125,140
            rot = math.radians(float(utilities.readbinary(meta,offset,start,stop)))
            #GeogCS
            src_srs=osr.SpatialReference()
            #src_srs.SetGeogCS('GRS 1980','GRS 1980','GRS 1980',6378137.00000,298.2572220972)
            src_srs.SetWellKnownGeogCS( "WGS84" )
            #Proj CS
            start,stop = 413,444
            projdesc = utilities.readbinary(meta,offset,start,stop)
            epsg=0#default
            if projdesc == 'UTM-PROJECTION':
                nZone = int(utilities.readbinary(meta,offset,477,480))
                dfFalseNorthing = float(utilities.readbinary(meta,offset,497,512))
                if dfFalseNorthing > 0.0:
                    bNorth=False
                    epsg=32700+nZone
                else:
                    bNorth=True
                    epsg=32600+nZone
                src_srs.ImportFromEPSG(epsg)
                #src_srs.SetUTM(nZone,bNorth) #generates WKT that osr.SpatialReference.AutoIdentifyEPSG() doesn't return an EPSG for
            elif projdesc == 'UPS-PROJECTION':
                dfCenterLon = float(utilities.readbinary(meta,offset,625,640))
                dfCenterLat = float(utilities.readbinary(meta,offset,641,656))
                dfScale = float(utilities.readbinary(meta,offset,657,672))
                src_srs.SetPS(dfCenterLat,dfCenterLon,dfScale,0.0,0.0) 	
            elif projdesc == 'MER-PROJECTION':
                dfCenterLon = float(utilities.readbinary(meta,offset,737,752))
                dfCenterLat = float(utilities.readbinary(meta,offset,753,768))
                src_srs.SetMercator(dfCenterLat,dfCenterLon,0,0,0)
            elif projdesc == 'LCC-PROJECTION':
                dfCenterLon = float(utilities.readbinary(meta,offset,737,752))
                dfCenterLat = float(utilities.readbinary(meta,offset,753,768))
                dfStdP1 = float(utilities.readbinary(meta,offset,769,784))
                dfStdP2 = float(utilities.readbinary(meta,offset,785,800))
                src_srs.SetLCC(dfStdP1,dfStdP2,dfCenterLat,dfCenterLon,0,0)
            srs=src_srs.ExportToWkt()
            if not epsg:epsg = spatialreferences.IdentifyAusEPSG(srs)
            units = spatialreferences.GetLinearUnitsName(srs)

            #UL-LR coords
            ##ext=[float(coord)*1000 for coord in utilities.readbinary(meta,offset,945,1072).split()] #Get lat/lon instead of eastings/northings
            ext=[float(coord) for coord in utilities.readbinary(meta,offset,1073,1200).split()]
            uly,ulx,ury,urx,lry,lrx,lly,llx=ext
            ext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]] #last xy pair closes the poly

            self.metadata['nbits'] = 16
            self.metadata['datatype']='UInt16'

            #Generate a GDAL Dataset object
            self._gdaldataset=geometry.OpenDataset(self._imgs[0])

        else:        #ALOS AVNIR2/PRISM
            ##Format - http://www.ga.gov.au/servlet/BigObjFileManager?bigobjid=GA10285
            
            '''
            leader file has 5 records, each is 4680 bytes long:
            1. File descriptor record;
            2. Scene header record;
            3. Map projection (scene-related) ancillary record;
            4. Radiometric transformation ancillary record;
            5. Platform position ancillary record.
            '''
            #ACRES ortho product is in GTIFF format
            if '.tif' in self._imgs[0].lower():
                tif=True
                level='ORTHOCORRECTED'
                __default__.Dataset.__getmetadata__(self, self._imgs[0])

            meta = open(led,'rb').read()
            recordlength = 4680

            #Record 2 - Scene header record
            record=2

            #Processing level
            if not tif:
                start,stop = 21,36
                procinfo = utilities.readbinary(meta,(record-1)*recordlength,start,stop)
                level=procinfo[1:4]
                #if level != '1B2':raise Exception, 'Level %s PRISM is not supported' % level
                self.metadata['level']==procinfo[1:4]
                opt=procinfo[4:6].strip().strip('_')
                if opt!='':level+='-'+opt

            #SceneID
            if level[0:3] == '1B2':start,stop = 197,212
            else:start,stop = 37,52
            sceneid = utilities.readbinary(meta,(record-1)*recordlength,start,stop)

            #Lat/Lon of scene center
            ##if level[0:3] == '1B2':start,stop = 245,276
            ##else:start,stop = 85,116
            ##cenrow, cencol=map(float,utilities.readbinary(meta,(record-1)*recordlength,start,stop).split())
            
            #Line & Pixel number for scene center
            ##if level[0:3] == '1B2':start,stop = 245,276
            ##else:start,stop = 85,116
            ##cenrow, cencol=map(float,utilities.readbinary(meta,(record-1)*recordlength,start,stop).split())

            #Orientation Angle NNN.N = degrees
            start,stop = 277,292
            rot = float(utilities.readbinary(meta,(record-1)*recordlength,start,stop))

            #Ascending/descendit orbit
            start,stop = 357,372
            orbit = utilities.readbinary(meta,(record-1)*recordlength,start,stop)

            #view, sun elevation and azimuth angles
            start,stop = 373,388
            self.metadata['viewangle'] = utilities.readbinary(meta,(record-1)*recordlength,start,stop)
            start,stop = 453,466
            sunangles = utilities.readbinary(meta,(record-1)*recordlength,start,stop)
            self.metadata['sunelevation'] = sunangles[6:9].strip()
            self.metadata['sunazimuth']   = sunangles[11:].strip()

            #Image aquisition date
            start,stop = 401,408
            imgdate = utilities.readbinary(meta,(record-1)*recordlength,start,stop)
            imgdate = time.strptime(imgdate,'%d%b%y') #DDMmmYY
            self.metadata['imgdate'] = time.strftime(utilities.dateformat,imgdate) #ISO 8601 

            #Sensor type and bands
            start,stop = 443,452
            sensor,bands=utilities.readbinary(meta,(record-1)*recordlength,start,stop).split()
            if sensor=='PSM':
                self.metadata['sensor']='PRISM'
                if sceneid[5] == 'N':  extra_md['SENSOR DIRECTION']='Nadir 35km'
                elif sceneid[5] == 'W':extra_md['SENSOR DIRECTION']='Nadir 70km'
                elif sceneid[5] == 'F':extra_md['SENSOR DIRECTION']='Forward 35km'
                elif sceneid[5] == 'B':extra_md['SENSOR DIRECTION']='Backward 35km'
            else:self.metadata['sensor']='AVNIR-2'
            self.metadata['filetype'] ='CEOS/ALOS %s CEOS Format' % self.metadata['sensor']
            self.metadata['bands']=','.join([band for band in bands])

            #Processing info
            if not tif:
                start,stop = 467,478
                procinfo = utilities.readbinary(meta,(record-1)*recordlength,start,stop)
                orient=procinfo[-1]
                if orient=='G':self.metadata['orientation']='Map oriented'
                else:self.metadata['orientation']='Path oriented'

                #No. bands
                start,stop = 1413,1428
                nbands = int(utilities.readbinary(meta,(record-1)*recordlength,start,stop))

                #No. cols
                start,stop = 1429,1444
                ncols = float(utilities.readbinary(meta,(record-1)*recordlength,start,stop))

                #No. rows
                start,stop = 1445,1460
                nrows = float(utilities.readbinary(meta,(record-1)*recordlength,start,stop))

            #Resampling
            start,stop = 1541,1556
            res = utilities.readbinary(meta,(record-1)*recordlength,start,stop)
            if   res=='NNNNN':self.metadata['resampling']=''      #Raw (L1A,L1B1)
            elif res=='YNNNN':self.metadata['resampling']='NN'    #Nearest neighbour
            elif res=='NYNNN':self.metadata['resampling']='BL'    #Bi-linear
            elif res=='NNYNN':self.metadata['resampling']='CC'    #Cubic convolution
            
            #Lat/Lon extent
            start,stop = 1733,1860
            coords = utilities.readbinary(meta,(record-1)*recordlength,start,stop).split()
            uly,ulx,ury,urx,lly,llx,lry,lrx = map(float, coords)
            ext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]

            if not tif:
                #Record 3
                record=3

                #Hemisphere
                start,stop = 93,96
                hemi = utilities.readbinary(meta,(record-1)*recordlength,start,stop)

                #UTM Zone - revisit if we get polarstereographic projection products
                start,stop = 97,108
                utm = utilities.readbinary(meta,(record-1)*recordlength,start,stop)
                if hemi=='1': #South
                    epsg=int('327%s' % utm) #Assume WGS84
                else:         #North
                    epsg=int('326%s' % utm)
                src_srs = osr.SpatialReference()
                src_srs.ImportFromEPSG(epsg)
                units = 'm'
                #Scene center position - revisit if we get polarstereographic projection products
                ##start,stop = 141,156
                ##ceny = float(utilities.readbinary(meta,(record-1)*recordlength,start,stop)) * 1000 #(Northing - km)
                ##start,stop = 157,172
                ##cenx = float(utilities.readbinary(meta,(record-1)*recordlength,start,stop)) * 1000 #(Easting - km)

                #Orientation Angle NNN.N = radians
                start,stop = 205,220
                rot = float(utilities.readbinary(meta,(record-1)*recordlength,start,stop))

                #Pixel size (x)
                start,stop=541,572
                xpix,ypix=map(float,utilities.readbinary(meta,(record-1)*recordlength,start,stop).split())

                #Get extent of scene
                ##xmin=(cenx+xpix/2)-(cencol*xpix)
                ##ymin=(ceny+ypix/2)-(cenrow*ypix)
                ##xmax=xmin+(ncols*xpix)
                ##ymax=ymin+(nrows*ypix)
                
                ##if procinfo[-1]=='R': #Calculate rotated extent coordinates
                ##    ##angc=math.cos(rot)
                ##    ##angs=math.sin(rot)
                ##    angc=math.cos(math.radians(rot))
                ##    angs=math.sin(math.radians(rot))
                ##    ulx =  (xmin-cenx)*angc + (ymax-ceny)*angs+cenx
                ##    uly = -(xmin-cenx)*angs + (ymax-ceny)*angc+ceny
                ##    llx =  (xmin-cenx)*angc + (ymin-ceny)*angs+cenx
                ##    lly = -(xmin-cenx)*angs + (ymin-ceny)*angc+ceny
                ##    urx =  (xmax-cenx)*angc + (ymax-ceny)*angs+cenx
                ##    ury = -(xmax-cenx)*angs + (ymax-ceny)*angc+ceny
                ##    lrx =  (xmax-cenx)*angc + (ymin-ceny)*angs+cenx
                ##    lry = -(xmax-cenx)*angs + (ymin-ceny)*angc+ceny
                ##else: #Just use xmin etc...
                ##    ulx,uly = xmin,ymax
                ##    llx,lly = xmin,ymin
                ##    urx,ury = xmax,ymax
                ##    lrx,lry = xmax,ymin
                ##ext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]

                #Geotransform
                ##gcps=[];i=0
                ##lr=[[0,0],[ncols,0],[ncols,nrows],[0,nrows]]
                ##while i < len(ext)-1: #don't need the last xy pair
                ##    gcp=gdal.GCP()
                ##    gcp.GCPPixel,gcp.GCPLine=lr[i]
                ##    gcp.GCPX,gcp.GCPY=ext[i]
                ##    gcp.Id=str(i)
                ##    gcps.append(gcp)
                ##    i+=1
                ##geotransform = gdal.GCPsToGeoTransform(gcps)

                self.metadata['nbits'] = 8
                self.metadata['datatype'] = 'Byte'

                #Generate a VRT GDAL Dataset object
                self._imgs.sort()
                img=self._imgs[0]
                meta = open(img,'rb').read(1024)
                start,stop = 187,192
                record=1
                recordlength=0
                offset=utilities.readbinary(meta,(record-1)*recordlength,start,stop)
                #don't use ALOS provided no. cols, as it doesn't include 'dummy' pixels
                #vrt=geometry.CreateRawRasterVRT(self._imgs,self.metadata['cols'],self.metadata['rows'],self.metadata['datatype'],offset,byteorder='MSB')
                vrt=geometry.CreateRawRasterVRT(self._imgs,offset,nrows,self.metadata['datatype'],offset,byteorder='MSB')
                self._gdaldataset=geometry.OpenDataset(vrt)

        #Reproject corners to lon,lat
        ##geom = geometry.GeomFromExtent(ext)
        ##tgt_srs=osr.SpatialReference()
        ##tgt_srs.ImportFromEPSG(4326)
        ##geom=geometry.ReprojectGeom(geom,src_srs,tgt_srs)
        ##points=geom.GetBoundary()
        ##ext=[[points.GetX(i),points.GetY(i)] for i in range(0,points.GetPointCount())]

        #Fix for Issue 17
        for i in range(1,self._gdaldataset.RasterCount+1):
            self._gdaldataset.GetRasterBand(i).SetNoDataValue(nodata)

        self.metadata['level'] = level
        self.metadata['sceneid'] = sceneid
        if orbit=='A':self.metadata['orbit']='Ascending'
        else: self.metadata['orbit']='Descending'
        self.metadata['metadata']='\n'.join(['%s: %s' %(m,extra_md[m]) for m in extra_md])
        if not tif:
            self.metadata['filesize']=sum([os.path.getsize(tmp) for tmp in self.filelist])
            self.metadata['srs'] = src_srs.ExportToWkt()
            self.metadata['epsg'] = epsg
            self.metadata['units'] = units
            self.metadata['cols'] = ncols
            self.metadata['rows'] = nrows
            self.metadata['nbands'] = nbands
            if abs(math.degrees(rot)) < 1.0:self.metadata['rotation'] = 0.0
            else: self.metadata['rotation'] = math.degrees(rot)
            self.metadata['UL']='%s,%s' % tuple(ext[0])
            self.metadata['UR']='%s,%s' % tuple(ext[1])
            self.metadata['LR']='%s,%s' % tuple(ext[2])
            self.metadata['LL']='%s,%s' % tuple(ext[3])
            self.metadata['cellx'],self.metadata['celly']=xpix,ypix
            self.metadata['nodata'] = nodata
            self.metadata['compressionratio']=0
            self.metadata['compressiontype']='None'
            self.extent=ext

    def getoverview(self,outfile=None,width=800,format='JPG'): 
        '''
        Generate overviews for ALOS imagery

        @type  outfile: str
        @param outfile: a filepath to the output overview image. If supplied, format is determined from the file extension
        @type  width:   int
        @param width:   image width
        @type  format:  str
        @param format:  format to generate overview image, one of ['JPG','PNG','GIF','BMP','TIF']. Not required if outfile is supplied.
        @rtype:         str
        @return:        filepath (if outfile is supplied)/binary image data (if outfile is not supplied)
        '''
        from metageta import overviews

        #First check for a browse graphic, no point re-inventing the wheel...
        for f in self.filelist:
            browse=False
            if '.jpg' in f.lower():
                browse=f
                break
        if browse:
            try:return overviews.resize(browse,outfile,width)
            except:return __default__.Dataset.getoverview(self,outfile,width,format) #Try it the slow way...
        else: return __default__.Dataset.getoverview(self,outfile,width,format)#Do it the slow way...
