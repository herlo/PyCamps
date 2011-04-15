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

        if project in settings.EXTERNAL_HOOKS:
            self.hook = settings.EXTERNAL_HOOKS[project]
        else:
            self.hook = None

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
        mysql_config = "echo '\n%s\n' >> /etc/my.cnf" % (settings.DB_CONFIG % {'camps_base': settings.CAMPS_ROOT, 'camps_basename': settings.CAMPS_BASENAME, 'camp_id': self.camp_id, 'port': (settings.DB_BASE_PORT + self.camp_id)})
        self.func.command.run(mysql_config)
        print "camp%d database configured" % self.camp_id

    def db_shell(self):

        command = """/usr/bin/mysql"""
        args = ["""--no-auto-rehash""", """--user=root""", """--port=%d""" % int(settings.DB_BASE_PORT + self.camp_id), """--socket=%s/%s/%s""" % (settings.DB_ROOT, self.campname, settings.DB_SOCKET)]
        if settings.DB_ROOT_PASSWORD:
            args.append("""--password=%s""" % settings.DB_ROOT_PASSWORD)
        os.execvp(command, args)

    def clone_db(self, lv_infos, db_config=True):
        """Clones the campmaster db into a particular camp db
        and adds appropriate configs into the database itself"""

        self._clone_db_lvm_snap(lv_infos)
        self._chown_db_path()
        if db_config:
            self._add_db_config()

    def is_up(self):
        result = self.func.command.run("(/bin/ps -ef | /bin/grep mysql | /bin/grep %s | /bin/grep -v grep)" % (settings.CAMPS_BASENAME + str(self.camp_id)))
        if result[settings.FUNC_DB_HOST][0] != 0:
            return False
        return True

    def disk_usage(self, db_location):
        self.func.command.run("ls %s" % db_location)
        result = self.func.command.run("/bin/df -h %s" % db_location)
        if result[settings.FUNC_DB_HOST][0] != 0:
            return None
        res = str(result[settings.FUNC_DB_HOST][1].split('\n')[2])
#        print "res: %s" % res
        return res.strip().split('  ')[0:3]

    def start_db(self):
        result = self.func.command.run("/usr/bin/mysqld_multi start %d" % self.camp_id)
        time.sleep(5)
        result = self.func.command.run("(/bin/ps -ef | /bin/grep mysql | /bin/grep %d | /bin/grep -v grep)" % self.camp_id)
        if result[settings.FUNC_DB_HOST][0] != 0:
            raise CampError("""Unable to start db for camp%d, contact an admin\n""" % (self.camp_id))
        print "camp%d database started" % self.camp_id

    def stop_db(self):
        command = """/usr/bin/mysqld_multi stop %s""" % str(self.camp_id)
        if settings.DB_ROOT_PASSWORD:
            command += """ --password='%s'""" % settings.DB_ROOT_PASSWORD

        result = self.func.command.run(command)
        time.sleep(10)
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
         if self.hook:
            self.hook.db_preconfig(settings, self.project, self.camp_id)

    def hooks_postconfig(self):
         if self.hook:
            self.hook.db_postconfig(settings, self.project, self.camp_id)

    def hooks_prestart(self):
         if self.hook:
            self.hook.db_prestart(settings, self.project, self.camp_id)

    def hooks_poststart(self):
         if self.hook:
            self.hook.db_poststart(settings, self.project, self.camp_id)

    def hooks_prestop(self):
         if self.hook:
            self.hook.db_prestop(settings, self.project, self.camp_id)

    def hooks_poststop(self):
         if self.hook:
            self.hook.db_poststop(settings, self.project, self.camp_id)

    def hooks_preremove(self):
         if self.hook:
            self.hook.db_preremove(settings, self.project, self.camp_id)

    def hooks_postremove(self):
        if self.hook:
            self.hook.db_postremove(settings, self.project, self.camp_id)
