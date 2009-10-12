'''
Script to run the Metadata Crawler
==================================

Contains code to show GUI to gather input arguments when none are provided
To run, call the eponymous batch file which sets the required environment variables

Usage::
    runcrawler.bat -d dir -x xls -s shp -l log {-o} {--nomd} {--gui} {--debug}

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
from Tkinter import *
import tkFileDialog

import progresslogger
import formats
import geometry
import utilities
import crawler

def main(dir,xls,shp,log, gui=False, debug=False, nomd=False, getovs=False): 
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
    pl = progresslogger.ProgressLogger('Metadata Crawler',logfile=log, logToConsole=True, logToFile=True, logToGUI=gui, level=level, windowicon=windowicon)

    pl.debug('%s %s %s %s %s %s' % (dir,xls,shp,log,gui,debug))

    if os.path.exists(xls):
        try:
            os.remove(xls)
        except:
            pl.error('Unable to delete %s' % xls)
            del pl
            sys.exit(1)

    ExcelWriter=utilities.ExcelWriter(xls,format_fields.keys())
    ShapeWriter=geometry.ShapeWriter(shp,format_fields,overwrite=True)

    pl.info('Searching for files...')
    now=time.time()
    Crawler=crawler.Crawler(dir)
    pl.info('Found %s files...'%Crawler.filecount)
    #Loop thru dataset objects returned by Crawler
    for ds in Crawler:
        try:
            if not nomd:
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
        pl.info("Metadata extraction complete!")

    del pl
    del ExcelWriter
    del ShapeWriter

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
    def __init__(self,gui,debug,nomd,getovs):
        windowicon=os.environ['CURDIR']+'/lib/wm_icon.ico'
        #base 64 encoded gif images for the GUI buttons
        shp_img = '''
            R0lGODlhEAAQAMIFABAQEIBnII+HgLS0pfDwsC8gIC8gIC8gICH5BAEKAAcALAAAAAAQABAAAAND
            eLrcJzBKqcQIN+MtwAvTNHTPSJwoQAigxwpouo4urZ7364I4cM8kC0x20n2GRGEtJGl9NFBMkBny
            HHzYrNbB7XoXCQA7'''

        dir_img='''
            R0lGODlhEAAQAMZUABAQEB8QEB8YEC8gIC8vIEA4ME9IQF9IIFpTSWBXQHBfUFBoj3NlRoBnII9v
            IIBwUGB3kH93YIZ5UZ94IJB/YIqAcLB/EI+IcICHn4+HgMCHEI6Oe4CPn4+PgMCQANCHEJ+PgICX
            r9CQANCQEJ+XgJKanaCgkK+fgJykoaKjo7CgkKimk+CfIKKoo6uoleCgMLCnkNCnUKuwpLSvkrSv
            mfCoMLWyn7+wkM+vcLS0pfCwML+4kPC3QNDAgM+/kPDAQP+/UODIgP/IUODQoP/QUPDQgP/QYP/P
            cPDYgP/XYP/XcP/YgPDgkP/ggP/gkPDnoP/noPDwoPDwsP/woP//////////////////////////
            ////////////////////////////////////////////////////////////////////////////
            /////////////////////////////////////////////////////////////////////////yH5
            BAEKAH8ALAAAAAAQABAAAAe1gH+Cg4SFhoQyHBghKIeEECV/ORwtEDYwmJg0hikLCzBDUlJTUCoz
            hZ4LKlGjUFBKJiQkIB0XgypPpFBLSb2+toImT643N5gnJ7IgIBkXJExQQTBN1NVNSkoxFc9OMDtK
            vkZEQjwvDC4gSNJNR0lGRkI/PDoNEn8gRTA+Su9CQPM1PhxY8SdDj2nw4umowWJEAwSCLqjAIaKi
            Bw0WLExwcGBDRAoRHihIYKAAgQECAARwxFJQIAA7'''
        xls_img='''
            R0lGODlhEAAQAPcAAAAAAIAAAACAAICAAAAAgIAAgACAgICAgMDAwP8AAAD/AP//AAAA//8A/wD/
            /////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
            AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMwAAZgAAmQAAzAAA/wAzAAAzMwAzZgAzmQAzzAAz/wBm
            AABmMwBmZgBmmQBmzABm/wCZAACZMwCZZgCZmQCZzACZ/wDMAADMMwDMZgDMmQDMzADM/wD/AAD/
            MwD/ZgD/mQD/zAD//zMAADMAMzMAZjMAmTMAzDMA/zMzADMzMzMzZjMzmTMzzDMz/zNmADNmMzNm
            ZjNmmTNmzDNm/zOZADOZMzOZZjOZmTOZzDOZ/zPMADPMMzPMZjPMmTPMzDPM/zP/ADP/MzP/ZjP/
            mTP/zDP//2YAAGYAM2YAZmYAmWYAzGYA/2YzAGYzM2YzZmYzmWYzzGYz/2ZmAGZmM2ZmZmZmmWZm
            zGZm/2aZAGaZM2aZZmaZmWaZzGaZ/2bMAGbMM2bMZmbMmWbMzGbM/2b/AGb/M2b/Zmb/mWb/zGb/
            /5kAAJkAM5kAZpkAmZkAzJkA/5kzAJkzM5kzZpkzmZkzzJkz/5lmAJlmM5lmZplmmZlmzJlm/5mZ
            AJmZM5mZZpmZmZmZzJmZ/5nMAJnMM5nMZpnMmZnMzJnM/5n/AJn/M5n/Zpn/mZn/zJn//8wAAMwA
            M8wAZswAmcwAzMwA/8wzAMwzM8wzZswzmcwzzMwz/8xmAMxmM8xmZsxmmcxmzMxm/8yZAMyZM8yZ
            ZsyZmcyZzMyZ/8zMAMzMM8zMZszMmczMzMzM/8z/AMz/M8z/Zsz/mcz/zMz///8AAP8AM/8AZv8A
            mf8AzP8A//8zAP8zM/8zZv8zmf8zzP8z//9mAP9mM/9mZv9mmf9mzP9m//+ZAP+ZM/+ZZv+Zmf+Z
            zP+Z///MAP/MM//MZv/Mmf/MzP/M////AP//M///Zv//mf//zP///ywAAAAAEAAQAAAIngBfuUKF
            ipBBg4MS9umTJYsrBAheSZwokGBBhwgeaNzIUSOhLKgydhz5EdWrB4oOelT5kdDJLwgUKRpEKOUX
            Gtpannzw5ZVNQje15czicmNPg1lwCtW5EeirQV+IEtI2iOjOmh9dQc2SimqWQa4efGzYcGZUr4NQ
            ddSWimwWr33UahRKly61qn0Iza1rl9qXKVIPIkyY8Mtft4gTTwkIADs='''

        log_img='''
            R0lGODlhEAAQAIQQAG9s0oJ5eatyP6tycpePj6ulP6ulctWeOaulpdWentXSOcvHx9XS0v/MzP//
            zP///y8gIC8gIC8gIC8gIC8gIC8gIC8gIC8gIC8gIC8gIC8gIC8gIC8gIC8gIC8gIC8gICH5BAEK
            ABAALAAAAAAQABAAAAViICSOUNMwjEOOhyIUyhAbzMoAgJAQi9EjtRGAIXgUjw9CUDR8OJ9OJakJ
            fUqFjCSBZ11CqNWkt7ndLqLjbFg8zZa5bOw6znSfoVfm3clYIP5eEH4EAQFlCAsrEH2ICygoJCEA
            Ow=='''
        self.root = Tk()
        self.root.title('Metadata Crawler')
        self.root.wm_iconbitmap(windowicon)

        # Calculate the geometry to centre the app
        scrnWt = self.root.winfo_screenwidth()
        scrnHt = self.root.winfo_screenheight()
        appWt = self.root.winfo_width()
        appHt = self.root.winfo_height()
        appXPos = (scrnWt / 2) - (appWt / 2)
        appYPos = (scrnHt / 2) - (appHt / 2)
        self.root.geometry('+%d+%d' % (appXPos, appYPos))
        
        last_dir = StringVar()
        last_dir.set('C:\\')

        bdebug = BooleanVar()
        bdebug.set(debug)
        bgui = BooleanVar()
        bgui.set(gui)
        bovs = BooleanVar()
        bovs.set(getovs)
        bnomd = BooleanVar()
        bnomd.set(nomd)

        dir_ico = PhotoImage(format='gif',data=dir_img)
        xls_ico = PhotoImage(format='gif',data=xls_img)
        shp_ico = PhotoImage(format='gif',data=shp_img)
        log_ico = PhotoImage(format='gif',data=log_img)

        sdir = StringVar()
        sxls = StringVar()
        sshp = StringVar()
        slog = StringVar()

        ldir=Label(self.root, text="Directory to search:")
        lxls=Label(self.root, text="Output spreadsheet:")
        lshp=Label(self.root, text="Output shapefile:")
        llog=Label(self.root, text="Output error log:")
        lovs=Label(self.root, text="Generate quicklook/thumbnail?:")
        lnomd=Label(self.root, text="Don't extract metadata (walk)?:")

        edir=Entry(self.root, textvariable=sdir)
        exls=Entry(self.root, textvariable=sxls)
        eshp=Entry(self.root, textvariable=sshp)
        elog=Entry(self.root, textvariable=slog)
        eovs=Checkbutton(self.root, variable=bovs)
        enomd=Checkbutton(self.root, variable=bnomd)

        bdir = Button(self.root,image=dir_ico, command=Command(self.cmdDir, sdir,last_dir))
        bxls = Button(self.root,image=xls_ico, command=Command(self.cmdFile,sxls,[('Excel Spreadsheet','*.xls')],last_dir))
        bshp = Button(self.root,image=shp_ico, command=Command(self.cmdFile,sshp,[('ESRI Shapefile','*.shp')],last_dir))
        blog = Button(self.root,image=log_ico, command=Command(self.cmdFile,slog,[('Log File',('*.txt','*.log'))],last_dir))

        ldir.grid(row=0, column=0,sticky=W)
        lxls.grid(row=1, column=0,sticky=W)
        lshp.grid(row=2, column=0,sticky=W)
        llog.grid(row=3, column=0,sticky=W)
        lovs.grid(row=4, column=0,sticky=W, columnspan=2)
        lnomd.grid(row=5, column=0,sticky=W, columnspan=2)

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

        bOK = Button(self.root,text="Ok", command=self.cmdOK)
        self.root.bind("<Return>", self.cmdOK)
        bOK.config(width=10)
        bCancel = Button(self.root,text="Cancel", command=self.cmdCancel)
        bOK.grid(row=6, column=1,sticky=E, padx=5,pady=5)
        bCancel.grid(row=6, column=2,sticky=E, pady=5)

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

    def cmdFile(self,var,filter,dir):
        fd = tkFileDialog.asksaveasfilename(parent=self.root,filetypes=filter,initialdir=dir.get(),title='Please select a file')
        if fd:
            var.set(fd)
            dir.set(os.path.split(fd)[0])
            if os.path.exists(fd):
                try:os.remove(fd)
                except:
                    tkMessageBox.showerror(parent=self.root, title='Error', message='Unable to delete %s' % fd)
                    var.set('')
#========================================================================================================
#Above is for the GUI if run without arguments
#========================================================================================================
def StrToBool(val):
    if type(val) is str:
        if val =='True': return True
        if val =='False': return False
    else: return val
    
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
    else:
        main(opts.dir,opts.xls,opts.shp,opts.log,opts.gui,opts.debug,opts.nomd,opts.ovs)
