#!/usr/bin/python26

import sys
import optparse

def do_camp(arguments):
    for a in arguments:
        print a

def main():                         

    p = optparse.OptionParser(description='Dispatches commands to create/manage development environments',
                                   prog='camp',
                                   version='camp 0.1',
                                   usage='%prog [-Vv] [init [<desc>]|refresh [web|db|conf]]')

    options, arguments = p.parse_args()
    if len(arguments) >= 1:
        do_camp(arguments)
    else:
        p.print_help()

if __name__ == "__main__":
    main()

