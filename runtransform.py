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
Metadata Transforms
===================
Script to run the Metadata Transforms.

Contains code to show GUI to gather input arguments when none are provided.
To run, call the eponymous batch file which sets the required environment variables.

Usage::
    runtransform.bat -x xls -t xsl -d dir

@newfield sysarg: Argument, Arguments
@sysarg: C{-x xls}: MS Excel spreadsheet to read from
@sysarg: C{-t xsl}: XSL transform - may be one of the pre-defined XSL transforms or a path to a custom XSL file.
@sysarg: C{-d dir}: Directory to write XML files to.

@note:B{Additional metadata elements}

      The ANZLIC ISO19139 stylesheet can make use of additional metadata elements that may be
      manually added to the Excel spreadsheet and will be included in the output XML/MEF metadata.
      See the L{transforms} module documentation for more information.

@todo: Set up logging & debug properly.
'''
#@sysarg: C{--nogui}         : Don't show the GUI progress dialog")

#Imports
import os,sys,glob
import Tkinter
import tkFileDialog
from metageta import utilities
from metageta import transforms
from metageta import progresslogger

def main(xls,xsl,dir,logger, mef=False,cat='',ops=''):
    '''
    Run the Metadata Transform
    @type  xls: C{str}
    @param xls: Excel spreadsheet to read metadata from
    @type  xsl: C{str}
    @param xsl: XSL transform {*.xsl|%s}
    @type  dir: C{str}
    @param dir: The directory to output metadata XML to
    @type  logger: C{progresslogger.ProgressLogger}
    @param logger: An instantiated logger
    @type  mef: C{boolean}
    @param mef: Create Metadata Exchange Format (MEF) file
    @type  cat: C{str}
    @param cat: The GeoNetwork category/ies to apply to the records ('|' separated)
    @type  ops: C{str}
    @param ops: The GeoNetwork operations privileges to apply to the records ('|' separated)

    @todo - start using the "-m" opt, currently not used at all.
          - add it to the GetArgs GUI
          - populate a dropdown list with transforms.categories
          - add a gui event that show/hides or enables/disables the categ list triggered by the mef opt
          - if <default> categ is selected, logic is:
            * check xls for categ column
            * if so use that,
            * if categ column is null for a row, of if no column at all then use default from config

    ''' % '|'.join(['"%s"'%s for s in transforms.transforms.keys()])

    xlrdr=utilities.ExcelReader(xls, list)
    qlkdir=os.path.dirname(xls)
    logger.info('Transforming %s metadata records'%xlrdr.records)
    for rec in xlrdr:
        try:
            tmpcat=cat #dummy var as we may overwrite it
            tmpops=ops
            overviews=[]
            deleted=False
            for i,val in enumerate(rec): #We use a list instead of a dict as there can be multiple fields with the same header/name
                if val[0]=='DELETED' and val[1] == 1:deleted=True
                elif val[0]=='filename':filename=val[1]
                elif val[0]=='guid':guid=val[1]
                elif val[0] in ['quicklook','thumbnail'] and val[1] != '':
                    overviews.append(os.path.join(qlkdir,val[1]))
                elif val[0] == 'category' and val[1]:
                    tmpcat=val[1]
                    del rec[i]
                elif val[0] == 'operations' and val[1]:
                    tmpops=val[1]
                    del rec[i]
            xmlfile='%s/%s.%s.xml'%(dir,filename,guid)
            meffile='%s/%s.%s.mef'%(dir,filename,guid)
            if deleted:
                logger.info('%s has been marked as deleted, XSLT processing will be terminated.'%filename)
                if os.path.exists(xmlfile):os.rename(xmlfile,'%s.deleted'%xmlfile)
                if os.path.exists(meffile):os.rename(meffile,'%s.deleted'%meffile)
                continue
            strxml=transforms.ListToXML(rec,'crawlresult')
            result = transforms.Transform(strxml, xsl, xmlfile)
            #if overviews:transforms.CreateMEF(dir,xmlfile,guid,overviews)
            #Create MEF even if there are no overviews
            if mef:transforms.CreateMEF(dir,xmlfile,guid,overviews,tmpcat,tmpops)
            logger.info('Transformed metadata for ' +filename)
        except Exception,err:
            logger.error('%s\n%s' % (filename, utilities.ExceptionInfo()))
            logger.debug(utilities.ExceptionInfo(10))
            try:os.remove(xmlfile)
            except:pass

        logger.updateProgress(xlrdr.records)

def exit():
    '''Force exit after closure of the ProgressBar GUI'''
    exe=os.path.splitext(os.path.basename(sys.executable.lower()))[0]
    if forceexit:   #Issue?
        if exe not in ['python','pythonw']: #Little kludge to stop killing dev IDEs
            os._exit(0)

def showmessage(title, msg,type=None):
    import Tkinter,tkMessageBox
    tk=Tkinter.Tk()
    tk.withdraw()
    val=tkMessageBox.showinfo(title,msg,type=type)
    tk.destroy()
    return val

def getlogger(name=None,nogui=False, debug=False, icon=None):
    if debug:
        level=progresslogger.DEBUG
    else:
        level=progresslogger.INFO
    try:   logger = progresslogger.ProgressLogger(name=name,logfile=None, logToConsole=True, logToFile=False, logToGUI=not nogui, level=level, icon=icon, callback=exit)
    except:logger = progresslogger.ProgressLogger(name=name,logfile=logfile, logToConsole=True, logToFile=False, logToGUI=not nogui, level=level, callback=exit)
    return logger

#========================================================================================================
if __name__ == '__main__':
    def mefcallback(mefarg,*args):
        #checked=mefarg.value.get()
        checked=mefarg.value
        for arg in args:
            arg.enabled=checked

    #To ensure uri's work...
    if os.path.basename(sys.argv[0])!=sys.argv[0]:os.chdir(os.path.dirname(sys.argv[0]))
    import optparse
    from metageta import icons,getargs

    APP='MetaGETA Transforms'
    ICON=icons.app_img
    description='Transform metadata to XML'

    parser = optparse.OptionParser(description=description)

    opt=parser.add_option("-x", dest="xls", metavar="xls", help="Excel spreadsheet")
    xlsarg=getargs.FileArg(opt,filter=[('Excel Spreadsheet','*.xls')],icon=icons.xls_img)
    xlsarg.tooltip="Excel spreadsheet to read metadata from."

    opt=parser.add_option('-d', dest="dir", metavar="dir", help='Output directory')
    opt.icon=icons.dir_img
    dirarg=getargs.DirArg(opt,initialdir='',enabled=True,icon=icons.dir_img)
    dirarg.tooltip='The directory to output metadata XML to.'

    opt=parser.add_option("-t", dest="xsl", metavar="xsl", help="XSL transform")
    xslarg=getargs.ComboBoxArg(opt,icon=icons.xsl_img)
    xslarg.tooltip="XSL transform {*.xsl|%s}." % '|'.join(['"%s"'%s for s in transforms.transforms.keys()])
    xslarg.options=transforms.transforms.keys()

    opt=parser.add_option("-m", action="store_true", dest="mef",default=False,
                     help="Create Metadata Exchange Format (MEF) file")
    mefarg=getargs.BoolArg(opt,icon=icons.xsl_img)
    mefarg.tooltip=opt.help+'?'

    opt=parser.add_option("-c", dest="cat", metavar="cat",default=transforms.categories['default'],
                     help="Dataset category")
    catarg=getargs.ComboBoxArg(opt,enabled=False,multiselect=True,icon=icons.xsl_img)
    catarg.options=transforms.categories['categories']
    catarg.tooltip='Dataset category for Metadata Exchange Format (MEF) file. Default is "%s". If a "category" column exists in the spreadsheet, values from that column will override any selection here.'%transforms.categories['default']

    opt=parser.add_option("-o", dest="ops", metavar="ops",default=transforms.operations['default'],
                     help="Allowed operations for all users")
    opsarg=getargs.ComboBoxArg(opt,enabled=False,multiselect=True,icon=icons.xsl_img)
    opsarg.options=transforms.operations['operations']
    opsarg.tooltip='Allowed operations for all users for Metadata Exchange Format (MEF) file. Default is "%s". If a "operations" column exists in the spreadsheet, values from that column will override any selection here.'%transforms.operations['default']

    mefarg.callback=getargs.Command(mefcallback,mefarg,catarg,opsarg)

    opt=parser.add_option("--keep-alive", action="store_true", dest="keepalive", default=False, help="Keep this dialog box open")
    kaarg=getargs.BoolArg(opt)
    kaarg.tooltip='Do you want to keep this dialog box open after running the metadata transform so you can run another?'

    opt=parser.add_option("--debug", action="store_true", dest="debug",default=False, help="Turn debug output on")
    opt=parser.add_option("-l", dest="log", metavar="log",
                      help=optparse.SUPPRESS_HELP) #help="Log file")                     #Not yet implemented
    opt=parser.add_option("--nogui", action="store_true", dest="nogui", default=False, help="Disable the GUI progress dialog")

    optvals,argvals = parser.parse_args()

    logger=None
    forceexit=True
    #Do we need to pop up the GUI?
    if not optvals.dir or not optvals.xls or not optvals.xsl:
        #Add existing command line args values to opt default values so they show in the gui
        for opt in parser.option_list:
            opt.default=vars(optvals).get(opt.dest,None)
        #Pop up the GUI
        keepalive=True
        hasrun=False
        while keepalive:
            args=getargs.GetArgs(xlsarg,dirarg,xslarg,mefarg,catarg,opsarg,kaarg,title=APP,icon=ICON)
            if args:#GetArgs returns None if user cancels the GUI
                if logger and logger.logging:
                    logger.resetProgress()
                else:
                    logger=getlogger(name=APP,nogui=optvals.nogui, debug=optvals.debug, icon=ICON)
                keepalive=args.keepalive
                forceexit=True
                main(args.xls,args.xsl,args.dir,logger,args.mef,args.cat,args.ops)
                forceexit=False
                hasrun=True
            else:
                if not hasrun:parser.print_help()
                keepalive=False
    else: #No need for the GUI
        #logger=getlogger(name=APP,nogui=optvals.nogui, debug=optvals.debug, icon=ICON)
        logger=getlogger(name=APP,nogui=True, debug=optvals.debug, icon=ICON)
        main(optvals.xls,optvals.xsl,optvals.dir,logger,optvals.mef,optvals.cat,optvals.ops)

    if logger:
        logger.shutdown()
        del logger

