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
                arguments.rcs_remote, arguments.db, arguments.db_lv, self.owner)
        print "== Adding %s to project list ==" % arguments.name

        pass

