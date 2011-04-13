# magento hooks for pycamps

from pycamps.contrib.hooks.base import BaseHooks

class MagentoHooks(BaseHooks):

#    @classmethod
#    def db_preconfig(self, settings, proj, camp_id):
#        print "calling db_preconfig"
#        pass

    @classmethod
    def db_postconfig(self, settings, proj, camp_id):
        pass

    @classmethod
    def db_poststart(self, settings, proj, camp_id):
        pass

    @classmethod
    def web_preconfig(self, settings, proj, camp_id):
        pass

    @classmethod
    def web_postconfig(self, settings, proj, camp_id):
        pass

    @classmethod
    def web_poststart(self, settings, proj, camp_id):
        pass
