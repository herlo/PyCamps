# PyCamps database manager

import sys
import os
try:
    import sqlite3 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

from pycamps.campserror import *
from pycamps.config.campsdb import CampsDB
import pycamps.config.settings as settings

class CampsAdminDB():
    
    def __init__(self):
        if os.path.isfile(settings.CAMPS_DB):
            self.conn = sqlite.connect(settings.CAMPS_DB)
        else:
            self.conn = sqlite.connect(settings.CAMPS_DB)
            self._create_tables()
            # detection of tables could work better
            # but this hack to just create tables 
            # for CampsDB works well, no need to change
            c = CampsDB()
            c._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE projects (id INTEGER PRIMARY KEY, name varchar(50) UNIQUE, description varchar(50), 
                    web_server varchar(50), rcs_remote TEXT, db_server varchar(50), db_lv TEXT, db_lv_snap_size varchar(10), 
                    owner VARCHAR(50), created DATE, active BOOLEAN)''') 
        c.execute('''CREATE TRIGGER insert_projects_createdNow AFTER INSERT ON projects BEGIN UPDATE projects SET created = DATETIME('NOW') WHERE rowid = new.rowid; END''')
        self.conn.commit()
        c.close()

    def create_project(self, name, description, rcs_remote, db_lv, db_lv_snap_size, owner, web_server='httpd', db_server='mysql'):
        try:
            c = self.conn.cursor()
            c.execute("""INSERT INTO projects (name, description, web_server, rcs_remote, 
                db_server, db_lv, db_lv_snap_size, owner) 
                values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', 
                '%s')""" % (name, description, web_server, rcs_remote, db_server, db_lv, db_lv_snap_size, owner))
            proj_id = c.execute("""select max(id) from projects""").fetchone()[0]
            self.conn.commit()
            c.close()
        except sqlite.IntegrityError, e:
            raise CampError("""Project '%s' already exists""" % name)
        return proj_id

    def edit_project(self, name, desc=None, remote=None, lv=None, snap=None):
        c = self.conn.cursor()
        comma = False
        sql = """UPDATE projects set"""
        if desc:
            sql += """description = '%s'""" % desc
            comma = True
        if remote:
            if comma:
                sql += ""","""
            sql += """ rcs_remote = '%s'""" % remote
            comma = True
        if lv:
            if comma:
                sql += ""","""
            sql += """ db_lv = '%s'""" % lv
        if snap:
            if comma:
                sql += ""","""
            sql += """ db_lv_snap_size = '%s'""" % snap

        sql += """ where name = '%s'""" % name

        c.execute(sql)
        self.conn.commit()
        c.close()

    def activate_project(self, name):
        c = self.conn.cursor()
        c.execute("""UPDATE projects set active = 1 where name = '%s'""" % name)
        self.conn.commit()
        c.close()

    def deactivate_project(self, proj_name):
        c = self.conn.cursor()
        c.execute("""UPDATE projects set active = 0 where name = '%s'""" % proj_name)
        self.conn.commit()
        c.close()

    def project_list(self, list_all=None, proj_name=None):
        c = self.conn.cursor()
        list_sql = """SELECT * from projects"""
        if proj_name:
            list_sql += """ where name = '%s'""" % proj_name
        if proj_name == None and (list_all == None or list_all == False):
            list_sql += """ where active = 1"""
        proj_list = c.execute(list_sql)
        projects = proj_list.fetchall()
        c.close()
        return projects

    def delete_project(self, proj_name):
        c = self.conn.cursor()
        c.execute("""delete from projects where id = '%s'""" % proj_name)
        self.conn.commit()
        c.close()

    # getters and setters
    def get_remote(self, name):
        c = self.conn.cursor()
        r = c.execute("""select rcs_remote from projects where name = '%s'""" % name)
        remote = r.fetchone()[0]
        c.close()
        return remote

    def get_lv_info(self, name):
        c = self.conn.cursor()
        r = c.execute("""select db_lv, db_lv_snap_size from projects where name = '%s'""" % name)
        lvm, snap = r.fetchone()[0:]
        vg, lv = lvm.split('/')[2:]
        c.close()
        return {'vg': vg, 'lv': lv, 'snap': snap}

def main():                         

    ##### CampsAdminDB table structure #####
    # c.execute('''CREATE TABLE projects (id INTEGER PRIMARY KEY, name varchar(50) UNIQUE, description varchar(50), 
    # web_server varchar(50), rcs_remote TEXT, db_server varchar(50), db_lv TEXT, db_lv_snap_size varchar(10), 
    # owner VARCHAR(50), created DATE, active BOOLEAN)''') 
    # def create_project(self, name, description, rcs_remote, db_lv, db_lv_snap_size, owner, web_server='httpd', db_server='mysql'):
    #####

    proj_db = CampsAdminDB()
    infos = proj_db.create_project(sys.argv[1], 'xyz project http://xyz.com', 'git@github.com:herlo/PyCamps.git', 
                            '/dev/db/campmaster', '200m', 'clints')
    print "Infos: %s" % str(infos)
    print proj_db.get_lv_info(sys.argv[1])

if __name__ == "__main__":
    main()
