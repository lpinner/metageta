# -*- coding: latin-1 -*-
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
Script to run the MetaGeta Metadata Crawler

Contains code to show GUI to gather input arguments when none are provided
To run, call the eponymous batch file/shell script which sets the required environment variables

Usage::
    runcrawler.bat/sh -d dir -x xls -s shp -l log {-o} {--nogui} {--debug}

@newfield sysarg: Argument, Arguments
@sysarg: C{-d [dir]}        : Directory to to recursively search for imagery
@sysarg: C{-x [xls]}        : MS Excel spreadsheet to write metadata to
@sysarg: C{-u, --update}    : Update previous crawl results.
@sysarg: C{-o, --overviews} : Generate overview (quicklook/thumbnail) images")
@sysarg: C{--nogui}         : Don't show the GUI progress dialog")
@sysarg: C{--debug}         : Turn debug output on

@note: See U{Issue 22<http://code.google.com/p/metageta/issues/detail?id=22>}
'''

import sys, os, re,time

import progresslogger
import formats
import geometry
import utilities
import crawler
import overviews

def main(dir,xls, update=False, getovs=False, nogui=True, debug=False): 
    """ Run the Metadata Crawler

        @type  dir:    C{str}
        @param dir:    The directory to start the metadata crawl.
        @type  xls:    C{str}
        @param xls:    Excel spreadsheet to write metadata to
        @type  getovs: C{boolean}
        @param getovs: Generate overview (quicklook/thumbnail) images
        @type  nogui:  C{boolean}
        @param nogui:  Don't show the GUI progress dialog
        @type  debug:  C{boolean}
        @param debug:  Turn debug output on
        @return:  C{None}
    """
    xls = utilities.checkExt(utilities.encode(xls), ['.xls'])
    shp=xls.replace('.xls','.shp')
    log=xls.replace('.xls','.log')

    format_regex  = formats.format_regex
    format_fields = formats.fields
    
    formats.debug=debug
    crawler.debug=debug
    geometry.debug=debug
    if debug:
        level=progresslogger.DEBUG
    else:
        level=progresslogger.INFO
        geometry.gdal.PushErrorHandler( 'CPLQuietErrorHandler' )
    
    windowicon=os.environ['CURDIR']+'/lib/wm_icon.ico'
    try:pl = progresslogger.ProgressLogger('MetadataCrawler',logfile=log, logToConsole=True, logToFile=True, logToGUI=not nogui, level=level, windowicon=windowicon, callback=exit)
    except:pl = progresslogger.ProgressLogger('MetadataCrawler',logfile=log, logToConsole=True, logToFile=True, logToGUI=not nogui, level=level, callback=exit)

    pl.debug(' '.join(sys.argv))
   
    try:

        #Are we updating an existing crawl?
        records={}
        if update and os.path.exists(xls):

            #Do we need to recreate the shapefile?
            if os.path.exists(shp):
                ShapeWriter=False
            else:
                pl.info('%s does not exist, it will be recreated...'%shp)
                ShapeWriter=geometry.ShapeWriter(shp,format_fields,update=False)

            #Build a dict of existing records
            for row,rec in enumerate(utilities.ExcelReader(xls)):
                #Check if the dataset still exists, mark it DELETED if it doesn't
                if os.path.exists(rec['filepath']):
                    if ShapeWriter:
                        ext=[rec['UL'].split(','),rec['UR'].split(','),rec['LR'].split(','),rec['LL'].split(',')]
                        ShapeWriter.WriteRecord(ext,rec)
                    #Kludge to ensure backwards compatibility with previously generated guids
                    #records[rec['guid']]=rec
                    records[utilities.uuid(rec['filepath'])]=(row,rec)
                else:
                    rec['DELETED']=1
                    ExcelWriter.UpdateRecord(rec,row)
                    pl.info('Marked %s as deleted' % (rec['filepath']))
            del ShapeWriter
        ExcelWriter=utilities.ExcelWriter(xls,format_fields.keys(),update=update)
        ShapeWriter=geometry.ShapeWriter(shp,format_fields,update=update)
    except Exception,err:
        pl.error('%s' % utilities.ExceptionInfo())
        pl.debug(utilities.ExceptionInfo(10))
        del pl
        time.sleep(0.5)# So the progresslogger picks up the error message before this python process exits.
        sys.exit(1)

    pl.info('Searching for files...')
    now=time.time()
    Crawler=crawler.Crawler(dir)
    pl.info('Found %s files...'%Crawler.filecount)

    #Loop thru dataset objects returned by Crawler
    for ds in Crawler:
        try:
            pl.debug('Attempting to open %s'%Crawler.file)
            fi=ds.fileinfo
            fi['filepath']=utilities.uncpath(fi['filepath'])
            fi['filelist']=','.join(utilities.uncpath(ds.filelist))
            qlk=utilities.uncpath(os.path.join(os.path.dirname(xls),'%s.%s.qlk.jpg'%(fi['filename'],fi['guid'])))
            thm=utilities.uncpath(os.path.join(os.path.dirname(xls),'%s.%s.thm.jpg'%(fi['filename'],fi['guid'])))

            if update and ds.guid in records:
                row,rec=records[ds.guid]
                if rec['datemodified']==fi['datemodified']:
                    pl.info('Metadata did not need updating for %s, %s files remaining' % (Crawler.file,len(Crawler.files)))
                    pl.updateProgress(newMax=Crawler.filecount)
                    continue
                else:
                    md=ds.metadata
                    geom=ds.extent
                    md.update(fi)
                    pl.info('Updated metadata for %s, %s files remaining' % (Crawler.file,len(Crawler.files)))
                    try:
                        if rec['quicklook']:getovs=True #Force update of overview
                        if getovs:
                            qlk=ds.getoverview(qlk, width=800)
                            #We don't need to regenerate it, just resize it
                            #thm=ds.getoverview(thm, width=150)
                            thm=overviews.resize(qlk,thm,width=150)
                            md['quicklook']=utilities.uncpath(qlk)
                            md['thumbnail']=utilities.uncpath(thm)
                            pl.info('Updated overviews for %s' % Crawler.file)
                    except Exception,err:
                        pl.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
                        pl.debug(utilities.ExceptionInfo(10))
                    try:
                        ExcelWriter.UpdateRecord(md,row)
                    except Exception,err:
                        pl.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
                        pl.debug(utilities.ExceptionInfo(10))
                    try:
                        ShapeWriter.UpdateRecord(geom,md,'guid="%s"'%rec['guid'])
                    except Exception,err:
                        pl.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
                        pl.debug(utilities.ExceptionInfo(10))
            else:
                md=ds.metadata
                geom=ds.extent
                md.update(fi)
                pl.info('Extracted metadata from %s, %s files remaining' % (Crawler.file,len(Crawler.files)))
                try:
                    if getovs:
                        qlk=ds.getoverview(qlk, width=800)
                        #We don't need to regenerate it, just resize it
                        #thm=ds.getoverview(thm, width=150)
                        thm=overviews.resize(qlk,thm,width=150)
                        md['quicklook']=utilities.uncpath(qlk)
                        md['thumbnail']=utilities.uncpath(thm)
                        pl.info('Generated overviews from %s' % Crawler.file)
                except Exception,err:
                    pl.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
                    pl.debug(utilities.ExceptionInfo(10))
                try:
                    ExcelWriter.WriteRecord(md)
                except Exception,err:
                    pl.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
                    pl.debug(utilities.ExceptionInfo(10))
                try:
                    ShapeWriter.WriteRecord(geom,md)
                except Exception,err:
                    pl.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
                    pl.debug(utilities.ExceptionInfo(10))

            pl.updateProgress(newMax=Crawler.filecount)
        except Exception,err:
            pl.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
            pl.debug(utilities.ExceptionInfo(10))
    then=time.time()
    pl.debug(then-now)
    #Check for files that couldn't be opened
    for file,err,dbg in Crawler.errors:
       pl.error('%s\n%s' % (file, err))
       pl.debug(dbg)

    if Crawler.filecount == 0:
        pl.info("No data found")
    else:
        pl.info("Metadata extraction complete!")
    pl.updateProgress(newMax=1) #Just so the progress meter hits 100%

    del pl
    del ExcelWriter
    del ShapeWriter
def exit(): 
    '''Force exit after closure of the ProgressBar GUI'''
    os._exit(0)

#========================================================================================================
#========================================================================================================
if __name__ == '__main__':
    import optparse,icons,getargs
    description='Run the metadata crawler'
    parser = optparse.OptionParser(description=description)
    opt=parser.add_option('-d', dest="dir", metavar="dir",help='The directory to crawl')
    opt.icon=icons.dir_img
    opt.argtype=getargs.DirArg
    opt.tooltip='The directory to start recursively searching for raster imagery.'
    
    opt=parser.add_option("-x", dest="xls", metavar="xls",help="Output metadata spreadsheet")
    opt.argtype=getargs.FileArg
    opt.icon=icons.xls_img
    opt.filter=[('Excel Spreadsheet','*.xls')]
    opt.tooltip='The Excel Spreadsheet to write the metadata to. A shapefile of extents, a logfile and overview images are also output to the same directory.'
    opt=parser.add_option("-u", "--update", action="store_true", dest="update",default=False,
                      help="Update existing crawl results")
    opt.argtype=getargs.BoolArg
    opt.tooltip='Do you want to update existing crawl results?'

    opt=parser.add_option("-o", "--overviews", action="store_true", dest="ovs",default=False,
                      help="Generate overview images")
    opt.tooltip='Do you want to generate overview (quicklook and thumbnail) images?'

    opt.argtype=getargs.BoolArg
    opt=parser.add_option("--debug", action="store_true", dest="debug",default=False,
                      help="Turn debug output on")
    opt=parser.add_option("--nogui", action="store_true", dest="nogui", default=False,
                      help="Don't show the GUI progress dialog")

    #Parse existing command line args
    optvals,argvals = parser.parse_args()

    #Do we need to pop up the GUI?
    #if not optvals.dir or not optvals.log or not optvals.shp or not optvals.xls:
    if not optvals.dir or not optvals.xls:
        #Add existing command line args values to opt default values so they show in the gui
        for opt in parser.option_list:
            if 'argtype' in vars(opt):
                opt.default=vars(optvals)[opt.dest]
        #Pop up the GUI
        args=getargs.GetArgs(*[opt for opt in parser.option_list if 'argtype' in vars(opt)])
        if args:#GetArgs returns None if user cancels the GUI
            main(args.dir,args.xls,args.update,args.ovs,optvals.nogui,optvals.debug)
    else: #No need for the GUI
        main(optvals.dir,optvals.xls,optvals.update,optvals.ovs,optvals.nogui,optvals.debug)
