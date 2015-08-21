# Installing required software #
  * Install an SVN command line client (e.g. http://www.sliksvn.com) or ensure that it is on your PATH
  * Install the Nullsoft Scriptable Install System (NSIS - http://nsis.sourceforge.net) or ensure that it is on your PATH

# Building the NSIS installer #
Run [buildmetageta.py](http://code.google.com/p/metageta/source/browse/build/installer/buildmetageta.py).

Note: This script relies on the following svn properties being set (and kept up to date) on the svn directories - tags/N.N, trunk, branches/`*`.
  * version (N.N.N.N format)
  * displayversion (free text, e.g 1.4 RC1)

The keyword "$Revision$" is used by [buildmetageta.py](http://code.google.com/p/metageta/source/browse/build/installer/buildmetageta.py) to substitute the current revision number. eg 1.3.1.$Revision$ will be replaced by 1.3.1.1234