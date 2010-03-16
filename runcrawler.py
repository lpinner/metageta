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
    runcrawler.bat/sh -d dir -x xls -s shp -l log {-o} {--nomd} {--gui} {--debug}

@newfield sysarg: Argument, Arguments
@sysarg: C{-d [dir]}: Directory to to recursively search for imagery
@sysarg: C{-x [xls]}: MS Excel spreadsheet to wrtite metadata to
@sysarg: C{-s [shp]}: ESRI Shapefile to write extents to
@sysarg: C{-l [log]}: Log file to write messages to
@sysarg: C{-o}      : Generate overview (quicklook/thumbnail) images")
@sysarg: C{--nomd}  : Extract metadata (crawl), if False just get basic file info (walk)")
@sysarg: C{--gui}   : Show the GUI progress dialog")
@sysarg: C{--debug} : Turn debug output on
'''

import sys, os, re,time
import Tkinter 
import tkFileDialog
import tkMessageBox

import progresslogger
import formats
import geometry
import utilities
import crawler

def main(dir,xls,shp,log, gui=False, debug=False, nomd=False, getovs=False): 
    """ Run the Metadata Crawler

        @type  dir: C{str}
        @param dir: The directory to start the metadata crawl.
        @type  xls: C{str}
        @param xls: Excel spreadsheet to write metadata to
        @type  shp: C{str}
        @param shp: Shapefile to write extents to
        @type  log: C{str}
        @param log: Log file
        @type  gui: C{boolean}
        @param gui: Show the GUI progress dialog
        @type  debug: C{boolean}
        @param debug: Turn debug output on
        @type  nomd: C{boolean}
        @param nomd: Extract metadata (crawl), if False just get basic file info (walk)
        @type  getovs: C{boolean}
        @param getovs: Generate overview (quicklook/thumbnail) images
        @return:  C{None}
    """
    xls = utilities.checkExt(xls, ['.xls'])
    shp = utilities.checkExt(shp, ['.shp'])
    log = utilities.checkExt(shp, ['.log', '.txt'])

    format_regex  = formats.format_regex
    format_fields = formats.fields
    
    if debug:
        level=progresslogger.DEBUG
        formats.debug=debug
        crawler.debug=debug
    else:level=progresslogger.INFO
    
    windowicon=os.environ['CURDIR']+'/lib/wm_icon.ico'
    try:pl = progresslogger.ProgressLogger('MetadataCrawler',logfile=log, logToConsole=True, logToFile=True, logToGUI=gui, level=level, windowicon=windowicon, callback=exit)
    except:pl = progresslogger.ProgressLogger('MetadataCrawler',logfile=log, logToConsole=True, logToFile=True, logToGUI=gui, level=level, callback=exit)

    #pl.debug('%s %s %s %s %s %s' % (dir,xls,shp,log,gui,debug))
    pl.debug(' '.join(sys.argv))

    try:
        ExcelWriter=utilities.ExcelWriter(xls,format_fields.keys())
        ShapeWriter=geometry.ShapeWriter(shp,format_fields,overwrite=True)
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
            if not nomd:
                pl.debug('Attempting to open %s'%Crawler.file)
                md=ds.metadata
                geom=ds.extent
                fi=ds.fileinfo
                fi['filepath']=utilities.convertUNC(fi['filepath'])
                fi['filelist']=','.join(utilities.convertUNC(ds.filelist))
                md.update(fi)
                pl.info('Extracted metadata from %s, %s of %s files remaining' % (Crawler.file,len(Crawler.files),Crawler.filecount))
                try:
                    if getovs:
                        qlk=os.path.join(os.path.dirname(xls),'%s.%s.qlk.jpg'%(fi['filename'],fi['guid']))
                        thm=os.path.join(os.path.dirname(xls),'%s.%s.thm.jpg'%(fi['filename'],fi['guid']))
                        qlk=ds.getoverview(qlk, width=800)
                        thm=ds.getoverview(thm, width=150)
                        md['quicklook']=utilities.convertUNC(qlk)
                        md['thumbnail']=utilities.convertUNC(thm)
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
            else:
                fi=ds.fileinfo
                fi['filepath']=utilities.convertUNC(fi['filepath'])
                fi['filelist']=','.join(utilities.convertUNC(ds.filelist))

                pl.info('Extracted file info from %s, %s of %s files remaining' % (Crawler.file,len(Crawler.files),Crawler.filecount))
                try:
                    ExcelWriter.WriteRecord(fi)
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
        pl.updateProgress(newMax=1) #Just so the progress meter hits 100%
    else:
        pl.updateProgress(newMax=1) #Just so the progress meter hits 100%
        pl.info("Metadata extraction complete!")

    del pl
    del ExcelWriter
    del ShapeWriter
def exit(): 
    '''Force exit after closure of the ProgressBar GUI'''
    os._exit(0)

#========================================================================================================
#Code below is for the GUI if run without arguments
#========================================================================================================
class Command:
    """ A class we can use to avoid using the tricky "Lambda" expression.
    "Python and Tkinter Programming" by John Grayson, introduces this idiom."""
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        apply(self.func, self.args, self.kwargs)
        

class GetArgs:
    '''Pop up a GUI dialog to gather arguments'''
    def __init__(self,gui,debug,nomd,getovs):
        '''Build and show the GUI dialog'''

        windowicon=os.environ['CURDIR']+'/lib/wm_icon.ico'
        #base 64 encoded gif images for the GUI buttons
        from icons import shp_img, dir_img, xls_img, log_img

        self.root = Tkinter.Tk()
        self.root.title('Metadata Crawler')
        try:self.root.wm_iconbitmap(windowicon)
        except:pass

        # Calculate the geometry to centre the app
        scrnWt = self.root.winfo_screenwidth()
        scrnHt = self.root.winfo_screenheight()
        appWt = self.root.winfo_width()
        appHt = self.root.winfo_height()
        appXPos = (scrnWt / 2) - (appWt / 2)
        appYPos = (scrnHt / 2) - (appHt / 2)
        self.root.geometry('+%d+%d' % (appXPos, appYPos))
        
        last_dir = Tkinter.StringVar()
        last_dir.set('C:\\')

        bdebug = Tkinter.BooleanVar()
        bdebug.set(debug)
        bgui = Tkinter.BooleanVar()
        bgui.set(gui)
        bovs = Tkinter.BooleanVar()
        bovs.set(getovs)
        bnomd = Tkinter.BooleanVar()
        bnomd.set(nomd)

        dir_ico = Tkinter.PhotoImage(format=dir_img.format,data=dir_img.data)
        xls_ico = Tkinter.PhotoImage(format=xls_img.format,data=xls_img.data)
        shp_ico = Tkinter.PhotoImage(format=shp_img.format,data=shp_img.data)
        log_ico = Tkinter.PhotoImage(format=log_img.format,data=log_img.data)

        sdir = Tkinter.StringVar()
        sxls = Tkinter.StringVar()
        sshp = Tkinter.StringVar()
        slog = Tkinter.StringVar()

        ldir=Tkinter.Label(self.root, text="Directory to search:")
        lxls=Tkinter.Label(self.root, text="Output spreadsheet:")
        lshp=Tkinter.Label(self.root, text="Output shapefile:")
        llog=Tkinter.Label(self.root, text="Output error log:")
        lovs=Tkinter.Label(self.root, text="Generate quicklook/thumbnail?:")
        lnomd=Tkinter.Label(self.root, text="Don't extract metadata (walk)?:")

        edir=Tkinter.Entry(self.root, textvariable=sdir)
        exls=Tkinter.Entry(self.root, textvariable=sxls)
        eshp=Tkinter.Entry(self.root, textvariable=sshp)
        elog=Tkinter.Entry(self.root, textvariable=slog)
        eovs=Tkinter.Checkbutton(self.root, variable=bovs)
        enomd=Tkinter.Checkbutton(self.root, variable=bnomd)

        bdir = Tkinter.Button(self.root,image=dir_ico, command=Command(self.cmdDir, sdir,last_dir))
        bxls = Tkinter.Button(self.root,image=xls_ico, command=Command(self.cmdFile,sxls,[('Excel Spreadsheet','*.xls')],last_dir))
        bshp = Tkinter.Button(self.root,image=shp_ico, command=Command(self.cmdFile,sshp,[('ESRI Shapefile','*.shp')],last_dir))
        blog = Tkinter.Button(self.root,image=log_ico, command=Command(self.cmdFile,slog,[('Log File',('*.txt','*.log'))],last_dir))

        ldir.grid(row=0, column=0,sticky=Tkinter.W)
        lxls.grid(row=1, column=0,sticky=Tkinter.W)
        lshp.grid(row=2, column=0,sticky=Tkinter.W)
        llog.grid(row=3, column=0,sticky=Tkinter.W)
        lovs.grid(row=4, column=0,sticky=Tkinter.W, columnspan=2)
        lnomd.grid(row=5, column=0,sticky=Tkinter.W, columnspan=2)

        edir.grid(row=0, column=1)
        exls.grid(row=1, column=1)
        eshp.grid(row=2, column=1)
        elog.grid(row=3, column=1)
        eovs.grid(row=4, column=1)
        enomd.grid(row=5, column=1)

        bdir.grid(row=0, column=2)
        bxls.grid(row=1, column=2)
        bshp.grid(row=2, column=2)
        blog.grid(row=3, column=2)

        bOK = Tkinter.Button(self.root,text="Ok", command=self.cmdOK)
        self.root.bind("<Return>", self.cmdOK)
        bOK.config(width=10)
        bCancel = Tkinter.Button(self.root,text="Cancel", command=self.cmdCancel)
        bOK.grid(row=6, column=1,sticky=Tkinter.E, padx=5,pady=5)
        bCancel.grid(row=6, column=2,sticky=Tkinter.E, pady=5)

        self.vars={'dir':sdir,'xls':sxls,'shp':sshp,'log':slog,'gui':bgui,'debug':bdebug,'getovs':bovs,'nomd':bnomd}
        
        self.root.mainloop()
        
    def cmdOK(self,*args,**kwargs):
        ok,kwargs=True,{}
        for var in self.vars:
            kwarg=self.vars[var].get()
            if kwarg=='':ok=False
            else:kwargs[var]=kwarg
        if ok:
            self.root.destroy()
            main(**kwargs)

    def cmdCancel(self):
        self.root.destroy()

    def cmdDir(self,var,dir):
        ad = tkFileDialog.askdirectory(parent=self.root,initialdir=dir.get(),title='Please select a directory to crawl for imagery')
        if ad:
            var.set(ad)
            dir.set(ad)

    def cmdFile(self,var,filter,dir,delete=False):
        fd = tkFileDialog.asksaveasfilename(parent=self.root,filetypes=filter,initialdir=dir.get(),title='Please select a file')
        if fd:
            var.set(fd)
            dir.set(os.path.split(fd)[0])
            if os.path.exists(fd) and delete:
                try:os.remove(fd)
                except:
                    tkMessageBox.showerror(parent=self.root, title='Error', message='Unable to delete %s' % fd)
                    var.set('')
#========================================================================================================
#Above is for the GUI if run without arguments
#========================================================================================================
if __name__ == '__main__':
    import optparse
    description='Run the metadata crawler'
    parser = optparse.OptionParser(description=description)
    parser.add_option('-d', dest="dir", metavar="dir",
                      help='The directory to start the metadata crawl')
    parser.add_option("-x", dest="xls", metavar="xls",
                      help="Excel spreadsheet to write metadata to")
    parser.add_option("-s", dest="shp", metavar="shp",
                      help="Shapefile to write extents to")
    parser.add_option("-l", dest="log", metavar="log",
                      help="Log file")
    parser.add_option("-o", action="store_true", dest="ovs",default=False,
                      help="Generate overview (quicklook/thumbnail) images")
    parser.add_option("--nomd", action="store_true", dest="nomd",default=False,
                      help="Extract metadata (crawl), if False just get basic file info (walk)")
    parser.add_option("--debug", action="store_true", dest="debug",default=False,
                      help="Turn debug output on")
    parser.add_option("--gui", action="store_true", dest="gui", default=False,
                      help="Show the GUI progress dialog")
    opts,args = parser.parse_args()
    if not opts.dir or not opts.log or not opts.shp or not opts.xls:
        GetArgs(True,opts.debug,opts.nomd,opts.ovs) #Show progress GUI.
        #GetArgs(opts.gui,opts.debug,opts.nomd,opts.ovs) #No progress GUI.
    else:
        main(opts.dir,opts.xls,opts.shp,opts.log,opts.gui,opts.debug,opts.nomd,opts.ovs)
