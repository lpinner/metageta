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
Splashscreen for startup
========================
Pop up a splashscreen on startup

This is the beginnings of a splash screen cos the GUI's in runcrawler.py and runtransforms.py take sooo long to start up...
No, they don't take long at all to load when run from C:\ drive. They take ages when the app is run from a network drive

Modified from Activestate Recipe 534124: Elegant Tkinter Splash Screen U{http://code.activestate.com/recipes/534124} 
by Luke Pinner (ERIN) to support threading & callback functions.

'''

import threading,os
#from Tkinter import *
import Tkinter
class SplashScreen(threading.Thread):
    def __init__(self, imagefile=None, imagedata=None, timeout=0.001, callback=lambda:True):
    
        if not imagefile and not imagedata:raise Exception,'Image file name or base 64 encoded image data required!'
        if not timeout   and not callback: raise Exception,'Timeout (secs) or boolean callback function required!'

        self._root              = Tkinter.Tk()
        self._splash            = None

        if imagefile:self._image = Tkinter.PhotoImage(file=imagefile)
        elif imagedata:self._image = Tkinter.PhotoImage(file=imagedata)
        self._timeout  = timeout
        self._callback = callback

        threading.Thread.__init__ (self)
        self.start()
    def run(self):
        # Remove the app window from the display
        self._root.withdraw()

        # Calculate the geometry to centre the splash image
        scrnWt = self._root.winfo_screenwidth()
        scrnHt = self._root.winfo_screenheight()

        imgWt = self._image.width()
        imgHt = self._image.height()

        imgXPos = (scrnWt / 2) - (imgWt / 2)
        imgYPos = (scrnHt / 2) - (imgHt / 2)

        self._root.overrideredirect(1)
        self._root.geometry('+%d+%d' % (imgXPos, imgYPos))
        Tkinter.Label(self._root, image=self._image, cursor='watch').pack()

        # Force Tk to draw the splash screen outside of mainloop()
        #self._splash.update()
        self._root.deiconify() # Become visible at the desired location
        self.__settimeout__()
        self._root.mainloop()

    def __settimeout__(self):
        self._root.after(int(self._timeout*1000),self.__poll__)
    def __poll__(self):
        if self._callback(): #If the callback function returns True
            self._root.destroy()
        else:
            self._root.after(int(self._timeout*1000),self.__poll__)

class CallBack:
    def __init__(self,value=False):
        self.value=value
    def check(self):
        return self.value

if __name__=='__main__':
    import time,sys,os
    c=CallBack()
    splash=SplashScreen(callback=c.check)
    print 'Yawn... I''m going to sleep now!'
    time.sleep(5)
    print 'Stretch... I''m awake now!'
    c.value=True

