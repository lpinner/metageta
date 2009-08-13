'''Generate documentation for crawler modules'''

import os,utilities,sys
from epydoc.cli import cli
from epydoc import docparser
docparser.IMPORT_STAR_HANDLING='ignore'

args=[]
args.append('--debug')
args.append('--name=Metadata Crawler')
#args.append('--css=white')     # Black on white, with blue highlights (similar to javadoc).
args.append('--css=blue')      # Black on steel blue.
#args.append('--css=green')     # Black on green.
#args.append('--css=black')     # White on black, with blue highlights.
#args.append('--css=grayscale') # Grayscale black on white.
args.append('--output=%s\\doc\\files'%os.environ['CURDIR'])
args.append('--html')
args.append('--show-private')
args.append('--no-imports')

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