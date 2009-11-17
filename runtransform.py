'''
Script to run the Metadata Transforms
=====================================
Contains code to show GUI to gather input arguments when none are provided
To run, call the eponymous batch file which sets the required environment variables

Usage::
    runtransform.bat -x xls -t xsl -d dir
    
@newfield sysarg: Argument, Arguments
@sysarg: C{-x xls}: MS Excel spreadsheet to read from
@sysarg: C{-t xsl}: XSL transform - may be one of the pre-defined XSL transforms or a path to a custom XSL file.
@sysarg: C{-d dir}: Directory to write XML files to.

@todo: Set up logging & debug properly. Enable selecting if MEF is created regardless of whether overviews exist
'''

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

#Imports
import os,sys,glob

#Set up the splash screen. Importing the FT.Xml module takes forever...
#Commented out as it's conflicting with the GetArgs GUI and needs to be sorted out - low priority...
#from splashscreen import SplashScreen,CallBack
#startup=CallBack()
#if len(sys.argv) == 1:SplashScreen(callback=startup.check)

from Tkinter import *
import tkFileDialog

from Ft.Xml import Domlette as Dom
import utilities
import transforms
import progresslogger
reload(transforms)
#Turn off the splashscreen
#startup.value=True

def main(xls,xsl,dir,mef=False,log=None,debug=False,gui=False):
    if debug:level=progresslogger.DEBUG
    else:level=progresslogger.INFO
    #pl = progresslogger.ProgressLogger('Metadata Crawler',logfile=log, logToConsole=True, logToFile=True, logToGUI=gui, level=level, windowicon=windowicon)
    pl = progresslogger.ProgressLogger('Metadata Transforms', logToConsole=True, logToFile=False, logToGUI=False, level=level)

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
#Below is for the GUI if run without arguments
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
        

class DropList(Widget):
    def __init__(self, root, options, stringvar, cnf={},**kwargs):
        self.root=root
        self.tk=root
        arrow=u'\u25bc'
        lbwidth=len(arrow)+2
        if kwargs.has_key('width'):
            fwidth=kwargs['width']
            ltwidth=fwidth-lbwidth
            self.width=fwidth
        else:
            ltwidth=max([len(o) for o in options])+4
            fwidth=ltwidth+lbwidth
            self.width=fwidth

        stringvar.set(options[0]) # default value

        self.frame=Frame(root,relief="sunken", bd=2,background='white')#,width=fwidth)
        self._lt=Label(self.frame,textvariable=stringvar, bd=0,relief="sunken",activebackground='white',background='white',width=ltwidth)
        self._lb=Label(self.frame,text=arrow,relief="raised", bd=2)
        self._m=Menu(root, tearoff=0,background='white')

        for o in options:
            self._m.add_command(label=o, command=Command(stringvar.set,o))

        # attach popup to canvas
        self._lt.bind("<Button-1>", self._popup)
        self._lt.grid(row=0, column=0)
        self._lb.bind("<Button-1>", self._popup)
        self._lb.grid(row=0, column=1)
        self.frame.pack()
    def _popup(self,event):
        self._m.post(self._lt.winfo_rootx(), self._lt.winfo_rooty())
    def pack(self, *args, **kw):
        self.frame.pack(*args, **kw)
    def grid(self, *args, **kw):
        self.frame.grid(*args, **kw)

