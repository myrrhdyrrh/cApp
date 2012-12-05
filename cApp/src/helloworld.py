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
            
            """
            self.response.out.write("<table>")
            for s in test:
                self.response.out.write("<tr>")
                self.response.out.write("<td>"+s.seriesName +"</td>")
                self.response.out.write("<td>" +s.releaseName +"</td>")
                self.response.out.write("<tr>")
            self.response.out.write("</table>")
            """
        else:
            self.redirect(users.create_login_url(self.request.uri))

class pickSeries(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            cuser= cUser(user)
            self.response.out.write(
            """<html>
            <body>
              <form action="/pickSeries" method="post">""")
            cdb = cDB()
            for s in cdb.getSeriesUserDoesNotFollow(user):
                self.response.out.write("<input type='checkbox' name='seriesName' value='")
                self.response.out.write(s)
                self.response.out.write("'>")
                self.response.out.write(s)
                self.response.out.write("<br>")
                  
            
            self.response.out.write("""<input type="submit" value="Submit">
              </form>
            </body>
          </html>""")
        else:
            self.redirect(users.create_login_url(self.request.uri))
                          
    def post(self):
        results = self.request.get_all("seriesName")
        cdb=cDB()
        user =users.get_current_user()
        if not cdb.userExists(user):
            cdb.createInfoForUser(user)
        self.response.out.write("added to your follow list:<br>")
        for r in results:
            self.response.out.write(r +"<br>")
            cdb.addSeriesToListForUser(r, "Follow", user)
            

class userSeries(webapp2.RequestHandler):
    """
    page for showing all series a user currently has in any list
    """
    def get(self):
        user=users.get_current_user()
        
        cdb=cDB()
        if user:
            cuser=cUser(user)
            series = cdb.getAllSeriesForUser(cuser.getUser())
            series = [s.name for s in series]
            for s in sorted(series):
                self.response.out.write(s+"<br>")
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
class userReleases(webapp2.RequestHandler):
    """
    page showing user their releases for the week
    """
    def get(self):
        user=users.get_current_user()
        cdb = cDB()
        cDBUtil.updateAllSeries()
        #db.delete(cList.all())
        if user:
            cuser= cUser(user)
            cdb.updateAllListsForUser(user)
            for l in cdb.getAllListsForUser(user):
                self.response.out.write(+l.name+":<br>")
                for s in l.releases:
                    self.response.out.write(s +"<br>")
        else:
            self.redirect(users.create_login_url(self.request.uri))
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/pickSeries', pickSeries),
                               ('/UserSeries', userSeries),
                               ('/UserReleases', userReleases)],
                              debug=True)