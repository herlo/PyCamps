import os
import sys
import time
import shutil

import func.overlord.client as fc

from pycamps.campserror import *
from pycamps.config.projectsdb import *
import pycamps.config.settings as settings

class DB:

    def __init__(self, project, camp_id):
        self.func = fc.Client(settings.FUNC_DB_HOST)
        self.camp_id = int(camp_id)
        self.campname = (settings.CAMPS_BASENAME + str(self.camp_id))
        self.project = project

    def set_camp_info(self, camp_info):
        self.camp_info = camp_info

    def _clone_db_lvm_snap(self, lv_infos):
        """Clones the campmaster db into a particular camp db 
        using logical volume snapshots"""
        
        lv_snapshot_cmd = "/sbin/lvcreate -L %s -s -p rw -n %s /dev/%s/%s" % (lv_infos['snap'], settings.CAMPS_BASENAME + str(self.camp_id), lv_infos['vg'], lv_infos['lv'])
        self.func.command.run(lv_snapshot_cmd)
        print "camp%d database snapshot complete" % self.camp_id

    def _clone_db_rsync(self):
        """Clones the campmaster db into a particular camp db 
        using logical volume snapshots"""

        rsync_cmd = "/usr/bin/rsync -a %s/%smaster/* %s/%s" % (settings.DB_ROOT, settings.CAMPS_BASENAME, settings.DB_ROOT, settings.CAMPS_BASENAME + str(self.camp_id))
        self.func.command.run(rsync_cmd)
        print "camp%d database rsync completed successfully" % self.camp_id

    def _chown_db_path(self):
        chown_cmd = "/bin/chown -R %s.%s %s/%s" % (settings.DB_USER, settings.DB_GROUP, settings.DB_ROOT, settings.CAMPS_BASENAME + str(self.camp_id))
        self.func.command.run(chown_cmd)

    def _add_db_config(self):
        mysql_config = "echo '\n%s\n' >> /etc/my.cnf" % (settings.DB_CONFIG % {'camp_id': self.camp_id, 'port': (settings.DB_BASE_PORT + self.camp_id)})
        self.func.command.run(mysql_config)
        print "camp%d database configured" % self.camp_id

    def clone_db(self, lv_infos):
        """Clones the campmaster db into a particular camp db
        and adds appropriate configs into the database itself"""

        self._clone_db_lvm_snap(lv_infos)
        self._chown_db_path()
        self._add_db_config()

    def start_db(self):
        result = self.func.command.run("/usr/bin/mysqld_multi start %d" % self.camp_id)
        time.sleep(5)
        result = self.func.command.run("(/bin/ps -ef | /bin/grep mysql | /bin/grep %d | /bin/grep -v grep)" % self.camp_id)
        if result[settings.FUNC_DB_HOST][0] != 0:
            raise CampError("""Unable to start db for camp%d, contact an admin\n""" % (self.camp_id))
        print "camp%d database started" % self.camp_id

    def stop_db(self):
        result = self.func.command.run("/usr/bin/mysqld_multi stop %s" % self.camp_id)
        time.sleep(5)
        result = self.func.command.run("(/bin/ps -ef | /bin/grep mysql | /bin/grep %s | /bin/grep -v grep)" % self.campname)
        if result[settings.FUNC_DB_HOST][0] != 1:
            raise CampError("""Unable to stop db for camp%s, contact an admin\n""" % self.camp_id)
        print "camp%d database stopped" % self.camp_id

    def remove_db_config(self):
        pass

    def unmount_db(self, lv_infos):
        result = self.func.command.run("/bin/umount -l /dev/mapper/%s-%s" % (lv_infos['vg'], self.campname))
        time.sleep(5)
        result = self.func.command.run("(/bin/df -h /dev/mapper/%s-%s | grep %s)" % (lv_infos['vg'], self.campname, self.campname))
        if result[settings.FUNC_DB_HOST][0] != 1:
            raise CampError("""Unable to unmount db for camp%s, contact an admin\n""" % self.camp_id)
        print "camp%d database unmounted" % self.camp_id

    def remove_db_lv(self, lv_infos):
        # remove the device mapped device
        self.func.command.run("dmsetup remove /dev/mapper/%s-%s" % (lv_infos['vg'], self.campname))
        # remove the copy-on-write for the device mapped device
        self.func.command.run("dmsetup remove /dev/mapper/%s-%s-cow" % (lv_infos['vg'], self.campname))
        # remove the logical volume
        result = self.func.command.run("/sbin/lvremove -f /dev/mapper/%s-%s" % (lv_infos['vg'], self.campname))
        time.sleep(5)
        result = self.func.command.run("/bin/lvs | grep %s" % self.campname)
        if result[settings.FUNC_DB_HOST][0] != 1:
            raise CampError("""Unable to remove db for camp%s, contact an admin\n""" % self.camp_id)
        print "camp%d database logical volume removed" % self.camp_id

    # lots of hooks to handle extra functionality per application

    def hooks_preconfig(self):
        for preconfig in settings.EXTERNAL_HOOKS:
            preconfig.db_preconfig(settings, self.project, self.camp_id)

    def hooks_postconfig(self):
        for postconfig in settings.EXTERNAL_HOOKS:
            postconfig.db_postconfig(settings, self.project, self.camp_id)

    def hooks_poststart(self):
        for poststart in settings.EXTERNAL_HOOKS:
            poststart.db_poststart(settings, self.project, self.camp_id)

    def hooks_prestop(self):
        for prestop in settings.EXTERNAL_HOOKS:
            prestop.db_prestop(settings, self.project, self.camp_id)

    def hooks_poststop(self):
        for poststop in settings.EXTERNAL_HOOKS:
            poststop.db_poststop(settings, self.project, self.camp_id)

    def hooks_preremove(self):
        for preremove in settings.EXTERNAL_HOOKS:
            preremove.db_preremove(settings, self.project, self.camp_id)

    def hooks_postremove(self):
        for postremove in settings.EXTERNAL_HOOKS:
            postremove.db_postremove(settings, self.project, self.camp_id)
