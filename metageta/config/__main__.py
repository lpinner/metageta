# -*- coding: utf-8 -*-
# Copyright (c) 2015 Australian Government, Department of the Environment
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

from metageta.config import get_config_file
import os, subprocess, sys

def main():

    f = get_config_file()

    if sys.platform=='win32':
        subprocess.call(['notepad', f])
    else:
        tries = [os.environ.get('EDITOR', None),
                 os.environ.get('VISUAL', None),
                 'nano',
                 'vim',
                 'edit',
                 'xdg-open',
                 'open',
                 ]
        for cmd in [c for c in tries if c]:
            try:
                subprocess.check_call([cmd, f])
                return
            except:
                pass
        sys.stderr.write('Unable to find an editor to open %s'%f)
        sys.exit(1)

if __name__ == '__main__':
    main()