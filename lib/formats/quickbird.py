'''
Metadata driver for Digital Globe Quickbird imagery
===================================================
@see:Format specification
    U{http://www.digitalglobe.com/digitalglobe2/file.php/646/QuickBird_Imagery_Products-Product_Guide.pdf}
'''
format_regex=[r'[0-9][0-9][A-Z]{3,3}.*\.imd$']#Digital Globe Quickbird
'''Regular expression list of file formats'''

#import base dataset modules
#import __dataset__
import __default__

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
    
class Dataset(__default__.Dataset): 
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __init__(self,f):
        self.filelist=glob.glob(os.path.dirname(f)+'/*')

    def __getmetadata__(self):
        '''Read Metadata for an Digital Globe Quickbird format image as GDAL doesn't quite get it all...

        @todo: does not handle QB tile files (*til). Must check if GDAL can read them...?
        @todo: Fix QB GDA94 Geographic CS "Unknown datum" problem
        '''
        f=self.fileinfo['filepath']
        imddata=self.__getimddata__(f)
        
        tif = os.path.splitext(f)[0]+'.tif'
        img = os.path.splitext(f)[0]+'.img'
        ntf = os.path.splitext(f)[0]+'.ntf'
        til = os.path.splitext(f)[0]+'.til'

        if   os.path.exists(tif):
            __default__.Dataset.__getmetadata__(self, tif)
        elif os.path.exists(img):
            __default__.Dataset.__getmetadata__(self, img)
        elif os.path.exists(ntf):
            __default__.Dataset.__getmetadata__(self, ntf)
        elif os.path.exists(til):
            vrt=self.__gettilevrt__(til,imddata)
            __default__.Dataset.__getmetadata__(self, vrt)
            for tmp in self.filelist:
                if tmp[-3:].lower()=='tif':
                    self.metadata['filetype']='GTiff/GeoTIFF'
                    break
                elif tmp[-3:].lower()=='img':
                    self.metadata['filetype']='HFA/Erdas Imagine Images (.img)'
                    break
                elif tmp[-3:].lower()=='ntf':
                    self.metadata['filetype']='NITF/National Imagery Transmission Format (.ntf)'
                    break
        else:raise IOError, 'Matching Quickbird imagery TIFF/IMG/NTF not found:\n'

        self.metadata['metadata']=open(f).read()

        if imddata.has_key('IMAGE_1'):imgkey='IMAGE_1'
        else:imgkey='SINGLE_IMAGE_PRODUCT'
        if imddata.has_key('MAP_PROJECTED_PRODUCT'):self.metadata['imgdate']=imddata['MAP_PROJECTED_PRODUCT']['earliestAcqTime'][0:10]#.replace('-','') #ISO 8601 format
        elif imddata[imgkey].has_key('firstLineTime'):self.metadata['imgdate']=imddata[imgkey]['firstLineTime'][0:10]#.replace('-','') #ISO 8601 format
        self.metadata['satellite']='Quickbird (%s)' % imddata[imgkey]['satId']
        if imddata['bandId'] == 'P':self.metadata['sensor']='PANCHROMATIC'
        else:
            if imddata['panSharpenAlgorithm']== 'None':self.metadata['sensor']='MULTISPECTRAL'
            else:self.metadata['sensor']='MULTI/PAN'
        if imddata['bandId']=='Multi':
            if imddata['nbands'] == 3:self.metadata['bands'] = 'B,G,R'
            elif imddata['nbands'] == 4:self.metadata['bands'] = 'B,G,R,N'
        else: #'BGRN','RGB','P'
            self.metadata['bands'] = ','.join([l for l in imddata['bandId']])
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
        ds=geometry.OpenDataset(os.path.join(curdir,datasets['filename'][0]))
        rb=ds.GetRasterBand(1)
        DataType=gdal.GetDataTypeName(rb.DataType)
        GeoTransform=','.join(map(str, ds.GetGeoTransform()))
        Projection=ds.GetProjection()
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
                vrtXML.append('  <SimpleSource>')
                vrtXML.append('   <SourceFilename  relativeToVRT="0">%s</SourceFilename>' % os.path.join(curdir,datasets['filename'][tile]))
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
        Generate overviews for Quickbird imagery

        @type  outfile: string
        @param outfile: a filepath to the output overview image. If supplied, format is determined from the file extension
        @type  width:   integer
        @param width:   image width
        @type  format:  string
        @param format:  format to generate overview image, one of ['JPG','PNG','GIF','BMP','TIF']. Not required if outfile is supplied.
        @return:        filepath (if outfile is supplied)/binary image data (if outfile is not supplied)
        '''
        import overviews

        #First check for a browse graphic, no point re-inventing the wheel...
        f=self.fileinfo['filepath']
        browse=os.path.splitext(f)[0]+'-browse.jpg'
        if os.path.exists(browse):

            ds=geometry.OpenDataset(browse)
            if not ds:return __default__.Dataset.getoverview(self,outfile,width,format) #Try it the slow way...

            nodata=0
            if ds.RasterCount == 1:
                bands=[1]
            else:
                bands=[1,2,3]

            #Default stretch type and additional args
            stretch_type='NONE'

            return overviews.getoverview(ds,outfile,width,format,bands,stretch_type)
        else: return __default__.Dataset.getoverview(self,outfile,width,format)#Do it the slow way...
        