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
 
@todo: Set up logging & debug properly. Enable selecting if MEF is created regardless of whether overviews exist
@todo: Fix the splashscreen, it's conflicting with the GetArgs GUI and needs to be sorted out - low priority...

'''

#Imports
import os,sys,glob
#Set up the splash screen. Importing the FT.Xml module takes forever...
#Commented out as it's conflicting with the GetArgs GUI and needs to be sorted out - low priority...
#from splashscreen import SplashScreen,CallBack
#startup=CallBack()
#if len(sys.argv) == 1:SplashScreen(callback=startup.check)
#from Tkinter import *
import Tkinter
import tkFileDialog
from Ft.Xml import Domlette as Dom
import utilities
import transforms
import progresslogger
#Turn off the splashscreen
#startup.value=True
def main(xls,xsl,dir,mef=False,log=None,debug=False,gui=False):
    '''
    Run the Metadata Transform
    @type  xls: C{str}
    @param xls: Excel spreadsheet to read metadata from
    @type  xsl: C{str}
    @param xsl: XSL transform {*.xsl|%s}
    @type  dir: C{str}
    @param dir: The directory to output metadata XML to
    @type  mef: C{boolean}
    @param mef: Create Metadata Exchange Format (MEF) file
    @type  log: C{boolean}
    @param log: Log file
    @type  debug: C{boolean}
    @param debug: Turn debug output on
    @type  gui: C{boolean}
    @param gui: Show the GUI progress dialog [Not yet implemented]
    ''' % '|'.join(['"%s"'%s for s in transforms.transforms.keys()])
    if debug:level=progresslogger.DEBUG
    else:level=progresslogger.INFO
    windowicon=os.environ['CURDIR']+'/lib/wm_icon.ico'
    try:pl = progresslogger.ProgressLogger('Metadata Transforms', logToConsole=True, logToFile=False, logToGUI=False, level=level, windowicon=windowicon)
    except:pl = progresslogger.ProgressLogger('Metadata Transforms', logToConsole=True, logToFile=False, logToGUI=False, level=level)
    for rec in utilities.ExcelReader(xls, list):
        try:
            overviews=[]
            for val in rec:
                if val[0]=='filename':filename=val[1]
                elif val[0]=='guid':guid=val[1]
                elif val[0] in ['quicklook','thumbnail'] and val[1] != '':overviews.append(val[1])
            strxml=transforms.ListToXML(rec,'crawlresult')
            xmlfile='%s/%s.%s.xml'%(dir,filename,guid)
            result = transforms.Transform(strxml, xsl, xmlfile)
            if overviews:transforms.CreateMEF(dir,xmlfile,guid,overviews)
            pl.info('Transformed metadata for ' +filename)
        except Exception,err:
            if 'message instruction' in err.args[0]:
                pl.info(''.join(err.args[1]).strip())
            else:
                pl.error('%s\n%s' % (filename, utilities.ExceptionInfo()))
                pl.debug(utilities.ExceptionInfo(10))
        
##    for rec in utilities.ExcelReader(xls):
##        try:
##            strxml=transforms.DictToXML(rec,'crawlresult')
##            result = transforms.Transform(strxml, xsl, '%s/%s.%s.xml'%(dir,rec['filename'],rec['guid']))
##            pl.info('Transformed metadata for ' +rec['filename'])
##        except Exception,err:
##            pl.error('%s\n%s' % (rec['filename'], utilities.ExceptionInfo()))
##            pl.debug(utilities.ExceptionInfo(10))


#========================================================================================================
if __name__ == '__main__':
    #To ensure uri's work...
    if os.path.basename(sys.argv[0])!=sys.argv[0]:os.chdir(os.path.dirname(sys.argv[0]))
    import optparse,icons,getargs
    description='Transform metadata to XML'
    parser = optparse.OptionParser(description=description)

    opt=parser.add_option("-x", dest="xls", metavar="xls", help="Excel spreadsheet")
    xlsarg=getargs.FileArg(opt,filter=[('Excel Spreadsheet','*.xls')],icon=icons.xls_img)
    xlsarg.tooltip="Excel spreadsheet to read metadata from"

    opt=parser.add_option('-d', dest="dir", metavar="dir", help='Output directory')
    opt.icon=icons.dir_img
    dirarg=getargs.DirArg(opt,initialdir='',enabled=True,icon=icons.dir_img,tooltip='Tooltip!')
    dirarg.tooltip='The directory to output metadata XML to'
    
    opt=parser.add_option("-t", dest="xsl", metavar="xsl", help="XSL transform")
    xslarg=getargs.ComboBoxArg(opt,icon=icons.xls_img)
    xslarg.tooltip="XSL transform {*.xsl|%s}" % '|'.join(['"%s"'%s for s in transforms.transforms.keys()])
    xslarg.options=transforms.transforms.keys()

    opt=parser.add_option("-m", action="store_true", dest="mef",default=False,   
                     help="Create Metadata Exchange Format (MEF) file")
    opt=parser.add_option("--debug", action="store_true", dest="debug",default=False, help="Turn debug output on")
    opt=parser.add_option("-l", dest="log", metavar="log",                            
                      help=optparse.SUPPRESS_HELP) #help="Log file")                     #Not yet implemented
    opt=parser.add_option("--gui", action="store_true", dest="gui", default=False,
                      help=optparse.SUPPRESS_HELP) #help="Show the GUI progress dialog") #Not yet implemented

    optvals,argvals = parser.parse_args()

    #Do we need to pop up the GUI?
    if not optvals.dir or not optvals.xls or not optvals.xsl:
        #Add existing command line args values to opt default values so they show in the gui
        for opt in parser.option_list:
            opt.default=vars(optvals).get(opt.dest,None)
        #Pop up the GUI
        args=getargs.GetArgs(dirarg,xlsarg,xslarg)
        if args:#GetArgs returns None if user cancels the GUI
            main(args.xls,args.xsl,args.dir,optvals.log,optvals.gui,optvals.debug)
    else: #No need for the GUI
        main(optvals.xls,optvals.xsl,optvals.dir,optvals.log,optvals.gui,optvals.debug)
        
