
# Copyright (c) 2009 Australian Government, Department of Environment, Heritage, Water and the Arts
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
Utility helper functions
'''

try:
    from xlutils import xlrd
    from xlutils import xlwt
except:
  import xlrd, xlwt
import sys, os.path, os, re, struct, glob, shutil,traceback,time

dateformat='%Y-%m-%d'  #ISO 8601
timeformat='%H:%M:%S' #ISO 8601
datetimeformat='%sT%s' % (dateformat,timeformat)

def runcmd(cmd, format='s'):
    ''' Run a command
        @type     cmd:  C{str}
        @param    cmd:  Command (inc arguments) to run
        @rtype:   C{tuple}
        @return:  Returns (exit_code,stdout,stderr)
    '''
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

def which(name, returnfirst=True, flags=os.F_OK | os.X_OK, path=None):
    ''' Search PATH for executable files with the given name.
    
        On newer versions of MS-Windows, the PATHEXT environment variable will be
        set to the list of file extensions for files considered executable. This
        will normally include things like ".EXE". This fuction will also find files
        with the given name ending with any of these extensions.

        On MS-Windows the only flag that has any meaning is os.F_OK. Any other
        flags will be ignored.
        
        Derived mostly from U{http://code.google.com/p/waf/issues/detail?id=531} with
        additions from Brian Curtins patch - U{http://bugs.python.org/issue444582}

        @type name: C{str}
        @param name: The name for which to search.
        @type returnfirst: C{boolean}
        @param returnfirst: Return the first executable found.
        @type flags: C{int}
        @param flags: Arguments to U{os.access<http://docs.python.org/library/os.html#os.access>}.

        @rtype: C{str}/C{list}
        @return: Full path to the first matching file found or a list of the full paths to all files found, 
                 in the order in which they were found.
    '''
    result = []
    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
    if not path:
        path = os.environ.get("PATH", os.defpath)
    for p in os.environ.get('PATH', '').split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            if returnfirst:return p
            else:result.append(p)
        for e in exts:
            pext = p + e
            if os.access(pext, flags):
                if returnfirst:return pext
                else:result.append(pext)
    return result

def ExceptionInfo(maxTBlevel=0):
    '''Get info about the last exception'''
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
    '''Format traceback'''
    return 'Traceback (most recent call last): '+''.join(traceback.format_tb(trbk, maxTBlevel))

def readbinary(data,offset, start, stop):
    ''' Read binary data
        @type    data:   C{str}
        @param   data:   data read from binary file
        @type    offset: C{int}
        @param   offset: Number of bytes to skip
        @type    start:  C{int}
        @param   start:  Byte to start reading from (from offset, not beginning of data)
        @type    stop:   C{int}
        @param   stop:   Byte to stop reading at (from offset, not beginning of data)
        @rtype:          C{str}
        @return:         String
    '''
    return ''.join(struct.unpack('s' * (stop-start+1), data[offset+start-1:offset+stop])).strip()

def readascii(data,offset,start,stop):
    ''' Read ASCII data
        @type    data:   C{str}
        @param   data:   data read from ASCII file
        @type    offset: C{int}
        @param   offset: Number of characters to skip
        @type    start:  C{int}
        @param   start:  Character to start reading from (from offset, not beginning of data)
        @type    stop:   C{int}
        @param   stop:   Character to stop reading at (from offset, not beginning of data)
        @rtype:          C{str}
        @return:         String
    '''
    return data[start+offset-1:stop+offset].strip()

def ByteOrder():
    ''' Determine byte order of host machine.

        @rtype:          C{str}
        @return:         String
    '''
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
        ownerid=str(oFolder.GetDetailsOf(oFolder.parsename(d[1]), OWNERID))
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
    ''' File information.

        @type    filepath: C{str}
        @param   filepath: Path to file
        @rtype:  C{dict}
        @return: Dictionary containing file: size, datemodified, datecreated, dateaccessed, ownerid & ownername
    '''
    fileinfo = {
        'size':0,
        'datemodified':'',
        'datecreated': '',
        'dateaccessed':''
    }
    try:
        filestat = os.stat(filepath)
        fileinfo['size']=filestat.st_size
        fileinfo['datemodified']=time.strftime(datetimeformat, time.localtime(filestat.st_mtime))
        fileinfo['datecreated']=time.strftime(datetimeformat, time.localtime(filestat.st_ctime))
        fileinfo['dateaccessed']=time.strftime(datetimeformat, time.localtime(filestat.st_atime))
        if sys.platform[0:3].lower()=='win':
            ownerid,ownername=_WinFileOwner(filepath)
        else:
            ownerid,ownername=_NixFileOwner(filestat.st_uid)
        fileinfo['ownerid']=ownerid
        fileinfo['ownername']=ownername

    finally:return fileinfo


def convertUNC(filepath):
    ''' Convert file path to UNC.

        @type    filepath: C{str}
        @param   filepath: Path to file
        @rtype:  C{str}
        @return: UNC filepath (if on Windows)
    '''
    if sys.platform[0:3].lower()=='win':
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

def fixSeparators(filepath):
    ''' Fix up any mixed forward/backward slahes in file path/s.

        @type    filepath: C{str/list}
        @param   filepath: Path to file/s
        @rtype:  C{str/list}
        @return: Path to file/s
    '''
    if type(filepath) in [list,tuple]:
        return [os.path.normpath(i) for i in filepath]
    else:
        return os.path.normpath(filepath)

def checkExt(filepath,ext):
    ''' Check a file has an allowed extension or apply a default extension if it has none.

        @type    filepath: C{str}
        @param   filepath: Path to file
        @type    ext: C{[str,...,str]}
        @param   ext: Allowed file extensions, ext[0] is the default
        @rtype:  C{str}
        @return: Path to file with updated extension
    '''
    vars=os.path.splitext(filepath)
    if vars[1] not in (ext):
        return vars[0]+ext[0]
    else:
        return filepath

class ExcelWriter:
    ''' A simple spreadsheet writer'''

    def __init__(self,xls,fields):
        ''' A simple spreadsheet writer.
        
            @type    xls: C{str}
            @param   xls: Path to xls file
            @type    fields: C{list}
            @param   fields: List of column/field headers
        '''
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
        self._wb = xlwt.Workbook(encoding='latin-1')
        #self._wb.encoding='latin-1'
        self.__addsheet__()

    def __addsheet__(self):
        self._sheets+=1
        self._ws = self._wb.add_sheet('Sheet %s'%self._sheets)
        #self._ws.keep_leading_zeros()

        for i,field in enumerate(self._fields):
            self._cols[field]=i
            self._ws.write(0, i, field, self._heading) #[row,col] = 0 based row, col ref
        self._rows = 0
        
    def WriteRecord(self,data):
        ''' Write a record
        
            @type    data: C{dict}
            @param   data: Dict containing column headers (dict.keys()) and values (dict.values())
        '''
        dirty=False
        if self._rows > 65535:
            self.__addsheet__()
        for field in data:
            if self._cols.has_key(field):
                self._ws.write(self._rows+1, self._cols[field], data[field])
                dirty=True
        if dirty:self._rows+=1
        self._wb.save(self._file)
        
    def __del__(self):
        self._wb.save(self._file)
        #del self._ws
        #del self._wb
    

class ExcelReader:
    '''A simple spreadsheet reader'''
    def __init__(self,xls,returntype=dict):
        ''' A simple spreadsheet reader.
        
            @type    xls: C{str}
            @param   xls: Path to xls file
            @type    returntype: C{type}
            @param   returntype: dict or list
        '''
        self.wb=xlrd.open_workbook(xls)
        self.returntype=returntype
    def __getitem__(self, index):
        i=index/65535
        j=index-i*65535
        ws=self.wb.sheets()[i]
        headers=[c.value for c in ws.row(0)]
        cells=[c.value for c in ws.row(j+1)]
        if self.returntype is dict:
            return dict(zip(headers,cells))
        else:
            return zip(headers,cells)

class rglob:
    '''A recursive/regex enhanced glob
       adapted from os-path-walk-example-3.py - http://effbot.org/librarybook/os-path.htm 
    '''
    def __init__(self, directory, pattern="*", regex=False, regex_flags=0, recurse=True):
        ''' @type    directory: C{str}
            @param   directory: Path to xls file
            @type    pattern: C{type}
            @param   pattern: Regular expression/wildcard pattern to match files against
            @type    regex: C{boolean}
            @param   regex: Use regular expression matching (if False, use fnmatch)
                            See U{http://docs.python.org/library/re.html}
            @type    regex_flags: C{int}
            @param   regex_flags: Flags to pass to the regular expression compiler.
                                  See U{http://docs.python.org/library/re.html}
            @type    recurse: C{boolean} 
            @param   recurse: Recurse into the directory?
        '''
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

