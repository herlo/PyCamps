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
    'db_host', db_port': useful for connecting and running queries and the like
    """
    
    def __init__(self):
    
        """Initializes some basic information about the camp. 
        Username and campsdb instances, for example."""
    
        self.login = os.getenv('LOGNAME')
        self.campdb = CampsDB()
        self.projdb = ProjectsDB()
        self.camp_id = self._get_camp_id()
        if self.camp_id:
            self.campname = settings.CAMPS_BASENAME + str(self.camp_id)
        else:
            self.campname = None

    def _get_camp_id(self):
        """Attempt to obtain the camp_id by looking at the basename of the path.  
           If the path is not in a camp, this function will return None."""
        camp_basename = os.path.basename(os.getcwd())
        if re.match("^%s\d+$" % settings.CAMPS_BASENAME, camp_basename):
            return int(re.split("^%s" % settings.CAMPS_BASENAME, camp_basename)[1])
        else:
            return None

    def _get_campname(self):
        if not self.campname:
            self.campname = "%s" % (settings.CAMPS_BASENAME + str(self.camp_id))
        return self.campname

    def _create_db(self, db_config=True):

       self.db = DB(self.project, self.camp_id)

       self.db.set_camp_info(self.campdb.get_camp_info(self.camp_id))

       # do any app specific configuration of the db 
       self.db.hooks_preconfig()

       lv_info = self.projdb.get_lv_info(self.project)
       self.db.clone_db(lv_info, db_config)

    def _pull_master(self, force=False):

        self.project = self.campdb.get_project(self.camp_id)

        print """refreshing the code base from the %s master repository""" % self.project
        self.web = Web(self.project, self.camp_id)
        self.web.set_camp_info(self.campdb.get_camp_info(self.camp_id))
        self.web.pull_from_master(force)

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
        print """removed %s symlink""" % (settings.CAMPS_BASENAME + str(self.camp_id))

    def _restart_web(self):

        self.project = self.campdb.get_project(self.camp_id)
        self.web = Web(self.project, self.camp_id)

        self.web.hooks_prestop()
        self.web.restart_web()
        self.web.hooks_poststart()

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
        
        self.db.stop_db()

        self.db.hooks_poststop()

    def _start_db(self):

        self.project = self.campdb.get_project(self.camp_id)
        self.db = DB(self.project, self.camp_id)
        # run app specific hooks for db
        self.db.hooks_prestart()

        self.db.start_db()

        self.db.hooks_poststart()

    def _push_shared_camp(self, shared_camp_id):

        self.project = self.campdb.get_project(self.camp_id)
        shared_project = self.campdb.get_project(shared_camp_id)

        if self.project != shared_project:
            raise CampError("""Camps must be from the same project to be shared""")

        if self.camp_id == shared_camp_id:
            print """\n** This is silly, you own this camp.  Just use 'git push' going forward, it'll save you typing. **\n"""

        self.web = Web(self.project, self.camp_id)
        self.web.set_camp_info(self.campdb.get_camp_info(self.camp_id))
        print """pushing code to shared %s""" % (settings.CAMPS_BASENAME + str(shared_camp_id))
        camp_url = self.campdb.get_remote(shared_camp_id)
        self.web.push_or_pull_shared_camp("""%s""" % (settings.CAMPS_BASENAME + str(shared_camp_id)), camp_url, 'push')

    def _pull_shared_camp(self, shared_camp_id):

        self.project = self.campdb.get_project(self.camp_id)
        shared_project = self.campdb.get_project(shared_camp_id)

        if self.project != shared_project:
            raise CampError("""Camps must be from the same project to be shared""")

        if self.camp_id == shared_camp_id:
            print """\n** This is silly, you own this camp.  Just use 'git pull origin master' going forward. **\n"""

        self.web = Web(self.project, self.camp_id)
        self.web.set_camp_info(self.campdb.get_camp_info(self.camp_id))
        print """pulling in code from shared camp%d""" % shared_camp_id
        camp_url = self.campdb.get_remote(shared_camp_id)
        self.web.push_or_pull_shared_camp("""%s""" % (settings.CAMPS_BASENAME + str(shared_camp_id)), camp_url, 'pull')

    def _share_camp(self):

        self.project = self.campdb.get_project(self.camp_id)
        self.web = Web(self.project, self.camp_id)
        self.web.set_camp_info(self.campdb.get_camp_info(self.camp_id))

        self.web.share_camp(self.user, self.perms)

    def _unshare_camp(self):

        self.project = self.campdb.get_project(self.camp_id)
        self.web = Web(self.project, self.camp_id)
        self.web.set_camp_info(self.campdb.get_camp_info(self.camp_id))

        self.web.unshare_camp(self.user)

    def _validate_action(self, action):

        print action
        y_n = 'N'

        yes_no = raw_input("""Is this okay [y/N]: """)

        if len(yes_no) == 0:
            raise CampError("""Exiting on user request""")
        if len(yes_no) == 1:
            try:
                y_n = str(yes_no).upper()
            except Exception, e:
                raise CampError("""Bad input""")

            if y_n == 'Y':
                return
            else:
                raise CampError("""Exiting on user request""")

    def _print_status(self):

        self.web = Web(self.project, self.camp_id)
        self.db = DB(self.project, self.camp_id)

        camp_info = self.campdb.get_camp_info(self.camp_id)
        proj_info = self.projdb.get_project_info(self.project)
        campname = settings.CAMPS_BASENAME + str(self.camp_id)

        active = 'INACTIVE'
        if camp_info['active']:
            active = 'ACTIVE'

        status_txt = """ --- %s ---\n\n""" % (campname)
        status_txt += """    status:\t\t%s\n""" % active
        status_txt += """    owner:\t\t%s\n""" % camp_info['owner']
        status_txt += """    description:\t%s\n""" % camp_info['desc']
        status_txt += """    location:\t\t%s\n\n""" % camp_info['path']
        status_txt += """    project:\t\t%s\n""" % camp_info['proj']
        status_txt += """    db master:\t\t%s\n""" % proj_info['db_lv']
        status_txt += """    master repo:\t%s\n\n""" % proj_info['rcs_remote']
        status_txt += """    camp repo:\t\t%s\n""" % camp_info['rcs_remote']
        status_txt += """    ----------\n"""

        self.web.set_ssh_client(rcs_remote=camp_info['rcs_remote'])
        camp_sharing = self.web.get_camp_sharing()

        if camp_sharing:
            key, value = camp_sharing.popitem()
            status_txt += """    shared with:\t%s %s\n""" % (value, key)
        while camp_sharing:
            key, value = camp_sharing.popitem()
            status_txt += """\t\t\t%s %s\n""" % (value, key)

        status_txt += """\n"""

        # need to add commit stats and last commit here later

        db_active = "DOWN"
        if self.db.is_up():
            db_active = "UP"

        status_txt += """    db status:\t\t%s\n""" % db_active
        status_txt += """    ----------\n"""
        status_txt += """    db host:\t\t%s\n""" % camp_info['db_host']
        status_txt += """    db port:\t\t%s\n""" % camp_info['db_port']

        lv_info = self.projdb.get_lv_info(self.project)
        db_location = "%s/%s" % (settings.DB_ROOT, campname)
        db_usage = self.db.disk_usage(db_location)

        status_txt += """    db location:\t%s\n""" % db_location
        status_txt += """    db snap:\t\t/dev/%s/%s\n""" % (lv_info['vg'], campname)
        if db_usage:
            status_txt += """    db usage:\t       %s total /%s used /%s available\n""" % (db_usage[0], db_usage[1], db_usage[2])

        print status_txt

    def db_shell(self, args):

        if args.id:
            self.camp_id = args.id
        else:
            self.camp_id = self._get_camp_id()
            if not self.camp_id:
                raise CampError("""Please provide the camp id with --id option or move to the camp home.""")

        self.project = self.campdb.get_project(self.camp_id)
        self.db = DB(self.project, self.camp_id)
        self.db.set_camp_info(self.campdb.get_camp_info(self.camp_id))

        self.db.db_shell()

    def status(self, args):

        if args.id:
            self.camp_id = args.id
        else:
            self.camp_id = self._get_camp_id()
            if not self.camp_id:
                raise CampError("""Please provide the camp id with --id option or move to the camp home.""")

        self.project = self.campdb.get_project(self.camp_id)

        self._print_status()

    # push to shared camp
    def push(self, args):

        if args.id:
            self.camp_id = args.id
        else:
            self.camp_id = self._get_camp_id()
            if not self.camp_id:
                raise CampError("""Please provide the camp id with --id option or move to the camp home.""")

        if not args.force:
            self._validate_action("Pushing to shared repo, %s" % (settings.CAMPS_BASENAME + str(args.shared_camp_id)))

        self._push_shared_camp(args.shared_camp_id)
        print """push to %s complete""" % (settings.CAMPS_BASENAME + str(args.shared_camp_id))

    # pull from shared camp
    def pull(self, args):

        if args.id:
            self.camp_id = args.id
        else:
            self.camp_id = self._get_camp_id()
            if not self.camp_id:
                raise CampError("""Please provide the camp id with --id option or move to the camp home.""")

        if not args.force:
            self._validate_action("Pulling from a shared camp may require manually merging code")

        self._pull_shared_camp(args.shared_camp_id)
        print """pull from %s complete""" % (settings.CAMPS_BASENAME + str(args.shared_camp_id))

    def unshare(self, args):

        self.user = args.user

        if args.id:
            self.camp_id = args.id
        else:
            self.camp_id = self._get_camp_id()
            if not self.camp_id:
                raise CampError("""Please provide the camp id with --id option or move to the camp home.""")

        if not args.force:
            self._validate_action("Removing shared access to %s for %s" % (self._get_campname(), self.user))

        # share camp
        self._unshare_camp()
        print """Sharing for user '%s' has been removed from %s""" % (self.user, self._get_campname())

    def share(self, args):

        self.user = args.user

        if args.perms:
            self.perms = args.perms
        else:
            self.perms = 'R'

        if args.id:
            self.camp_id = args.id
        else:
            self.camp_id = self._get_camp_id()
            if not self.camp_id:
                raise CampError("""Please provide the camp id with --id option or move to the camp home.""")

        self._get_campname()
        print "Sharing %s with %s permissions for %s" % (self.campname, self.perms, self.user)
        # share camp
        self._share_camp()
        print "%s is now shared with %s permissions for %s" % (self._get_campname(), self.perms, self.user)

    # for web code #
    # push code to repo
    # pull in master repo
    # alert if dirty repo

    # for the db #
    # stop db 
    # unmount db
    # lvremove /dev/db_vg/campname
    # lv snapshot from camp master

    def refresh(self, args):

        if not args.db and not args.web and not args.all:
            raise CampError("""Please provide one of the following [--db] [--web] [--all]""")

        if args.db or args.all:

            if not args.force:
                self._validate_action("A refresh will destroy any database changes for %s" % (self._get_campname()))

            # stop db
            print """stopping db on camp%d""" % self.camp_id
            self._stop_db()
            # load app specific hooks for db
            self.db.hooks_poststop()
            self.db.hooks_preremove()
            # probably ought to remove the config from 
            # /etc/my.cnf at some point 
            #  this function does nothing atm
            lv_info = self.projdb.get_lv_info(self.project)
            self.db.unmount_db(lv_info)
            self.db.remove_db_lv(lv_info)
            self.db.hooks_postremove()

            # clone db lv
            self._create_db(db_config=False)
            # start db
            print """starting db on camp%d""" % self.camp_id
            self.db.start_db()
            # load app specific hooks for db
            self.db.hooks_poststart()

        if args.web or args.all:

            if not args.force:
                self._validate_action("A refresh may require manually merging code")

            self._pull_master(args.force)
            print """%s code base refreshed""" % self._get_campname()

    def stop(self, arguments):

        if arguments.id:
            self.camp_id = arguments.id
        else:
            self.camp_id = self._get_camp_id()
            if not self.camp_id:
                raise CampError("""Please provide the camp id with --id option or move to the camp home.""")

        print "Stopping database on %s" % self._get_campname()
        # stop db
        self._stop_db()

    def start(self, arguments):

        if arguments.id:
            self.camp_id = arguments.id
        else:
            self.camp_id = self._get_camp_id()
            if not self.camp_id:
                raise CampError("""Please provide the camp id with --id option or move to the camp home.""")

        print "Starting database on camp%s" % self.camp_id
        # clone db lv
        self._start_db()

    def restart(self, args):

        if not args.db and not args.web and not args.all:
            args.all = True

        if args.id:
            self.camp_id = args.id
        else:
            self.camp_id = self._get_camp_id()
            if not self.camp_id:
                raise CampError("""Please provide the camp id with --id option or move to the camp home.""")

        if args.db or args.all:
            print """stopping db on camp%d""" % self.camp_id
            self._stop_db()
            print """starting db on camp%d""" % self.camp_id
            self._start_db()

        if args.web or args.all: 
            print """restarting web server"""
            self._restart_web()

    def remove(self, args):
        """Removes a camp directory and its corresponding db directory"""

        # ensure code in repo is pushed to remote camp
        # (in httpd function) remove the symlink to httpd dir
        # remove camp directory
        # (in the mysql function)     
        # stop the database
        # remove sql directory

        if args.id:
            self.camp_id = args.id
        else:
            raise CampError("""A camp id must be provided.""")

        camp_id = self._get_camp_id()
        if camp_id:
            raise CampError("""A camp cannot be removed from within its own directory.""")

        if not args.force:
            self._validate_action("Remove will destroy any database changes for %s" % (self._get_campname()))

        self.camp_id = args.id
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
            if args.force == None:
                raise CampError("""The camp directory %s/%s does not exist.""" % (settings.CAMPS_ROOT, self._get_campname()))

        if args.force == None:
            self._confirm_remove(args)

        # remove web configs
        self._remove_web_config()
        self.web.push_camp()
        self.web.remove_camp()
        self.web.hooks_prestop()
        self.web.restart_web()
        self.web.hooks_poststart()

        # stop db
        self._stop_db()
        # load app specific hooks for db
        self.db.hooks_poststop()
        self.db.hooks_preremove()
        # probably ought to remove the config from 
        # /etc/my.cnf at some point 
        #  this function does nothing atm
        self.db.remove_db_config()
        lv_info = self.projdb.get_lv_info(self.project)
        self.db.unmount_db(lv_info)
        self.db.remove_db_lv(lv_info)
        self.db.hooks_postremove()
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
                if c[9]:
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
        if not self.projdb.is_active(self.project):
            raise CampError("""Project '%s' is not an active project.  Please contact an admin or choose a different project""" % self.project)

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
            print """-- camp%d has been setup at %s --""" % (self.camp_id, self.camppath)
        except CampError, e:
            self.campdb.delete_camp(self.camp_id)
            #also possibly need to delete the camp db instance
            raise CampError(e.value)
