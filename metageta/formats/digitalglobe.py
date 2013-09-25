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
Metadata driver for Digital Globe imagery

B{Format specification}:
    - U{http://www.digitalglobe.com/downloads/Imagery_Support_Data_Documentation.pdf}
'''

format_regex=[r'-[0-9]*_[0-9]{2,2}_[A-Z][0-9]{3,3}.*\.imd$',
              r'-[0-9]*_[0-9]{2,2}_[A-Z][0-9]{3,3}.*\.tif$',
              r'-[0-9]*_[0-9]{2,2}_[A-Z][0-9]{3,3}.*\.img$',
              r'-[0-9]*_[0-9]{2,2}_[A-Z][0-9]{3,3}.*\.ntf$']#Digital Globe
'''Regular expression list of file formats'''

#import base dataset modules
import __dataset__
import __default__

# import other modules (use "_"  prefix to import privately)
import sys, os, re, glob, time, math, string
from metageta import utilities, geometry

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
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __init__(self,f):
        if f[:4]=='/vsi':raise NotImplementedError
        self.filelist=glob.glob(os.path.dirname(f)+'/*')
        if os.path.splitext(f)[1].lower() !='imd':
            imd=glob.glob(os.path.splitext(f)[0]+'.[Ii][Mm][Dd]')
            if imd:
                self.__setfileinfo__(imd[0])
            else:raise NotImplementedError, 'No matching IMD file'

        self.exts={'.tif':'GTiff/GeoTIFF','.img':'HFA/Erdas Imagine Images (.img)','.ntf':'NITF/National Imagery Transmission Format (.ntf)','.pix':'PCI Geomatics Database File (.pix)'}
        self.til=False
        self.img=False

        btil,self.til = utilities.exists(os.path.splitext(f)[0]+'.til',True)
        if not btil:
            for ext in self.exts:
                bext,ext = utilities.exists(os.path.splitext(f)[0]+ext,True)
                if bext:
                    self.img=ext
                    break

            if not self.img:raise NotImplementedError, 'Matching DigitalGlobe imagery file not found:\n'

    def __getmetadata__(self):
        '''Read Metadata for an Digital Globe format image as GDAL doesn't quite get it all...

        @todo: Fix QB GDA94 Geographic CS "Unknown datum" problem
        '''
        f=self.fileinfo['filepath']
        imddata=self.__getimddata__(f)

        if self.til:
            vrt=self.__gettilevrt__(self.til,imddata)
            __default__.Dataset.__getmetadata__(self, vrt)
            for tmp in self.filelist:
                for ext in self.exts:
                    if tmp[-4:].lower()==ext:
                        self.metadata['filetype']=self.exts[ext]
                        break
        else:
            __default__.Dataset.__getmetadata__(self, self.img)

        self.metadata['metadata']=open(f).read()

        if imddata.has_key('IMAGE_1'):imgkey='IMAGE_1'
        else:imgkey='SINGLE_IMAGE_PRODUCT'
        if imddata.has_key('MAP_PROJECTED_PRODUCT'):
            imgdate1=imddata['MAP_PROJECTED_PRODUCT']['earliestAcqTime'][0:19]#Already in ISO 8601 format, just strip off millisecs
            imgdate2=imddata['MAP_PROJECTED_PRODUCT']['latestAcqTime'][0:19]
            if imgdate1==imgdate2:self.metadata['imgdate']='%s'%(imgdate1)
            else:self.metadata['imgdate']='%s/%s'%(imgdate1,imgdate2)
        elif imddata[imgkey].has_key('firstLineTime'):
            self.metadata['imgdate']=imddata[imgkey]['firstLineTime'][0:19] #Already in ISO 8601 format, just strip off millisecs
        if imddata[imgkey]['satId']=='QB02':
            self.metadata['satellite']='Quickbird (QB02)'
        elif imddata[imgkey]['satId']=='WV01':
            self.metadata['satellite']='Worldview-1 (WV01)'
        elif imddata[imgkey]['satId']=='WV02':
            self.metadata['satellite']='Worldview-2 (WV02)'
        else:
            self.metadata['satellite']=imddata[imgkey]['satId']
        if imddata['bandId'] == 'P':self.metadata['sensor']='PANCHROMATIC'
        else:
            if imddata['panSharpenAlgorithm']== 'None':self.metadata['sensor']='MULTISPECTRAL'
            else:self.metadata['sensor']='MULTI/PAN'
        #if imddata['bandId']=='Multi':
        #    if imddata['nbands'] == 3:self.metadata['bands'] = 'B,G,R'
        #    elif imddata['nbands'] == 4:self.metadata['bands'] = 'B,G,R,N'
        #else: #'BGRN','RGB','P'
        #    self.metadata['bands'] = ','.join([l for l in imddata['bandId']])
        self.metadata['bands'] = ','.join([b.split('_')[1] for b in imddata.keys() if b[0:5]=='BAND_'])
        if imddata[imgkey].has_key('meanSunEl'):
            self.metadata['sunelevation'] = imddata[imgkey]['meanSunEl']
            self.metadata['sunazimuth'] = imddata[imgkey]['meanSunAz']
        elif imddata[imgkey].has_key('sunEl'):
            self.metadata['sunelevation'] = imddata[imgkey]['sunEl']
            self.metadata['sunazimuth'] = imddata[imgkey]['sunAz']
        self.metadata['level'] = imddata['productLevel']
        if imddata[imgkey].has_key('cloudCover'):
            self.metadata['cloudcover'] = imddata[imgkey]['cloudCover']
        elif imddata[imgkey].has_key('manualCloudCover'):
            self.metadata['cloudcover'] = max([0, imddata[imgkey]['manualCloudCover']]) #hack for -999 cloud cover
        elif imddata[imgkey].has_key('autoCloudCover'):
            self.metadata['cloudcover'] = max([0, imddata[imgkey]['autoCloudCover']])
        if imddata[imgkey].has_key('offNadirViewAngle'):
            self.metadata['viewangle'] = imddata[imgkey]['offNadirViewAngle']
        elif imddata[imgkey].has_key('meanOffNadirViewAngle'):
            self.metadata['viewangle'] = imddata[imgkey]['meanOffNadirViewAngle']
        if imddata[imgkey].has_key('CatId'):
            self.metadata['sceneid'] = imddata[imgkey]['CatId']
        if imddata[imgkey].has_key('resamplingKernel'):
            self.metadata['resampling'] = imddata[imgkey]['resamplingKernel']
        elif imddata.has_key('MAP_PROJECTED_PRODUCT') and imddata['MAP_PROJECTED_PRODUCT'].has_key('resamplingKernel'):
            self.metadata['resampling'] = imddata['MAP_PROJECTED_PRODUCT']['resamplingKernel']
        if imddata.has_key('MAP_PROJECTED_PRODUCT') and imddata['MAP_PROJECTED_PRODUCT'].has_key('DEMCorrection'):
            self.metadata['demcorrection'] = imddata['MAP_PROJECTED_PRODUCT']['DEMCorrection']
        #self.extent is set in __default__.Dataset.__getmetadata__()

    def __gettilevrt__(self,f,imddata):
        til=iter(open(f).readlines())
        tileinfo={}
        datasets={}
        line=til.next()
        while line: #Extract all keys and values from the header file into a dictionary
            line=line.strip().strip(';').replace('"','')
            if line == 'END':break
            if 'BEGIN_GROUP' in line:
                line=til.next()
                while line:
                    line=line.strip().strip(';').replace('"','')
                    if 'END_GROUP' in line:break
                    else:
                        dat=map(string.strip, line.split('=',1))
                        if not dat[0] in datasets:datasets[dat[0]]=[]
                        datasets[dat[0]].append(dat[1])
                    line=til.next()
            else:
                var=map(string.strip, line.split('=',1))
                tileinfo[var[0]]=var[1]
            line=til.next()
        curdir=os.path.dirname(f)
        bimg,img=utilities.exists(os.path.join(curdir,datasets['filename'][0]),True)
        ds=geometry.OpenDataset(img)
        rb=ds.GetRasterBand(1)
        DataType=gdal.GetDataTypeName(rb.DataType)
        GeoTransform=ds.GetGeoTransform()
        Projection=ds.GetProjection()
        if GeoTransform==(0.0, 1.0, 0.0, 0.0, 0.0, 1.0):
            GeoTransform=gdal.GCPsToGeoTransform(ds.GetGCPs())
        if Projection=='':
            Projection=ds.GetGCPProjection()
        GeoTransform=','.join(map(str, GeoTransform))
        numTiles=int(tileinfo['numTiles'])
        BlockXSize,BlockYSize=rb.GetBlockSize()

        vrtXML = []
        vrtXML.append('<VRTDataset rasterXSize="%s" rasterYSize="%s">' % (imddata['numColumns'],imddata['numRows']))
        vrtXML.append('<SRS>%s</SRS>' % Projection)
        vrtXML.append('<GeoTransform>%s</GeoTransform>' % GeoTransform)

        for b, band in enumerate(imddata['bands']):
            b+=1
            vrtXML.append(' <VRTRasterBand dataType="%s" band="%s">' % (DataType,b))
            #vrtXML.append('  <ColorInterp>Gray</ColorInterp>')
            for tile in range(0,numTiles):
                tileSizeX=int(datasets['URColOffset'][tile])-int(datasets['ULColOffset'][tile])+1
                tileSizeY=int(datasets['LLRowOffset'][tile])-int(datasets['ULRowOffset'][tile])+1
                ULColOffset=datasets['ULColOffset'][tile]
                ULRowOffset=datasets['ULRowOffset'][tile]
                bimg,img=utilities.exists(os.path.join(curdir,datasets['filename'][tile]),True)
                vrtXML.append('  <SimpleSource>')
                vrtXML.append('   <SourceFilename  relativeToVRT="0">%s</SourceFilename>' % img)
                vrtXML.append('   <SourceBand>%s</SourceBand>' % (b))
                vrtXML.append('   <SourceProperties RasterXSize="%s" RasterYSize="%s" DataType="%s"/>'%(tileSizeX,tileSizeY,DataType))# BlockXSize="%s" BlockYSize="%s"/>'(tileSizeX,tileSizeY,DataType,BlockXSize,BlockYSize))
                vrtXML.append('   <SrcRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' %(tileSizeX,tileSizeY))
                vrtXML.append('   <DstRect xOff="%s" yOff="%s" xSize="%s" ySize="%s"/>' % (ULColOffset,ULRowOffset,tileSizeX,tileSizeY))
                vrtXML.append('  </SimpleSource>')
            vrtXML.append(' </VRTRasterBand>')
        vrtXML.append('</VRTDataset>')
        vrtXML='\n'.join(vrtXML)
        return vrtXML

    def __getimddata__(self,f):
        #Loop thru and parse the IMD file.
        #would be easier to walk the nodes in the XML files, but not all of our QB imagery has this
        #perhaps someone deleted them...?
        lines=iter(open(f).readlines())
        imddata={}
        bands=[]
        line=lines.next()
        while line:
            line=[item.strip() for item in line.replace('"','').split('=')]
            #line = map(string.strip, lines[i].split('='))
            group=line[0]
            if group == 'END;':break
            value=line[1]
            if group == 'BEGIN_GROUP':
                group=value
                subdata={}
                if 'BAND_' in group:bands.append(group)
                while line:
                    line=lines.next()
                    line = [l.replace('"','').strip() for l in line.split('=')]
                    subgroup=line[0]
                    subvalue=line[1]
                    if subgroup == 'END_GROUP':break
                    elif line[1] == '(':
                        while line:
                            line=lines.next()
                            line = line.replace('"','').strip()
                            subvalue+=line
                            if line[-1:]==';':
                                subvalue=eval(subvalue.strip(';'))
                                break
                    else:subvalue=subvalue.strip(';')
                    subdata[subgroup]=subvalue
                imddata[group]=subdata
            else: imddata[group]=value.strip(');')
            line=lines.next()
        imddata['bands']=bands
        imddata['nbands']=len(bands)
        return imddata

    def getoverview(self,outfile=None,width=800,format='JPG'):
        '''
        Generate overviews for Digital Globe imagery

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
        f=self.fileinfo['filepath']
        browse=os.path.splitext(f)[0]+'-browse.jpg'
        if os.path.exists(browse):

            try:return overviews.resize(browse,outfile,width)
            except:return __default__.Dataset.getoverview(self,outfile,width,format) #Try it the slow way...

        else: return __default__.Dataset.getoverview(self,outfile,width,format)#Do it the slow way...

