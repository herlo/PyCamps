import os
import sys
import grp
import time
import stat
import shutil

#import re
#import time
#import shutil

import func.overlord.client as fc

import git
from git.errors import InvalidGitRepositoryError, NoSuchPathError, GitCommandError


import pycamps.config.settings as settings

class Web:

    def __init__(self, project, camp_id):
        self.func = fc.Client(settings.FUNC_WEB_HOST)
        self.camp_id = int(camp_id)
        self.campname = settings.CAMPS_BASENAME + str(self.camp_id)
        self.project = project

    def clone_docroot(self, remote_url, camp_info):

        self.owner = camp_info['owner']
        self.camppath = camp_info['path']
        self.db_port = camp_info['db_port']

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

    def create_symlink_config(self):
        # do the symbolic link to httpd_config_root
        symlink_httpd_config = '''/bin/ln -s %s %s/%s.conf''' % (self.web_conf_file, settings.HTTP_CONFIG_DIR, self.campname)
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

    def restart_web(self):
        # restart the web service
        web_restart_cmd = """service httpd restart"""
        result = self.func.command.run(web_restart_cmd)
        time.sleep(5)
        result = self.func.command.run("(/bin/ps -ef | /bin/grep httpd | /bin/grep -v grep)")
        if result[settings.FUNC_WEB_HOST][0] != 0:
            raise CampError("""Unable to start web server for camp%d, contact an admin\n""" % (self.camp_id))

        print """camp%d web server restarted""" % (self.camp_id)

    def hooks_pre(self):
        pass

    def hooks_post(self):
        pass
