import os
import sys
import grp
import time
import stat
import shutil
import paramiko

#import re
#import time
#import shutil

import func.overlord.client as fc

import git
from git.errors import InvalidGitRepositoryError, NoSuchPathError, GitCommandError

from pycamps.campserror import *
import pycamps.config.settings as settings

class Web:

    def __init__(self, project, camp_id):
        self.func = fc.Client(settings.FUNC_WEB_HOST)
        self.camp_id = int(camp_id)
        self.campname = settings.CAMPS_BASENAME + str(self.camp_id)
        self.project = project

    def set_camp_info(self, camp_info):
        self.camp_info = camp_info

    def _get_camp_access(self, camp_name):

        stdin, stdout, stderr = self.sshclient.exec_command("""expand %s""" % camp_name)

        self.perm_list = []
        for line in stdout.read().splitlines()[2:]:
            self.perm_list = line.split('\t')[0].strip().split('  ')

        stdin.close()
        stdout.close()
        stderr.close()

    def _set_camp_sharing(self, user, perm, remove=False):

        stdin, stdout, stderr = self.sshclient.exec_command("""setperms %s""" % self.rcs_remote)

        if remove:
            # remove the rights
            self.perm_list.pop(user, None)
        else:
            # add/overwrite current perms
            self.perm_list[user] = perm

        # writing perms should be input like so
        # ['R kynalya\n', 'RW herlo\n']

        for key in self.perm_list.keys():
            stdin.write("""%s %s\n""" % (self.perm_list[key], key))

        stdin.flush()

        stdin.close()
        stdout.close()
        stderr.close()

    def _get_camp_sharing(self):

        stdin, stdout, stderr = self.sshclient.exec_command("""getperms %s""" % self.rcs_remote)

        self.perm_list = {}

        for line in stdout.read().splitlines():
            perm, user = line.split(' ')
            self.perm_list[user] = perm

    def _set_ssh_client(self, rcs_remote=None):

        if not rcs_remote:
            self.host_info, self.rcs_remote = self.camp_info['rcs_remote'].split(':')
        else:
            self.host_info, self.rcs_remote = rcs_remote.split(':')

        self.git_user, self.git_host = self.host_info.split('@')

        self.sshclient = paramiko.SSHClient()
        self.sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshclient.connect(self.git_host, username=self.git_user)

    def unshare_camp(self, user):

        self._set_ssh_client()

        self._get_camp_sharing()

        self._set_camp_sharing(user, None, True)

        self.sshclient.close()

    def share_camp(self, user, perms):

        self._set_ssh_client()

        self._get_camp_sharing()

        self._set_camp_sharing(user, perms)

        self.sshclient.close()

    def pull_from_master(self, force=False):

        self.camppath = self.camp_info['path']

        try:
            repo = git.Repo(self.camppath)
            if repo.is_dirty() and not force:
                raise CampError("""Please commit/stash uncommitted code, or use -f/--force option at your own risk""")
            repo.remotes[self.project].pull('refs/heads/master:refs/heads/master')
        except AssertionError, e:
            raise CampError("""Update failed with error: %s""" % e)
        except IndexError, e:
            raise CampError("""Update failed with error: %s""" % e)

    def push_or_pull_shared_camp(self, shared_camp, rcs_remote, action):

        self.camppath = self.camp_info['path']
        self.owner = self.camp_info['owner']

        try:
            repo = git.Repo(self.camppath)
            if repo.is_dirty() and not force:
                raise CampError("""Please commit/stash uncommitted code, or use -f/--force option at your own risk""")
        except AssertionError, e:
            if e and str(e) != '':
                raise CampError("""Update failed with error: %s""" % e)
        except IndexError, e:
            raise CampError("""Update failed with error: %s""" % e)

        self._set_ssh_client(rcs_remote)
        self._get_camp_access(shared_camp)

        if action == 'pull':
            if not len(self.perm_list) or self.perm_list[0] != 'R':
                raise CampError("""Update failed, READ access for %s DENIED to %s""" % (shared_camp, self.owner))
        if action == 'push':
            if not len(self.perm_list) or self.perm_list[1] != 'W':
                raise CampError("""Update failed, WRITE access for %s DENIED to %s""" % (shared_camp, self.owner))

        add_remote = True
        for r in repo.remotes:
            if str(r) == shared_camp:
                add_remote = False
                break

        if add_remote:
            repo.create_remote(shared_camp, rcs_remote)

        try:
            if action == 'pull':
                repo.remotes[shared_camp].pull('refs/heads/master:refs/heads/master')
            if action == 'push':
                repo.remotes[shared_camp].push('refs/heads/master:refs/heads/master')
        except IndexError, e:
            raise CampError("""Update failed with error: %s""" % e)
        except AssertionError, e:
            # odds are that unless the exception 'e' has a value
            # the assertionerror is wrong.  Usually, this is because
            # gitPython shows a warning, not an actual error
            if e and len(str(e)) != 0:
                raise CampError("""Update failed with error: %s""" % e)

    def clone_docroot(self, remote_url):

        self.owner = self.camp_info['owner']
        self.camppath = self.camp_info['path']
        self.db_port = self.camp_info['db_port']

        try: 
            os.stat('%s' % self.camppath)
            raise CampError("""Camp directory '%s' already exists, please remove and try again""" % self.camppath)
        except OSError, e:
            os.makedirs('%s' % self.camppath, 0775)
            # there's a bug somewhere that won't let me do 2775 above
            # these two lines fix that
            current_permissions = os.stat('%s' % self.camppath).st_mode
            os.chmod('%s' % self.camppath, current_permissions | stat.S_ISGID )
            gid = grp.getgrnam(settings.WEB_GROUP).gr_gid
            os.chown('%s' %self.camppath, -1, gid)
            print """camp%d directory created""" % self.camp_id

        try:
            gitrepo = git.Git(self.camppath)
            cmd = ['git', 'init']
            result = git.Git.execute(gitrepo, cmd)
            repo = git.Repo(self.camppath)
            repo.create_remote(self.project, remote_url)
            repo.remotes[self.project].pull('refs/heads/master:refs/heads/master')
            print """camp%d repo cloned from project '%s' repo""" % (self.camp_id, self.project)

            camp_url = """%s/%s""" % (remote_url.split('/')[0], self.campname)
            repo.create_remote('origin', camp_url)
            repo.remotes['origin'].push('refs/heads/master:refs/heads/master')
            print """camp%d repo cloned and pushed to camp%d remote""" % (self.camp_id, self.camp_id)
            return camp_url
        except AssertionError, e:
            shutil.rmtree('%s' % camppath)
            raise CampError(e)

    def create_config(self):
        """configure the camp to work with the web server.  Default server is apache"""

        # confirm the full path exists, if not, create it
        try:
            os.stat('%s/%s' %(self.camppath, settings.WEB_CONFIG_BASE) )
        except OSError, e:
            os.makedirs('%s/%s' %(self.camppath, settings.WEB_CONFIG_BASE), 0775)

        # write the config file out
        # assuming here that the full directory structure is built
        self.web_conf_file = '''%s/%s/%s''' % (self.camppath, settings.WEB_CONFIG_BASE, settings.WEB_CONFIG_FILE)

        file = open(self.web_conf_file, 'w+')
        if settings.WEB_DELIVERY == "ALIAS":
            file.write('''Alias /%s %s/%s\n''' % (self.campname, self.camppath, settings.WEB_DOCROOT) )
            print """camp%d web alias config created""" % (self.camp_id)
        else:
            file.write(settings.VHOST_CONFIG % {'camp_id': self.camp_id, 'camppath': str(self.camppath)})
            print """camp%d web vhost config created""" % (self.camp_id)

        file.close()

    def remove_symlink_config(self):
        """remove the configuration link in the web server"""
        self.camppath = self.camp_info['path']

        rm_httpd_symlink_config = """/bin/rm -f %s/%s.conf""" % (settings.HTTPD_CONFIG_DIR, self.campname)
        result = self.func.command.run(rm_httpd_symlink_config)
        if result[settings.FUNC_WEB_HOST][0] != 0:
            raise CampError("""Unable to start web server for camp%d, contact an admin\n""" % (self.camp_id))

    def create_symlink_config(self):
        # do the symbolic link to httpd_config_root
        symlink_httpd_config = '''/bin/ln -s %s %s/%s.conf''' % (self.web_conf_file, settings.HTTPD_CONFIG_DIR, self.campname)
        result = self.func.command.run(symlink_httpd_config)

    def create_log_dir(self):
        try:
            os.mkdir('%s/%s' %(self.camppath, settings.WEB_LOG_DIR))
            current_permissions = os.stat('%s/%s' %(self.camppath, settings.WEB_LOG_DIR)).st_mode
            os.chmod('%s/%s' %(self.camppath, settings.WEB_LOG_DIR), current_permissions | stat.S_ISGID )
            os.chown('%s/%s' %(self.camppath, settings.WEB_LOG_DIR), -1, os.getgid())
        except OSError, e:
            pass

        print """camp%d web log directory created""" % (self.camp_id)

    def push_camp(self):
        self.owner = self.camp_info['owner']
        self.camppath = self.camp_info['path']
        self.db_port = self.camp_info['db_port']
        self.rcs_remote = self.camp_info['rcs_remote']

        try:
            repo = git.Repo(self.camppath)
            repo.remotes.origin.push('refs/heads/master:refs/heads/master')
            print """camp%d code pushed""" % self.camp_id

        except NoSuchPathError, e:
            pass

    def remove_camp(self):
        self.camppath = self.camp_info['path']

        rm_camp_command = """/bin/rm -rf %s""" % self.camppath
        result = self.func.command.run(rm_camp_command)
        if result[settings.FUNC_WEB_HOST][0] != 0:
            print """Unable to remove camp%d, this is not a fatal error.  Please remove '%s' manually.""" % (self.camp_id, self.camppath)

    def restart_web(self):
        # restart the web service
        web_restart_cmd = """service httpd restart"""
        result = self.func.command.run(web_restart_cmd)
        time.sleep(5)
        result = self.func.command.run("(/bin/ps -ef | /bin/grep httpd | /bin/grep -v grep)")
        if result[settings.FUNC_WEB_HOST][0] != 0:
            raise CampError("""Unable to start web server for camp%d, contact an admin\n""" % (self.camp_id))

        print """camp%d web server restarted""" % (self.camp_id)

    def hooks_preconfig(self):
        for preconfig in settings.EXTERNAL_HOOKS:
            preconfig.web_preconfig(settings, self.project, self.camp_id)

    def hooks_postconfig(self):
        for postconfig in settings.EXTERNAL_HOOKS:
            postconfig.web_postconfig(settings, self.project, self.camp_id)

    def hooks_prestart(self):
        for prestart in settings.EXTERNAL_HOOKS:
            prestart.web_prestart(settings, self.project, self.camp_id)

    def hooks_poststart(self):
        for poststart in settings.EXTERNAL_HOOKS:
            poststart.web_poststart(settings, self.project, self.camp_id)

    def hooks_prestop(self):
        for prestop in settings.EXTERNAL_HOOKS:
            prestop.web_prestop(settings, self.project, self.camp_id)

    def hooks_poststop(self):
        for poststop in settings.EXTERNAL_HOOKS:
            poststop.web_poststop(settings, self.project, self.camp_id)

    def hooks_preremove(self):
        for preremove in settings.EXTERNAL_HOOKS:
            preremove.web_preremove(settings, self.project, self.camp_id)

    def hooks_postremove(self):
        for postremove in settings.EXTERNAL_HOOKS:
            postremove.web_postremove(settings, self.project, self.camp_id)
