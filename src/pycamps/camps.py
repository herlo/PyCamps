# Main class for pycamps

import os
import stat
import sys
import re
import time
import shutil

import git
from git.errors import InvalidGitRepositoryError, NoSuchPathError, GitCommandError

import pycamps.config.settings as settings
from pycamps.config.campsdb import *
from pycamps.config.projectsdb import *
from pycamps.campserror import *
from pycamps.web import Web
from pycamps.db import DB

class Camps:
    """
    Camps are an independent dev environment per feature or mini-project.
    Each camp is associated with an upstream project.  A git repository is 
    created for each camp and the initial bits of code are pulled in from 
    the project's repository.

    Certain variables are core to camps:

    'camp_id': each camp *must* have a unique id
    'description': to help identify one camp from another
    'db_user, db_pass, db_host, db_port': useful for connecting and running queries and the like
    """
    
    def __init__(self):
    
        """Initializes some basic information about the camp. 
        Username and campsdb instances, for example."""
    
        #print arguments
    
        self.login = os.getenv('LOGNAME')
        self.campdb = CampsDB()
        self.projdb = ProjectsDB()
        self.camp_id = self._get_camp_id()

    def _get_camp_id(self):
        """Attempt to obtain the camp_id by looking at the basename of the path.  
           If the path is not in a camp, this function will fail."""
        camp_basename = os.path.basename(os.getcwd())
        if re.match("^%s\d+$" % settings.CAMPS_BASENAME, camp_basename):
            return re.split("^%s" % settings.CAMPS_BASENAME, camp_basename)[1]
        else:
            return None

    def _create_db(self):

       self.db = DB(self.project, self.camp_id)

       self.db.set_camp_info(self.campdb.get_camp_info(self.camp_id))

       # do any app specific configuration of the db 
       self.db.hooks_preconfig()

       lv_info = self.projdb.get_lv_info(self.project)
       self.db.clone_db(lv_info)

    def _remove_web_config(self):

        # set the project info
        self.project = self.campdb.get_project(self.camp_id)

        # initialize the web class
        self.web = Web(self.project, self.camp_id)

        # set the camp_info 
        self.web.set_camp_info(self.campdb.get_camp_info(self.camp_id))

        # preremove hook
        self.web.hooks_preremove()

        # remove symlink for web config
        self.web.remove_symlink_config()

    def _stop_web(self):

        self.project = self.campdb.get_project(self.camp_id)
        self.web = Web(self.project, self.camp_id)

        # do any app specific configuration for web 
        self.web.hooks_prestop()

    def _create_web(self):

        self.web = Web(self.project, self.camp_id)

        self.web.set_camp_info(self.campdb.get_camp_info(self.camp_id))

        # do any app specific configuration for web 
        self.web.hooks_preconfig()

        master_url = self.projdb.get_remote(self.project)
        camp_info = self.campdb.get_camp_info(self.camp_id)
        camp_url = self.web.clone_docroot(master_url)
        self.campdb.set_remote(self.camp_id, camp_url)

        self.web.create_config()
        self.web.create_symlink_config()
        self.web.create_log_dir()

    def _stop_db(self):

        self.project = self.campdb.get_project(self.camp_id)
        self.db = DB(self.project, self.camp_id)
        
        # run app specific hooks for db
        self.db.hooks_prestop()
        
        try:         
            self.db.stop_db()
        except CampError, e:
            print e.value
            pass

    def stop(self, arguments):

        if not arguments.db and not arguments.web and not arguments.all:
            raise CampError("""One of the following options is required: --db, --web, --all""")

        if arguments.id:
            self.camp_id = arguments.id
        else:
            try:
                self.camp_id = self._get_camp_id()
            except CampError, e:
                raise CampError("""Please provide the camp id with --id option or move to the camp directory""")

        if arguments.db:
            print "Stopping database on camp%s" % self.camp_id
            # clone db lv
            self._stop_db()
    
            # load app specific hooks for db
            self.db.hooks_poststop()

        if arguments.web:
            pass

    def start(self, arguments):
#        if arguments.id == None:
#            camp_id = self._get_camp_id()
#            if camp_id == None:
#                raise CampError("The camp_id was not supplied or could not be obtained")
#        else:
#            camp_id = arguments.id
#
#        if arguments.db:
#            print "Starting database on camp%s" % camp_id
#            client = fc.Client(settings.FUNC_DB_HOST)
#            self._start_db(client, camp_id)
#            print "camp%s database server successfully started" % camp_id
#        if arguments.web:
#            print "camp%s web server successfully started" % camp_id
            pass

    def restart(self, arguments):
