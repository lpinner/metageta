'''
Utility helper functions
========================
'''
from xlutils import xlrd
from xlutils import xlwt
import sys, os.path, os, re, struct, glob, shutil,traceback,time

dateformat='%Y-%m-%d'  #ISO 8601
timeformat='%H:%M:%S' #ISO 8601
datetimeformat='%sT%s' % (dateformat,timeformat)

def ExceptionInfo(maxTBlevel=0):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    if maxTBlevel > 0:
        excArgs=[]
        excTb = FormatTraceback(trbk, maxTBlevel)
        #return '%s: %s\nTraceback: %s' % (excName, str(exc), excTb)
        return '%s: %s\n%s' % (excName, str(exc), excTb)
    else:
        return '%s: %s' % (excName, str(exc))

def FormatTraceback(trbk, maxTBlevel):
    return 'Traceback (most recent call last): '+''.join(traceback.format_tb(trbk, maxTBlevel))

def readbinary(data,offset, start, stop):
    return ''.join(struct.unpack('s' * (stop-start+1), data[offset+start-1:offset+stop])).strip()

def ByteOrder():
    from struct import pack
    if pack('<h', 1) == pack('=h',1):
        return 'LSB'
    elif pack('>h', 1) == pack('=h',1):
        return 'MSB'
    else:
        raise Exception,'Unknown byte order'

def _WinFileOwner(filepath):
    import win32com.client
    import win32net
    import win32netcon

    OWNERID=8
    try:
        d=os.path.split(filepath)
        oShell = win32com.client.Dispatch("Shell.Application")
        oFolder = oShell.NameSpace(d[0])
        ownerid=oFolder.GetDetailsOf(oFolder.parsename(d[1]), OWNERID)
        ownerid=ownerid.split('\\')[-1]
    except: ownerid='0'
    #Too slow...
    ##oWMI = win32com.client.GetObject(r"winmgmts:\\.\root\cimv2")
    ##qry = "Select * from Win32_UserAccount where NAME = '%s'" % ownerid
    ##qry = oWMI.ExecQuery(qry)
    ##if qry.count > 0:
    ##for result in qry:
    ##    ownername=str(result.FullName)
    ##    break
    ##else: ownername='No user match'
    #Much quicker...
    try:
       dc=win32net.NetServerEnum(None,100,win32netcon.SV_TYPE_DOMAIN_CTRL)
       if dc[0]:
           dcname=dc[0][0]['name']
           ownername=win32net.NetUserGetInfo(r"\\"+dcname,ownerid,2)['full_name']
       else:
           ownername=win32net.NetUserGetInfo(None,ownerid,2)['full_name']
    except: ownername='No user match'

    return ownerid,ownername

def _NixFileOwner(uid):
    import pwd
    pwuid=pwd.getpwuid(uid)
    ownerid = pwuid[0]
    ownername = pwuid[4]
    return ownerid,ownername

def FileInfo(filepath):
    filestat = os.stat(filepath)
    fileinfo = {
        'size':filestat.st_size,
        'datemodified':time.strftime(datetimeformat, time.localtime(filestat.st_mtime)),
        'datecreated': time.strftime(datetimeformat, time.localtime(filestat.st_ctime)),
        'dateaccessed':time.strftime(datetimeformat, time.localtime(filestat.st_atime))
    }
    if sys.platform[0:3] =='win':
        ownerid,ownername=_WinFileOwner(filepath)
    else:
        ownerid,ownername=_NixFileOwner(filestat.st_uid)

    fileinfo['ownerid']=ownerid
    fileinfo['ownername']=ownername

    return fileinfo


def convertUNC(filepath):
    if sys.platform[0:3] =='win':
        import win32wnet
        if type(filepath) is list or type(filepath) is tuple: #is it a list of filepaths
            uncpath=[]
            for path in filepath:
                try:    uncpath.append(win32wnet.WNetGetUniversalName(path))
                except: uncpath.append(path) #Local path
        else:
            try:    uncpath=win32wnet.WNetGetUniversalName(filepath)
            except: uncpath=filepath #Local path
    else:uncpath=filepath
    return uncpath

def fixSeparators(f):
    if type(f) in [list,tuple]:
        return [os.path.normpath(i) for i in f]
    else:
        return os.path.normpath(f)

def checkExt(var,vals):
    vars=os.path.splitext(var)
    if vars[1] not in (vals):
        return vars[0]+vals[0]
    else:
        return var

