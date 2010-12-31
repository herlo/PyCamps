#!/usr/bin/python

import os
import sys
import git
import optparse

from db import *
import settings

class PyCamps:
    """
    Certain variables are stored per camp in the ~/user/campX/INFO file:
    
    'camp_id': each camp *must* have a unique id
    'description': to help identify one camp from another
    'db_user, db_pass, db_host, db_port': useful for connecting and running queries and the like
    """
    
    def __init__(self):
    
        """Initializes some basic information about the camp. 
        User name and campsdb instances, for example."""
    
        #print arguments
    
        self.login = os.getenv('LOGNAME')
        self.campdb = PyCampsDB()

    def do_init(self, options, arguments):

        """Initializes a new camp within the current user's home directory.  The following occurs:
        
        git clone -b campX origin/master #clones master branch 
        git remote add camps/campX <path/url to central repo> #creates remote branch configuration
        git push camps/campX 
        creates new snapshot from live db
        configures new database on devdb
        creates symbolic link to static data (images)
    
        """

        camp_id = self.campdb.create_camp(arguments[0], settings.CAMPS_ROOT, self.login, settings.DB_USER, settings.DB_PASS, settings.DB_HOST, settings.DB_PORT)
    
        self.basecamp = settings.GIT_ROOT
        self.camppath = settings.CAMPS_ROOT + '/' + settings.CAMPS_BASENAME + str(camp_id) + '/'
    
        #print "Camp Path: %s" % camppath
    
        try:
            repo = git.Repo(self.basecamp)
            clone = repo.clone(self.camppath)
            branch = repo.create_head(settings.CAMPS_BASENAME + str(camp_id))
        except git.GitCommandError as stderr_value:
            print "The following error occurred: %s" % stderr_value
    
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

