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

"""
Config file handling

@todo:
    - Handle merging of newer default config file with existing user config file
"""

import os, errno
from appdirs import user_config_dir

def _mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


def get_config_dir():
    """
        Get the user application config directory, creating it if required.

        @rtype:   C{str}
        @return:  directory path
    """
    user_conf_dir = user_config_dir('MetaGETA')
    _mkdirs(user_conf_dir)
    return user_conf_dir


def get_config_file():
    """
        Get the user application config file, creating it if required.

        @rtype:   C{str}
        @return:  file path
    """
    conf_file = 'config.xml'
    default_conf_file = os.path.join(os.path.dirname(__file__), conf_file)
    user_conf_dir = get_config_dir()
    user_conf_file = os.path.join(user_conf_dir, conf_file)
    if not os.path.exists(user_conf_file):
        import shutil
        shutil.copy(default_conf_file, user_conf_file)
    return user_conf_file
