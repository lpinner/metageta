#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2013 Australian Government, Department of the Environment
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
    runcrawler.bat/sh -d dir -x xls {-o} {--debug}

@newfield sysarg: Argument, Arguments
@sysarg: C{-d [dir]}        : Directory to search for imagery
@sysarg: C{-x [xls]}        : MS Excel spreadsheet to write metadata to
@sysarg: C{-m, --mediaid}   : CD/DVD media ID, defaults to volume label.
@sysarg: C{-u, --update}    : Update previous crawl results.
@sysarg: C{-o, --overviews} : Generate overview (quicklook/thumbnail) images")
@sysarg: C{-r, --recurse}   : Search directory recursively?
@sysarg: C{-a, --archive}   : Search compressed archives?
@sysarg: C{--debug}         : Turn debug output on

@note: See U{Issue 22<http://code.google.com/p/metageta/issues/detail?id=22>}
'''

import sys, os, re,time,tempfile
from metageta import formats
from metageta import geometry
from metageta import utilities
from metageta import crawler
from metageta import overviews
from metageta import progresslogger

def main(dir, xls, logger, mediaid=None, update=False, getovs=False, recurse=False, archive=False):
    """ Run the Metadata Crawler

        @type  dir:    C{str}
        @param dir:    The directory to start the metadata crawl.
        @type  xls:    C{str}
        @param xls:    Excel spreadsheet to write metadata to
        @type  logger: C{progresslogger.ProgressLogger}
        @param logger: Use an already instantiated logger
        @type  mediaid:C{str}
        @param mediaid:CD/DVD media ID
        @type  getovs: C{boolean}
        @param getovs: Generate overview (quicklook/thumbnail) images
        @type  recurse: C{boolean}
        @param recurse: Search directory recursively?
        @type  archive: C{boolean}
        @param archive: Search compressed archives (tar/zip)?
        @return:  C{progresslogger.ProgressLogger}
    """

    shp=xls.replace('.xls','.shp')

    format_regex  = formats.format_regex
    format_fields = formats.fields

    logger.debug(' '.join(sys.argv))

    try:
        #raise Exception
        ExcelWriter=utilities.ExcelWriter(xls,format_fields.keys(),update=update)

        #Are we updating an existing crawl?
        records={}
        if update and os.path.exists(xls):

            #Do we need to recreate the shapefile?
            if os.path.exists(shp):
                ShapeWriter=False
            else:
                logger.info('%s does not exist, it will be recreated...'%shp)
                ShapeWriter=geometry.ShapeWriter(shp,format_fields,update=False)

            #Build a dict of existing records
            row=-1
            for row,rec in enumerate(utilities.ExcelReader(xls)):
                #Check if the dataset still exists, mark it DELETED if it doesn't

                if os.path.exists(rec['filepath']) or rec['mediaid'] !='' or \
                   (rec['filepath'][0:4]=='/vsi' and utilities.compressed_file_exists(rec['filepath'],False)):
                    if ShapeWriter:
                        ext=[rec['UL'].split(','),rec['UR'].split(','),rec['LR'].split(','),rec['LL'].split(',')]
                        ShapeWriter.WriteRecord(ext,rec)
                    #Kludge to ensure backwards compatibility with previously generated guids
                    #records[rec['guid']]=rec
                    records[utilities.uuid(rec['filepath'])]=(row,rec)
                else:
                    if rec.get('DELETED',0)!=1:
                        rec['DELETED']=1
                        ExcelWriter.UpdateRecord(rec,row)
                        logger.info('Marked %s as deleted' % (rec['filepath']))
            if row==-1:logger.info('Output spreadsheet is empty, no records to update')
            del ShapeWriter
        ShapeWriter=geometry.ShapeWriter(shp,format_fields,update=update)
    except Exception,err:
        logger.error('%s' % utilities.ExceptionInfo())
        logger.debug(utilities.ExceptionInfo(10))
        time.sleep(0.5)# So the progresslogger picks up the error message before this python process exits.
        #sys.exit(1)
        return

    logger.info('Searching for files...')
    now=time.time()
    Crawler=crawler.Crawler(dir,recurse=recurse,archive=archive)
    logger.info('Found %s files...'%Crawler.filecount)

    #Loop thru dataset objects returned by Crawler
    for ds in Crawler:
        try:
            logger.debug('Attempting to open %s'%Crawler.file)
            fi=ds.fileinfo
            fi['filepath']=utilities.uncpath(fi['filepath'])
            fi['filelist']='|'.join(utilities.uncpath(ds.filelist))
            #qlk=utilities.uncpath(os.path.join(os.path.dirname(xls),'%s.%s.qlk.jpg'%(fi['filename'],fi['guid'])))
            #thm=utilities.uncpath(os.path.join(os.path.dirname(xls),'%s.%s.thm.jpg'%(fi['filename'],fi['guid'])))
            qlk=os.path.join(os.path.dirname(xls),'%s.%s.qlk.jpg'%(fi['filename'],fi['guid']))
            thm=os.path.join(os.path.dirname(xls),'%s.%s.thm.jpg'%(fi['filename'],fi['guid']))

            if update and ds.guid in records:
                row,rec=records[ds.guid]
                #Issue 35: if it's not modified, but we've asked for overview images and it doesn't already have them....
                if ismodified(rec,fi,os.path.dirname(xls)) or (not rec['quicklook'] and getovs):
                    md=ds.metadata
                    geom=ds.extent
                    md.update(fi)
                    logger.info('Updated metadata for %s, %s files remaining' % (Crawler.file,len(Crawler.files)))
                    try:
                        if rec['quicklook'] and os.path.exists(rec['quicklook']):getovs=False #Don't update overview
                        if getovs:
                            qlk=ds.getoverview(qlk, width=800)
                            #We don't need to regenerate it, just resize it
                            #thm=ds.getoverview(thm, width=150)
                            thm=overviews.resize(qlk,thm,width=150)
                            md['quicklook']=os.path.basename(qlk)
                            md['thumbnail']=os.path.basename(thm)
                            #md['quicklook']=utilities.uncpath(qlk)
                            #md['thumbnail']=utilities.uncpath(thm)
                            logger.info('Updated overviews for %s' % Crawler.file)
                    except Exception,err:
                        logger.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
                        logger.debug(utilities.ExceptionInfo(10))
                    try:
                        ExcelWriter.UpdateRecord(md,row)
                    except Exception,err:
                        logger.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
                        logger.debug(utilities.ExceptionInfo(10))
                    try:
                        ShapeWriter.UpdateRecord(geom,md,'guid="%s"'%rec['guid'])
                    except Exception,err:
                        logger.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
                        logger.debug(utilities.ExceptionInfo(10))
                else:
                    logger.info('Metadata did not need updating for %s, %s files remaining' % (Crawler.file,len(Crawler.files)))
                    continue
            else:
                md=ds.metadata
                geom=ds.extent
                md.update(fi)
                if mediaid:md.update({'mediaid':mediaid})
                logger.info('Extracted metadata from %s, %s files remaining' % (Crawler.file,len(Crawler.files)))
                try:
                    if getovs:
                        qlk=ds.getoverview(qlk, width=800)
                        #We don't need to regenerate it, just resize it
                        #thm=ds.getoverview(thm, width=150)
                        thm=overviews.resize(qlk,thm,width=150)
                        md['quicklook']=os.path.basename(qlk)
                        md['thumbnail']=os.path.basename(thm)
                        #md['quicklook']=utilities.uncpath(qlk)
                        #md['thumbnail']=utilities.uncpath(thm)
                        logger.info('Generated overviews from %s' % Crawler.file)
                except Exception,err:
                    logger.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
                    logger.debug(utilities.ExceptionInfo(10))
                try:
                    ExcelWriter.WriteRecord(md)
                except Exception,err:
                    logger.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
                    logger.debug(utilities.ExceptionInfo(10))
                try:
                    ShapeWriter.WriteRecord(geom,md)
                except Exception,err:
                    logger.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
                    logger.debug(utilities.ExceptionInfo(10))

        except NotImplementedError,err:
            logger.warn('%s: %s' % (Crawler.file, err.message))
            logger.debug(utilities.ExceptionInfo(10))
        except Exception,err:
            logger.error('%s\n%s' % (Crawler.file, utilities.ExceptionInfo()))
            logger.debug(utilities.ExceptionInfo(10))
    then=time.time()
    logger.debug(then-now)
    #Check for files that couldn't be opened
    for file,err,dbg in Crawler.errors:
       logger.error('%s\n%s' % (file, err))
       logger.debug(dbg)

    if Crawler.filecount == 0:
        logger.info("No data found")
    else:
        logger.info("Metadata extraction complete!")

    del ExcelWriter
    del ShapeWriter

def ismodified(record,fileinfo,xlspath):
    ''' Check if a record from a previous metadata crawl needs to be updated.

        @type  record:   C{dict}
        @param record:   The record from a previous crawl.
        @type  fileinfo: C{dict}
        @param fileinfo: The fileinfo from a dataset located in the current crawl
        @type  xlspath: C{str}
        @param xlspath:  The path to the XLS that holds the record from the previous crawl
        @return:  C{boolean}
    '''
    if record['datemodified']!=fileinfo['datemodified']:
        return True
    elif record['filelist']!=fileinfo['filelist']:
        return True
    elif record['quicklook']:
        if os.path.basename(record['quicklook'])==record['quicklook']:
            qlk=os.path.join(xlspath,record['quicklook'])
        else:qlk=record['quicklook']
        if not os.path.exists(qlk):
            return True
    else:
        try:md=time.mktime(time.strptime(record['metadatadate'],utilities.datetimeformat))
        except:md=time.mktime(time.strptime(record['metadatadate'],utilities.dateformat)) + (60*60*24-1) #Mainain backwards compatibility with spreadsheets created using MetaGETA <=1.3.3
        for f in fileinfo['filelist'].split('|'):
            fs = os.stat(f)
            if md<fs.st_mtime:return True

    return False

def exit():
    '''Force exit after closure'''
    exe=os.path.splitext(os.path.basename(sys.executable.lower()))[0]
    if forceexit:   #Issue?
        if exe in ['python','pythonw']: #Little kludge to stop killing dev IDEs
            os._exit(0)

def getlogger(logfile,name=None, debug=False):
    geometry.debug=debug
    if debug:
        level=progresslogger.DEBUG
    else:
        level=progresslogger.INFO
        geometry.gdal.PushErrorHandler( 'CPLQuietErrorHandler' )

    return progresslogger.ProgressLogger(name=name,logfile=logfile, logToConsole=True, logToFile=True, level=level, callback=exit)

#========================================================================================================
#========================================================================================================
if __name__ == '__main__':

    def mediacallback(dirarg,medarg):
        #dirname=dirarg.value.get()
        dirname=dirarg.value
        if os.path.exists(dirname):
            volname=utilities.volname(dirname)
            if volname: #Is it a CD/DVD
                #if not medarg.value.get():#If it hasn't already been set
                if not medarg.value:#If it hasn't already been set
                        medarg.enabled=True
                        #medarg.value.set(volname)
                        medarg.value=volname
            else:
                medarg.enabled=False
                #medarg.value.set('')
                medarg.value=''

    #This is an extra check so existing spreadsheets don't get overwritten unless
    #the update arg is explicitly unchecked
    def xlscallback(xlsarg,updatearg):
        #xls=xlsarg.value.get()
        xls=xlsarg.value
        if utilities.exists(xls):
            updatearg.enabled=True
            #updatearg.value.set(True)
            updatearg.value=True
        else:
            updatearg.enabled=False
            #updatearg.value.set(False)
            updatearg.value=False

    def writablecallback(arg):
        #filepath=arg.value.get()
        filepath=arg.value
        if utilities.writable(filepath):
            return True
        else:
            #arg.value.set('')
            arg.value
            err='I/O Error','%s is not writable.'%filepath
            logger.error('%s' % utilities.ExceptionInfo())
            try:getargs.tkMessageBox.showerror()
            except:pass
            return False

    import optparse
    from metageta import icons,getargs

    APP='MetaGETA Crawler'
    ICON=icons.app_img

    description='Run the metadata crawler'
    parser = optparse.OptionParser(description=description)

    opt=parser.add_option('-d', dest="dir", metavar="dir",help='The directory to crawl')
    dirarg=getargs.DirArg(opt,initialdir='',enabled=True,icon=icons.dir_img)
    dirarg.tooltip='The directory to start recursively searching for raster imagery.'

    opt=parser.add_option("-r", "--recurse", action="store_true", dest="recurse",default=False,
                      help="Search directory recursively")
    recursearg=getargs.BoolArg(opt,tooltip='Do you want to search in sub-directories?')

    opt=parser.add_option("-a", "--archive", action="store_true", dest="archive",default=False,
                      help="Search compressed archives (tar/zip)?")
    archivearg=getargs.BoolArg(opt,tooltip='Do you want to search compressed archives (tar/zip)?\nNote that this will slow the crawler down considerably.')

    opt=parser.add_option('-m', dest="med", metavar="media",help='CD/DVD ID')
    medarg=getargs.StringArg(opt,enabled=False,required=False)
    medarg.tooltip='You can enter an ID for a CD/DVD, this defaults to the disc volume label.'

    opt=parser.add_option("-x", dest="xls", metavar="xls",help="Output metadata spreadsheet")
    xlsarg=getargs.FileArg(opt,filter=[('Excel Spreadsheet','*.xls')],icon=icons.xls_img,saveas=True)
    xlsarg.tooltip='The Excel Spreadsheet to write the metadata to. A shapefile of extents, a logfile and overview images are also output to the same directory.'

    opt=parser.add_option("-u", "--update", action="store_true", dest="update",default=False,
                      help="Update existing crawl results")
    updatearg=getargs.BoolArg(opt,tooltip='Do you want to update existing crawl results?', enabled=False)

    opt=parser.add_option("-o", "--overviews", action="store_true", dest="ovs",default=False,
                      help="Generate overview images")
    ovarg=getargs.BoolArg(opt)
    ovarg.tooltip='Do you want to generate overview (quicklook and thumbnail) images?'

    opt=parser.add_option("--debug", action="store_true", dest="debug",default=False,
                      help="Turn debug output on")

    opt=parser.add_option("--keep-alive", action="store_true", dest="keepalive", default=False, help="Keep this dialog box open")
    kaarg=getargs.BoolArg(opt)
    kaarg.tooltip='Do you want to keep this dialog box open after running the metadata crawl so you can run another?'

    #Add a callback to the directory arg, use the Command class so we can has arguments
    dirarg.callback=getargs.Command(mediacallback,dirarg,medarg)
    #Add a callback to the xls arg, use the Command class so we can has arguments
    xlsarg.callback=getargs.Command(xlscallback,xlsarg,updatearg)

    #Parse existing command line args
    optvals,argvals = parser.parse_args()
    if optvals.dir and optvals.dir[-1]=='"': #Fix C:" issue when called from Explorer context menu
            optvals.dir=optvals.dir[:-1]+'\\'

    logger=None
    forceexit=True
    #Do we need to pop up the GUI?
    if not optvals.dir or not optvals.xls:
        #Add existing command line args values to opt default values so they show in the gui
        for opt in parser.option_list:
            opt.default=vars(optvals).get(opt.dest,None)
        keepalive=True
        hasrun=False
        validate=getargs.Command(writablecallback,xlsarg)
        if optvals.xls:
            optvals.xls=utilities.checkExt(utilities.encode(optvals.xls), ['.xls'])
            xlsarg.value=optvals.xls
            xlsarg.callback()
        while keepalive:
            #Pop up the GUI
            args=getargs.GetArgs(dirarg,medarg,xlsarg,updatearg,recursearg,archivearg,ovarg,kaarg,callback=validate,title=APP,icon=ICON)
            if args:#GetArgs returns None if user cancels the GUI/closes the dialog (or Tkinter can not be imported)
                keepalive=args.keepalive
                args.xls = utilities.checkExt(utilities.encode(args.xls), ['.xls'])

                log=args.xls.replace('.xls','.log')
                if logger and logger.logging:
                    logger.logfile=log
                else:
                    logger=getlogger(log,name=APP,debug=optvals.debug)
                keepalive=args.keepalive
                forceexit=True
                main(args.dir,args.xls,logger,args.med,args.update,args.ovs,args.recurse,args.archive)
                forceexit=False
                hasrun=True
            else:
                if not hasrun:parser.print_help()
                keepalive=False
    else: #No need for the GUI
        xls = utilities.checkExt(utilities.encode(optvals.xls), ['.xls'])
        log=xls.replace('.xls','.log')
        #logger=getlogger(log, name=APP, debug=optvals.debug, icon=ICON)
        logger=getlogger(log, name=APP, debug=optvals.debug, icon=ICON)
        main(optvals.dir,xls,logger,optvals.med,optvals.update,optvals.ovs,optvals.recurse,optvals.archive)

    if logger:
        logger.shutdown()
        del logger
