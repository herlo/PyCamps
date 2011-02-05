# Main class for pycamps

import os
import sys
import re
import git
import time
import shutil

import func.overlord.client as fc

from db import *
import settings

class Camps:
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
        except git.GitCommandError:
            stderr_value = 'Unknown'
            print "The following error occurred: %s" % stderr_value

    def _start_camp_db(self, func_client, camp):
        result = func_client.command.run("/usr/bin/mysqld_multi start %s" % camp)

    def _stop_camp_db(self, func_client, camp):
        func_client.command.run("/usr/bin/mysqld_multi stop %s" % camp)

    def do_stop(self, svc, camp_id=None):
        if camp_id == None:
            camp_id = self._get_camp_id()
            if camp_id == None:
                return 0
        if svc == "db":
            print "Stopping database on camp%s" % camp_id
            client = fc.Client(settings.DB_HOST)
            self._stop_camp_db(client, camp_id)
            # wait for it to stop
            time.sleep(5)
            # should actually check that the db is stopped 
            print "camp%s database successfully stopped" % camp_id

        if svc == "web":
            pass

    def do_start(self, svc, camp_id=None):
        if camp_id == None:
            camp_id = self._get_camp_id()
            if camp_id == None:
                return 0
        if svc == "db":
            print "Starting database on camp%s" % camp_id
            client = fc.Client(settings.DB_HOST)
            self._start_camp_db(client, camp_id)
            # wait for it to start
            time.sleep(5)
            print "camp%s database successfully started" % camp_id
        if svc == "web":
            print "camp%s webserver successfully started" % camp_id
            pass

    def _get_camp_id(self):
        """Attempt to obtain the camp_id by looking at the basename of the path.  
           If the path is not in a camp, this function will fail."""
        camp_basename = os.path.basename(os.getcwd())
        if re.match("^%s\d+$" % settings.CAMPS_BASENAME, camp_basename):
            return re.split("^%s" % settings.CAMPS_BASENAME, camp_basename)[1]
        else:
            return None

    def _clone_db_lvm_snap(self, client):
        """Clones the campmaster db into a particular camp db 
        using logical volume snapshots"""
        
        lv_snapshot_cmd = "lvcreate -L %s -s -p rw -n %s /dev/%s/%s" % (settings.CAMPS_LV_SIZE, settings.CAMPS_BASENAME + str(self.camp_id), settings.CAMPS_VG, settings.CAMPS_LV)
        client.command.run(lv_snapshot_cmd)
        print "camp%d database snapshot complete" % self.camp_id

    def _clone_db_rsync(self, client):
        """Clones the campmaster db into a particular camp db 
        using logical volume snapshots"""

    def _chown_db_path(self, client):
        rsync_cmd = "/usr/bin/rsync -a %s/%smaster/* %s/%s" % (settings.DB_ROOT, settings.CAMPS_BASENAME, settings.DB_ROOT, settings.CAMPS_BASENAME + str(self.camp_id))
        client.command.run(rsync_cmd)
        chown_cmd = "/bin/chown -R %s.%s %s/%s" % (settings.DB_USER, settings.DB_GROUP, settings.DB_ROOT, settings.CAMPS_BASENAME + str(self.camp_id))
        client.command.run(chown_cmd)

    def _add_db_config(self, client):
        mysql_config = "echo '\n%s\n' >> /etc/my.cnf" % (settings.DB_CONFIG % {'camp_id': self.camp_id, 'port': (settings.DB_BASE_PORT + self.camp_id)})
        client.command.run(mysql_config)
        print "camp%d database configured" % self.camp_id

    def clone_db(self):
        """Clones the campmaster db into a particular camp db
        and adds appropriate configs into the database itself"""

        # determine the method of cloning
        client = fc.Client(settings.DB_HOST)
        
        if settings.DB_CLONE_METHOD == "RSYNC":
            self._clone_db_rsync(client)
        else:
            self._clone_db_lvm_snap(client)
        self._chown_db_path(client)
        self._add_db_config(client)

    def do_remove(self, options, arguments):
        """Removes a camp directory and its corresponding db directory"""

        # add something here to check for pycampsadmin later on

        camp_id = self._get_camp_id()
        if camp_id != None:
            return 0

        camp_id = arguments[0]
        try:
            filestats = os.stat('%s/%s' %(settings.CAMPS_ROOT, settings.CAMPS_BASENAME + str(camp_id)) )
        except OSError:
            return 1

        if os.getuid() != filestats[4]:
            return 2

        client = fc.Client(settings.DB_HOST)
        # self._stop_camp_db(client, camp_id)
        rm_db_cmd = "/bin/rm -r %s/%s" % (settings.DB_ROOT, settings.CAMPS_BASENAME + str(camp_id))
        # ensure the db is stopped for this camp
        self._stop_camp_db(client, camp_id)
        print "camp%s database stopped" % camp_id
        client.command.run(rm_db_cmd)
        print "camp%s database directory removed" % camp_id
        os.chdir(settings.CAMPS_ROOT)
        shutil.rmtree("%s/%s" % (settings.CAMPS_ROOT, settings.CAMPS_BASENAME + str(camp_id)) )
        print "camp%s directory removed" % camp_id

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
        self.do_start('web', camp_id=self.camp_id)
        self.clone_db()
        self.do_start('db', camp_id=self.camp_id)