#        self.stop(arguments)
#        self.start(arguments)
        pass

    def remove(self, arguments):
        """Removes a camp directory and its corresponding db directory"""

        # ensure code in repo is pushed to remote camp
        # (in httpd function) remove the symlink to httpd dir
        # remove camp directory
        # (in the mysql function)     
        # stop the database
        # remove sql directory

        if arguments.id == None:
            self.camp_id = self._get_camp_id()
            if self.camp_id != None and arguments.force == None:
                raise CampError("""A camp cannot be removed from within its own directory.""")

        self.camp_id = arguments.id
        try:
            valid_user = False
            for admin in settings.ADMINS:
                if self.login == admin[1]:
                    valid_user = True
                    break

            if not valid_user and self.login == self.campdb.get_owner(int(self.camp_id)):
                valid_user = True

            if not valid_user:
                    raise CampError("""A camp can only be removed by its owner or an admin.""")
        except OSError, e:
            if arguments.force == None:
                raise CampError("""The camp directory %s/%s does not exist.""" % (settings.CAMPS_ROOT, settings.CAMPS_BASENAME + str(camp_id)) )

        # remove web configs
        self._remove_web_config()

        self.web.push_camp()

        self.web.remove_camp()

        self.web.hooks_prestop()
        self.web.stop_web()
        self.web.hooks_poststop()
        self.web.hooks_prestart()
        self.web.start_web()
        self.web.hooks_poststart()

        # stop db
        self._stop_db()

        # load app specific hooks for db
        self.db.hooks_poststop()
        self.db.hooks_preremove()

#        self.db.unmount_db()
#
#        self.db.remove_db_data()
#
#        self.db.hooks_postremove()

        self.campdb.deactivate_camp(self.camp_id)

    def list(self, args=None):
        camps = self.campdb.camp_list(args.all, args.id)
        print """== Camps List =="""
        for c in camps:
            if c[2] == 'None' or c[2] == None:
                if c[9]:
                    print "camp%d 'no description' (project: %s, owner: %s) %s" % (c[0], c[1], c[4], "ACTIVE")
                else:
                    print "camp%d 'no description' (project: %s, owner: %s) %s" % (c[0], c[1], c[4], "INACTIVE")
            else:
                if c[8]:
                    print "camp%d '%s' (project: %s, owner: %s) %s" % (c[0], c[2], c[1], c[4], "ACTIVE")
                else:
                    print "camp%d '%s' (project: %s, owner: %s) %s" % (c[0], c[2], c[1], c[4], "INACTIVE")

            if args.long:
                print """\t[path: %s, remote: %s, db host: %s, db port: %d]""" % (c[3], c[5], c[6], c[7])
                print

    def create(self, args):
        """Initializes a new camp within the current user's home directory.  The following occurs:
        
        creates a camps db entry and returns the camp_id
        sets the campname value
        sets the camppath value
        creates new snapshot from live db
        updates any needed database configs (db hook)
        starts database (db hook)

        clones web docroot from master repo
        creates configuration file for web server virtual host (web hook)
        creates log dir and files with proper perms (web hook)
        creates symbolic link to static data (app hook)
        starts web server (web hook)
        """

        self.project = args.proj

        try:
            self.camp_id = self.campdb.create_camp(args.proj, args.desc, settings.CAMPS_ROOT, self.login, settings.DB_HOST)
            self.campname = settings.CAMPS_BASENAME + str(self.camp_id)
            self.camppath = """%s/%s""" % (settings.CAMPS_ROOT, self.campname )
            print "== Creating camp%d ==" % self.camp_id

            # clone db lv
            self._create_db()

            # load app specific hooks for db
            self.db.hooks_postconfig()

            # start db
            self.db.start_db()

            # load app specific hooks for db
            self.db.hooks_poststart()

            # clone and configure web
            self._create_web()

            # load app specific hooks for web
            self.web.hooks_postconfig()

            # restart web server
            self.web.restart_web()

            # load app specific hooks for db
            self.web.hooks_poststart()

            self.campdb.activate_camp(self.camp_id)
            print """-- camp%d is ready for use --""" % self.camp_id
        except CampError, e:
            self.campdb.delete_camp(self.camp_id)
            #also possibly need to delete the camp db instance
            raise CampError(e.value)
