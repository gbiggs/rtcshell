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

File: state_control_base.py

Base for the scripts that change component state.

'''

__version__ = '$Revision: $'
# $Source$


from optparse import OptionParser, OptionError
import os
import sys

from rtcshell import RTSH_PATH_USAGE, RTSH_VERSION
from rtctree.tree import create_rtctree, BadECIndexError
from rtctree.path import parse_path


def alter_component_state(action, cmd_path, full_path, options):
    path, port = parse_path(full_path)
    if port:
        # Can't cat a port
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1

    trailing_slash = False
    if not path[-1]:
        # There was a trailing slash
        print >>sys.stderr, '{0}: {1}: Not an \
object'.format(sys.argv[0], cmd_path)
        return 1

    tree = create_rtctree(paths=path)
    if not tree:
        return 1

    if not tree.has_path(path):
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1
    object = tree.get_node(path)
    if not object.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: Not an \
object'.format(sys.argv[0], cmd_path)
        return 1

    try:
        action(object, options.ec_index)
    except BadECIndexError, e:
        print >>sys.stderr, '{0}: No execution context at index \
{1}'.format(sys.argv[0], e.args[0])
        return 1

    return 0


def base_main(argv, description, action):
    usage = '''Usage: %prog [options] <path>
{0}

{1}'''.format(description, RTSH_PATH_USAGE)
    version = RTSH_VERSION
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
            default=False, help='Print debugging information. \
[Default: %default]')
    parser.add_option('-e', '--exec_context', dest='ec_index', type='int',
            action='store', default=0,
            help='Index of the execution context to activate within. \
[Default: %default]')

    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print 'OptionError:', e
        sys.exit(1)

    if not args:
        cmd_path = ''
    elif len(args) == 1:
        cmd_path = args[0]
    else:
        print >>sys.stderr, usage
        return 1

    # Build the full path by checking the RTCSH_CWD environment variable.
    if 'RTCSH_CWD' in os.environ:
        full_path = os.path.join(os.environ['RTCSH_CWD'], cmd_path)
    else:
        full_path = cmd_path
    if not full_path:
        # If no path given, and the cwd is not set, then can't do anything.
        print >>sys.stderr, '{0}: Cannot cat a directory.'.format(sys.argv)
        return 1

    return alter_component_state(action, cmd_path, full_path, options)


# vim: tw=79

