# Main class for pycamps

import os
import stat
import sys
import re
import time
import shutil

import git
from git.errors import InvalidGitRepositoryError, NoSuchPathError, GitCommandError

import func.overlord.client as fc

from pycamps.config.campsadmindb import *
from pycamps.campserror import *
import pycamps.config.settings as settings

class CampsAdmin:
    """
    """
    
    def __init__(self):
    
        """Initializes some basic information about each camp project."""
    
        #print arguments
    
        self.login = os.getenv('LOGNAME')
        self.admindb = CampsAdminDB()

    def add_project(self, arguments):
        self.owner = self.login
        if arguments.owner:
            self.owner = arguments.owner

        self.proj_id = self.admindb.create_project(arguments.name, arguments.desc, arguments.web, 
                arguments.rcs_remote, arguments.db, arguments.db_lv, arguments.db_lv_snap, self.owner)
        print "== Adding %s to project list ==" % arguments.name

        pass

    def list_projects(self, arguments=None):
        projects = self.admindb.project_list(arguments.all)
        print """== Project List =="""
        for p in projects:
            if p[10]:
                print """Project: %s '%s' (status: %s, owner: %s)""" % (p[1], p[2], 'ACTIVE', p[8])
            else:
                print """Project: %s '%s' (status: %s, owner: %s)""" % (p[1], p[2], 'INACTIVE', p[8])

            if arguments.long:
                print """  [remote: %s, webserver: %s, database server: %s, database location: %s, snap size: %s]""" % (p[4], p[3], p[5], p[6], p[7])
                print 

        if not arguments.long:
            print
