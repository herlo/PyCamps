#!/usr/bin/python

import optparse

from pycamps import *

def do_camp(options, arguments):
    if arguments[0] == "init":
        camps = PyCamps()
        camps.do_init(options, arguments[1:])

def main():                         
    p = optparse.OptionParser(description='Dispatches commands to create/manage development environments',
        prog='pycamp', version='pycamp 0.1', usage='%prog <options>')

    options, arguments = p.parse_args()
    #print "Options: %s" % str(options)
    #print "Arguments: %s" % str(arguments)
    if len(arguments) >= 2:
        do_camp(options, arguments)
    else:
        p.print_help()

if __name__ == "__main__":
    main()


