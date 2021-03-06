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

File: rtdel.py

Implementation of deleting an object from a name server.

'''

# $Source$


from optparse import OptionParser, OptionError
import os
from rtctree.exceptions import RtcTreeError, BadPathError
from rtctree.tree import create_rtctree
from rtctree.path import parse_path
import sys

from rtcshell import RTSH_PATH_USAGE, RTSH_VERSION
from rtcshell.path import cmd_path_to_full_path


def delete_object_reference(cmd_path, full_path, options, tree=None):
    path, port = parse_path(full_path)
    if port:
        # Can't delete a port
        print >>sys.stderr, '{0}: Cannot access {1}: Cannot delete \
ports.'.format(sys.argv[0], cmd_path)
        return 1

    trailing_slash = False
    if not path[-1]:
        path = path[:-1]

    # Cannot delete name servers
    if len(path) == 2:
        print >>sys.stderr, '{0}: {1}: Cannot delete name servers.'.format(\
                sys.argv[0], cmd_path)
        return 1

    if not tree:
        tree = create_rtctree(paths=path)
    if not tree:
        return 1

    # There is no point in doing path checks for the path, as the path we are
    # deleting may not be in the tree if it's a zombie. Instead, we need to
    # find its parent, and use that to remove the name.
    parent = tree.get_node(path[:-1])
    if parent.is_manager:
        print >>sys.stderr, '{0}: {1}: Use rtmgr to delete components from \
managers.'.format(sys.argv[0], cmd_path)
        return 1
    if not parent.is_directory:
        print >>sys.stderr, '{0}: {1}: Parent is not a directory.'.format(\
                sys.argv[0], cmd_path)
        return 1

    try:
        parent.unbind(path[-1])
    except BadPathError:
        print >>sys.stderr, '{0}: {1}: No such name registered.'.format(\
                sys.argv[0], cmd_path)
        return 1
    return 0


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path>
Delete an object from a name server.

This command is particularly useful to remove zombie registrations. However,
care must be taken not to unlink a large section of the tree, as you will not
be able to get it back.

''' + RTSH_PATH_USAGE
    version = RTSH_VERSION
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
            default=False, help='Print debugging information. \
[Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print 'OptionError:', e
        return 1

    if not args:
        # If no path given then can't do anything.
        print >>sys.stderr, '{0}: No object specified.'.format(sys.argv[0])
        return 1
    elif len(args) == 1:
        cmd_path = args[0]
    else:
        print >>sys.stderr, usage
        return 1
    full_path = cmd_path_to_full_path(cmd_path)

    # Some sanity checks
    if full_path == '/':
        print >>sys.stderr, '{0}: Cannot delete the root directory.'.format(\
                sys.argv[0])
        return 1

    return delete_object_reference(cmd_path, full_path, options, tree)


# vim: tw=79