# def GetFileList(f):
    # '''Get all files that have the same name, or are related according to gdalinfo
        # special cases (eg hdf, ccrs, etc) are handled separately in their respective
        # metadata functions'''
    # files=[]
    # files=glob.glob(os.path.splitext(f)[0]+'.*')
    # if os.path.exists(os.path.splitext(f)[0]):files.append(os.path.splitext(f)[0])
    # hdr_dir=os.path.join(os.path.split(f)[0], 'headers') #Cause ACRES creates a 'headers' directory
    # if os.path.exists(hdr_dir):
        # files.extend(glob.glob(os.path.join(hdr_dir,'*')))

    # try:
        ##the GDALDataset object has a GetFileList method, but it is not exposed to the python API
        ##So use the commandline utility instead and parse the output
        # exit_code, stdout, stderr=runcmd('gdalinfo  -nogcp -nomd -noct '+f, 'l')
        # lines=stdout.readlines()
        # i=0
        # while i < len(lines):
            # line=lines[i].strip()
            # if line[0:5]  == 'Files':
                # file=os.path.realpath(line.replace('Files:','').strip())
                # if not file in files:files.append(file)
                # i+=1
                # while i < len(lines):
                    # line=lines[i]
                    # if line[0:4] == 'Size':
                        # break
                    # else:
                        # file=os.path.realpath(line.strip())
                        # if not file in files:files.append(file)
                    # i+=1
                # break
            # i+=1
        # i=0
    # except:pass
    # return fixSeparators(files)

class ExcelWriter:
    _files=0
    def __init__(self,xls,fields):
        fields.sort()
        self._file=xls
        self._fields=fields
        self._sheets=0 #sheet index
        self._rows=0   #row index
        self._cols={}  #col dictionary

        font = xlwt.Font()
        font.bold = True
        self._heading = xlwt.XFStyle()
        self._heading.font = font        

        if os.path.exists(xls):os.remove(xls)
        self._wb = xlwt.Workbook()
        self.AddSheet()

    def AddSheet(self):
        self._sheets+=1
        self._ws = self._wb.add_sheet('Sheet %s'%self._sheets)
        #self._ws.keep_leading_zeros()

        for i,field in enumerate(self._fields):
            self._cols[field]=i
            self._ws.write(0, i, field, self._heading) #[row,col] = 0 based row, col ref
        self._rows = 0
        
    def WriteRecord(self,data):
        dirty=False
        if self._rows > 65535:
            self.AddSheet()
        for field in data:
            if self._cols.has_key(field):
                if type(data[field]) is unicode:data[field]=str(data[field])
                self._ws.write(self._rows+1, self._cols[field], data[field])
                dirty=True
        if dirty:self._rows+=1

    def __del__(self):
        self._wb.save(self._file)
        #del self._ws
        #del self._wb
    

def ExcelReader(xls,returntype=dict):
    wb=xlrd.open_workbook(xls)
    for ws in wb.sheets():
        headers=[c.value for c in ws.row(0)]
        for i in range(1,ws.nrows):
            cells=[c.value for c in ws.row(i)]
            if returntype is dict:
                yield dict(zip(headers,cells))
            else:
                yield zip(headers,cells)

def runcmd(cmd, format='s'):
    import subprocess
    proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if format.lower() == 's': #string output
        stdout,stderr=proc.communicate()
    #elif format.lower() == 'f': #file object output #doesn't flush IO buffer, causes python to hang
    #    stdout,stderr=proc.stdout,proc.stderr
    elif format.lower() == 'l': #list output
        stdout,stderr=proc.stdout.readlines(),proc.stderr.readlines()
    #else:raise TypeError, "fomat argument must be in ['s','f','l'] (string, file, list)"
    else:raise TypeError, "fomat argument must be in ['s','l'] (string or list format)"
    exit_code=proc.wait()
    return exit_code,stdout,stderr
class rglob:
    '''a forward iterator that traverses a directory tree'''
    def __init__(self, directory, pattern="*", regex=False, regex_flags=0, recurse=True):
        self.stack = [directory]
        self.pattern = pattern
        self.regex = regex
        self.recurse = recurse
        self.regex_flags = regex_flags
        self.files = []
        self.index = 0

    def __getitem__(self, index):
        while 1:
            try:
                file = self.files[self.index]
                self.index = self.index + 1
            except IndexError:
                # pop next directory from stack
                
                self.directory = self.stack.pop()
                try:
                    self.files = os.listdir(self.directory)
                    self.index = 0
                except:pass
            else:
                # got a filename
                fullname = os.path.join(self.directory, file)
                if os.path.isdir(fullname) and not os.path.islink(fullname) and self.recurse:
                    self.stack.append(fullname)
                if self.regex:
                    import re
                    if re.search(self.pattern,file,self.regex_flags):
                        return fullname
                else:
                    import fnmatch
                    if fnmatch.fnmatch(file, self.pattern):
                        return fullname

