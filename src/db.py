# PyCamps database manager

import os
import sqlite3 as sqlite

import settings

class PyCampsDB:
    
    def __init__(self):
        if os.path.isfile(settings.CAMPS_DB):
            self.conn = sqlite.connect(settings.CAMPS_DB)
        else:
            self.conn = sqlite.connect(settings.CAMPS_DB)
            self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE camps (id INTEGER PRIMARY KEY, description varchar(50), path TEXT, owner VARCHAR(50), db_user VARCHAR(25), db_pass VARCHAR(25), db_host VARCHAR(50), db_port INTEGER, status varchar(20), created DATE)''') 
        c.execute('''CREATE TRIGGER insert_camps_createdNow AFTER INSERT ON camps BEGIN UPDATE camps SET created = DATETIME('NOW') WHERE rowid = new.rowid; END''')
        self.conn.commit()
        c.close()

    def create_camp(self, description, path, owner, db_user=None, db_pass=None, db_host=None, db_port=None):
        c = self.conn.cursor()
        c.execute('''INSERT INTO camps (description, path, owner, db_user, db_pass, db_host, status) 
            values ('%s', '%s', '%s', '%s', '%s', '%s', '%s')''' % (description, path, owner, db_user, db_pass, db_host, 'ACTIVE'))
        camp_id = c.execute('''select max(id) from camps''').fetchone()[0]
        c.execute('''UPDATE camps set db_port = %d where id = %d''' %((settings.DB_BASE_PORT + camp_id), camp_id))
        self.conn.commit()
        c.close()
        return camp_id

def main():                         
    camp_db = PyCampsDB()
    infos = camp_db.create_camp('test camp', '/home', 'clints', 'test', 'test', 'localhost')
    print "Infos: %s" % str(infos)

if __name__ == "__main__":
    main()
