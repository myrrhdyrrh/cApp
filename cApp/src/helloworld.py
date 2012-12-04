'''
Created on Dec 3, 2012

@author: Frank
'''
import webapp2
from google.appengine.api import users
import cEntities as cE
from cUser import *
from cDB import *
class MainPage(webapp2.RequestHandler):
    def get(self):
        user= users.get_current_user()
        if user:
            cuser = cUser(user)
            cdb = cDB()
            cdb.createInfoForUser(cuser.getUser())
            cdb.createListForUser("test", cuser.user)
            cdb.addSeriesToListForUser("mytest", "test",cuser.getUser())
            for s in cdb.getListForUser("test", cuser.getUser()).series:
                self.response.out.write("1")
                self.response.out.write(s)

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)