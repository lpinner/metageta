# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from codecs import open
from os import path

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
                        'lxml >= 3.3.1',
                        'openpyxl >= 2.0.5'],
    'extras_require':{':sys_platform == "win32"': ['pypiwin32']},
    'package_data':{'metageta': ['config/config.xml'],
                   'metageta.transforms': ['*.xml','*.xsl'],
                   'metageta.config': ['*.xml'],
                    },
    'entry_points':{
        'console_scripts': [
            'runcrawler=metageta.__runcrawler__:main',
            'runtransform=metageta.__runtransform__:main',
            'metagetaconfig=metageta.config.__main__:main',
        ],
    }
}

setup(**setupargs)

