'''
Metadata driver for ENVI imagery
================================
'''

#list of file name regular expressions
format_regex=[r'\.hdr$']

#import base dataset modules
#import __dataset__
import __default__

# import other modules
import sys, os

class Dataset(__default__.Dataset): 
    '''Subclass of __default__.Dataset class so we get a load of metadata populated automatically'''
    def __init__(self,f=None):
        if not f:f=self.fileinfo['filepath']
        lin=open(f).readline().strip() #read first line
        hdr=os.path.splitext(f)[0]
        if os.path.exists(hdr):self._datafile=hdr
        else:  #Handle the odd ENVI files held by SSD (.bil/etc. files with ENVI style headers)
            data_formats=['bil','bip','bsq'] 
            for fmt in data_formats:
                dat='%s.%s' % (hdr,fmt)
                if os.path.exists(dat):break
                else: dat=False
            if dat:self._datafile=dat

        if not lin == 'ENVI' or not os.path.exists(self._datafile): #is it an ENVI format hdr...?
            raise NotImplementedError #This error gets ignored in __init__.Open()

            
    def __getmetadata__(self):
        '''Read Metadata for a ENVI image as GDAL doesn't work if you pass the header file...'''
        try:__default__.Dataset.__getmetadata__(self, self._datafile) #autopopulate basic metadata
        except IOError,err:             #Handle the odd ENVI files held by SSD (file type = ENVI instead of file type = ENVI standard)
            hdr=self.__parseheader__()
            if hdr['file type']=='ENVI':
                #make a dummy hdr with a dummy 1 byte image file
                import tempfile,geometry,shutil

                tmpd=tempfile.mkdtemp(prefix='gdal')
                tmph=open(tmpd+'/dummy.hdr','w')
                tmpf=open(tmpd+'/dummy','wb')
                hdr['file type']+=' Standard'
                tmph.write('ENVI\n')
                for key in hdr:
                    if '\n' in hdr[key]:tmph.write(key+' = {'+hdr[key]+'}\n')
                    else: tmph.write(key+' = '+hdr[key]+'\n')
                tmph.close()
                tmpf.write('\x00\x00')
                tmpf.close()
                __default__.Dataset.__getmetadata__(self, tmpd+'/dummy')
                del self._gdaldataset
                shutil.rmtree(tmpd, ignore_errors=True)
                md=self.metadata
                byteorder={'':None,'0':'LSB','1':'MSB'}
                byteorder=byteorder[hdr.get('byte order','')]
                nodata=hdr.get('data ignore value','0')
                if hdr.get('interleave','').upper()=='BSQ':
                    vrt=geometry.CreateBSQRawRasterVRT(self._datafile,md['nbands'],md['cols'],md['rows'],md['datatype'],md['nbits'],nodata,headeroffset=0,byteorder=byteorder,relativeToVRT=0)
                elif hdr.get('interleave','').upper()=='BIP':
                    vrt=geometry.CreateBIRawRasterVRT(self._datafile,md['nbands'],md['cols'],md['rows'],md['datatype'],md['nbits'],nodata,headeroffset=0,byteorder=byteorder,relativeToVRT=0)
                else:#Assume bil
                    vrt=geometry.CreateBILRawRasterVRT(self._datafile,md['nbands'],md['cols'],md['rows'],md['datatype'],md['nbits'],nodata,headeroffset=0,byteorder=byteorder,relativeToVRT=0)
                self._gdaldataset=geometry.OpenDataset(vrt)
                pass
                
            else:raise #not the dodgy SSD files, re-raise the orig. error
    def __parseheader__(self):
        hdr=open(self.fileinfo['filepath']).readlines()
        md={}
        i=1 #Skip the ENVI line
        while True: #Extract all keys and values from the header file into a dictionary
            line=hdr[i].strip()
            if line.find('{') > -1:
                var=[s.strip() for s in line.replace('{','').split('=',1)]
                if line.find('}') == -1:
                    i+=1
                    while True:
                        line=hdr[i].strip()
                        var[1] += '\n'+line
                        if line.find('}') > -1:break
                        i+=1
                var[1]=var[1].replace('}','')
            else:var=[s.strip() for s in line.split('=',1)]
            md[var[0]]=var[1]
            i+=1
            if i >=len(hdr):break
        return md