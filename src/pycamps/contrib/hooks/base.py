# base hooks for pycamps

class BaseHooks:

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
        pass
    
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
