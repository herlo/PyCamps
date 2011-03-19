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
        c.execute('''CREATE TABLE camps (id INTEGER PRIMARY KEY, project VARCHAR(50), description VARCHAR(50), 
                path TEXT, owner VARCHAR(50), db_host VARCHAR(50), db_port INTEGER, created DATE, active BOOLEAN)''') 
        c.execute('''CREATE TRIGGER insert_camps_createdNow AFTER INSERT ON camps BEGIN UPDATE camps 
                SET created = DATETIME('NOW') WHERE rowid = new.rowid; END''')
        self.conn.commit()
        c.close()

    def create_camp(self, project, description, path, owner, db_host):
        c = self.conn.cursor()
        c.execute("""INSERT INTO camps (project, description, path, owner, db_host) 
            values ('%s', '%s', '%s', '%s', '%s')""" % (project, description, path, owner, db_host))
        camp_id = c.execute('''select max(id) from camps''').fetchone()[0]
        c.execute('''UPDATE camps set db_port = %d where id = %d''' %((settings.DB_BASE_PORT + camp_id), camp_id))
        self.conn.commit()
        c.close()
        return camp_id

    def camp_list(self, list_all=None):
        c = self.conn.cursor()
        list_sql = '''SELECT * from camps'''
        if list_all == None or list_all == False:
            list_sql += ''' where active = 1'''
        camp_list = c.execute(list_sql)
        return camp_list.fetchall()

    def deactivate_camp(self, camp_id):
        c = self.conn.cursor()
        c.execute('''UPDATE camps set active = 0 where id = %s''' % camp_id)
        self.conn.commit()

    def delete_camp(self, camp_id):
        c = self.conn.cursor()
        c.execute('''delete from camps where id = %s''' % camp_id)
        self.conn.commit()

def main():                         
    camp_db = PyCampsDB()
    infos = camp_db.create_camp('test camp', '/home', 'clints', 'test', 'test', 'localhost')
    print "Infos: %s" % str(infos)

if __name__ == "__main__":
    main()
