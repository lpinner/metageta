# Introduction #
The standard python and pywin32 install is fairly large.  The MetaGETA package provides a slimmed down and slightly modified Python version.  The modifications are required to reduce the risk of conflicts with existing pywin32 installs (see http://code.google.com/p/metageta/issues/detail?id=9) and to update the 4Suite xml library to point to %PYTHONHOME% install of the original install location.

# Installing Python and required packages #
Note: all references are to Python 2.6, this is the version required by the GDAL library we provide (see BuildingGDAL).

Firstly, download and install the following:
  * Python  - http://www.python.org/ftp/python/2.6.4/python-2.6.4.msi
  * Pywin32 - http://sourceforge.net/projects/pywin32/files/pywin32/Build%20214/pywin32-214.win32-py2.6.exe/download
  * 4Suite  - http://www.xml3k.org/Amara/Install?action=AttachFile&do=view&target=4Suite-XML-1.0.2.win32-py2.6.exe
  * Epydoc  - http://sourceforge.net/projects/epydoc/files/epydoc/3.0.1/epydoc-3.0.1.win32.exe/download
  * xlutils - http://www.python.org/ftp/python/2.6.4/python-2.6.4.msi
  * xlrd    - http://pypi.python.org/packages/any/x/xlrd/xlrd-0.7.1.win32.exe
  * xlwt    - http://pypi.python.org/packages/any/x/xlwt/xlwt-0.7.2.win32.exe

Then copy the Python26 directory to <your metageta development dir>\bin.

Modify appropriate files either by:
  * using [modify\_python.py](http://code.google.com/p/metageta/source/browse/build/python/modify_python.py)
  * or
    * Locate python26.dll, pythoncom26.dll and pywintypes26.dll, usually in C:\Windows\System32, and copy them to the <metageta dir>\bin\Python26 directory (and copy pythoncom26.dll and pywintypes26.dll to <metageta dir>\bin\Python26\Lib\site-packages\pythonwin if you wish to use Pythonwin for developing, testing etc...).
    * Edit <metageta dir>\bin\Python26\Lib\site-packages\Ft\config.py and change:
```
        # standard distutils installation directories
        RESOURCEBUNDLE = False
        PYTHONLIBDIR   = 'C:\\Python26\\Lib\\site-packages\\'
        BINDIR         = 'C:\\Python26\\Scripts'
        DATADIR        = 'C:\\Python26\\Share\\4Suite'
        SYSCONFDIR     = 'C:\\Python26\\Share\\Settings\\4Suite'
        LOCALSTATEDIR  = 'C:\\Python26\\Share\\4Suite'
        LIBDIR         = 'C:\\Python26\\Share\\4Suite'
        LOCALEDIR      = 'C:\\Python26\\Share\\Locale'
```
> > to:
```
        # standard distutils installation directories
        import os
        PYTHONHOME=os.environ['PYTHONHOME']
        RESOURCEBUNDLE = False
        PYTHONLIBDIR   = '%s\\Lib\\site-packages\\'%PYTHONHOME
        BINDIR         = '%s\\Scripts'%PYTHONHOME
        DATADIR        = '%s\\Share\\4Suite'%PYTHONHOME
        SYSCONFDIR     = '%s\\Share\\Settings\\4Suite'%PYTHONHOME
        LOCALSTATEDIR  = '%s\\Share\\4Suite'%PYTHONHOME
        LIBDIR         = '%s\\Share\\4Suite'%PYTHONHOME
        LOCALEDIR      = '%s\\Share\\Locale'%PYTHONHOME
        del os
```

To slim it down, initially I just deleted all the doc/test/example/script type directories, removed any existing pyc/pyo compiled file ([cleanup\_compiled\_files.py](http://code.google.com/p/metageta/source/browse/build/python/cleanup_compiled_files.py)) then ran docgen, runcrawler, runtransform, pythonwin (inc. debug and tabnanny).  I then deleted any `*.py` files that didn't have a corresponding pyc/pyo compiled file ([slimdown\_python\_pyco.py](http://code.google.com/p/metageta/source/browse/build/python/slimdown_python_pyco.py)) and finally went around deleting non `*.py` files manually till something broke.

The final filelist is [python\_filelist.txt](http://code.google.com/p/metageta/source/browse/build/python/python_filelist.txt) which was created with [create\_python\_filelist.py](http://code.google.com/p/metageta/source/browse/build/python/create_python_filelist.py).

To avoid the trial and error method I used, use the http://code.google.com/p/metageta/source/browse/build/python/slimdown_python_filelist.py script.

You can then uninstall the initial Python26 and associated packages if you wish.  Note: you may need to reinstall Python2X if ArcGIS breaks (where "X" is the ArcGIS python version).