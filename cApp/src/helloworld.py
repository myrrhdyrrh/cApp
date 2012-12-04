'''
Created on Dec 3, 2012

@author: Frank
'''
import webapp2
from google.appengine.api import users
import cEntities as cE
import cDBUtil
from cUser import *
from cDB import *
class MainPage(webapp2.RequestHandler):
    def get(self):
        user= users.get_current_user()
        if user:
            cuser = cUser(user)
            cdb = cDB()
            test = cDBUtil.test()
            self.response.out.write("<table>")
            for s in test:
                self.response.out.write("<tr>")
                self.response.out.write("<td>"+s.seriesName +"</td>")
                self.response.out.write("<td>" +s.releaseName +"</td>")
                self.response.out.write("<tr>")
            self.response.out.write("</table>")

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)