class GetArgs:
    def __init__(self):

        windowicon=os.environ['CURDIR']+'/lib/wm_icon.ico'

        #base 64 encoded gif images for the GUI buttons
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

        xsl_img='''
            R0lGODdhEAAQAOMPAAAAAAAAgAAAmQAA/zNmmQCAgDNm/zOZAIaGhjOZ/zPM/8DAwKbK8DP///Hx
            8f///ywBAAAADwAQAAAEWBDJSeW76Or9Vn4f5zzOAp5kOo5AC2QOMxaFQcrP+zDCUzyNROAhkL14
            pEJDcQiMijqkIXEYDIsOXWwU6N5Yn5VKpSWYz2fwRcwmldFo9bidhc3Hrrw+HwEAOw=='''
        
        self.root = Tk()
        self.root.title('Metadata Transform')
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

        xls_ico = PhotoImage(format='gif',data=xls_img)
        xsl_ico = PhotoImage(format='gif',data=xsl_img)
        dir_ico = PhotoImage(format='gif',data=dir_img)

        sxls = StringVar()
        sxsl = StringVar()
        sdir = StringVar()
        smef = IntVar()

        lxls=Label(self.root, text="Input spreadsheet:")
        lxsl=Label(self.root, text="XSL Stylesheet:")
        ldir=Label(self.root, text="Output directory:")
        lmef=Label(self.root, text="Create MEF:")

        self.transforms=transforms.transforms.keys()

        # exls=Entry(self.root, textvariable=sxls)
        # exsl=DropList(self.root,options,sxsl)
        # edir=Entry(self.root, textvariable=sdir)
        exsl=DropList(self.root,self.transforms,sxsl)
        exls=Entry(self.root, textvariable=sxls, width=exsl.width)
        edir=Entry(self.root, textvariable=sdir, width=exsl.width)
        emef=Checkbutton(self.root, variable=smef, text="",onvalue=True, offvalue=False)

        bxls = Button(self.root,image=xls_ico, command=Command(self.cmdFile,sxls,[('Excel Spreadsheet','*.xls')],last_dir))
        bxsl = Label(self.root,image=xsl_ico)
        bdir = Button(self.root,image=dir_ico, command=Command(self.cmdDir, sdir,last_dir))

        lxls.grid(row=0, column=0, sticky=W)
        lxsl.grid(row=1, column=0, sticky=W)
        ldir.grid(row=2, column=0, sticky=W)
        #lmef.grid(row=3, column=0, sticky=W)

        exls.grid(row=0, column=1, sticky=W)
        exsl.grid(row=1, column=1, sticky=W)
        edir.grid(row=2, column=1, sticky=W)

        #emef.grid(row=3, column=1, sticky=W)

        bxls.grid(row=0, column=2, sticky=E)
        bxsl.grid(row=1, column=2, sticky=E)
        bdir.grid(row=2, column=2, sticky=E)

        bOK = Button(self.root,text="Ok", command=self.cmdOK)
        self.root.bind("<Return>", self.cmdOK)
        bOK.config(width=10)
        bCancel = Button(self.root,text="Cancel", command=self.cmdCancel)
        bOK.grid(row=4, column=1,sticky=E, padx=5,pady=5)
        bCancel.grid(row=4, column=2,sticky=E, pady=5)

        scrnWt = self.root.winfo_screenwidth()
        scrnHt = self.root.winfo_screenheight()

        imgWt = self.root.winfo_width()
        imgHt = self.root.winfo_height()

        imgXPos = (scrnWt / 2.0) - (imgWt / 2.0)
        imgYPos = (scrnHt / 2.0) - (imgHt / 2.0)

        #self.root.overrideredirect(1)
        self.root.geometry('+%d+%d' % (imgXPos, imgYPos))
        
        self.vars={'dir':sdir,'xls':sxls,'xsl':sxsl,'mef':smef}

       #self.root.update()
        self.root.mainloop()
        
    def cmdOK(self):
        ok,args=True,{}
        for var in self.vars:
            arg=self.vars[var].get()
            if arg=='':ok=False
            else:args[var]=arg
        if ok:
            self.root.destroy()
            main(**args)

    def cmdCancel(self):
        self.root.destroy()

    def cmdDir(self,var,dir):
        ad = tkFileDialog.askdirectory(parent=self.root,initialdir=dir.get(),title='Please select a directory to output metadata to')
        if ad:
            var.set(ad)
            dir.set(ad)

    def cmdFile(self,var,filter,dir):
        fd = tkFileDialog.askopenfilename(parent=self.root,filetypes=filter,initialdir=dir.get(),title='Please select a file')
        if fd:
            var.set(fd)
            dir.set(os.path.split(fd)[0])
#========================================================================================================
#Above is for the GUI if run without arguments
#========================================================================================================

if __name__ == '__main__':
    #To ensure uri's work...
    if os.path.basename(sys.argv[0])!=sys.argv[0]:os.chdir(os.path.dirname(sys.argv[0]))

    import optparse
    description='Transform metadata to XML'
    parser = optparse.OptionParser(description=description)
    parser.add_option('-d', dest="dir", metavar="dir",
                      help='The directory to output metadata XML to')
    parser.add_option("-x", dest="xls", metavar="xls",
                      help="Excel spreadsheet to read metadata from")
    parser.add_option("-t", dest="xsl", metavar="xsl",
                      help="XSL transform {*.xsl|%s}" % '|'.join(['"%s"'%s for s in transforms.transforms.keys()]))
                      #help="XSL transform {*.xsl|%s}" % '|'.join(['"%s"'%s for s in transforms.xslfiles.values()]))
    parser.add_option("-m", action="store_true", dest="mef",default=False,   
                      help="Create Metadata Exchange Format (MEF) file")
    parser.add_option("--debug", action="store_true", dest="debug",default=False,   
                      help="Turn debug output on")
    parser.add_option("-l", dest="log", metavar="log",                            
                      help=optparse.SUPPRESS_HELP) #help="Log file")                     #Not yet implemented
    parser.add_option("--gui", action="store_true", dest="gui", default=False,
                      help=optparse.SUPPRESS_HELP) #help="Show the GUI progress dialog") #Not yet implemented
    opts,args = parser.parse_args()
    if not opts.dir or not opts.xls or not opts.xsl:
        GetArgs()
    else:
        if opts.xsl in transforms.xslfiles.values():pass
        main(opts.xls,opts.xsl,opts.dir,opts.log,opts.gui,opts.debug)
