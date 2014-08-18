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
Provide file progress logging

Example:

>>> import progresslogger
>>> if debug:level=progresslogger.DEBUG
>>> else:level=progresslogger.INFO
>>> pl = progresslogger.ProgressLogger('Metadata Crawler',logfile=log, logToConsole=True, logToFile=True, level=level)
>>> try:
>>>     do somthing
>>>     pl.info('That worked!')
>>> except:
>>>     pl.error('That didn't work!')

'''

import logging,warnings
from metageta import utilities

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
               maxprogress=100,
               logfile=None,
               mode='w',
               callback=lambda:None):

        self._logfile=logfile
        self.mode=mode
        self.level=level
        self.dateformat=dateformat
        self.logging=True

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

        #Handle warnings
        warnings.simplefilter('always')
        warnings.showwarning = self.showwarning


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


