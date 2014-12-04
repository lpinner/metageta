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
Generate overviews for imagery

@note:This module is not generally used on its own, but may be if required.
      It's is usually used only by L{Dataset.getoverview()<formats.__dataset__.Dataset.getoverview>} methods.
'''

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
from metageta import geometry,utilities
import sys, os.path, os, csv, re, struct, math, glob, string, time,shutil, tempfile

def getoverview(ds,outfile,width,format,bands,stretch_type,*stretch_args):
    '''
    Generate overviews for imagery

    @type  ds:      C{GDALDataset}
    @param ds:      a GDALDataset object
    @type  outfile: C{str}
    @param outfile: a filepath to the output overview image. If supplied, format is determined from the file extension
    @type  width:   C{int}
    @param width:   output image width
    @type  format:  C{str}
    @param format:  format to generate overview image, one of ['JPG','PNG','GIF','BMP','TIF']. Not required if outfile is supplied.
    @type  bands:   C{list}
    @param bands:   list of band numbers (base 1) in processing order - e.g [3,2,1]
    @type  stretch_type:  C{str}
    @param stretch_type:  stretch to apply to overview image,
                          one of [L{NONE<_stretch_NONE>},L{PERCENT<_stretch_PERCENT>},L{MINMAX<_stretch_MINMAX>},L{STDDEV<_stretch_STDDEV>},L{COLOURTABLE<_stretch_COLOURTABLE>},L{COLOURTABLELUT<_stretch_COLOURTABLELUT>},L{RANDOM<_stretch_RANDOM>},L{UNIQUE<_stretch_UNIQUE>}].
    @type stretch_args:   C{list}
    @param stretch_args:  args to pass to the stretch algorithms
    @rtype:         C{str}
    @return:        filepath (if outfile is supplied)/binary image data (if outfile is not supplied)
    '''

    #mapping table for file extension -> GDAL format code
    imageformats={'JPG':'JPEG', #JPEG JFIF (.jpg)
                  'PNG':'PNG',  #Portable Network Graphics (.png)
                  'GIF':'GIF',  #Graphics Interchange Format (.gif)
                  'BMP':'BMP',  #Microsoft Windows Device Independent Bitmap (.bmp)
                  'TIF':'GTiff' #Tagged Image File Format/GeoTIFF (.tif)
                 }
    worldfileexts={'JPG':'.jgw', #JPEG JFIF (.jpg)
                   'PNG':'.pgw',  #Portable Network Graphics (.png)
                   'GIF':'.gfw',  #Graphics Interchange Format (.gif)
                   'BMP':'.bpw',  #Microsoft Windows Device Independent Bitmap (.bmp)
                   'TIF':'.tfw' #Tagged Image File Format/GeoTIFF (.tif)
                 }
    if outfile:
        outfile=utilities.encode(outfile)
        format=os.path.splitext(outfile)[1].replace('.','')                  #overrides "format" arg if supplied
    ovdriver=gdal.GetDriverByName(imageformats.get(format.upper(), 'JPEG'))  #Get format code, default to 'JPEG' if supplied format doesn't match the predefined ones...

    cols=ds.RasterXSize
    rows=ds.RasterYSize
    vrtcols=width
    vrtrows=int(math.ceil(width*float(rows)/cols))
    gt=ds.GetGeoTransform()
    vrtpx=cols/float(vrtcols)*gt[1]
    vrtpy=rows/float(vrtrows)*gt[5]
    vrtgt=(gt[0],vrtpx,gt[2],gt[3],gt[4],vrtpy)

    vrtdrv=gdal.GetDriverByName('VRT')
    #tempvrts={} #dict with keys=file descriptor and values=[filename,GDALDataset]

    #Below is a bit of a kludge to handle creating a VRT that is based on an in-memory vrt file
    #drv=ds.GetDriver().ShortName
    #desc=ds.GetDescription()
    #if drv == 'VRT':
    #    if not desc or desc[0] == '<':# input path is an in-memory vrt file
    #        vrtfd,vrtfn=tempfile.mkstemp('.vrt')
    #        ds=vrtdrv.CreateCopy(vrtfn,ds)
    #        tempvrts[vrtfd]=[vrtfn,ds]

    #if stretch_type != 'NONE':
    #    tmpxml=stretch('NONE',vrtcols,vrtrows,ds,bands)
    #    vrtfd,vrtfn=tempfile.mkstemp('.vrt')
    #    ds=vrtdrv.CreateCopy(vrtfn,geometry.OpenDataset(tmpxml))
    #    tempvrts[vrtfd]=[vrtfn,ds]

    #vrtxml=stretch(stretch_type,vrtcols,vrtrows,ds,bands,*stretch_args)
    #vrtfn='/vsimem/%s.vrt'%tempfile._RandomNameSequence().next()
    #geometry.write_vsimem(vrtfn,vrtxml)
    vrtfn=stretch(stretch_type,vrtcols,vrtrows,ds,bands,*stretch_args)
    gdal.UseExceptions()
    vrtds=gdal.OpenShared(vrtfn, gdal.GA_ReadOnly) #geometry.OpenDataset(vrtfn)

    vrtds.SetGeoTransform(vrtgt)
    if outfile:
        cpds=ovdriver.CreateCopy(outfile, vrtds)
        wf_ext=worldfileexts.get(format.upper(), '.jgw')
        open(outfile[:-4]+wf_ext,'w').write('\n'.join([
            str(vrtgt[1]),
            str(vrtgt[4]),
            str(vrtgt[2]),
            str(vrtgt[5]),
            str(vrtgt[0] + 0.5 * vrtgt[1] + 0.5 * vrtgt[2]),
            str(vrtgt[3] + 0.5 * vrtgt[4] + 0.5 * vrtgt[5])]))

        if not cpds:raise geometry.GDALError, 'Unable to generate overview image.'
    else:
        #fd,fn=tempfile.mkstemp(suffix='.'+format.lower(), prefix='getoverviewtempimage')
        fn='/vsimem/%s.%s'%(tempfile._RandomNameSequence().next(),format.lower())
        cpds=ovdriver.CreateCopy(fn, vrtds)
        if not cpds:raise geometry.GDALError, 'Unable to generate overview image.'

        #outfile=os.fdopen(fd).read()
        #os.unlink(fn)
        outfile=read_vsimem(fn)
        gdal.Unlink(fn)
    #for vrt in tempvrts:
    #    tempvrts[vrt][1]=None
    #    os.close(vrt)
    #    del tempvrts[vrt][1]
    #    os.unlink(tempvrts[vrt][0])
    return outfile
#========================================================================================================
#Stretch algorithms
#========================================================================================================
def stretch(stretchType,vrtcols,vrtrows,ds,*args):
    '''Calls the requested stretch function.

        For further info on VRT's, see the U{GDAL VRT Tutorial<http://www.gdal.org/gdal_vrttut.html>}

        @type stretchType:  C{str}
        @param stretchType: One of COLORTABLE, COLORTABLELUT, COLOURTABLE, COLOURTABLELUT,
                                   MINMAX, NONE, PERCENT, RANDOM, STDDEV, UNIQUE
        @type vrtcols:      C{int}
        @param vrtcols:     The number of columns in the output VRT
        @type vrtrows:      C{int}
        @param vrtrows:     The number of rows in the output VRT
        @param args:        Other args
        @rtype:             C{xml}
        @return:            VRT XML string
    '''
    stretch=globals()['_stretch_'+stretchType.upper()]
    vrt=stretch(vrtcols,vrtrows,ds,*args)
    return geometry.CreateCustomVRT(vrt,vrtcols,vrtrows)

def _stretch_NONE(vrtcols,vrtrows,ds,bands):
    ''' No stretch.

        For further info on VRT's, see the U{GDAL VRT Tutorial<http://www.gdal.org/gdal_vrttut.html>}

        @type ds:     C{gdal.Dataset}
        @param ds:    A gdal dataset object
        @type bands:  C{[int,...,int]}
        @param bands: A list of band numbers to output (in output order). E.g [4,2,1]
                      Band numbers are not zero indexed.
        @rtype:       C{xml}
        @return:      VRT XML string
    '''
    vrt=[]
    rb=ds.GetRasterBand(1)
    nodata=rb.GetNoDataValue()
    if rb.DataType == gdal.GDT_Byte:
        rescale=False
    else:
        rescale=True
        dfScaleSrcMin,dfScaleSrcMax=GetDataTypeRange(rb.DataType)
        dfRatio,dfOffset = GetScaleRatioOffset(dfScaleSrcMin,dfScaleSrcMax,0,255)
    for bandnum, band in enumerate(bands):
        rb=ds.GetRasterBand(band)
        vrt.append('  <VRTRasterBand dataType="Byte" band="%s">' % str(bandnum+1))
        #if nodata is not None:vrt.append('    <NoDataValue>%s</NoDataValue>'%nodata)
        if rescale:
            vrt.append('    <ComplexSource>')
            vrt.append('      <SourceFilename relativeToVRT="0">%s</SourceFilename>' % ds.GetDescription())
            vrt.append('      <SourceBand>%s</SourceBand>' % band)
            vrt.append('      <SrcRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (ds.RasterXSize,ds.RasterYSize))
            vrt.append('      <DstRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (vrtcols,vrtrows))
            vrt.append('      <ScaleOffset>%s</ScaleOffset>' % dfOffset)
            vrt.append('      <ScaleRatio>%s</ScaleRatio>' % dfRatio)
            vrt.append('    </ComplexSource>')
        else:
            vrt.append('    <SimpleSource>')
            vrt.append('      <SourceFilename relativeToVRT="0">%s</SourceFilename>' % ds.GetDescription())
            vrt.append('      <SourceBand>%s</SourceBand>' % band)
            vrt.append('      <SrcRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (ds.RasterXSize,ds.RasterYSize))
            vrt.append('      <DstRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (vrtcols,vrtrows))
            vrt.append('    </SimpleSource>')
        vrt.append('  </VRTRasterBand>')
    return '\n'.join(vrt)

def _stretch_PERCENT(vrtcols,vrtrows,ds,bands,low,high):
    ''' Min, max percentage stretch.

        For further info on VRT's, see the U{GDAL VRT Tutorial<http://www.gdal.org/gdal_vrttut.html>}

        @type ds:     C{gdal.Dataset}
        @param ds:    A gdal dataset object
        @type bands:  C{[int,...,int]}
        @param bands: A list of band numbers to output (in output order). E.g [4,2,1]
                      Band numbers are not zero indexed.
        @type low:    C{float}
        @param low:   Minimum percentage
        @type high:   C{float}
        @param high:  Maximum percentage
        @rtype:       C{xml}
        @return:      VRT XML string
    '''
    #if low >=1:
    if high > 1:
        low=low/100.0
        high=high/100.0
    vrt=[]
    for bandnum, band in enumerate(bands):
        rb=ds.GetRasterBand(band)
        nodata=rb.GetNoDataValue()
        nbits=gdal.GetDataTypeSize(rb.DataType)
        dfScaleSrcMin,dfScaleSrcMax=GetDataTypeRange(rb.DataType)
        try:dfBandMin,dfBandMax,dfBandMean,dfBandStdDev = GetStatistics(rb,1,1)
        except:dfBandMin,dfBandMax,dfBandMean,dfBandStdDev = GetStatistics(rb,0,1)
        dfBandRange=dfBandMax-dfBandMin
        if nbits == 8 or 2 < dfBandRange <= 255:
            nbins=int(math.ceil(dfBandRange))
            binsize=1
        else:
            nbins=256
            binsize=int(math.ceil(dfBandRange/nbins))
            if binsize<=2:binsize=dfBandRange/nbins

        #hs=rb.GetHistogram(dfBandMin+abs(dfBandMin)*0.0001,dfBandMax-abs(dfBandMax)*0.0001, nbins,include_out_of_range=1,approx_ok=0)
        #hs=rb.GetHistogram(dfBandMin+abs(dfBandMin)*0.0001,dfBandMax-abs(dfBandMax)*0.0001, nbins,include_out_of_range=1,approx_ok=1)
        hs=rb.GetHistogram(dfBandMin+abs(dfBandMin)*0.0001,dfBandMax-abs(dfBandMax)*0.0001, nbins,include_out_of_range=0,approx_ok=1)
        #Check that outliers haven't really skewed the histogram
        #this is a kludge to workaround datasets with multiple nodata values
        # for j in range(0,10):
        #     if len([v for v in hs if v > 0]) < nbins/4: #if only 25% of the bins have values...
        #        startbin=256
        #        lastbin=0
        #        for i,bin in enumerate(hs):
        #            if bin > 0:
        #                lastbin=i
        #                if i<startbin:startbin=i
        #        dfBandMin=dfBandMin+startbin*binsize
        #        dfBandMax=dfBandMin+lastbin*binsize+binsize
        #        #hs=rb.GetHistogram(dfBandMin-abs(dfBandMin)*0.0001,dfBandMax+abs(dfBandMax)*0.0001,include_out_of_range=1,approx_ok=0)
        #        hs=rb.GetHistogram(dfBandMin-abs(dfBandMin)*0.0001,dfBandMax+abs(dfBandMax)*0.0001,include_out_of_range=1,approx_ok=1)
        #        if nbits == 8:binsize=1
        #        else:binsize=(dfBandRange)/nbins
        #     else:break
        try:
            dfScaleSrcMin=max([dfScaleSrcMin, HistPercentileValue(hs, low, binsize,dfBandMin)])
            dfScaleSrcMax=min([dfScaleSrcMax, HistPercentileValue(hs, high, binsize,dfBandMin)])
            dfScaleDstMin,dfScaleDstMax=0.0,255.0 #Always going to be Byte for output jpegs
            dfScale = (dfScaleDstMax - dfScaleDstMin) / (dfScaleSrcMax - dfScaleSrcMin)
            dfOffset = -1 * dfScaleSrcMin * dfScale + dfScaleDstMin
        except:
            dfOffset=0
            dfScale=1

        vrt.append('  <VRTRasterBand dataType="Byte" band="%s">' % str(bandnum+1))
        #if nodata is not None:vrt.append('    <NoDataValue>%s</NoDataValue>'%nodata)
        vrt.append('    <ComplexSource>')
        vrt.append('      <SourceFilename relativeToVRT="0">%s</SourceFilename>' % ds.GetDescription())
        vrt.append('      <SourceBand>%s</SourceBand>' % band)
        vrt.append('      <SrcRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (ds.RasterXSize,ds.RasterYSize))
        vrt.append('      <DstRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (vrtcols,vrtrows))
        vrt.append('      <ScaleOffset>%s</ScaleOffset>' % dfOffset)
        vrt.append('      <ScaleRatio>%s</ScaleRatio>' % dfScale)
        vrt.append('    </ComplexSource>')
        vrt.append('  </VRTRasterBand>')
    return '\n'.join(vrt)

def _stretch_MINMAX(vrtcols,vrtrows,ds,bands):
    ''' Minimum-maximum stretch.

        For further info on VRT's, see the U{GDAL VRT Tutorial<http://www.gdal.org/gdal_vrttut.html>}

        @type ds:     C{gdal.Dataset}
        @param ds:    A gdal dataset object
        @type bands:  C{[int,...,int]}
        @param bands: A list of band numbers to output (in output order). E.g [4,2,1]
                      Band numbers are not zero indexed.
        @rtype:       C{xml}
        @return:      VRT XML string
    '''
    vrt=[]
    for bandnum, band in enumerate(bands):
        rb=ds.GetRasterBand(band)
        nodata=rb.GetNoDataValue()
        dfScaleSrcMin,dfScaleSrcMax=GetDataTypeRange(rb.DataType)
        try:dfBandMin,dfBandMax,dfBandMean,dfBandStdDev = GetStatistics(rb,1,1)
        except:dfBandMin,dfBandMax,dfBandMean,dfBandStdDev = GetStatistics(rb,0,1)
        dfScaleDstMin,dfScaleDstMax=0.0,255.0 #Always going to be Byte for output jpegs
        dfScale = (dfScaleDstMax - dfScaleDstMin) / (dfScaleSrcMax - dfScaleSrcMin)
        dfOffset = -1 * dfScaleSrcMin * dfScale + dfScaleDstMin

        vrt.append('  <VRTRasterBand dataType="Byte" band="%s">' % str(bandnum+1))
        #if nodata is not None:vrt.append('    <NoDataValue>%s</NoDataValue>'%nodata)
        vrt.append('    <ComplexSource>')
        vrt.append('      <SourceFilename relativeToVRT="0">%s</SourceFilename>' % ds.GetDescription())
        vrt.append('      <SourceBand>%s</SourceBand>' % band)
        vrt.append('      <SrcRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (ds.RasterXSize,ds.RasterYSize))
        vrt.append('      <DstRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (vrtcols,vrtrows))
        vrt.append('      <ScaleOffset>%s</ScaleOffset>' % dfOffset)
        vrt.append('      <ScaleRatio>%s</ScaleRatio>' % dfScale)
        vrt.append('    </ComplexSource>')
        vrt.append('  </VRTRasterBand>')
    return '\n'.join(vrt)

def _stretch_STDDEV(vrtcols,vrtrows,ds,bands,std):
    ''' Standard deviation stretch.

        For further info on VRT's, see the U{GDAL VRT Tutorial<http://www.gdal.org/gdal_vrttut.html>}

        @type ds:     C{gdal.Dataset}
        @param ds:    A gdal dataset object
        @type bands:  C{[int,...,int]}
        @param bands: A list of band numbers to output (in output order). E.g [4,2,1]
                      Band numbers are not zero indexed.
        @type std:    float
        @param std:   Standard deviation
        @rtype:       C{xml}
        @return:      VRT XML string
    '''
    vrt=[]
    for bandnum, band in enumerate(bands):
        rb=ds.GetRasterBand(band)
        nodata=rb.GetNoDataValue()
        dfScaleSrcMin,dfScaleSrcMax=GetDataTypeRange(rb.DataType)
        try: dfBandMin,dfBandMax,dfBandMean,dfBandStdDev = GetStatistics(rb,1,1)
        except:dfBandMin,dfBandMax,dfBandMean,dfBandStdDev = GetStatistics(rb,0,1)
        dfScaleDstMin,dfScaleDstMax=0.0,255.0 #Always going to be Byte for output jpegs
        dfScaleSrcMin=max([dfScaleSrcMin, math.floor(dfBandMean-std*dfBandStdDev)])
        dfScaleSrcMax=min([dfScaleSrcMax, math.ceil(dfBandMean+std*dfBandStdDev)])

        try:dfScale = (dfScaleDstMax - dfScaleDstMin) / (dfScaleSrcMax - dfScaleSrcMin)
        except ZeroDivisionError:return _stretch_RANDOM(vrtcols,vrtrows,ds,bands)

        dfOffset = -1 * dfScaleSrcMin * dfScale + dfScaleDstMin

        vrt.append('  <VRTRasterBand dataType="Byte" band="%s">' % str(bandnum+1))
        #if nodata is not None:vrt.append('    <NoDataValue>%s</NoDataValue>'%nodata)
        vrt.append('    <ComplexSource>')
        vrt.append('      <SourceFilename relativeToVRT="0">%s</SourceFilename>' % ds.GetDescription())
        vrt.append('      <SourceBand>%s</SourceBand>' % band)
        vrt.append('      <SrcRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (ds.RasterXSize,ds.RasterYSize))
        vrt.append('      <DstRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (vrtcols,vrtrows))
        vrt.append('      <ScaleOffset>%s</ScaleOffset>' % dfOffset)
        vrt.append('      <ScaleRatio>%s</ScaleRatio>' % dfScale)
        vrt.append('    </ComplexSource>')
        vrt.append('  </VRTRasterBand>')
    return '\n'.join(vrt)

def _stretch_UNIQUE(vrtcols,vrtrows,ds,bands,vals):
    ''' Unique values stretch.

        For further info on VRT's, see the U{GDAL VRT Tutorial<http://www.gdal.org/gdal_vrttut.html>}

        @type ds:      C{gdal.Dataset}
        @param ds:     A gdal dataset object
        @type bands:   C{[int]}
        @param bands:  Band number to output. Band numbers are not zero indexed.
        @type vals:    C{list/tuple}
        @param vals:   List of cell values and R,G,B[,A] values e.g [(12, 0,0,0), (25, 255,255,255)]
        @rtype:        C{xml}
        @return:       VRT XML string
    '''
    band=bands[0]
    rb=ds.GetRasterBand(band)
    nodata=rb.GetNoDataValue()
    vrt=[]
    for iclr,clr in enumerate(['Red','Green','Blue']):
        vrt.append('  <VRTRasterBand dataType="Byte" band="%s">' % str(iclr+1))
        #if nodata is not None:vrt.append('    <NoDataValue>%s</NoDataValue>'%nodata)
        vrt.append('    <ColorInterp>%s</ColorInterp>' % clr)
        vrt.append('    <ComplexSource>')
        vrt.append('      <SourceFilename relativeToVRT="0">%s</SourceFilename>' % ds.GetDescription())
        vrt.append('      <SourceBand>%s</SourceBand>'%band)
        vrt.append('      <SrcRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (ds.RasterXSize,ds.RasterYSize))
        vrt.append('      <DstRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (vrtcols,vrtrows))
        vrt.append('      <LUT>%s</LUT>' % ','.join(['%s:%s' % (v[0], v[iclr+1]) for v in vals]))
        vrt.append('    </ComplexSource>')
        vrt.append('  </VRTRasterBand>')
    return '\n'.join(vrt)

def _stretch_RANDOM(vrtcols,vrtrows,ds,bands):
    ''' Random values stretch.

        For further info on VRT's, see the U{GDAL VRT Tutorial<http://www.gdal.org/gdal_vrttut.html>}

        @type ds:      C{gdal.Dataset}
        @param ds:     A gdal dataset object
        @type bands:   C{[int]}
        @param bands:  Band number to output. Band numbers are not zero indexed.
        @rtype:        C{xml}
        @return:       VRT XML string

        @change: 22/01/2010 lpinner fix for U{r2<http://code.google.com/p/metageta/issues/detail?id=2&can=1>}
    '''
    from random import randint as r

    band=bands[0]
    vals=[]

    rb=ds.GetRasterBand(bands[0])
    min,max=map(int,rb.ComputeRasterMinMax())

    nodata=rb.GetNoDataValue() #Is this kludge required if we include <NoDataValue> in the VRT...?
    if nodata is not None:
        nodata=int(nodata)
        nodatavals=(nodata,255,255,255,0)
        if min>nodata:vals.append(nodatavals)

    for i in range(min,max+1):#build random RGBA tuple
        if nodata is not None:
            if i != nodata:vals.append((i,r(0,255),r(0,255),r(0,255),255))
            else:vals.append(nodatavals)
        else:vals.append((i,r(0,255),r(0,255),r(0,255),255))

    if nodata is not None and nodata > max:
        vals.append(nodatavals)

    return _stretch_UNIQUE(vrtcols,vrtrows,ds,bands,vals)

def _stretch_COLOURTABLE(vrtcols,vrtrows,ds,bands):
    ''' Colour table stretch.

        This is a workaround for GDAL not liking color tables with negative or missing values.
        U{r3253<http://trac.osgeo.org/gdal/ticket/3253>}

        For further info on VRT's, see the U{GDAL VRT Tutorial<http://www.gdal.org/gdal_vrttut.html>}

        @type ds:      C{gdal.Dataset}
        @param ds:     A gdal dataset object
        @type bands:   C{[int]}
        @param bands:  Band number to output. Band numbers are not zero indexed.
        @rtype:        C{xml}
        @return:       VRT XML string
    '''
    band=bands[0]
    rb=ds.GetRasterBand(band)
    nodata=rb.GetNoDataValue()
    if nodata is not None:nodata=int(nodata)
    ct=rb.GetColorTable()
    min,max=map(int,rb.ComputeRasterMinMax())
    #rat=rb.GetHistogram(min, max, abs(min)+abs(max)+1,include_out_of_range=1,approx_ok=0)
    rat=rb.GetHistogram(min, max, abs(min)+abs(max)+1,include_out_of_range=1,approx_ok=1)
    vals=[]
    ct_count=ct.GetCount()
    for val,count in zip(range(min,max+1),rat):
        if val != nodata and count > 0 and val < ct_count: #Bugfix - sometime there are more values than
            ce=[val]                                       #colortable entries which causes gdal to segfault
            ce.extend(ct.GetColorEntry(val))               #http://trac.osgeo.org/gdal/ticket/3271
            vals.append(ce)
        else:vals.append([val,255,255,255,0])
    return _stretch_UNIQUE(vrtcols,vrtrows,ds,bands,vals)
##def _stretch_COLOURTABLE(vrtcols,vrtrows,ds,bands): #gdal doesn't handle esri colour tables with missing or negative values
##    vrt=[]
##    colours=['Red','Green','Blue']
##    for index, colour in enumerate(colours):
##        vrt.append('  <VRTRasterBand dataType="Byte" band="%s">' % str(index+1))
##        vrt.append('    <ColorInterp>%s</ColorInterp>' % colour)
##        vrt.append('    <ComplexSource>')
##        vrt.append('      <SourceFilename relativeToVRT="0">%s</SourceFilename>' % ds.GetDescription())
##        vrt.append('      <SourceBand>%s</SourceBand>' % bands[0])
##        vrt.append('      <SrcRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (ds.RasterXSize,ds.RasterYSize))
##        vrt.append('      <DstRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (vrtcols,vrtrows))
##        vrt.append('      <ColorTableComponent>%s</ColorTableComponent>' % str(index+1))
##        vrt.append('    </ComplexSource>')
##        vrt.append('  </VRTRasterBand>')
##    return '\n'.join(vrt)
_stretch_COLORTABLE=_stretch_COLOURTABLE #Synonym for the norteamericanos

def _stretch_COLOURTABLELUT(vrtcols,vrtrows,ds,bands,clr):
    ''' Colour table file LUT stretch.

        This is a workaround for GDAL not liking color tables with negative or missing values.
        U{r3253<http://trac.osgeo.org/gdal/ticket/3253>}

        For further info on VRT's, see the U{GDAL VRT Tutorial<http://www.gdal.org/gdal_vrttut.html>}

        @type ds:      C{gdal.Dataset}
        @param ds:     A gdal dataset object
        @type bands:   C{[int]}
        @param bands:  Band number to output. Band numbers are not zero indexed.
        @type clr:     C{str}
        @param clr:    Path to colour lookup file.
                       See file format in L{ParseColourLUT<ParseColourLUT>}
        @rtype:        C{xml}
        @return:       VRT XML string
    '''
    vrt=[]
    band=bands[0]
    rb=ds.GetRasterBand(band)
    nodata=rb.GetNoDataValue()
    lut=ColourLUT(clr,rb)
    for iclr,clr in enumerate(['Red','Green','Blue']):
        vrt.append('  <VRTRasterBand dataType="Byte" band="%s">' % str(iclr+1))
        #if nodata is not None:vrt.append('    <NoDataValue>%s</NoDataValue>'%nodata)
        vrt.append('    <ColorInterp>%s</ColorInterp>' % clr)
        vrt.append('    <ComplexSource>')
        vrt.append('      <SourceFilename relativeToVRT="0">%s</SourceFilename>' % ds.GetDescription())
        vrt.append('      <SourceBand>1</SourceBand>')
        vrt.append('      <SrcRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (ds.RasterXSize,ds.RasterYSize))
        vrt.append('      <DstRect xOff="0" yOff="0" xSize="%s" ySize="%s"/>' % (vrtcols,vrtrows))
        vrt.append('      <LUT>\n        %s\n      </LUT>' % ',\n        '.join(['%s:%s' % (v[0], v[iclr+1]) for v in lut]))
        vrt.append('    </ComplexSource>')
        vrt.append('  </VRTRasterBand>')
    return '\n'.join(vrt)
_stretch_COLORTABLELUT=_stretch_COLOURTABLELUT #Synonym for the norteamericanos
#========================================================================================================
#Helper functions
#========================================================================================================
def GetStatistics(band,*args,**kwargs):
    gdal.UseExceptions()
    try:
        stats=band.GetStatistics(*args,**kwargs)
    except:
        gdal.DontUseExceptions()
        raise geometry.GDALError
    gdal.DontUseExceptions()
    return stats
def GetScaleRatioOffset(dfScaleSrcMin,dfScaleSrcMax,dfScaleDstMin,dfScaleDstMax):
    ''' Calculate data scale and offset

        @type dfScaleSrcMin:   C{float}
        @param dfScaleSrcMin:  input minimum value
        @type dfScaleSrcMax:   C{float}
        @param dfScaleSrcMax:  input maximum value
        @type dfScaleDstMin:   C{float}
        @param dfScaleDstMin:  output minimum value
        @type dfScaleDstMax:   C{float}
        @param dfScaleDstMax:  output maximum value
        @rtype:           C{[float,float]}
        @return:          Scale and offset values
    '''
    dfScaleSrcMin,dfScaleSrcMax,dfScaleDstMin,dfScaleDstMax=map(float, [dfScaleSrcMin,dfScaleSrcMax,dfScaleDstMin,dfScaleDstMax])
    dfScale = (float(dfScaleDstMax) - dfScaleDstMin) / (dfScaleSrcMax - dfScaleSrcMin)
    dfOffset = -1 * dfScaleSrcMin * dfScale + dfScaleDstMin
    return dfScale,dfOffset

def GetDataTypeRange(datatype):
    ''' Calculate data type range

        @type datatype:   C{int}
        @param datatype:  gdal data type constant
        @rtype:           C{[int,int]}
        @return:          Min and max value for data type
    '''
    nbits   =gdal.GetDataTypeSize(datatype)
    datatype=gdal.GetDataTypeName(datatype)
    if datatype[0:4] in ['Byte','UInt']:
        dfScaleSrcMin=0             #Unsigned
        dfScaleSrcMax=2**(nbits)-1
    else:
        dfScaleSrcMin=-2**(nbits-1) #Signed
        dfScaleSrcMax= 2**(nbits-1)-1
    return (dfScaleSrcMin,dfScaleSrcMax)
def HistPercentileValue(inhist, percent, binsize, lowerlimit):
    ''' Returns the score at a given percentile relative to the distribution given by inhist.

        Usage:   histpercentilevalue(inhist, percent, binsize,lowerlimit)

        @type inhist:       C{list}
        @param inhist:      gdal histogram
        @type percent:      C{float}
        @param percent:     percentile to return score for
        @type binsize:      C{float}
        @param binsize:     width of histogram bins
        @type lowerlimit:   C{float}
        @param lowerlimit:  min value of histogram
        @rtype:             C{float}
        @return:            score at a given percentile
    '''

    # NOTE this function is from "python-statlib" - http://code.google.com/p/python-statlib/
    #
    # Copyright (c) 1999-2007 Gary Strangman; All Rights Reserved.
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
    #
    # Comments and/or additions are welcome (send e-mail to:
    # strang@nmr.mgh.harvard.edu).
    #
    if percent > 1:
        percent = percent / 100.0
    targetcf = percent*len(inhist)
    total=sum(inhist)
    cumulsum=0.0
    for i in range(len(inhist)):
        cumulsum+=inhist[i]
        if cumulsum/total >= percent:break
    score = lowerlimit+binsize*i-binsize
    return score

def RATtoLUT(rat):
    ''' Create a LUT from an attribute table with RGB columns

        @type rat:   C{GDALRasterAttributeTable}
        @param rat:  A GDALRasterAttributeTable
        @rtype:      C{list}
        @return:     List of cell values and R,G,B,A values e.g ((12,0,0,0,255), (25,255,255,255,0))
    '''
    rgbcols={}
    for iCol in range(0,rat.GetColumnCount()):#+1):
        sCol=rat.GetNameOfCol(iCol)
        if sCol.upper() == 'VALUE':
            rgbcols['VALUE']=iCol
        if sCol.upper() in ['R','RED']:
            rgbcols['R']=iCol
        if sCol.upper() in ['G','GREEN']:
            rgbcols['G']=iCol
        if sCol.upper() in ['B','BLUE']:
            rgbcols['B']=iCol
    if sorted(rgbcols.keys()) == ['B', 'G', 'R','VALUE']:
        clr,vals=[],[]
        for iRow in range(0,rat.GetRowCount()):#+1):
            val=rat.GetValueAsInt(iRow,rgbcols['VALUE'])
            if not val in vals: #Have been getting VALUE=0,COUNT=0 as the last row
                                #in the ESRI grids I've tested on, even if 0 is already in the VAT
                r=rat.GetValueAsDouble(iRow,rgbcols['R'])
                if r > 0 and r < 1:r=int(r*255)
                g=rat.GetValueAsDouble(iRow,rgbcols['G'])
                if g > 0 and g < 1:g=int(g*255)
                b=rat.GetValueAsDouble(iRow,rgbcols['B'])
                if b > 0 and b < 1:b=int(b*255)
                vals.append(val)
                clr.append([val,r,g,b,255])
        return clr
    else:
        return None

def ParseColourLUT(filepath):
    ''' Open and parse a colour lookup table

        Values must be space separated. Comment characters are stripped out.
        Format is: C{pixel red green blue [optional alpha]}.
        Pixel value may be a range (eg 15-20).
        The following comment characters may be used: C{'#' '//' ';' '/*'}.

        Example::

                #value   R   G   B   A
                 11-15   255 0   0   255 #(red)
                 16      255 165 0   255 #(orange)
                 18      255 255 0   255 #(yellow)
                 19      0   255 0   255 /*(green)
                 21      0   0   255 255 /*(blue)
                 98      0   255 255 255 ;(cyan)
                 99-255  160 32  240 255 ;(purple)

        @type filepath:   C{str}
        @param filepath:  Path to colour lookup file
        @rtype:           C{list}
        @return:          List of cell values and R,G,B,A values e.g ((12,0,0,0,255), (25,255,255,255,0))
    '''
    commentchars=['#','//',';','/*']
    lut=open(filepath,'r')
    clr=[]
    for line in lut:
        line=line.strip()

        #strip out comment characters
        for char in commentchars:
            if line.find(char) >= 0:
                line=line.split(char)[0].strip()

        #Split into pixel, red, green, blue, alpha values
        #if optional alpha value was not included, add it in (255 = non-transparent)
        line=line.split()
        if len(line) > 0: #If it's not a comment line
            if len(line) < 4 or len(line) > 5: raise Exception, 'Unable to process %s' % (f)
            elif len(line) == 4: line.append('255') #Is it just pixel, r, g, b?

            #Check for range of pixel values
            sep=line[0].find('-',1)
            if sep != -1:
                r,g,b,a=line[1:]
                i,j=int(line[0][:sep]),int(line[0][sep+1:])
                for val in range(i,j+1):
                    line=[str(val),r,g,b,a]
                    clr.append(line)
            else:
                clr.append(line)
    #close and exit
    lut.close()
    return clr
ParseColorLUT=ParseColourLUT #Synonym for the norteamericanos
def ColourLUT(lut,rb):
    ''' Populate a colour lookup table, making sure all values get included

        @type lut:  C{list}
        @param lut: A list of one or more [values,r,g,b,a] lists.
        @type rb:   C{gdal.RasterBand}
        @param rb:  A gdal RasterBand object.
        @rtype:     C{list}
        @return:    A list of one or more [values,r,g,b,a] lists.
    '''
    clr=dict((key,val) for key,val in [[v[0],v[1:]] for v in lut])
    nodata=rb.GetNoDataValue()
    min,max=rb.ComputeRasterMinMax()
    rat=rb.GetHistogram(min-0.5,max+0.5,int(max-min+1),0,1)
    vals=[]
    keys=clr.keys()
    for val,count in zip(range(int(min),int(max)+1),rat):
        if count > 0:
            val=str(val)
            if val in keys:
                vals.append([val])
                vals[-1].extend(clr[val])
            else:vals.append([val,'255','255','255','0'])
    return vals
    #Not all entries in colourtable occur in the dataset
    #return [map(str, col) for col in lut]
ColorLUT=ColourLUT #Synonym for the norteamericanos
def ExpandedColourLUT(lut,rb):
    ''' Populate a colour lookup table, expanding missing values as required.
        Workaround for http://trac.osgeo.org/gdal/ticket/3253

        @type lut:  C{list}
        @param lut: A list of one or more [values,r,g,b,a] lists.
        @type rb:   C{gdal.RasterBand}
        @param rb:  A gdal RasterBand object.
        @rtype:     C{list}
        @return:    A list of one or more [values,r,g,b,a] lists.
    '''
    lut=iter(lut)
    tbl=[]
    dfScaleSrcMin,dfScaleSrcMax=GetDataTypeRange(rb.DataType)
    rng=range(dfScaleSrcMin,dfScaleSrcMax)
    val,red,green,blue,alpha=[str(v) for v in lut.next()]
    for r in rng:
        if int(val) == r:
            clr = (str(r),red,green,blue,alpha)
            try:val,red,green,blue,alpha=[str(v) for v in lut.next()]
            except:pass #No more color table entries
        else:clr = (str(r),'255','255','255','0') #default - white/transparent
        tbl.append(clr)
    return tbl
ExpandedColorLUT=ExpandedColourLUT #Synonym for the norteamericanos
#Workaround for missing values http://trac.osgeo.org/gdal/ticket/3253
if int(gdal.VersionInfo()[0:2]) < 17: #Missing values fixed in 1.7+
    ColourLUT = ExpandedColourLUT
    ColorLUT  = ExpandedColorLUT

def resize(infile,outfile,width):
    ''' Resize an image

        @type infile:   C{str}
        @param infile:  Path to image to resize
        @type outfile:   C{str}
        @param outfile:  Path to output image that will be created
        @type width:    C{int}
        @param width:   Width in pixels of output image
        @rtype:         C{str}
        @return:        Path to output image that was created
    '''
    ds=gdal.Open(infile)
    bands=range(1,ds.RasterCount+1)
    outfile =  getoverview(ds,outfile,width,None,bands,'NONE')
    del ds
    return outfile


