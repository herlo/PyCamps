# PyCamps database manager

import os
try:
    import sqlite3 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

from pycamps.campserror import *
import pycamps.config.settings as settings

class CampsAdminDB:
    
    def __init__(self):
        if os.path.isfile(settings.CAMPS_DB):
            self.conn = sqlite.connect(settings.CAMPS_DB)
        else:
            self.conn = sqlite.connect(settings.CAMPS_DB)
            self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE projects (id INTEGER PRIMARY KEY, name varchar(50) UNIQUE, description varchar(50), 
                    web_server varchar(50), rcs_remote TEXT, db_server varchar(50), db_lv TEXT, db_lv_snap_size varchar(10), 
                    owner VARCHAR(50), created DATE, active BOOLEAN)''') 
        c.execute('''CREATE TRIGGER insert_projects_createdNow AFTER INSERT ON projects BEGIN UPDATE projects SET created = DATETIME('NOW'), active = 1 WHERE rowid = new.rowid; END''')
        self.conn.commit()
        c.close()

    def create_project(self, name, description, web_server, rcs_remote, db_server, db_lv, db_lv_snap_size, owner):
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
            raise CampError("""Project %s already exists""" % name)
        return proj_id

    def activate_project(self, name):
        c = self.conn.cursor()
        c.execute("""UPDATE projects set active = 1 where name = '%s'""" %(name))
        self.conn.commit()
        c.close()

    def deactivate_project(self, proj_name):
        c = self.conn.cursor()
        c.execute("""UPDATE projects set active = 0 where name = '%s'""" % proj_name)
        self.conn.commit()

    def project_list(self, list_all=None):
        c = self.conn.cursor()
        list_sql = '''SELECT * from projects'''
        if list_all == None or list_all == False:
            list_sql += ''' where active = 1'''
        proj_list = c.execute(list_sql)
        return proj_list.fetchall()

    def delete_project(self, proj_name):
        c = self.conn.cursor()
        c.execute("""delete from projects where id = '%s'""" % proj_name)
        self.conn.commit()

def main():                         
    proj_db = PyCampsAdminDB()
    infos = proj_db.create_project('xyz', 'xyz project http://xyz.com',
                                'httpd', 'git@github.com:herlo/PyCamps.git', 'mysql', '/dev/db/pycampmaster', 'clints')
    print "Infos: %s" % str(infos)

if __name__ == "__main__":
    main()
