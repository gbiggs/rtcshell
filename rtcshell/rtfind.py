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

File: rtfind.py

Implementation of the command to find components, managers, etc.

'''

# $Source$


from optparse import OptionParser, OptionError
import os
import re
from rtctree.exceptions import RtcTreeError
from rtctree.tree import create_rtctree, InvalidServiceError, \
                         FailedToNarrowRootNamingError, \
                         NonRootPathError
from rtctree.path import parse_path
from rtctree.utils import build_attr_string, get_num_columns_and_rows, \
                          get_terminal_size
import sys

from rtcshell import RTSH_PATH_USAGE, RTSH_VERSION
from rtcshell.path import cmd_path_to_full_path


def search(cmd_path, full_path, options, tree=None, returnvalue=None):
    path, port = parse_path(full_path)
    if port:
        # Can't search in a port
        print >>sys.stderr, '{0}: Cannot access {1}: No such directory or \
object.'.format(sys.argv[0], cmd_path)
        if returnvalue == 'list':
            return None
        else:
            return 1

    trailing_slash = False
    if not path[-1]:
        # There was a trailing slash
        trailing_slash = True
        path = path[:-1]

    if not tree:
        tree = create_rtctree(paths=path)
    if not tree:
        if returnvalue == 'list':
            return None
        else :
            return 1        

    # Find the root node of the search
    root = tree.get_node(path)
    if not root:
        print >>sys.stderr, '{0}: Cannot access {1}: No such directory or \
object.'.format(sys.argv[0], cmd_path)
        if returnvalue == 'list':
            return None
        else :
            return 1
    if root.is_component and trailing_slash:
        # If there was a trailing slash, complain that a component is not a
        # directory.
        print >>sys.stderr, '{0}: cannot access {1}: Not a directory.'.format(\
                sys.argv[0], address)
        if returnvalue == 'list':
            return None
        else :
            return 1

    name_res = []
    for name in options.name:
        # Replace regex special characters
        name = re.escape (name)
        # * goes to .*?
        name = name.replace (r'\*', '.*?')
        # ? goes to .
        name = name.replace (r'\?', r'.')
        name_res.append(re.compile(name))
    for name in options.iname:
        # Replace regex special characters
        name = re.escape (name)
        # * goes to .*?
        name = name.replace (r'\*', '.*?')
        # ? goes to .
        name = name.replace (r'\?', r'.')
        name_res.append(re.compile(name, re.IGNORECASE))

    def get_result(node, args):
        if node.full_path.startswith(cmd_path):
            result = node.full_path[len(cmd_path):]
            if not result:
                # This will happen if the search root is a component
                return node.name
            return node.full_path
        else:
            return node.full_path
    def matches_search(node):
        # Filter out types
        if node.is_component and 'c' not in options.type:
            return False
        if node.is_manager and 'm' not in options.type and \
                'd' not in options.type:
            return False
        if node.is_nameserver and 'n' not in options.type and \
                'd' not in options.type:
            return False
        if node.is_directory and 'd' not in options.type and \
                (not node.is_nameserver and not node.is_manager):
            return False
        if not name_res:
            return True
        # Check for name matches
        for name_re in name_res:
            if name_re.search(node.full_path):
                return True
        return False
    matches = root.iterate(get_result, filter=[matches_search])
    
    if returnvalue == 'list':
        return matches
    else :
        for m in matches:
            print m
        return 0

def main(argv=None, tree=None, returnvalue=None):
    usage = '''Usage: %prog <search path> [options]
Find entries in the RTC tree matching given constraints.

Equivalent to the UNIX 'find' command.

''' + RTSH_PATH_USAGE
    version = RTSH_VERSION
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
            default=False, help='Print debugging information. \
[Default: %default]')
    parser.add_option('--maxdepth', dest='max_depth', action='store',
                      type='int', default=0,
                      help='Maximum depth to search down to in the tree. Set \
to 0 to disable. [Default: %default]')
    parser.add_option('--iname', dest='iname', action='append', type='string',
                      default=[], help='Case-insensitive name pattern. This \
option can be specified multiple times.')
    parser.add_option('--name', dest='name', action='append', type='string',
                      default=[], help='Case-sensitive name pattern. This \
option can be specified multiple times.')
    parser.add_option('--type', dest='type', action='store', type='string',
                      help='Type of object: c (component), d (directory), m \
(manager), n (name server). Multiple types can be specified in a single entry, \
e.g. "--type dmn".')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print 'OptionError:', e
        if returnvalue == 'list':
            return None
        else :
            return 1

    if len(args) == 1:
        cmd_path = args[0]
    else:
        print >>sys.stderr, usage
        if returnvalue == 'list':
            return None
        else:
            return 1
    full_path = cmd_path_to_full_path(cmd_path)

    return search(cmd_path, full_path, options, tree, returnvalue)


# vim: tw=79

