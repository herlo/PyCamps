#!/usr/bin/python

import time
import argparse

from camps import *

camps = Camps()

def main():

    p = argparse.ArgumentParser(
        description='''Dispatches commands to 
        create/manage development environments''',
    )

    # create a camp
    sp = p.add_subparsers()
    p_init = sp.add_parser('init', help='initialize (create) a shed')
    p_init.add_argument('desc', help='description of shed')
    p_init.set_defaults(func=camps.create)

    # list camps
    p_list = sp.add_parser('list', help='list all active sheds (by default)')
    p_list.add_argument('-a', '--all', action='store_true', help='include inactive sheds')
    p_list.set_defaults(func=camps.list)

    # remove a camp
    p_rm = sp.add_parser('rm', help='remove a shed')
    p_rm.add_argument('id', help='shed #')
    p_rm.add_argument('-f', '--force', action='store_true', help='ignore checks, remove anyway')
    p_rm.set_defaults(func=camps.remove)

    # start camp components
    p_start = sp.add_parser('start', help='start a shed component')
    p_start.add_argument('-i', '--id', metavar='id', help='shed id')
    p_start.add_argument('--db', help='start db', action='store_true')
    p_start.add_argument('--web', help='start web server', action='store_true')
    p_start.add_argument('-a', '--all', help='start db and web', action='store_true')
    p_start.set_defaults(func=camps.start)

    # stop camp components
    p_stop = sp.add_parser('stop', help='stop a shed component')
    p_stop.add_argument('-i', '--id', metavar='id', help='shed id')
    p_stop.add_argument('--db', help='stop db', action='store_true')
    p_stop.add_argument('--web', help='stop web server', action='store_true')
    p_stop.add_argument('-a', '--all', help='stop all', action='store_true')
    p_stop.set_defaults(func=camps.stop)

    # restart camp components
    p_stop = sp.add_parser('restart', help='restart shed component')
    p_stop.add_argument('-i', '--id', metavar='id', help='shed id')
    p_stop.add_argument('--db', help='stop db', action='store_true')
    p_stop.add_argument('--web', help='stop web server', action='store_true')
    p_stop.add_argument('-a', '--all', help='stop all', action='store_true')
    p_stop.set_defaults(func=camps.restart)

#    # restart camp components
#    p_refresh = sp.add_parser('refresh', help='refresh shed component')
#    p_refresh.add_argument('-i', '--id', metavar='id', help='shed id')
#    p_refresh.add_argument('--db', help='stop db', action='store_true')
#    p_refresh.add_argument('--web', help='stop web server', action='store_true')
#    p_refresh.add_argument('-a', '--all', help='stop all', action='store_true')
#    p_refresh.set_defaults(func=camps.refresh)

    #print p_list

    args = p.parse_args()
    try:
        args.func(args)
    except CampError as e:
        print e.value


if __name__ == "__main__":
    main()
