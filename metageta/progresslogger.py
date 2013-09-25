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
Provide GUI & file progress logging

Example:

>>> import progresslogger
>>> if debug:level=progresslogger.DEBUG
>>> else:level=progresslogger.INFO
>>> pl = progresslogger.ProgressLogger('Metadata Crawler',logfile=log, logToConsole=True, logToFile=True, logToGUI=True, level=level)
>>> try:
>>>     do somthing
>>>     pl.info('That worked!')
>>> except:
>>>     pl.error('That didn't work!')

'''

#Workaround for Issue 34:
#pickle doesn't like unicode, so use cPickle instead
import logging,warnings,random,os,sys,socket,cPickle,threading,Queue,time,subprocess
from metageta import utilities
try:
    import Tkinter,tkMessageBox,ScrolledText
except:
    warnings.warn('Unable to import Tkinter, tkMessageBox and/or ScrolledText')

#Define some constants
DEBUG=logging.DEBUG
INFO=logging.INFO
WARNING=logging.WARNING
ERROR=logging.ERROR
CRITICAL=logging.CRITICAL
FATAL=logging.FATAL

class ProgressLogger(logging.Logger):
    '''Provide logger interface'''

    def __init__(self,
               name='Progress Log',
               level=logging.INFO,
               format='%(asctime)s\t%(levelname)s\t%(message)s',
               dateformat='%H:%M:%S',
               logToConsole=False,
               logToFile=False,
               logToGUI=True,
               maxprogress=100,
               logfile=None,
               mode='w',
               icon=None,
               callback=lambda:None):

        self.logToGUI=logToGUI
        self._logfile=logfile
        self.mode=mode
        self.level=level
        self.dateformat=dateformat
        self.logging=True

        #Dummy methods, updated if logToGUI is True
        self.updateProgress=lambda *a,**k:None
        self.resetProgress=lambda *a,**k:None

        ##Cos we've overwritten the class __init__ method
        logging.Logger.__init__(self,name,level=level-1)#To handle the PROGRESS log records without them going to the console or file

        #Set up the handlers
        self.format = logging.Formatter(format, dateformat)

        if logToConsole:
           #create console handler and set level
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(self.format)
            self.addHandler(ch)

        if logToFile:
            #create file handler and set level
            if logfile:
                fh = logging.FileHandler(logfile, mode=mode)
                fh.setLevel(level)
                fh.setFormatter(self.format)
                self.addHandler(fh)

        if logToGUI:
            self.progress=0
            try:
                self.ProgressLoggerHandler = ProgressLoggerHandler(self, name=name, maxprogress=maxprogress,icon=icon,callback=callback)

                #To handle the PROGRESS & END events without them going to the console or file
                logging.PROGRESS = level - 1
                logging.addLevelName(logging.PROGRESS, "PROGRESS")
                self.ProgressLoggerHandler.setLevel(logging.PROGRESS)
                self.ProgressLoggerHandler.setFormatter(self.format)
                self.addHandler(self.ProgressLoggerHandler)

                #Update the dummy methods
                self.updateProgress=self.ProgressLoggerHandler.updateProgress
                self.resetProgress=self.ProgressLoggerHandler.resetProgress

            except:
                if logToFile:
                    msg='The Progress Logger GUI failed.\nLog messages will be output to %s'%logfile
                else:
                    msg='The Progress Logger failed.'
                self.warn(msg.replace('\n',' '))
                self.showmessage('Progress Logger error', msg)

        #Handle warnings
        warnings.simplefilter('always')
        warnings.showwarning = self.showwarning

    # ================ #
    # Class Methods
    # ================ #
    def showmessage(self, title, msg,type=None):
        try:
            tk=Tkinter.Tk()
            tk.withdraw()
            tkMessageBox.showinfo(title,msg,type=type)
            tk.destroy()
        except:print msg

    def showwarning(self, msg, cat, fname, lno, file=None, line=None):
        self.warn(msg)

    def shutdown(self):
        '''
        Perform any cleanup actions in the logging system (e.g. flushing
        buffers).

        Should be called at application exit.
        '''
        self.debug('Shutting down')
        self.logging=False
        for h in self.handlers:
            try:
                h.flush()
                h.close()
            except:pass

    # ================ #
    # Class Properties
    # ================ #
    def __classproperty__(fcn):
        '''The class property decorator function'''
        try:return property( **fcn() )
        except:pass

    @__classproperty__
    def logfile():
        '''The logfile property.'''

        def fget(self):
            return self._logfile

        def fset(self, *args, **kwargs):
            self._logfile=args[0]
            for h in self.handlers:
                if isinstance(h, logging.FileHandler):
                    h.flush()
                    h.close()
                    self.removeHandler(h)
                    fh = logging.FileHandler(self._logfile, mode=self.mode)
                    fh.setLevel(self.level)
                    fh.setFormatter(self.format)
                    self.addHandler(fh)
                    break

        def fdel(self):pass
        return locals()

class ProgressLoggerHandler(logging.Handler):
    ''' Provide a Progress Bar Logging handler '''

    def __init__(self, parent, name='Progress Log', level=logging.INFO, maxprogress=100, icon=None, callback=lambda:None):
        '''
        Initializes the instance - set up the Tkinter GUI and log output.
        '''
        self.parent=parent
        self.callback=callback

        ##Cos we've overwritten the class __init__ method
        logging.Handler.__init__(self)

        #Message queue to handle ansychronous gui
        self.msgs = []

        ##Create the GUI
        ##Run as a separate process as even multithreading will block on long IO operations
        ##as only a single thread will run at a time.
        self.host='localhost'
        self.inport= random.randint(1024, 10000)
        self.outport= random.randint(1024, 10000)

        if utilities.iswin:python = 'pythonw.exe'
        else: python = 'python'
        pythonPath=utilities.which(python)
        pythonScript=__file__
        parameterList = [pythonPath, pythonScript,str(self.inport),str(self.outport),'-s',self.host,'-n',name,'-m',str(maxprogress)]
        if icon:parameterList.extend(['-i',str(icon)])
        #for i,v in enumerate(parameterList): #Fix any spaces in parameters
        #    if ' ' in v:parameterList[i]='"%s"'%v
        pid = subprocess.Popen(parameterList).pid
        pc=ProgressLoggerChecker(parent,self.host,self.outport,pid)
        while not pc.ready: #Fixes Issue 29
            if pc.failed:raise
            else:time.sleep(0.1)

    def sendmsgs(self, host=None,port=None):
        if host is None:host=self.host
        if port is None:port=self.inport
        for msg in range(len(self.msgs)):
            try:
                msg=self.msgs.pop(0)
                client = socket.socket (socket.AF_INET, socket.SOCK_STREAM )
                client.connect((host,port))
                client.send(cPickle.dumps(msg))
                client.close()
                del client
                time.sleep(0.1)
            except:pass

    def emit(self, record):
        ''' Process a log message '''
        self.msgs.append([record.levelname, self.format(record)])
        self.sendmsgs()

    def close(self):
        '''
        Tidy up any resources used by the handler.
        '''
        self.msgs.append(['EXIT',0])
        self.sendmsgs()
        self.callback()

    def updateProgress(self,newMax=None):
        self.msgs.append(['PROGRESS',newMax])
        self.sendmsgs()

    def resetProgress(self):
        self.msgs.append(['RESET',0])
        self.sendmsgs()

class ProgressLoggerChecker(threading.Thread):
    def __init__(self,parent,host,port,pid):
        self.parent=parent
        self.gui=True
        self.host = host
        self.port = int(port)
        self.pid = pid
        self.ready=False
        self.failed=False

        threading.Thread.__init__ (self)
        self.start()

    def run(self):
        #Start listening on the given host:port
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host,self.port))
        self.server.listen(1)

        #Give the GUI time to start
        time.sleep(1)
        if utilities.isrunning(self.pid):
            while True:
                #Check for messages
                channel, details = self.server.accept()
                data=''
                while True:
                    part=channel.recv(1024).strip()
                    if part:data+=part
                    else:break
                msg=cPickle.loads(data)
                if msg[0]=='STARTUP':
                    self.ready=True
                elif msg[0]=='EXIT':
                    channel.close()
                    self.stop()
                channel.close()
                time.sleep(1)
        else:self.failed=True

    def stop(self):
        #Stop listening
        self.server.close()
        del self.server
        self.parent.shutdown()
        sys.exit()

class ProgressLoggerServer:
    ''' Provide a Progress Bar Logging Server '''

    def __init__(self,inport,outport,name=None, server='localhost',maxprogress=100, icon=None):
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((server,int(inport)))
        self.server.listen(1)
        self.serving=True

        self.host = server
        self.inport = int(inport)
        self.outport = int(outport)
        self.name = name
        self.maxprogress = int(maxprogress)
        self.progress = 0

        ##Create the log message queue & shutdown
        self.queue  = Queue.Queue()

        ##Create the GUI
        #self.gui=ProgressLoggerGUI(self.queue, self.host,self.inport,self.outport, name=name, maxprogress=maxprogress, icon=icon)
        #self.gui.start()
        #Don't subclass threading.Thread, just use it. This avoids "RuntimeError: RuntimeError('main thread is not in main loop',)"
        self.t=threading.Thread(target=ProgressLoggerGUI,args=(self.queue, self.host,self.inport,self.outport), kwargs={'name':name, 'maxprogress':maxprogress, 'icon':icon})
        self.t.start()

        self.startLogging()

    def startLogging(self):
        #Start listening on the given host:port
        while self.serving:
            channel, details = self.server.accept()
            data=''
            while True:
                part=channel.recv(1024).strip()
                if part:data+=part
                else:break
            msg=cPickle.loads(data)
            if msg[0]=='EXIT':
                self.serving=False
            self.queue.put(msg)
            channel.close()

        #Stop listening
        self.server.close()

class ProgressLoggerGUI(object):#(threading.Thread): #Don't subclass threading.Thread
    ''' Provide a Progress Bar Logging GUI '''
    def __init__(self, queue, host, inport, outport, name=None, maxprogress=100, icon=None):

        ##Cos we've overwritten the class __init__ method
        #threading.Thread.__init__(self)
        self.queue = queue
        self.host = host
        self.inport = inport
        self.outport = outport
        self.name = name
        self.maxprogress = maxprogress
        self.progress = 0
        self.keepchecking = True
        self.ppid = os.getppid()
        self.icon=icon
        self.run()

    def run(self):
        '''
        Initializes the instance - set up the Tkinter progress bar and log output.
        '''

        self.master=Tkinter.Tk()
        self.master.withdraw()
        self.master.protocol("WM_DELETE_WINDOW", self.onOk)
        self.master.title(self.name)

        # Set geometry and centre the GUI:
        swidth = self.master.winfo_screenwidth()
        sheight = self.master.winfo_screenheight()
        width = min([700, int(swidth/10 * 0.75)*10])
        height = int(sheight/10 * 0.75)*10
        xpos = max([0, (swidth - width)   / 2 - self.master.winfo_vrootx()])
        ypos = max([0, (sheight - height) / 3 - self.master.winfo_vrooty()])
        self.master.geometry("%sx%s"%(width,height))
        self.master.geometry('+%d+%d' % (xpos, ypos))

        if self.icon is not None:
            icon=self.icon.split('.')
            try:
                try:
                    self.icon=getattr(__import__('.'.join(icon[:-1])),icon[-1])
                except:
                    pass
                try:
                    self.icon=Tkinter.PhotoImage(master=self.master,data=self.icon.data,format=self.icon.format)
                except:
                    self.icon=Tkinter.PhotoImage(master=self.master,file=self.icon)
                self.master.tk.call('wm', 'iconphoto', self.master._w, self.icon)
            except:
                pass

        ''' Pack text message '''
        Tkinter.Label(self.master, text='Progress', anchor=Tkinter.NW, justify=Tkinter.LEFT).pack(fill=Tkinter.X)

        ''' Pack progress bar '''
        self.progress_bar = ProgressBarView(self.master, max=self.maxprogress)
        self.progress_bar.pack(fill=Tkinter.X)

        ''' Pack log window '''
        self.logwnd = ScrolledText.ScrolledText(self.master, width=60, height=12, state=Tkinter.DISABLED)
        self.logwnd.pack(fill=Tkinter.BOTH, expand=1)

        ''' Pack OK button '''
        self.ok = Tkinter.Button(self.master, text="OK", width=10, command=self.onOk, state=Tkinter.DISABLED)
        self.ok.pack(side=Tkinter.RIGHT, padx=5, pady=5)

        self.master.deiconify()
        self.onStartup()
        self.checkQueue()
        self.master.mainloop()

    def checkQueue(self):
        '''
        Handle all the messages currently in the queue (if any).
        '''
        #print 'checking queue'
        while self.queue.qsize():
            try:
                # Check contents of events queue
                msg = self.queue.get(block=False)
                self.onMsg(msg)
            except Queue.Empty:
                pass
        #Check parent is still alive.
        if os.getppid() == 1:
            self.onMsg(['INFO','Parent process "%s" has stopped working unexpectedly.'%self.name])
            self.onMsg(['EXIT',''])
        if self.keepchecking:self.master.after(100, self.checkQueue)

    def onMsg(self, msg):
        ''' Process events '''
        eventName = msg[0]
        eventMsg  = msg[1]
        if eventName == 'EXIT':
            self.ok.configure(state=Tkinter.ACTIVE)
            self.master.bind("<Return>", self.onOk)
            self.keepchecking=False
        elif eventName == 'PROGRESS':
            max=float(eventMsg)
            self.progress+=1
            self.progress_bar.updateProgress(self.progress, newMax=max)
            if self.progress>=max:
                self.ok.configure(state=Tkinter.ACTIVE)
                self.master.bind("<Return>", self.onOk)
        elif eventName == 'RESET':
            self.progress=0
            self.progress_bar.updateProgress(self.progress)
            self.ok.configure(state=Tkinter.DISABLED)
            self.master.bind("<Return>", lambda *a,**k:'break')
        else:
            self.onLogMessage(eventMsg)

    def onLogMessage(self, msg):
        ''' Display log message '''
        w = self.logwnd
        w.configure(state=Tkinter.NORMAL)
        w.insert(Tkinter.END, msg)
        w.insert(Tkinter.END, "\n")
        w.see(Tkinter.END)
        w.configure(state=Tkinter.DISABLED)

    def onStartup(self):
        try:
            client = socket.socket (socket.AF_INET, socket.SOCK_STREAM )
            client.connect((self.host,self.outport))
            client.send(cPickle.dumps(['STARTUP',0]))
            client.close()
            del client
        except:pass

    def onOk(self, event=None):
        self.master.withdraw()
        try:
            for port in (self.inport,self.outport):
                client = socket.socket (socket.AF_INET, socket.SOCK_STREAM )
                client.connect((self.host,port))
                client.send(cPickle.dumps(['EXIT',0]))
                client.close()
                del client
        except:pass
        self.master.destroy()

class ProgressBarView:
    '''A progress bar widget

       Modified from U{http://www.faqts.com/knowledge_base/view.phtml/aid/2718/fid/264} and U{http://www.sarfrosh.com/URDU/teachings/HP/BIN/BlockTracker.py}
    '''
    def __init__(self, master=None, orientation='horizontal',
          min=0, max=100, width=100, height=None,
          doLabel=1, appearance=None,
          fillColor=None, background=None,
          labelColor=None, labelFont=None,
          labelText='', labelFormat="%d%%",
          value=0.1, bd=2):
        # preserve various values
        self.master=master
        self.orientation=orientation
        self.min=min
        self.max=max
        self.doLabel=doLabel
        self.labelText=labelText
        self.labelFormat=labelFormat
        self.value=value
        if (fillColor == None) or (background == None) or (labelColor == None):
            # We have no system color names under linux. So use a workaround.
            #btn = Tkinter.Button(font=labelFont)
            btn = Tkinter.Button(master, text='0', font=labelFont)
            if fillColor == None:
                fillColor  = btn['foreground']
            if background == None:
                background = btn['disabledforeground']
            if labelColor == None:
                labelColor = btn['background']
        if height == None:
            l = Tkinter.Label(font=labelFont)
            height = l.winfo_reqheight()
        self.width      = width
        self.height     = height
        self.fillColor  = fillColor
        self.labelFont  = labelFont
        self.labelColor = labelColor
        self.background = background
        #
        # Create components
        #
        self.frame=Tkinter.Frame(master, relief=appearance, bd=bd, width=width, height=height)
        self.canvas=Tkinter.Canvas(self.frame, bd=0,
            highlightthickness=0, background=background, width=width, height=height)
        self.scale=self.canvas.create_rectangle(0, 0, width, height,
            fill=fillColor)
        self.label=self.canvas.create_text(width / 2, height / 2,
            text=labelText, anchor=Tkinter.CENTER, fill=labelColor, font=self.labelFont)
        self.canvas.pack(fill=Tkinter.BOTH)
        self.update()
        self.canvas.bind('<Configure>', self.onResize) # monitor size changes

    def onResize(self, event):
        if (self.width == event.width) and (self.height == event.height):
            return
        # Set new sizes
        self.width  = event.width
        self.height = event.height
        # Move label
        self.canvas.coords(self.label, event.width/2, event.height/2)
        # Display bar in new sizes
        self.update()

    def updateProgress(self, newValue, newMax=None):
        if newMax:self.max = newMax
        self.value = newValue
        self.update()

    def pack(self, *args, **kw):
        self.frame.pack(*args, **kw)

    def update(self):
        # Trim the values to be between min and max
        value=float(self.value)
        max=float(self.max)
        min=float(self.min)
        if value > max:
            value = max
        if value < min:
            value = min
        # Adjust the rectangle
        if self.orientation == "horizontal":
            self.canvas.coords(self.scale, 0, 0, value / max * self.width, self.height)
        else:
          self.canvas.coords(self.scale, 0, self.height - (value / max*self.height), self.width, self.height)
        # And update the label
        if self.doLabel:
            if value:
                if value >= 0:
                    pvalue = int((value / max) * 100.0)
                else:
                    pvalue = 0
                self.canvas.itemconfig(self.label, text=self.labelFormat % pvalue)
            else:
                self.canvas.itemconfig(self.label, text='')
        else:
            self.canvas.itemconfig(self.label, text=self.labelFormat % self.labelText)
        self.canvas.update_idletasks()

############################################################################
# PROCESSENTRY32 and getppid derived from:
# http://d.hatena.ne.jp/chrono-meter/20090325/p1
############################################################################
if utilities.iswin:
    import ctypes
    class PROCESSENTRY32(ctypes.Structure):
        from ctypes.wintypes import DWORD,POINTER,ULONG,LONG,MAX_PATH,c_char
        _fields_ = (
            ('dwSize', DWORD, ),
            ('cntUsage', DWORD, ),
            ('th32ProcessID', DWORD, ),
            ('th32DefaultHeapID', POINTER(ULONG), ),
            ('th32ModuleID', DWORD, ),
            ('cntThreads', DWORD, ),
            ('th32ParentProcessID', DWORD, ),
            ('pcPriClassBase', LONG, ),
            ('dwFlags', DWORD, ),
            ('szExeFile', c_char * MAX_PATH, ),
            )
    def getppid(pid=None):
        """the Windows version of os.getppid"""
        if pid is None:pid=os.getpid()
        from ctypes import windll,sizeof,byref
        import win32process
        pe = PROCESSENTRY32()
        pe.dwSize = sizeof(PROCESSENTRY32)

        snapshot = windll.kernel32.CreateToolhelp32Snapshot(2, 0)
        try:
            if not windll.kernel32.Process32First(snapshot, byref(pe)):
                raise WindowsError
            while pe.th32ProcessID != pid:
                if not windll.kernel32.Process32Next(snapshot, byref(pe)):
                    raise WindowsError
            result = pe.th32ParentProcessID
        finally:
            windll.kernel32.CloseHandle(snapshot)

        if result not in win32process.EnumProcesses():
            result = 1

        return result
    os.getppid = getppid
############################################################################
if __name__ == '__main__':
    import optparse
    description='Run the progress logger GUI'
    usage = "usage: %prog in_port out_port [options]"
    parser = optparse.OptionParser(usage=usage,description=description)
    opt=parser.add_option('-m', '--maxprogress', type="int", dest="maxprogress",default=100,help='The maximum value to show in the progress bar (%default)')
    opt=parser.add_option('-n', '--name', type="string", dest="name",default='Progress', help='The name to display in the window title bar (%default)')
    opt=parser.add_option('-i', '--icon', type="string", dest="icon", help='The GIF to display in the window title bar, either a filepath or a class string')
    opt=parser.add_option('-s', '--server', type="string", dest="server",default='localhost', help='The server hostname (%default)')
    #Parse command line args
    kwargs,args = parser.parse_args()
    kwargs=kwargs.__dict__
    if len(args) <> 2:
        parser.error('Incorrect number of arguments.')
    try: args=map(int,args)
    except:parser.error('Incorrect argument types.')
    pl = ProgressLoggerServer(*args,**kwargs)
