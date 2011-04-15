# wordpress hooks for pycamps

import MySQLdb
#
#   cursor.execute ("SELECT VERSION()")
#   row = cursor.fetchone ()
#   print "server version:", row[0]


class WPHooks:


    @classmethod
    def db_preconfig(self, settings, proj, camp_id):
        pass

    @classmethod
    def db_postconfig(self, settings, proj, camp_id):
        pass


    @classmethod
    def db_prestart(self, settings, proj, camp_id):
        pass

    @classmethod
    def db_poststart(self, settings, proj, camp_id):
        campname = settings.CAMPS_BASENAME + str(camp_id)
        conn = MySQLdb.connect (host = "%s" % settings.DB_HOST,
                                unix_socket = "%s/%s/%s" % (settings.DB_ROOT, campname, settings.DB_SOCKET),
                                user = "root",
                                passwd = "",
                                db = proj)
        cursor = conn.cursor ()
        sql = "update wp_options set option_value='http://%s.example.com' where option_value like 'http://%s%%';" % ( campname, settings.CAMPS_BASENAME ) 
#        print "SQL: %s" % sql
        cursor.execute( sql )
        cursor.close ()
        conn.close ()
    
    @classmethod
    def db_prestop(self, settings, proj, camp_id):
        pass

    @classmethod
    def db_poststop(self, settings, proj, camp_id):
        pass

    @classmethod
    def db_preremove(self, settings, proj, camp_id):
        pass

    @classmethod
    def db_postremove(self, settings, proj, camp_id):
        pass

    @classmethod
    def web_preconfig(self, settings, proj, camp_id):
        pass

    @classmethod
    def web_postconfig(self, settings, proj, camp_id):
        pass

    @classmethod
    def web_prestart(self, settings, proj, camp_id):
        pass

    @classmethod
    def web_poststart(self, settings, proj, camp_id):
        pass

    @classmethod
    def web_prestop(self, settings, proj, camp_id):
        pass

    @classmethod
    def web_poststop(self, settings, proj, camp_id):
        pass

    @classmethod
    def web_preremove(self, settings, proj, camp_id):
        pass

    @classmethod
    def web_postremove(self, settings, proj, camp_id):
        pass
