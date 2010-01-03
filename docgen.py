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

'''Generate documentation for crawler modules'''

import os,utilities,sys
from epydoc.cli import cli
from epydoc import docparser
docparser.IMPORT_STAR_HANDLING='ignore'

args=[]
args.append('--debug')
args.append('--name=Extract and Transform Metadata (ETM)')
#args.append('--css=white')     # Black on white, with blue highlights (similar to javadoc).
args.append('--css=blue')      # Black on steel blue.
#args.append('--css=green')     # Black on green.
#args.append('--css=black')     # White on black, with blue highlights.
#args.append('--css=grayscale') # Grayscale black on white.
args.append('--output=%s\\doc\\files'%os.environ['CURDIR'])
args.append('--html')
args.append('--show-private')
args.append('--inheritance=grouped')
args.append('--exclude=.*builtin.*')
args.append('--exclude=.*Tkinter.*')
#args.append('--no-imports')

if '--debug' in args:args.extend(['--verbose']*3)
else:args.extend(['--quiet']*3)
args.append('%s\\runcrawler.py'%os.environ['CURDIR'])
args.append('%s\\runtransform.py'%os.environ['CURDIR'])

for py in utilities.rglob('%s\\lib'%os.environ['CURDIR'],'*.py'):
    args.append(py)
sys.argv.extend(args)
cli()

#Copy the index.html frameset file one level up
html=open('%s\\doc\\files\\index.html'%os.environ['CURDIR']).read()
index=open('%s\\doc\\index.html'%os.environ['CURDIR'],'w')
index.write(html.replace('src="','src="files/'))
index.close()

#Get rid of the "int" and float classes cos I can't figure out how to exclude them from epydoc
toc='%s\\doc\\files\\toc-everything.html'%os.environ['CURDIR']
int='%s\\doc\\files\\int-class.html'%os.environ['CURDIR']
flt='%s\\doc\\files\\float-class.html'%os.environ['CURDIR']
html=open(toc).read()
html=html.replace('    <a target="mainFrame" href="int-class.html"\n     >int</a><br />','')
html=html.replace('    <a target="mainFrame" href="float-class.html"\n     >float</a><br />','')
toc=open(toc,'w')
toc.write(html)
toc.close()
os.unlink(int)
os.unlink(flt)
