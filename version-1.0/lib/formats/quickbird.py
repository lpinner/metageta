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
        '''Read Metadata for an Digital Globe Quickbird format image as GDAL doesn't quite get it all...

        @todo: does not handle QB tile files (*til). Must check if GDAL can read them...?
        '''
        
        tif = os.path.splitext(f)[0]+'.tif'
        img = os.path.splitext(f)[0]+'.img'
        til = os.path.splitext(f)[0]+'.til'
        if   os.path.exists(tif):__default__.Dataset.__init__(self, tif)
        elif os.path.exists(img):__default__.Dataset.__init__(self, img)
        #elif os.path.exists(til):__default__.Dataset.__init__(self, til) #NEED TO DO SOMETHING WITH THE TILE FILE!!!
        else:raise IOError, 'Matching Quickbird imagery TIFF/IMG not found:\n'
        #Loop thru and parse the IMD file.
        #would be easier to walk the nodes in the XML files, but not all of our QB imagery has this
        #perhaps someone deleted them...?
        lines=open(f).readlines()
        i=0
        data={}
        while i < len(lines):
            line=[item.strip() for item in lines[i].replace('"','').split('=')]
            #line = map(string.strip, lines[i].split('='))
            group=line[0]
            if group == 'END;':break
            value=line[1]
            if group == 'BEGIN_GROUP':
                group=value
                subdata={}
                while True:
                    i+=1
                    line = map(string.strip, lines[i].replace('"','').split('='))
                    subgroup=line[0]
                    subvalue=line[1]
                    if subgroup == 'END_GROUP':break
                    elif line[1] == '(':
                        while True:
                            i+=1
                            line = lines[i].replace('"','').strip()
                            subvalue+=line
                            if line[-1:]==';':
                                subvalue=eval(subvalue.strip(';'))
                                break
                    else:subvalue=subvalue.strip(';')
                    subdata[subgroup]=subvalue
                data[group]=subdata
            else: data[group]=value.strip(');')
            i+=1
        if data.has_key('IMAGE_1'):imgkey='IMAGE_1'
        else:imgkey='SINGLE_IMAGE_PRODUCT'
        if data.has_key('MAP_PROJECTED_PRODUCT'):self.metadata['imgdate']=data['MAP_PROJECTED_PRODUCT']['earliestAcqTime'][0:10]#.replace('-','') #ISO 8601 format
        elif data[imgkey].has_key('firstLineTime'):self.metadata['imgdate']=data[imgkey]['firstLineTime'][0:10]#.replace('-','') #ISO 8601 format
        self.metadata['satellite']='Quickbird (%s)' % data[imgkey]['satId']
        if data['bandId'] == 'BGRN':self.metadata['sensor']='MULTI/PAN'
        elif data['bandId'] == 'P':self.metadata['sensor']='PANCHROMATIC'
        elif data['bandId'] == 'Multi':self.metadata['sensor']='MULTISPECTRAL'
        if data[imgkey].has_key('meanSunEl'):
            self.metadata['sunelevation'] = data[imgkey]['meanSunEl']
            self.metadata['sunazimuth'] = data[imgkey]['meanSunAz']
        elif data[imgkey].has_key('sunEl'):
            self.metadata['sunelevation'] = data[imgkey]['sunEl']
            self.metadata['sunazimuth'] = data[imgkey]['sunAz']
        self.metadata['level'] = data['productLevel']
        if self.metadata['nbands'] == 4:self.metadata['bands'] = 'B,G,R,N'
        else:self.metadata['bands'] = 'P'
        if data[imgkey].has_key('cloudCover'):
            self.metadata['cloudcover'] = data[imgkey]['cloudCover']
        elif data[imgkey].has_key('manualCloudCover'):
            self.metadata['cloudcover'] = max([0, data[imgkey]['manualCloudCover']]) #hack for -999 cloud cover
        elif data[imgkey].has_key('autoCloudCover'):
            self.metadata['cloudcover'] = max([0, data[imgkey]['autoCloudCover']])
        if data[imgkey].has_key('offNadirViewAngle'):
            self.metadata['viewangle'] = data[imgkey]['offNadirViewAngle']
        elif data[imgkey].has_key('meanOffNadirViewAngle'):
            self.metadata['viewangle'] = data[imgkey]['meanOffNadirViewAngle']
        if data[imgkey].has_key('CatId'):
            self.metadata['sceneid'] = data[imgkey]['CatId']
        if data[imgkey].has_key('resamplingKernel'):
            self.metadata['resampling'] = data[imgkey]['resamplingKernel']
        elif data.has_key('MAP_PROJECTED_PRODUCT') and data['MAP_PROJECTED_PRODUCT'].has_key('resamplingKernel'):
            self.metadata['resampling'] = data['MAP_PROJECTED_PRODUCT']['resamplingKernel']
        if data.has_key('MAP_PROJECTED_PRODUCT') and data['MAP_PROJECTED_PRODUCT'].has_key('DEMCorrection'):
            self.metadata['demcorrection'] = data['MAP_PROJECTED_PRODUCT']['DEMCorrection']
        #self.extent is set in __default__.Dataset.__init__()

