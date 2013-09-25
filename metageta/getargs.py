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
Module to generate a GUI dialog to collect arguments
'''
import os,sys
from metageta import utilities

try:
    import Tix,tkFileDialog,tkMessageBox
except ImportError:
    import warnings
    warnings.warn('Unable to import Tix, tkFileDialog and/or tkMessageBox')

class GetArgs(object):
    def __new__(self,*args,**kwargs):#We use __new__ instead of __init__ so we can return None if the user clicks cancel
        ''' Build and show a GUI dialog to collect arguments
            @type  args:        C{list of L{Arg}s}
            @param args:        One or more C{L{Arg}s}.
            @type    title:     C{str}
            @keyword title:     Window title.
            @type    icon:      C{L{icons}}
            @keyword icon:      An icon class from the L{icons} module.
            @type    callback:  C{U{callable<http://docs.python.org/library/functions.html#callable>} object}
            @keyword callback:  A function/class that is called when the OK button is clicked.
                                No positional/keyword arguments are supported (unless the L{Command} class is used).

            @rtype:  C{GetArgs}
            @return:  C{GetArgs}

            @see: L{runcrawler} for an example.
        '''
        try:import Tix
        except:return None

        self=object.__new__(self)

        title=kwargs.get('title','Arguments')
        icon=kwargs.get('icon',None)

        self._root = Tix.Tk()
        self._root.withdraw()
        self._root.title(title)

        if icon is not None:
            self.icon=Tix.PhotoImage(data=icon.data,format=icon.format)
            self._root.tk.call('wm', 'iconphoto', self._root._w, self.icon)

        #On Ok callback
        self._callback=lambda *a,**kw:True #default
        self.callback=kwargs.get('callback',self._callback)

        # Calculate the geometry to centre the app
        scrnWt = self._root.winfo_screenwidth()
        scrnHt = self._root.winfo_screenheight()
        appWt = self._root.winfo_width()
        appHt = self._root.winfo_height()
        appXPos = (scrnWt / 2) - (appWt / 2)
        appYPos = (scrnHt / 2) - (appHt / 2)
        self._root.geometry('+%d+%d' % (appXPos, appYPos))
        initialdir=''
        self._lastdir = Tix.StringVar(self._root,initialdir)

        self._args={}
        self._objs={}
        for i,arg in enumerate(args):
            argname=arg.opt.dest
            if 'initialdir' in vars(arg) and not arg.initialdir:
                arg.lastdir=self._lastdir
            arg.__build__(self._root,i)
            self._args[argname]=arg

        nargs=len(self._args)
        self._root.bind("<Return>", self._cmdok)
        self._root.protocol("WM_DELETE_WINDOW", self._cmdcancel)
        TkFrame=Tix.Frame(self._root)
        TkFrame.grid(row=nargs,columnspan=3,sticky=Tix.E)
        bOK = Tix.Button(TkFrame,text="Ok", command=self._cmdok)
        bOK.config(width=8)
        bOK.grid(row=0, column=1,sticky=Tix.E, padx=5,pady=5)
        bCancel = Tix.Button(TkFrame,text="Cancel", command=self._cmdcancel)
        bCancel.config(width=8)
        bCancel.grid(row=0, column=2,sticky=Tix.E, padx=5,pady=5)

        self._cancelled = False

        self._root.deiconify()
        self._root.mainloop()
        if self._cancelled:return None
        else:return self

    def _cmdok(self,*args,**kwargs):
        for arg in self._args:
            #try:vars(self)[arg]=self._args[arg].value.get()
            try:vars(self)[arg]=self._args[arg].value
            except:pass
            #Every required arg (except disabled ones) must have a value
            if vars(self)[arg]=='' and self._args[arg].enabled and self._args[arg].required:
                return None
            self._args[arg].opt.default=vars(self)[arg]
        ok=self.callback()
        if ok:
            self._root.destroy()

    def _cmdcancel(self):
        self._root.destroy()
        self._cancelled =True

    def __classproperty__(fcn):
        '''The class property decorator function'''
        try:return property( **fcn() )
        except:pass

    @__classproperty__
    def callback():
        '''The callback property.'''

        def fget(self):
            return self._callback

        def fset(self,arg):
            if callable(arg):
                self._callback=arg
            else:
                raise AttributeError, 'Callback object is not callable.'

        def fdel(self):pass

        return locals()

class Arg(object):
    ''' Build and show a GUI dialog to collect arguments
        @type  opt:  C{U{Option<http://docs.python.org/library/optparse.html>}}
        @param opt:  An U{Option<http://docs.python.org/library/optparse.html>}.
        @type    enabled:  C{boolean}
        @keyword enabled:  The Arg is enabled.
        @type    callback:  C{U{callable<http://docs.python.org/library/functions.html#callable>} object}
        @keyword callback:  A function/class that is called when the Arg value is changed.
        @type    icon:      C{L{icons}}
        @keyword icon:      An icon class from the L{icons} module.
        @type    tooltip:   C{str}
        @keyword tooltip:   A tooltip string.
        @type    required:  C{boolean}
        @keyword required:  The Arg is required to have a value .
    '''
    def __init__(self,opt,enabled=True,callback=None,icon=None,tooltip=None,required=True):
        self.opt=opt
        self._enabled=True #default
        self._callback=lambda *a,**kw:'break' #default
        self._value = opt.default
        self.enabled=enabled
        self.required=required
        self.icon=icon
        self.tooltip=tooltip

        #On update callback
        if callback and callable(callback):
            self.callback=callback
        else:
            self.callback=self._callback

    @property
    def value(self):
        try:return self._value.get()
        except:return self._value
    @value.setter
    def value(self, val):
        try:self._value.set(val)
        except:self._value=val

    def __classproperty__(fcn):
        '''The class property decorator function'''
        try:return property( **fcn() )
        except:pass

    @__classproperty__
    def callback():
        '''The callback property.'''

        def fget(self):
            return self._callback

        def fset(self,arg):
            if callable(arg):
                self._callback=arg
            else:
                raise AttributeError, 'Callback object is not callable.'

        def fdel(self):pass

        return locals()

    @__classproperty__
    def enabled():
        '''The enabled property.'''

        def fget(self):
            return self._enabled

        def fset(self,enabled,*args, **kwargs):
            if enabled:
                for var in vars(self).values():
                    try:var.config(state=Tix.NORMAL)
                    except:pass
            else:
                for var in vars(self).values():
                    try:var.config(state=Tix.DISABLED)
                    except:pass
            self._enabled=enabled

        def fdel(self):pass

        return locals()

class DirArg(Arg):
    ''' Build a directory browser

        @type    initialdir:   C{str}
        @keyword initialdir:   The folder to open the browser at initially.
    '''
    def __init__(self,opt,initialdir='',**kwargs):
        self.initialdir=initialdir
        self.lastdir=None
        Arg.__init__(self,opt,**kwargs)

    def __build__(self,root,row):
        self.TkPhotoImage = Tix.PhotoImage(format=self.icon.format,data=self.icon.data) # keep a reference! See http://effbot.org/tkinterbook/photoimage.htm
        self._value = Tix.StringVar(root)
        if not self.lastdir:self.lastdir=Tix.StringVar(root,self.initialdir)

        if self.opt.default is not None:self._value.set(self.opt.default)
        self.TkLabel=Tix.Label(root, text=self.opt.help+':')
        self.TkEntry=Tix.Entry(root, textvariable=self._value)

        self.TkButton = Tix.Button(root,image=self.TkPhotoImage, command=Command(self.cmd,root,self.opt.help,self.lastdir,self._value))
        self.TkLabel.grid(row=row, column=0,sticky=Tix.W, padx=2)
        self.TkEntry.grid(row=row, column=1,sticky=Tix.E+Tix.W, padx=2)
        self.TkButton.grid(row=row, column=2,sticky=Tix.E, padx=2)
        if self.tooltip:
            self.TkLabelToolTip=_ToolTip(self.TkLabel, delay=250, follow_mouse=1, text=self.tooltip)
            self.TkEntryToolTip=_ToolTip(self.TkEntry, delay=250, follow_mouse=1, text=self.tooltip)
            self.TkButtonToolTip=_ToolTip(self.TkButton, delay=250, follow_mouse=1, text=self.tooltip)

        self._value.trace('w',self.callback)
        self.enabled=self.enabled #Force update

    def cmd(self,root,label,dir,var):
        ad = tkFileDialog.askdirectory(parent=root,initialdir=dir.get(),title=label)
        if ad:
            ad=utilities.encode(os.path.normpath(ad))
            dir.set(ad)
            var.set(ad)

class FileArg(Arg):
    ''' Build a file browser

        @type    initialdir:   C{list/tuple of strings}
        @keyword initialdir:   The folder to open the browser at initially.
        @type    filter:       C{str}
        @keyword filter:       The filter to show in the file browser.
                               eg. [('Log File',('*.txt','*.log'))]
    '''
    def __init__(self,opt,initialdir='',filter='',saveas=False,**kwargs):
        self.filter=filter
        self.initialdir=initialdir
        self.lastdir=None
        self.saveas=saveas
        Arg.__init__(self,opt,**kwargs)

    def __build__(self,root,row):
        self.TkPhotoImage = Tix.PhotoImage(format=self.icon.format,data=self.icon.data) # keep a reference! See http://effbot.org/tkinterbook/photoimage.htm
        self._value = Tix.StringVar(root)

        if not self.lastdir:self.lastdir=Tix.StringVar(root,self.initialdir)
        if self.opt.default is not None:self._value.set(self.opt.default)
        self.TkLabel=Tix.Label(root, text=self.opt.help+':')
        self.TkEntry=Tix.Entry(root, textvariable=self._value)
        self.TkButton = Tix.Button(root,image=self.TkPhotoImage,command=Command(self.cmd,root,self.opt.help,self.filter,self.lastdir,self._value))
        self.TkLabel.grid(row=row, column=0,sticky=Tix.W, padx=2)
        self.TkEntry.grid(row=row, column=1,sticky=Tix.E+Tix.W, padx=2)
        self.TkButton.grid(row=row, column=2,sticky=Tix.E, padx=2)
        if self.tooltip:
            self.TkLabelToolTip=_ToolTip(self.TkLabel, delay=250, follow_mouse=1, text=self.tooltip)
            self.TkEntryToolTip=_ToolTip(self.TkEntry, delay=250, follow_mouse=1, text=self.tooltip)
            self.TkButtonToolTip=_ToolTip(self.TkButton, delay=250, follow_mouse=1, text=self.tooltip)

        self._value.trace('w',self.callback)
        self.enabled=self.enabled #Force update

    def cmd(self,root,label,filter,dir,var):
        if self.saveas:
            if sys.platform[0:3].lower()=='win':
                ##Win32 GUI hack to avoid "<somefile>/ exists. Do you want to replace it?"
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
        else:
            fd = tkFileDialog.askopenfilename(parent=root,filetypes=filter,initialdir=dir.get(),title=label)

        if fd:
            fd=os.path.normpath(fd)
            dir.set(os.path.split(fd)[0])
            var.set(fd)

class ComboBoxArg(Arg):
    ''' Build a combobox

        @type    options:  C{list of strings}
        @keyword options:  The options to show in the combo box.
                           ['Some value','Another value']
    '''
    def __init__(self,opt,options=[],multiselect=False,**kwargs):

        self.options=options
        self.multiselect=multiselect
        Arg.__init__(self,opt,**kwargs)

    def __build__(self,root,row):
        ''' Build a combobox

            @type  root: C{Tix.Tk}
            @param root: Root Tk instance.
            @type  row:  C{int}
            @param row:  Grid row to place the file browser in.
        '''
        self.TkPhotoImage = Tix.PhotoImage(format=self.icon.format,data=self.icon.data) # keep a reference! See http://effbot.org/tkinterbook/photoimage.htm
        if self.multiselect:
            self._value = Tix.StringVar(root)
            self.dummy = Tix.StringVar(root)
            self.TkComboBox=Tix.ComboBox(root, dropdown=1, command=self.__updatemulti__,selectmode='immediate',editable=1,variable=self.dummy,options='listbox.height 6 listbox.background white')
            self.TkComboBox.subwidget('slistbox').subwidget('listbox').configure(selectmode='extended')
        else:
            self._value = Tix.StringVar(root)
            self.TkComboBox=Tix.ComboBox(root, command=self.callback, dropdown=1, editable=1,variable=self._value,options='listbox.height 6 listbox.background white')

        self.TkLabel=Tix.Label(root, text=self.opt.help+':')
        for o in self.options:self.TkComboBox.insert(Tix.END, o)
        if self.opt.default is not None:
            selected=self.opt.default
        else:
            selected=self.options[0]

        self.TkComboBox.set_silent(selected)
        self._value.set(selected)

        self.TkComboBox.subwidget('entry').bind('<Key>', lambda e: 'break')
        self.TkImage = Tix.Label(root,image=self.TkPhotoImage)
        self.TkLabel.grid(row=row, column=0,sticky=Tix.W, padx=2)
        self.TkComboBox.grid(row=row, column=1,sticky=Tix.E+Tix.W)
        self.TkImage.grid(row=row, column=2,sticky=Tix.E, padx=2)
        if self.tooltip:
            self.TkLabelToolTip=_ToolTip(self.TkLabel, delay=250, follow_mouse=1, text=self.tooltip)
            self.TkDropListToolTip=_ToolTip(self.TkComboBox, delay=250, follow_mouse=1, text=self.tooltip)
            self.TkImageToolTip=_ToolTip(self.TkImage, delay=250, follow_mouse=1, text=self.tooltip)

        #self._value.trace('w',self.callback)

        self.enabled=self.enabled #Force update
    def __updatemulti__(self,*args):
        try:listbox=self.TkComboBox.subwidget('slistbox').subwidget('listbox')
        except:return
        self._value.set('|'.join([listbox.get(i) for i in listbox.curselection()]))
        self.callback()

class StringArg(Arg):
    ''' Build a text entry box'''
    def __build__(self,root,row):
        self._value = Tix.StringVar(root)
        if self.opt.default is not None:self._value.set(self.opt.default)

        self.TkLabel=Tix.Label(root, text=self.opt.help+':')
        self.TkEntry=Tix.Entry(root, textvariable=self._value)
        #self.TkEntry.bind('<Key>', self.keypress)
        self.TkLabel.grid(row=row, column=0,sticky=Tix.W)
        self.TkEntry.grid(row=row, column=1,sticky=Tix.E+Tix.W, padx=2)
        if self.tooltip:
            self.TkLabelToolTip=_ToolTip(self.TkLabel, delay=250, follow_mouse=1, text=self.tooltip)
            self.TkEntryToolTip=_ToolTip(self.TkEntry, delay=250, follow_mouse=1, text=self.tooltip)

        self._value.trace('w',self.callback)
        self.enabled=self.enabled #Force update

class BoolArg(Arg):
    ''' Build a boolean checkbox '''

    def __build__(self,root,row):
        self._value = Tix.BooleanVar(root)
        self._value.set(self.opt.default)
        self.TkLabel=Tix.Label(root, text=self.opt.help+':')
        self.TkCheckbutton=Tix.Checkbutton(root, variable=self._value)
        self.TkLabel.grid(row=row, column=0,sticky=Tix.W)
        self.TkCheckbutton.grid(row=row, column=1,sticky=Tix.W)
        if self.tooltip:
            self.TkLabelToolTip=_ToolTip(self.TkLabel, delay=250, follow_mouse=1, text=self.tooltip)
            self.TkCheckbuttonToolTip=_ToolTip(self.TkCheckbutton, delay=250, follow_mouse=1, text=self.tooltip)

        self._value.trace('w',self.callback)
        self.enabled=self.enabled #Force update

class Command(object):
    ''' A class we can use to avoid using the tricky "Lambda" expression.
    "Python and Tkinter Programming" by John Grayson, introduces this idiom.'''
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return apply(self.func, self.args, self.kwargs)


class _ToolTip:
    '''
    From http://Tix.unpythonic.net/wiki/ToolTip
    Michael Lange <klappnase at 8ung dot at>

    The ToolTip class provides a flexible tooltip widget for Tkinter; it is based on IDLE's ToolTip
    module which unfortunately seems to be broken (at least the version I saw).

    INITIALIZATION OPTIONS::
        anchor:        where the text should be positioned inside the widget, must be on of "n", "s", "e", "w", "nw" and so on;
                       default is "center"
        bd:            borderwidth of the widget; default is 1 (NOTE: don't use "borderwidth" here)
        bg:            background color to use for the widget; default is "lightyellow" (NOTE: don't use "background")
        delay:         time in ms that it takes for the widget to appear on the screen when the mouse pointer has
                       entered the parent widget; default is 1500
        fg:            foreground (i.e. text) color to use; default is "black" (NOTE: don't use "foreground")
        follow_mouse:  if set to 1 the tooltip will follow the mouse pointer instead of being displayed
                       outside of the parent widget; this may be useful if you want to use tooltips for
                       large widgets like listboxes or canvases; default is 0
        font:          font to use for the widget; default is system specific
        justify:       how multiple lines of text will be aligned, must be "left", "right" or "center"; default is "left"
        padx:          extra space added to the left and right within the widget; default is 4
        pady:          extra space above and below the text; default is 2
        relief:        one of "flat", "ridge", "groove", "raised", "sunken" or "solid"; default is "solid"
        state:         must be "normal" or "disabled"; if set to "disabled" the tooltip will not appear; default is "normal"
        text:          the text that is displayed inside the widget
        textvariable:  if set to an instance of Tix.StringVar() the variable's value will be used as text for the widget
        width:         width of the widget; the default is 0, which means that "wraplength" will be used to limit the widgets width
        wraplength:    limits the number of characters in each line; default is 150

    WIDGET METHODS::
        configure(**opts): change one or more of the widget's options as described above; the changes will take effect the
                           next time the tooltip shows up; NOTE: follow_mouse cannot be changed after widget initialization

    Other widget methods that might be useful if you want to subclass ToolTip::
        enter():           callback when the mouse pointer enters the parent widget
        leave():           called when the mouse pointer leaves the parent widget
        motion():          is called when the mouse pointer moves inside the parent widget if follow_mouse is set to 1 and the
                           tooltip has shown up to continually update the coordinates of the tooltip window
        coords():          calculates the screen coordinates of the tooltip window
        create_contents(): creates the contents of the tooltip window (by default a Tix.Label)
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
    config=configure

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
            self._tipwindow = tw = Tix.Toplevel(self.master)
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
        label = Tix.Label(self._tipwindow, **opts)
        label.pack()


if __name__ == '__main__':
    def testcmd(dirarg,filearg):
        print dirarg.value.get()
        if dirarg.value.get() == 'C:\\':
            filearg.enabled=False
        else:
            filearg.enabled=True

    def onupdate(*args,**kwargs):
        print args
        print 'Something has been updated...'

    import optparse,icons,getargs
    reload(getargs)
    description='Run the getargs test'
    parser = optparse.OptionParser(description=description)

    opt=parser.add_option('-d', dest="dir", metavar="dir",help='A directory')
    dirarg=getargs.DirArg(opt,initialdir='',enabled=True,icon=icons.dir_img,tooltip='Tooltip!')

    opt=parser.add_option("-f", dest="f", metavar="f",help="A file")
    filearg=getargs.FileArg(opt,initialdir='',enabled=False)
    filearg.icon=icons.log_img
    filearg.filter=[('Log File',('*.txt','*.log'))]

    #Add a callback
    dirarg.callback=Command(testcmd,dirarg,filearg)

    opt=parser.add_option('-s', dest="str", metavar="str",help='string test')
    strarg=getargs.StringArg(opt,callback=onupdate,enabled=True)
    strarg.tooltip='Testing string entry 123'


    opt=parser.add_option("-n", action="store_true", dest="no",default=False,
                      help="A boolean arg")
    boolarg=getargs.BoolArg(opt)

    opt=parser.add_option('-l', dest="lst", metavar="lst",help='A list')
    comboboxarg=getargs.ComboBoxArg(opt,icon=icons.xsl_img,callback=onupdate)
    comboboxarg.options=['aaaa','bbbb','cccc','dddd']
    comboboxarg.tooltip='Tooltip!'
    comboboxarg.enabled=False

    optvals,argvals = parser.parse_args()
    callback=lambda *a,**kw:False
    for opt in parser.option_list:
        opt.default=vars(optvals).get(opt.dest,None)
    args=getargs.GetArgs(dirarg,filearg,strarg,boolarg,comboboxarg,callback=callback)
