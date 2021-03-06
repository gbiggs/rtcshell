#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtcshell

Copyright (C) 2009-2010
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

File: rtcwd.py

Create a command to change the current working directory environment variable.

'''

__version__ = '$Revision: $'
# $Source$


#!/usr/bin/env python

import os
from rtctree.exceptions import RtcTreeError
from rtctree.tree import create_rtctree
from rtctree.path import parse_path
import sys

from rtcshell.path import ENV_VAR, cmd_path_to_full_path


if sys.platform == 'win32':
    SET_CMD = 'set'
    EQUALS = '='
    QUOTE = ''
elif 'SHELL' in os.environ and 'csh' in os.environ['SHELL']:
    SET_CMD = 'setenv'
    EQUALS = ' '
    QUOTE = '"'
else:
    SET_CMD = 'export'
    EQUALS = '='
    QUOTE = '"'


def make_cmd_line(path):
    return '{0} {1}{2}{3}{4}{3}'.format(SET_CMD, ENV_VAR, EQUALS, QUOTE, path)


def cd(cmd_path, full_path):
    path, port = parse_path(full_path)
    if port:
        # Can't change dir to a port
        print >>sys.stderr, 'rtcd: {0}: Not a \
directory'.format(cmd_path)
        return 1

    if not path[-1]:
        # Remove trailing slash part
        path = path[:-1]

    tree = create_rtctree(paths=path)
    if not tree:
        return 1

    if not tree.has_path(path):
        print >>sys.stderr, 'rtcd: {0}: No such directory or \
object'.format(cmd_path)
        return 1
    if not tree.is_directory(path):
        print >>sys.stderr, 'rtcd: {0}: Not a directory'.format(cmd_path)
        return 1

    print make_cmd_line(full_path)
    return 0


def main(argv):
    if len(argv) < 2:
        # Change to the root dir
        print '{0} {1}{3}{2}/{2}'.format(SET_CMD, ENV_VAR, QUOTE, EQUALS)
        return 0
    else:
        # Take the first argument only
        cmd_path = argv[1]

        if cmd_path == '.' or cmd_path == './':
            # Special case for '.': do nothing
            if ENV_VAR in os.environ:
                print make_cmd_line(os.environ[ENV_VAR])
                return 0
            else:
                print make_cmd_line('/')
                return 0
        elif cmd_path == '..' or cmd_path == '../':
            # Special case for '..': go up one directory
            if ENV_VAR in os.environ and os.environ[ENV_VAR] and \
                    os.environ[ENV_VAR] != '/':
                parent = os.environ[ENV_VAR][:os.environ[ENV_VAR].rstrip('/').rfind('/')]
                if not parent:
                    parent = '/'
                print make_cmd_line(parent)
                return 0
            else:
                print make_cmd_line('/')
                return 0

        full_path = cmd_path_to_full_path(cmd_path)
        return cd(cmd_path, full_path)


if __name__ == '__main__':
    sys.exit(main(sys.argv))


# vim: tw=79

