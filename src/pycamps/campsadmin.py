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

    def _send_new_project_email(self, args):
        print "Project: %s with remote repo: %s, has been activated by %s" % (args.name, args.rcs_remote, args.owner)

    def _send_activate_email(self, args):
        print "Project %s, with remote repo: %s, failed to activate. Please ensure you can clone the repo and then run 'pc admin project activate %s'" % (args.name, args.rcs_remote, args.name)

    def _valid_repo(self, project_name, remote_url):
        project_repo = "%s/%s" %(settings.TESTREPO_PATH, project_name)

        try: 
            os.stat('%s' % project_repo)
            shutil.rmtree('%s' % project_repo)
        except OSError, e:
            os.makedirs('%s' % project_repo, 0775)

        try:
            gitrepo = git.Git(project_repo)
            cmd = ['git', 'init']
            result = git.Git.execute(gitrepo, cmd)
            repo = git.Repo(project_repo)
            repo.create_remote('test', remote_url)
            repo.remotes.test.pull('refs/heads/master:refs/heads/master')
        except AssertionError, e:
            shutil.rmtree('%s' % project_repo)
            return False

        shutil.rmtree('%s' % project_repo)
        return True

    def _admin_check(self):
        is_admin = False
        admin_list = ''
        for admin in settings.ADMINS:
            admin_list += """\t%s: <%s>\n""" % (admin[0], admin[2])
            if admin[1] == self.login:
                is_admin = True

        if not is_admin:
            raise CampError("""\nYou must be in the admin group to muck around here.\n\nCurrent Admins:\n\n%s""" % admin_list)

    def add_project(self, args):
        self._admin_check()
        args.owner = self.login
        if args.owner:
            self.owner = args.owner

        try:
            self.proj_id = self.admindb.create_project(args.name, args.desc, args.rcs_remote, 
                                                    args.db_lv, args.db_lv_snap, args.owner)
            print "== Adding %s to project list ==" % args.name
            self.activate_project(args)
        except CampError, e:
                #also possibly need to delete the camp db instance
                raise CampError(e.value)

    def edit_project(self, args):
        self._admin_check()
        if not args.desc and not args.remote and not args.snap_size and not args.lv:
            raise CampError("""Please provide one of the following [--desc description] [--remote rcs_url] [--snap-size size] [--lv lvm_path]""")
        else:
            self.admindb.edit_project(args.name, desc=args.desc, remote=args.remote, lv=args.lv, snap=args.snap_size)

    def activate_project(self, args):
        self._admin_check()
        print """Activating '%s'""" % args.name
        args.owner = self.login
        args.rcs_remote = self.admindb.get_remote(args.name)
        if (self._valid_repo(args.name, args.rcs_remote)):
            self.admindb.activate_project(args.name)
            self._send_new_project_email(args)
        else:
            self._send_activate_email(args)

    def deactivate_project(self, args):
        self._admin_check()
        print """Deactivating '%s'""" % args.name
        self.admindb.deactivate_project(args.name)
        print """Project '%s' deactivated""" % args.name
        
    def list_projects(self, arguments=None):
        projects = self.admindb.project_list(arguments.all, arguments.name)
        print """== Project List =="""
        for p in projects:
            if p[10]:
                print """Project: %s '%s' (status: %s, owner: %s)""" % (p[1], p[2], 'ACTIVE', p[8])
            else:
                print """Project: %s '%s' (status: %s, owner: %s)""" % (p[1], p[2], 'INACTIVE', p[8])

            if arguments.long:
                print """  [remote: %s, webserver: %s, database server: %s, master db: %s, snap size: %s]""" % (p[4], p[3], p[5], p[6], p[7])
                print 

        if not arguments.long:
            print

def main():
    ca = CampsAdmin()
#    p_id = ca.create_project()

if __name__ == "__main__":
    main()

