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
Module to generate a GUI dialog to collect arguments
'''
import os,sys,Tkinter,tkFileDialog
from icons import *

class GetArgs(object):
    ''' Build and show a GUI dialog to collect arguments
        @type  args:    C{U{Option<http://docs.python.org/library/optparse.html>}}
        @param args:    One or more U{Option<http://docs.python.org/library/optparse.html>}s.
        
        @return:  C{None}

        @note:  The GetArgs class requires at least one additional custom attribute to be
                added to the optparse.Option. The required attribute is the 'argtype' to use,
                either L{DirArg}, L{FileArg} or L{BoolArg}.  L{DirArg} and L{FileArg} also require
                additional custom attributes.

                L{DirArg}, L{FileArg} or L{BoolArg} also accept an optional 'tooltip' custom attribute.

                Example::
                        parser = optparse.OptionParser(description=description)
                        opt=parser.add_option('-d', dest="dir", metavar="dir",help='The directory to crawl')
                        opt.icon=icons.dir_img      #Custom icon and argtype attributes
                        opt.argtype=getargs.DirArg
                        
                        opt=parser.add_option("-u", "--update", action="store_true", dest="update",default=False,
                                          help="Update existing spreadsheet")
                        opt.argtype=getargs.BoolArg #Custom argtype attribute
                        opt.tooltip='This is a tool tip!'
                        
                        opt=parser.add_option("-l", dest="log", metavar="log",help="Log file")
                        opt.argtype=getargs.FileArg #Custom argtype, icon and filter attributes
                        opt.icon=icons.log_img
                        opt.filter=[('Log File',('*.txt','*.log'))]

                        #Parse existing command line args
                        optvals,argvals = parser.parse_args()
                        #Pop up the GUI
                        args=getargs.GetArgs(*parser.option_list)

            @see: L{runcrawler} for a more complete example.                  
    '''
    def __new__(self,*args):
        self=object.__new__(self)
        title='MetaGETA'
        icon=os.environ['CURDIR']+'/lib/wm_icon.ico'
        windowicon=icon

        self._root = Tkinter.Tk()
        self._root.title(title)
        try:self._root.wm_iconbitmap(windowicon)
        except:pass

        # Calculate the geometry to centre the app
        scrnWt = self._root.winfo_screenwidth()
        scrnHt = self._root.winfo_screenheight()
        appWt = self._root.winfo_width()
        appHt = self._root.winfo_height()
        appXPos = (scrnWt / 2) - (appWt / 2)
        appYPos = (scrnHt / 2) - (appHt / 2)
        self._root.geometry('+%d+%d' % (appXPos, appYPos))
        
        self._lastdir = Tkinter.StringVar()
        self._lastdir.set('')

        self._args={}
        self._objs={}
        for i,arg in enumerate(args):
            if 'argtype' in vars(arg):
                argtype=arg.argtype
                argname=arg.dest
                arg.lastdir=self._lastdir
                self._objs[argname]=argtype(self._root,i, arg)
                self._args[argname]=self._objs[argname].value

        nargs=len(self._args)
        self._root.bind("<Return>", self._cmdok)
        TkFrame=Tkinter.Frame(self._root)
        TkFrame.grid(row=nargs,columnspan=3,sticky=Tkinter.E)
        bOK = Tkinter.Button(TkFrame,text="Ok", command=self._cmdok)
        bOK.config(width=8)
        bOK.grid(row=0, column=1,sticky=Tkinter.E, padx=5,pady=5)
        bCancel = Tkinter.Button(TkFrame,text="Cancel", command=self._cmdcancel)
        bCancel.config(width=8)
        bCancel.grid(row=0, column=2,sticky=Tkinter.E, padx=5,pady=5)
        self._cancelled = False

        self._root.mainloop()
        if self._cancelled:return None
        else:return self

    def _cmdok(self,*args,**kwargs):
        ok=True
        for arg in self._args:
            try:vars(self)[arg]=self._args[arg].get()
            except:pass            
            if vars(self)[arg]=='':
                ok=False
                break
        if ok:
            self._root.destroy()

    def _cmdcancel(self):
        self._root.destroy()
        self._cancelled =True

class DirArg(object):
    ''' Build a directory browser 

        @type  root: C{Tkinter.Tk}
        @param root: Root Tk instance.
        @type  row:  C{int}
        @param row:  Grid row to place the directory browser in.
        @type  arg:  C{U{Option<http://docs.python.org/library/optparse.html>}}
        @param arg:  An U{Option<http://docs.python.org/library/optparse.html>}.
        
        @note:  The DirArg class requires an additional custom attribute to be
                added to the optparse.Option. This is the L{icon<icons>} to display on the button.

                Example::
                        parser = optparse.OptionParser(description=description)
                        opt=parser.add_option('-d', dest="dir", metavar="dir",help='The directory to crawl')
                        opt.argtype=getargs.DirArg
                        opt.icon=icons.dir_img
    '''
    def __init__(self,root,row,arg):
        self.TkPhotoImage = Tkinter.PhotoImage(format=arg.icon.format,data=arg.icon.data) # keep a reference! See http://effbot.org/tkinterbook/photoimage.htm
        self.value = Tkinter.StringVar()
        if arg.default is not None:self.value.set(arg.default)
        TkLabel=Tkinter.Label(root, text=arg.help+':')
        TkEntry=Tkinter.Entry(root, textvariable=self.value)
        TkButton = Tkinter.Button(root,image=self.TkPhotoImage, command=_Command(self.cmd,root,arg.help,arg.lastdir,self.value))
        TkLabel.grid(row=row, column=0,sticky=Tkinter.W, padx=2)
        TkEntry.grid(row=row, column=1,sticky=Tkinter.E+Tkinter.W, padx=2)
        TkButton.grid(row=row, column=2,sticky=Tkinter.E, padx=2)
        if 'tooltip' in vars(arg):
            TkLabelToolTip=_ToolTip(TkLabel, delay=250, follow_mouse=1, text=arg.tooltip)
            TkEntryToolTip=_ToolTip(TkEntry, delay=250, follow_mouse=1, text=arg.tooltip)
            TkButtonToolTip=_ToolTip(TkButton, delay=250, follow_mouse=1, text=arg.tooltip)
        
    def cmd(self,root,label,dir,var):
        ad = tkFileDialog.askdirectory(parent=root,initialdir=dir.get(),title=label)
        if ad:
            ad=os.path.normpath(ad)
            var.set(ad)
            dir.set(ad)
            
class FileArg(object):
    ''' Build a file browser 

        @type  root: C{Tkinter.Tk}
        @param root: Root Tk instance.
        @type  row:  C{int}
        @param row:  Grid row to place the file browser in.
        @type  arg:  C{U{Option<http://docs.python.org/library/optparse.html>}}
        @param arg:  An U{Option<http://docs.python.org/library/optparse.html>}.
        
        @note:  The FileArg class requires two additional custom attributes to be
                added to the optparse.Option. These are the L{icon<icons>} to display on the button
                and filter in U{tkFileDialog.askopenfilename<http://tkinter.unpythonic.net/wiki/tkFileDialog>}
                filetypes format.

                Example::
                    opt=parser.add_option("-l", dest="log", metavar="log",help="Log file")
                    opt.argtype=getargs.FileArg
                    opt.icon=icons.log_img
                    opt.filter=[('Log File',('*.txt','*.log'))]
    '''
    def __init__(self,root,row,arg):
        self.TkPhotoImage = Tkinter.PhotoImage(format=arg.icon.format,data=arg.icon.data) # keep a reference! See http://effbot.org/tkinterbook/photoimage.htm
        self.value = Tkinter.StringVar()
        if arg.default is not None:self.value.set(arg.default)
        TkLabel=Tkinter.Label(root, text=arg.help+':')
        TkEntry=Tkinter.Entry(root, textvariable=self.value)
        TkButton = Tkinter.Button(root,image=self.TkPhotoImage,command=_Command(self.cmd,root,arg.help,arg.filter,arg.lastdir,self.value))
        TkLabel.grid(row=row, column=0,sticky=Tkinter.W, padx=2)
        TkEntry.grid(row=row, column=1,sticky=Tkinter.E+Tkinter.W, padx=2)
        TkButton.grid(row=row, column=2,sticky=Tkinter.E, padx=2)
        if 'tooltip' in vars(arg):
            TkLabelToolTip=_ToolTip(TkLabel, delay=250, follow_mouse=1, text=arg.tooltip)
            TkEntryToolTip=_ToolTip(TkEntry, delay=250, follow_mouse=1, text=arg.tooltip)
            TkButtonToolTip=_ToolTip(TkButton, delay=250, follow_mouse=1, text=arg.tooltip)
        
    def cmd(self,root,label,filter,dir,var):
        if sys.platform[0:3].lower()=='win':
            ##Win32 GUI hack to avoid "<somefile> exists. Do you want to replace it?"
            ##when using tkFileDialog.asksaveasfilename
            import win32gui
            #Convert filter from [('Python Scripts',('*.py','*.pyw')),('Text files','*.txt')] format
            #to 'Python Scripts\0*.py;*.pyw\0Text files\0*.txt\0' format
            winfilter=''
            for desc,ext in filter:
                if type(ext) in [list,tuple]:ext=';'.join(ext)
                winfilter+='%s (%s)\0%s\0'%(desc,ext,ext)
            try:
                fd, filter, flags=win32gui.GetSaveFileNameW(
                    InitialDir=dir.get(),
                    Title='Please select a file',
                    Filter=winfilter)
            except:fd=None
        else:
            fd = tkFileDialog.asksaveasfilename(parent=root,filetypes=filter,initialdir=dir.get(),title=label)
        if fd:
            fd=os.path.normpath(fd)
            var.set(fd)
            dir.set(os.path.split(fd)[0])

class DropListArg(object):
    ''' Build a droplist 

        @type  root: C{Tkinter.Tk}
        @param root: Root Tk instance.
        @type  row:  C{int}
        @param row:  Grid row to place the file browser in.
        @type  arg:  C{U{Option<http://docs.python.org/library/optparse.html>}}
        @param arg:  An U{Option<http://docs.python.org/library/optparse.html>}.
        
        @note:  The DropListArg class requires two additional custom attributes to be
                added to the optparse.Option. These are the L{icon<icons>} to display on the button
                and options to populate the droplist with.

                Example::
                    opt=parser.add_option("-z", dest="somevar", metavar="somevar",help="Some value")
                    opt.argtype=getargs.DropListArg
                    opt.icon=icons.some_img
                    opt.options=['Some value','Another value']
    '''
    def __init__(self,root,row,arg):
        self.TkPhotoImage = Tkinter.PhotoImage(format=arg.icon.format,data=arg.icon.data) # keep a reference! See http://effbot.org/tkinterbook/photoimage.htm
        self.value = Tkinter.StringVar()
        if arg.default is not None:self.value.set(arg.default)
        TkLabel=Tkinter.Label(root, text=arg.help+':')
        width=20
        TkDropList=_DropList(root,arg.options, textvariable=self.value,width=width)
        TkImage = Tkinter.Label(root,image=self.TkPhotoImage)
        TkLabel.grid(row=row, column=0,sticky=Tkinter.W, padx=2)
        TkDropList.grid(row=row, column=1,sticky=Tkinter.E+Tkinter.W, padx=2)
        TkImage.grid(row=row, column=2,sticky=Tkinter.E, padx=2)
        if 'tooltip' in vars(arg):
            TkLabelToolTip=_ToolTip(TkLabel, delay=250, follow_mouse=1, text=arg.tooltip)
            TkDropListToolTip=_ToolTip(TkDropList, delay=250, follow_mouse=1, text=arg.tooltip)
            TkImageToolTip=_ToolTip(TkImage, delay=250, follow_mouse=1, text=arg.tooltip)

        
class BoolArg(object):
    ''' Build a boolean checkbox 

        @type  root: C{Tkinter.Tk}
        @param root: Root Tk instance.
        @type  row:  C{int}
        @param row:  Grid row to place the checkbox in.
        @type  arg:  C{U{Option<http://docs.python.org/library/optparse.html>}}
        @param arg:  An U{Option<http://docs.python.org/library/optparse.html>}.
    '''
    def __init__(self,root,row,arg):
        self.value = Tkinter.BooleanVar()
        self.value.set(arg.default)
        TkLabel=Tkinter.Label(root, text=arg.help+':')
        TkCheckbutton=Tkinter.Checkbutton(root, variable=self.value)
        TkLabel.grid(row=row, column=0,sticky=Tkinter.W)
        TkCheckbutton.grid(row=row, column=1,sticky=Tkinter.W)
        if 'tooltip' in vars(arg):
            TkLabelToolTip=_ToolTip(TkLabel, delay=250, follow_mouse=1, text=arg.tooltip)
            TkCheckbuttonToolTip=_ToolTip(TkCheckbutton, delay=250, follow_mouse=1, text=arg.tooltip)

class _Command(object):
    """ A class we can use to avoid using the tricky "Lambda" expression.
    "Python and Tkinter Programming" by John Grayson, introduces this idiom."""
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        apply(self.func, self.args, self.kwargs)
        

class _ToolTip:
    '''
    From http://tkinter.unpythonic.net/wiki/ToolTip
    Michael Lange <klappnase at 8ung dot at>
    The ToolTip class provides a flexible tooltip widget for Tkinter; it is based on IDLE's ToolTip
    module which unfortunately seems to be broken (at least the version I saw).
    INITIALIZATION OPTIONS:
    anchor :        where the text should be positioned inside the widget, must be on of "n", "s", "e", "w", "nw" and so on;
                    default is "center"
    bd :            borderwidth of the widget; default is 1 (NOTE: don't use "borderwidth" here)
    bg :            background color to use for the widget; default is "lightyellow" (NOTE: don't use "background")
    delay :         time in ms that it takes for the widget to appear on the screen when the mouse pointer has
                    entered the parent widget; default is 1500
    fg :            foreground (i.e. text) color to use; default is "black" (NOTE: don't use "foreground")
    follow_mouse :  if set to 1 the tooltip will follow the mouse pointer instead of being displayed
                    outside of the parent widget; this may be useful if you want to use tooltips for
                    large widgets like listboxes or canvases; default is 0
    font :          font to use for the widget; default is system specific
    justify :       how multiple lines of text will be aligned, must be "left", "right" or "center"; default is "left"
    padx :          extra space added to the left and right within the widget; default is 4
    pady :          extra space above and below the text; default is 2
    relief :        one of "flat", "ridge", "groove", "raised", "sunken" or "solid"; default is "solid"
    state :         must be "normal" or "disabled"; if set to "disabled" the tooltip will not appear; default is "normal"
    text :          the text that is displayed inside the widget
    textvariable :  if set to an instance of Tkinter.StringVar() the variable's value will be used as text for the widget
    width :         width of the widget; the default is 0, which means that "wraplength" will be used to limit the widgets width
    wraplength :    limits the number of characters in each line; default is 150

    WIDGET METHODS:
    configure(**opts) : change one or more of the widget's options as described above; the changes will take effect the
                        next time the tooltip shows up; NOTE: follow_mouse cannot be changed after widget initialization

    Other widget methods that might be useful if you want to subclass ToolTip:
    enter() :           callback when the mouse pointer enters the parent widget
    leave() :           called when the mouse pointer leaves the parent widget
    motion() :          is called when the mouse pointer moves inside the parent widget if follow_mouse is set to 1 and the
                        tooltip has shown up to continually update the coordinates of the tooltip window
    coords() :          calculates the screen coordinates of the tooltip window
    create_contents() : creates the contents of the tooltip window (by default a Tkinter.Label)
    '''
    # Ideas gleaned from PySol
    def __init__(self, master, text='Your text here', delay=1500, **opts):
        self.master = master
        self._opts = {'anchor':'center', 'bd':1, 'bg':'lightyellow', 'delay':delay, 'fg':'black',\
                      'follow_mouse':0, 'font':None, 'justify':'left', 'padx':4, 'pady':2,\
                      'relief':'solid', 'state':'normal', 'text':text, 'textvariable':None,\
                      'width':0, 'wraplength':150}
        self.configure(**opts)
        self._tipwindow = None
        self._id = None
        self._id1 = self.master.bind("<Enter>", self.enter, '+')
        self._id2 = self.master.bind("<Leave>", self.leave, '+')
        self._id3 = self.master.bind("<ButtonPress>", self.leave, '+')
        self._follow_mouse = 0
        if self._opts['follow_mouse']:
            self._id4 = self.master.bind("<Motion>", self.motion, '+')
            self._follow_mouse = 1

    def configure(self, **opts):
        for key in opts:
            if self._opts.has_key(key):
                self._opts[key] = opts[key]
            else:
                KeyError = 'KeyError: Unknown option: "%s"' %key
                raise KeyError

    ##----these methods handle the callbacks on "<Enter>", "<Leave>" and "<Motion>"---------------##
    ##----events on the parent widget; override them if you want to change the widget's behavior--##

    def enter(self, event=None):
        self._schedule()

    def leave(self, event=None):
        self._unschedule()
        self._hide()

    def motion(self, event=None):
        if self._tipwindow and self._follow_mouse:
            x, y = self.coords()
            self._tipwindow.wm_geometry("+%d+%d" % (x, y))

    ##------the methods that do the work:---------------------------------------------------------##

    def _schedule(self):
        self._unschedule()
        if self._opts['state'] == 'disabled':
            return
        self._id = self.master.after(self._opts['delay'], self._show)

    def _unschedule(self):
        id = self._id
        self._id = None
        if id:
            self.master.after_cancel(id)

    def _show(self):
        if self._opts['state'] == 'disabled':
            self._unschedule()
            return
        if not self._tipwindow:
            self._tipwindow = tw = Tkinter.Toplevel(self.master)
            # hide the window until we know the geometry
            tw.withdraw()
            tw.wm_overrideredirect(1)

            if tw.tk.call("tk", "windowingsystem") == 'aqua':
                tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "none")

            self.create_contents()
            tw.update_idletasks()
            x, y = self.coords()
            tw.wm_geometry("+%d+%d" % (x, y))
            tw.deiconify()

    def _hide(self):
        tw = self._tipwindow
        self._tipwindow = None
        if tw:
            tw.destroy()

    ##----these methods might be overridden in derived classes:----------------------------------##

    def coords(self):
        # The tip window must be completely outside the master widget;
        # otherwise when the mouse enters the tip window we get
        # a leave event and it disappears, and then we get an enter
        # event and it reappears, and so on forever :-(
        # or we take care that the mouse pointer is always outside the tipwindow :-)
        tw = self._tipwindow
        twx, twy = tw.winfo_reqwidth(), tw.winfo_reqheight()
        w, h = tw.winfo_screenwidth(), tw.winfo_screenheight()
        # calculate the y coordinate:
        if self._follow_mouse:
            y = tw.winfo_pointery() + 20
            # make sure the tipwindow is never outside the screen:
            if y + twy > h:
                y = y - twy - 30
        else:
            y = self.master.winfo_rooty() + self.master.winfo_height() + 3
            if y + twy > h:
                y = self.master.winfo_rooty() - twy - 3
        # we can use the same x coord in both cases:
        x = tw.winfo_pointerx() - twx / 2
        if x < 0:
            x = 0
        elif x + twx > w:
            x = w - twx
        return x, y

    def create_contents(self):
        opts = self._opts.copy()
        for opt in ('delay', 'follow_mouse', 'state'):
            del opts[opt]
        label = Tkinter.Label(self._tipwindow, **opts)
        label.pack()
        
class _DropList(Tkinter.Frame):
    '''
    A Tkinter DropList menu
    Derived from http://effbot.org/tkinterbook/menu.htm
    '''
    def __init__(self, root, options, textvariable, *args,**kwargs):
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
        textvariable.set(options[0]) # default value
        Tkinter.Frame.__init__(self,root,relief="sunken", bd=2,background='white',width=fwidth)
        self._lt=Tkinter.Label(self,textvariable=textvariable, bd=0,relief="sunken",activebackground='white',background='white',width=ltwidth)
        self._lb=Tkinter.Label(self,text=arrow,relief="raised", bd=2)
        self._m=Tkinter.Menu(self, tearoff=0,background='white')
        for o in options:
            self._m.add_command(label=o.center(ltwidth), command=_Command(textvariable.set,o))
        # attach popup to canvas
        self._lt.bind("<Button-1>", self._popup)
        self._lt.grid(row=0, column=0)
        self._lb.bind("<Button-1>", self._popup)
        self._lb.grid(row=0, column=1)
        self.pack()
    def _popup(self,event):
        self._m.post(self._lt.winfo_rootx(), self._lt.winfo_rooty())

if __name__ == '__main__':
    import optparse,icons,getargs
    reload(getargs)
    description='Run the getargs test'
    parser = optparse.OptionParser(description=description)

    opt=parser.add_option('-d', dest="dir", metavar="dir",help='A directory')
    opt.icon=icons.dir_img
    opt.argtype=getargs.DirArg
    
    opt=parser.add_option("-f", dest="f", metavar="f",help="A file")
    opt.argtype=getargs.FileArg
    opt.icon=icons.log_img
    opt.filter=[('Log File',('*.txt','*.log'))]

    opt=parser.add_option("-n", action="store_true", dest="no",default=False,
                      help="A boolean arg")
    opt.argtype=getargs.BoolArg

    opt=parser.add_option('-l', dest="lst", metavar="lst",help='A list')
    opt.icon=icons.xsl_img
    opt.options=['aaaa','bbbb','cccc','dddd']
    opt.argtype=getargs.DropListArg
    opt.tooltip='Tooltip!'
    
    optvals,argvals = parser.parse_args()
    for opt in parser.option_list:
        if 'argtype' in vars(opt):
            opt.default=vars(optvals)[opt.dest]
    args=getargs.GetArgs(*[opt for opt in parser.option_list if 'argtype' in vars(opt)])