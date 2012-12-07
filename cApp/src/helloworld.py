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
            self.response.out.write("""<a href='/PickSeries'> Pick Series To Follow</a><br>
                                        <a href='/UserSeries'> See Series You Follow</a><br>
                                        <a href='/UserReleases'> See This Week's Releases For Series You Follow</a><br>""")
            self.response.out.write("<a href='" +users.create_login_url(self.request.uri)+"'> Logout</a><br>")
        else:
            self.redirect(users.create_login_url(self.request.uri))

class pickSeries(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        cdb = cDB()
        if user:
            u = UserInfo(key_name = user.user_id())
            u.userLists=["Follow"]
            u.put()
            cuser= cUser(user)
            self.response.out.write(
            """<html>
            <body>
              <form action="/PickSeries" method="post">
            <textarea name="batchAdd" id="message"></textarea>
            <input type="submit" name="submit" id="submit" value="Send"/>
            </form>
            """)
            self.response.out.write(
            """<html>
              <form action="/PickSeries" method="post">""")
            
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
        val= self.request.get("batchAdd")
        for r in val.split('\n'):
            r=r.strip()
            if cdb.addSeriesToListForUser(r, "Follow", user):
                self.response.out.write(r +"<br>")
            

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
        if user:
            cuser= cUser(user)
            cdb.updateAllListsForUser(user)
            for l in cdb.getAllListsForUser(user):
                self.response.out.write(l.name+":<br>")
                for s in l.releases:
                    self.response.out.write(s +"<br>")
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
class UpdateSeries(webapp2.RequestHandler):
    def get(self):
        user= users.get_current_user()
        if user:
            cDBUtil.makeNextWednesday()
            cDBUtil.storeSeries()
            cDBUtil.updateAllSeries()
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
class SetUp(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            cdb = cDB()
            u = UserInfo(key_name = user.user_id())
            u.userLists=["Follow"]
            u.put()
            c = cList(key_name="Follow"+user.user_id())
            c.name="Follow"
            c.put()
            w= Wednesday()
            w.date= datetime.date(year=2012, month=12, day=5)
            w.put()
            r = Release()
            r.seriesName="dummy series"
            r.releaseName = "dummy series #1"
            r.put()
        else:
            self.redirect(users.create_login_url(self.request.uri))

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/PickSeries', pickSeries),
                               ('/UserSeries', userSeries),
                               ('/UserReleases', userReleases),
                               ('/update/UpdateSeries',UpdateSeries),
                               ('/update/Setup', SetUp)],
                              debug=True)