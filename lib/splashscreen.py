'''
This is the beginnings of a splash screen cos the GUI's in runcrawler.py and runtransforms.py take sooo long to start up...
===========================================================================================================================

Modified from Activestate Recipe 534124: Elegant Tkinter Splash Screen U{http://code.activestate.com/recipes/534124} 
by Luke Pinner (ERIN) to support threading & callback functions.

'''
import threading,os
from Tkinter import *
class SplashScreen(threading.Thread):
    def __init__(self, imagefile=None, imagedata=None, timeout=0.001, callback=lambda:True):
    
        if not imagefile and not imagedata:#raise Exception,'Image file name or base 64 encoded image data required!'
            #imagefile=__file__[:-3]+'.gif' - this don't work cos __file__ might .pyc or .pyo not .py
            imagefile=os.path.splitext(__file__)[0]+'.gif'
        if not timeout   and not callback: raise Exception,'Timeout (secs) or boolean callback function required!'

        self._root              = Tk()
        self._splash            = None

        if imagefile:self._image = PhotoImage(file=imagefile)
        else:        self._image = PhotoImage(data=imagedata)
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
        Label(self._root, image=self._image, cursor='watch').pack()

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

