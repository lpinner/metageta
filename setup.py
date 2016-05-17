# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from codecs import open
from os import path
import sys

here = path.abspath(path.dirname(__file__))

# Get the version from the VERSION file
with open(path.join(here, 'VERSION'), encoding='utf-8') as f:
    version = f.read()

setupargs = {
    'name':'MetaGETA',
    'version':version,
    'description':'Metadata Gathering, Extraction and Transformation Application',
    'long_description':'MetaGETA is a python application for discovering and extracting metadata from spatial raster datasets (metadata crawler) and transforming it into xml (metadata transformation). A number of generic and specialised imagery formats are supported. The format support has a plugin architecture and more formats can easily be added.',
    'platforms':['linux','windows','darwin'],
    'author':'Luke Pinner and Simon Oliver',
    'url':'https://github.com/lpinner/metageta',
    'license':'MIT',
    'keywords':'metadata raster',
    'classifiers':['Development Status :: 4 - Beta',
                   'Environment :: Win32 (MS Windows)',
                   'Environment :: X11 Applications',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: POSIX :: Linux',
                   'Operating System :: Microsoft :: Windows',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Scientific/Engineering :: GIS'],
    'packages':find_packages(),
    'install_requires':['GDAL >= 1.7, < 2.0',
                        'lxml >= 3.3',
                        'openpyxl >= 2.0'],
    'extras_require':{':sys_platform == "win32"': ['pypiwin32']},
    'package_data':{'metageta': ['config/config.xml'],
                   'metageta.transforms': ['*.xml','*.xsl'],
                   'metageta.config': ['*.xml'],
                    },
    'entry_points':{
        'console_scripts': [
            'metagetacrawler=metageta.__runcrawler__:main',
            'metagetatransform=metageta.__runtransform__:main',
            'metagetaconfig=metageta.config.__main__:main',
        ],
    }
}

if 'bdist_wininst' in sys.argv:

    args = [a for a in sys.argv[1:] if not a=='bdist_wininst']
    del sys.argv[1:]
    sys.argv.append('bdist_wininst')

    directory = path.join(path.dirname(__file__), 'build')
    if path.exists(path.join(directory, 'wininst-9.0.exe')):

        from distutils.command.bdist_wininst import bdist_wininst as _bdist_wininst
        from sysconfig import get_python_version

        class bdist_wininst(_bdist_wininst):
            """
                Monkey-patch bdist_wininst to allow building from non-standard wininst-9.0*.exes.

                Patched wininst*.exes from the spyderlib project that can run an uninstall script.
                Based on patch suggested in python distutils issue 13276.
            """
            def get_exe_bytes (self):
                cur_version = get_python_version()
                bv=9.0
                directory = path.join(path.dirname(__file__), 'build')
                if self.plat_name != 'win32' and self.plat_name[:3] == 'win':
                    sfix = self.plat_name[3:]
                else:
                    sfix = ''

                filename = path.join(directory, "wininst-%.1f%s.exe" % (bv, sfix))
                f = open(filename, "rb")
                try:
                    return f.read()
                finally:
                    f.close()
        setupargs['cmdclass']={'bdist_wininst':bdist_wininst}

    setupargs['options']={"bdist_wininst":
                               {"install_script": "register_metageta.py",
                                "title": "%s %s" % ('MetaGETA', version),
                                "bitmap": 'build/metageta.ico',
                                "user_access_control": "force"}
                          }
    setupargs['data_files'] = [('Scripts', ('build/metageta.ico',),)]
    setupargs['scripts'] = ['build/register_metageta.py']

    sys.argv += ['--plat-name', 'win32']
    setup(**setupargs)
    sys.argv += ['--plat-name', 'win-amd64']
    setup(**setupargs)

    if args:
        del sys.argv[1:]
        sys.argv+=args
    else:
        sys.exit(0)

setup(**setupargs)

