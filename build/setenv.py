import os,sys

#General vars
CURDIR=os.path.dirname(os.path.abspath(__file__))
TOPDIR=os.path.dirname(os.path.dirname(CURDIR))
DOWNLOAD_DIR=os.path.join(TOPDIR,'downloads')

#Default vars
PY_VER='Python27'
BIN_DIR=os.path.join(TOPDIR,'bin')
PY_DIR=os.path.join(BIN_DIR,PY_VER) #Don't mess with PYTHONHOME

############################################################
#Check environment settings in case they'e been overridden
env=os.environ
CURDIR=env.get('CURDIR',CURDIR)
TOPDIR=env.get('TOPDIR',os.path.dirname(os.path.dirname(CURDIR)))
DOWNLOAD_DIR=env.get('DOWNLOAD_DIR',DOWNLOAD_DIR)
PY_VER=env.get('PY_VER',PY_VER)
BIN_DIR=env.get('BIN_DIR',BIN_DIR)
PY_DIR=env.get('PY_DIR',PY_DIR)

#Hide from autocomplete IDEs
del os  
del sys
del env
