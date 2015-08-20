#!/usr/bin/python
from distutils.core import setup
import os,sys,warnings,shutil

def getpaths():
    #fake a setup to get the paths
    lib,scripts,data,prefix=('','','','')
    args=sys.argv[:]
    idx=sys.argv.index('install')
    sys.argv.insert(idx,'-q')
    sys.argv.insert(idx,'--dry-run')
    s=setup()
    lib=s.command_obj['install'].install_lib
    scripts=s.command_obj['install'].install_scripts
    data=s.command_obj['install'].install_data
    prefix=s.command_obj['install'].prefix
    sys.argv=args[:]
    return lib,scripts,data,prefix

if __name__=='__main__':
    version=open('version.txt').read().split()[1]
    os.chdir('metageta')

    setupargs={'name':'MetaGETA',
          'version':version,
          'description':'Metadata Gathering, Extraction and Transformation Application',
          'long_description':'MetaGETA is a python application for discovering and extracting metadata from spatial raster datasets (metadata crawler) and transforming it into xml (metadata transformation). A number of generic and specialised imagery formats are supported. The format support has a plugin architecture and more formats can easily be added.',
          'platforms':['linux','windows','darwin'],
          'author':'Luke Pinner and Simon Oliver',
          'url':'http://code.google.com/p/metageta',
          'license':'MIT License',
          'classifiers':['Development Status :: 4 - Beta',
                       'Environment :: Win32 (MS Windows)',
                       'Environment :: X11 Applications',
                       'Intended Audience :: End Users/Desktop',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: MIT License',
                       'Operating System :: POSIX :: Linux',
                       'Operating System :: Microsoft :: Windows',
                       'Programming Language :: Python',
                       'Topic :: Scientific/Engineering :: GIS'],
          'packages':['metageta','metageta.formats','metageta.transforms'],
          'requires':['osgeo.gdal','lxml','openpyxl'],
          'scripts':['runcrawler.py','runtransform.py'],
          'package_data':{'metageta': ['config/config.xml'],'metageta.transforms': ['*.xml','*.xsl']}
        }

    if 'install' in sys.argv:
        lib,scripts,data,prefix=getpaths()
        errors=[]
	warns=[]
        try:
            from osgeo import gdal
            v=gdal.VersionInfo("RELEASE_NAME")
            assert [int(i) for i in gdal.VersionInfo("RELEASE_NAME").split('.')] >= [1,6,0]
            print 'Found GDAL %s Ok.'%v
        except ImportError:
            error='The GDAL (www.gdal.org) python bindings are not installed or not configured correctly.'
            errors.append(error)
        except AssertionError:
            error='GDAL (www.gdal.org) version %s is not supported, try upgrading.'%v
            errors.append(error)
        try:
            import openpyxl
            assert [int(i) for i in openpyxl.__version__.split('.')] >= [2,0,5]
            print 'Found openpyxl Ok.'
        except AssertionError:
            msg='openpyxl version %s has not been tested, you may wish to upgrade.'%openpyxl.__version__
            warns.append(msg)
        except ImportError:
            error='openpyxl is not installed.'
            errors.append(error)
        except Exception as err:
            error='openpyxl is not configured correctly, error message:\n'+repr(err)
            errors.append(error)
        try:
            import lxml
            from lxml.etree import LXML_VERSION
            assert LXML_VERSION >= (3, 3, 1, 0)
            print 'Found lxml Ok.'
        except AssertionError:
            msg='lxml version %s is too old to be used with openpyxl, you may wish to upgrade.'%'.'.join(map(str,LXML_VERSION))
            warns.append(msg)
        except ImportError:
            error='lxml is not installed.'
            errors.append(error)
        except Exception as err:
            error='lxml is not configured correctly, error message:\n'+repr(err)
            errors.append(error)
        try:
            import Tix,tkFileDialog,tkMessageBox
        except ImportError:
            msg='Tix, tkFileDialog and/or tkMessageBox are not installed or not configured correctly, you will not be able to use the MetaGETA GUI.'
            warns.append(msg)

        if errors:
            print 'MetaGETA setup can not continue. Correct the following errors and then try again:'
            print '\t'+'\n\t'.join(errors)
            sys.exit(1)

        if 'linux' in sys.platform or 'darwin' in sys.platform:
            setupargs['data_files']=[('bin',['runcrawler.py','runtransform.py'])]
            try:
                shutil.rmtree(os.path.join(lib,'metageta'))
                os.unlink(os.path.join(data,'bin/runcrawler.py'))
                os.unlink(os.path.join(data,'bin/runtransform.py'))
                os.unlink(os.path.join(data,'bin/runcrawler'))
                os.unlink(os.path.join(data,'bin/runtransform'))
            except:pass

    s=setup(**setupargs)

    if 'install' in sys.argv and ('linux' in sys.platform or 'darwin' in sys.platform):
        import stat
        print 'Changing mode of %s/bin/runcrawler|runtransform to 755'%data
        os.chmod(os.path.join(data,'bin/runcrawler.py'),stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
        os.chmod(os.path.join(data,'bin/runtransform.py'),stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
        try:
            os.link(os.path.join(data,'bin/runcrawler.py'),os.path.join(data,'bin/runcrawler'))
            os.link(os.path.join(data,'bin/runtransform.py'),os.path.join(data,'bin/runtransform'))
        except:pass
	
    if 'install' in sys.argv and warns:
        for msg in warns:
            warnings.warn(msg)

