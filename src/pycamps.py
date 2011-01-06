# Main class for pycamps

import os
import sys
import git

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

    def clone_docroot(self):
        try:
            repo = git.Repo(self.basecamp)
            clone = repo.clone(self.camppath)
            branch = clone.create_head(settings.CAMPS_BASENAME + str(self.camp_id))
            clone.heads[settings.CAMPS_BASENAME + str(self.camp_id)].checkout()
            print "Cloning camp%d web data complete" % self.camp_id
        except git.GitCommandError as stderr_value:
            print "The following error occurred: %s" % stderr_value

    def clone_db(self):
        
        print "camp%d database snapshot complete" % self.camp_id
        print "camp%d database configured" % self.camp_id
        print "camp%d database started" % self.camp_id
        pass

    def do_init(self, options, arguments):

        """Initializes a new camp within the current user's home directory.  The following occurs:
        
        git clone -b campX origin/master #clones master branch 
        git remote add camps/campX <path/url to central repo> #creates remote branch configuration
        git push camps/campX 
        creates new snapshot from live db
        configures new database on devdb
        creates symbolic link to static data (images)
    
        """

        self.camp_id = self.campdb.create_camp(arguments[0], settings.CAMPS_ROOT, self.login, settings.DB_USER, settings.DB_PASS, settings.DB_HOST, settings.DB_PORT)
        self.basecamp = settings.GIT_ROOT
        self.camppath = settings.CAMPS_ROOT + '/' + settings.CAMPS_BASENAME + str(self.camp_id) + '/'
        print "== Creating camp%d ==\n" % self.camp_id
        self.clone_docroot()
        self.clone_db()
    
