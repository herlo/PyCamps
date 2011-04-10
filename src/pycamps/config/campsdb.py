# PyCamps database manager

import os
try:
    import sqlite3 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

import pycamps.config.settings as settings

class CampsDB:
    
    def __init__(self):
        if os.path.isfile(settings.CAMPS_DB):
            self.conn = sqlite.connect(settings.CAMPS_DB)
        else:
            print 'camps db path: %s' % settings.CAMPS_DB
            self.conn = sqlite.connect(settings.CAMPS_DB)
            self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE camps (id INTEGER PRIMARY KEY, project VARCHAR(50), description VARCHAR(50), 
                path TEXT, owner VARCHAR(50), rcs_remote TEXT, db_host VARCHAR(50), db_port INTEGER, created DATE, active BOOLEAN)""") 
        c.execute("""CREATE TRIGGER insert_camps_createdNow AFTER INSERT ON camps BEGIN UPDATE camps 
                SET created = DATETIME('NOW') WHERE rowid = new.rowid; END""")
        self.conn.commit()
        c.close()

    def create_camp(self, project, description, path, owner, db_host):
        c = self.conn.cursor()
        c.execute("""INSERT INTO camps (project, description,  owner, db_host) 
            values ('%s', '%s', '%s', '%s')""" % (project, description, owner, db_host))
        camp_id = c.execute('''select max(id) from camps''').fetchone()[0]
        c.execute('''UPDATE camps set path = '%s/%s' where id = %d''' %(path, ('camp' + str(camp_id)), camp_id))
        c.execute('''UPDATE camps set db_port = %d where id = %d''' %((settings.DB_BASE_PORT + camp_id), camp_id))
        self.conn.commit()
        c.close()
        return camp_id

    def set_remote(self, camp_id, remote_url):
        c = self.conn.cursor()
        c.execute("""UPDATE camps set rcs_remote = '%s' where id = %s""" % (remote_url, camp_id))
        self.conn.commit()
        c.close()

    def activate_camp(self, camp_id):
        c = self.conn.cursor()
        c.execute("""UPDATE camps set active = 1 where id = %s""" % camp_id)
        self.conn.commit()
        c.close()

    def deactivate_camp(self, camp_id):
        c = self.conn.cursor()
        c.execute("""UPDATE camps set active = 0 where id = %s""" % camp_id)
        self.conn.commit()
        c.close()

    def delete_camp(self, camp_id):
        c = self.conn.cursor()
        c.execute("""delete from camps where id = %s""" % camp_id)
        self.conn.commit()
        c.close()

    def camp_list(self, list_all=None, id=None):
        c = self.conn.cursor()
        list_sql = """SELECT * from camps"""
        if id:
            list_sql += """ where id = %d""" % id
        if id == None and (list_all == None or list_all == False):
            list_sql += """ where active = 1"""

        camp_list = c.execute(list_sql)
        camps = camp_list.fetchall()
        c.close()
        return camps

    def get_camp_info(self, camp_id):
        c = self.conn.cursor()
        info_sql = """SELECT project, path, owner, db_port, rcs_remote from camps where id = '%d'""" % int(camp_id)
        result = c.execute(info_sql)
        proj, path, owner, db_port, rcs_remote = result.fetchone()
        c.close()
        return {'proj': proj, 'path': path, 'owner': owner, 'db_port': db_port, 'rcs_remote': rcs_remote} 

    def get_owner(self, camp_id):
        return self.get_camp_info(camp_id)['owner']

    def get_remote(self, camp_id):
        return self.get_camp_info(camp_id)['rcs_remote']

    def get_project(self, camp_id):
        return self.get_camp_info(camp_id)['proj']

def main():                         
    camp_db = PyCampsDB()
    infos = camp_db.create_camp('test camp', '/home', 'clints', 'test', 'test', 'localhost')
    print "Infos: %s" % str(infos)

if __name__ == "__main__":
    main()
