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
Metadata driver for ASTER imagery

B{Format specifications}:
    - U{http:#www.gdal.org/frmt_hdf4.html}
    - U{http://asterweb.jpl.nasa.gov/documents/ASTER_L1_Product_Spec_Ver_1.3_July01.pdf}
    - U{http://asterweb.jpl.nasa.gov/content/03_data/04_Documents/ASTER_L1_Product_Spec_Ver_1.3_July01.pdf} (inc description of GCTP projection parameters)
    - U{http://lpdaac.usgs.gov/aster/ASTER_GeoRef_FINAL.pdf}
    - U{http://www.science.aster.ersdac.or.jp/en/documnts/users_guide/index.html}
    - U{http://www.science.aster.ersdac.or.jp/en/documnts/pdf/ASTER_Ref_V1.pdf}
'''

format_regex=[r'ast_l1[ab].*\.hdf$',r'pg-PR1[AB]0000-\d{10}_\d{3}_\d{3}$'] #HDF inc. ASTER
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
        if not f:f=self.fileinfo['filepath']
        if f[:4]=='/vsi':raise NotImplementedError
        self.filelist=glob.glob(os.path.splitext(f)[0]+'.*')
        self._gdaldataset = geometry.OpenDataset(f)
        self._hdf_md=self._gdaldataset.GetMetadata()
        if not self._hdf_md.get('INSTRUMENTSHORTNAME')=='ASTER':
            raise NotImplementedError #This error gets ignored in __init__.Open()

    def __getmetadata__(self,f=None):
        '''Read Metadata for ASTER HDF images as GDAL doesn't.'''
        if not f:f=self.fileinfo['filepath']

        hdf_sd=self._gdaldataset.GetSubDatasets()
        hdf_sd= [sd for sd,sz in hdf_sd if 'ImageData' in sd]
        hdf_md=self._hdf_md

        #sd,sz = hdf_sd[0]
        sd = hdf_sd[0]
        sd=geometry.OpenDataset(sd)

        nbands=len(hdf_sd)
        ncols=[]
        nrows=[]
        nbits=[]
        bands=[]
        datatypes=[]
        cellxy=[]
        for i in range(0,len(hdf_md['PROCESSEDBANDS']), 2):
            band=hdf_md['PROCESSEDBANDS'][i:i+2]
            if i/2+1 <= 4:
                bands.append('VNIR'+band)
                cellxy.append('15')
            elif i/2+1 <= 10:
                bands.append('SWIR'+band)
                cellxy.append('30')
            else:
                bands.append('TIR'+band)
                cellxy.append('90')
            if band.isdigit():band=str(int(band)) #Get rid of leading zero
            cols,rows,bytes=map(int,hdf_md['IMAGEDATAINFORMATION%s' % band].split(','))
            if bytes==1:datatypes.append('Byte')
            elif bytes==2:datatypes.append('UInt16')
            ncols.append(str(cols))
            nrows.append(str(rows))
            nbits.append(str(bytes*8))
        ncols=','.join(ncols)
        nrows=','.join(nrows)
        nbits=','.join(nbits)
        bands=','.join(bands)
        datatypes=','.join(datatypes)
        cellxy=','.join(cellxy)


        uly,ulx=[float(xy) for xy in hdf_md['UPPERLEFT'].split(',')]
        ury,urx=[float(xy) for xy in hdf_md['UPPERRIGHT'].split(',')]
        lry,lrx=[float(xy) for xy in hdf_md['LOWERRIGHT'].split(',')]
        lly,llx=[float(xy) for xy in hdf_md['LOWERLEFT'].split(',')]
        ext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]

        #SRS reported by GDAL is slightly dodgy, GDA94 is not recognised and doesn't set the North/South properly
        #Get it anyway so we can work out if it's GDA94 based on the spheroid
        srs=sd.GetGCPProjection()
        src_srs=osr.SpatialReference(srs)
        tgt_srs=osr.SpatialReference()
        geogcs=osr.SpatialReference()
        if src_srs.GetAttrValue('SPHEROID') == 'GRS 1980':geogcs.ImportFromEPSG(4283) #Assume 'GDA94'
        else:geogcs.ImportFromEPSG(4326)                                              #Assume 'WGS84'
        tgt_srs.CopyGeogCSFrom(geogcs)

        if hdf_md['PROCESSINGLEVELID'].upper()=='1A':
            units='deg'
        else:
            #projparams=map(float, hdf_md['PROJECTIONPARAMETERS1'].split(','))
            if hdf_md['MPMETHOD1'] == 'UTM':#Universal Transverse Mercator
                if uly < 0:bNorth=False #GDAL doesn't set the North/South properly
                else:bNorth=True
                nZone = int(hdf_md['UTMZONECODE1'])
                tgt_srs.SetUTM(nZone,bNorth)
                units='m'
            #Other projections not (yet?) implemented...
            #elif hdf_md['MPMETHOD1'] == 'PS':#Polar Stereographic
            #    #dfCenterLon = ? GTCP projection params don't list cenlon/lat for PS
            #    dfCenterLat = ?
            #    dfScale = ?
            #    tgt_srs.SetPS(dfCenterLat,dfCenterLon,dfScale,0.0,0.0)
            #elif hdf_md['MPMETHOD1'] == 'LAMCC':#Lambert Conformal Conic
            #    dfCenterLon = ?
            #    dfCenterLat = ?
            #    dfStdP1 = ?
            #    dfStdP2 = ?
            #    tgt_srs.SetLCC(dfStdP1,dfStdP2,dfCenterLat,dfCenterLon,0,0)
            #elif hdf_md['MPMETHOD1'] == 'SOM':#Space Oblique Mercator
            #    dfCenterLon = ?
            #    dfCenterLat = ?
            #    srs.SetMercator(dfCenterLat,dfCenterLon,0,0,0)
            #elif hdf_md['MPMETHOD1'] == 'EQRECT':#Equi-Rectangular
            #    dfCenterLon = ?
            #    dfCenterLat = ?
            #    tgt_srs.SetMercator(dfCenterLat,dfCenterLon,0,0,0)
            else: #Assume Geog
                units='deg'

        srs=tgt_srs.ExportToWkt()

        self.metadata['UL']='%s,%s' % tuple(ext[0])
        self.metadata['UR']='%s,%s' % tuple(ext[1])
        self.metadata['LR']='%s,%s' % tuple(ext[2])
        self.metadata['LL']='%s,%s' % tuple(ext[3])

        self.metadata['metadata']='\n'.join(['%s: %s' %(m,hdf_md[m]) for m in hdf_md])

        self.metadata['satellite']='Terra'
        self.metadata['sensor']='ASTER'
        self.metadata['filetype'] = self._gdaldataset.GetDriver().ShortName+'/'+self._gdaldataset.GetDriver().LongName + ' (ASTER)'
        self.metadata['sceneid'] = hdf_md['ASTERSCENEID']
        self.metadata['level'] = hdf_md['PROCESSINGLEVELID']
        if '-' in hdf_md['CALENDARDATE']:imgdate = hdf_md['CALENDARDATE']
        else:imgdate = time.strftime(utilities.dateformat,time.strptime(hdf_md['CALENDARDATE'],'%Y%m%d')) #ISO 8601
        imgtime = hdf_md.get('TIMEOFDAY')
        if imgtime:self.metadata['imgdate'] = time.strftime(utilities.datetimeformat,time.strptime(imgdate+imgtime[0:6],'%Y-%m-%d%H%M%S')) #ISO 8601
        else:self.metadata['imgdate'] = imgdate
        #self.metadata['imgdate'] = hdf_md['CALENDARDATE']
        self.metadata['cloudcover'] = float(hdf_md['SCENECLOUDCOVERAGE'])
        if hdf_md['FLYINGDIRECTION']=='DE':self.metadata['orbit'] = 'Descending'
        else:self.metadata['orbit'] = 'Ascending'
        self.metadata['rotation']=float(hdf_md.get('MAPORIENTATIONANGLE',hdf_md.get('SCENEORIENTATIONANGLE')))
        if abs(self.metadata['rotation']) < 1.0: self.metadata['orientation']='Map oriented'
        else: self.metadata['orientation']='Path oriented'
        self.metadata['sunazimuth'],self.metadata['sunelevation']=map(float,hdf_md['SOLARDIRECTION'].split(','))
        self.metadata['viewangle'] = float(hdf_md['POINTINGANGLE'])
        self.metadata['cols'] = ncols
        self.metadata['rows'] = nrows
        self.metadata['nbands'] = nbands
        self.metadata['datatype'] = datatypes
        self.metadata['nbits'] = nbits
        self.metadata['nodata']=','.join(['0' for i in range(0,nbands)])
        self.metadata['bands'] = bands
        self.metadata['resampling'] = hdf_md.get('RESMETHOD1') #Assume same for all...
        self.metadata['srs']= srs
        self.metadata['epsg']= spatialreferences.IdentifyAusEPSG(srs)
        self.metadata['units']= units
        self.metadata['cellx'],self.metadata['celly']=cellxy,cellxy

        #Geotransform
        ext=[[ulx,uly],[urx,ury],[lrx,lry],[llx,lly],[ulx,uly]]
        ncols=map(int, str(ncols).split(','))
        nrows=map(int, str(nrows).split(','))
        cellx,celly=[],[]
        j=0
        while j < len(ncols):
            gcps=[];i=0
            lr=[[0,0],[ncols[j],0],[ncols[j],nrows[j]],[0,nrows[j]]]
            while i < len(ext)-1: #don't need the last xy pair
                gcp=gdal.GCP()
                gcp.GCPPixel,gcp.GCPLine=lr[i]
                gcp.GCPX,gcp.GCPY=ext[i]
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

        srs=osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        self.metadata['srs']= srs.ExportToWkt()

        self.metadata['UL']='%s,%s' % tuple(ext[0])
        self.metadata['UR']='%s,%s' % tuple(ext[1])
        self.metadata['LR']='%s,%s' % tuple(ext[2])
        self.metadata['LL']='%s,%s' % tuple(ext[3])

        self.metadata['metadata']='\n'.join(['%s: %s' %(m,hdf_md[m]) for m in hdf_md])

        self.metadata['filesize']=sum([os.path.getsize(file) for file in self.filelist])
        self.metadata['compressionratio']=0
        self.metadata['compressiontype']='None'
        self.extent=ext

        #Build gdaldataset object for overviews
        vrtcols=ncols[0]
        vrtrows=nrows[0]
        #vrtbands=[sd for sd,sn in hdf_sd[0:4]]#The 4 VNIR bands
        vrtbands=hdf_sd[0:4]#The 4 VNIR bands
        vrt=geometry.CreateSimpleVRT(vrtbands,vrtcols,vrtrows,datatypes.split(',')[0])
        self._gdaldataset=geometry.OpenDataset(vrt)
        for i in range(1,5):
            self._gdaldataset.GetRasterBand(i).SetNoDataValue(0)
