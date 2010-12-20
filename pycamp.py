#!/usr/bin/python

import os
import sys
import git
import optparse

import settings

"""
Certain variables are stored per camp in the ~/user/campX/INFO file:

'camp_id': each camp *must* have a unique id
'description': to help identify one camp from another
'db_user, db_pass, db_host, db_port': useful for connecting and running queries and the like
"""

def do_init(arguments):

    """Usage: pycamp init <desc>
    Initializes a new camp within the current user's home directory.  The following occurs:
    
    git clone -b campX origin/master #clones master branch 
    creates new snapshot from live db
    configures new database on devdb
    creates symbolic link to static data (images)

    """

    #print arguments

    login = os.getuid()
    home = os.environ['HOME']

    basecamp = '/home/clints/Projects/GitPyCamps/'
    camppath = home + '/' + settings.CAMP_NAME + '1' + '/'

    try:
        pass
    #    os.mkdir(pathtocamp)
    #    os.chdir(pathtocamp)

    except OSError:
        # we'll assume the dir is already there
        # probably need to increment camp # 
        print "Camp %s already exists" % pathtocamp

    try:
        repo = git.Repo(basecamp)
        clone = repo.clone(camppath)
    except git.GitCommandError as stderr_value:
        print "The following error occurred: %s" % stderr_value

def do_camp(options, arguments):
    if arguments[0] == "init":
        do_init(arguments[1:])

def main():                         
    p = optparse.OptionParser(description='Dispatches commands to create/manage development environments',
        prog='pycamp', version='pycamp 0.1', usage='%prog <options>')

    options, arguments = p.parse_args()
    if options:
        do_camp(options, arguments)
    else:
        p.print_help()

if __name__ == "__main__":
    main()

