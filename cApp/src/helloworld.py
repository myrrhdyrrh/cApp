'''
Created on Dec 3, 2012

@author: Frank
'''
import webapp2,os
from google.appengine.api import users
from google.appengine.ext.webapp import template
import cEntities as cE
import cDBUtil
from cUser import *
from cDB import *


path = os.path.join(os.path.dirname(__file__)+"\\templates\\","navigation.html")

def getNav(url):
    """
    gets the navigation bar, using provided url to generate the logout url
    """
    tv= { 'url':url}
    return template.render(path,tv)


    
def getLogoutUrl(item):
    """
    gets the logout url
    """
    return users.create_logout_url(item.request.uri)

def writeNavBar(item):
    """
    write the navigation bar to the response of the given item
    """
    item.response.out.write(getNav(getLogoutUrl(item))+"<br>")
class MainPage(webapp2.RequestHandler):
    def get(self):
        user= users.get_current_user()
        if user:
            writeNavBar(self)
        else:
            self.redirect(users.create_login_url(self.request.uri))

class pickSeries(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        cdb = cDB()
        if user:
            #u = UserInfo(key_name = user.user_id())
            #u.userLists=["Follow"+user.user_id()]
            #u.put()
            cuser= cUser(user)
            
            writeNavBar(self)
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
        writeNavBar(self)
        self.response.out.write("added to your follow list:<br>")
        for r in results:
            self.response.out.write(r +"<br>")
            cdb.addSeriesToListForUser(r, "Follow", user)
        val= self.request.get("batchAdd")
        for r in val.split('\n'):
            r=r.strip()
            if r!="":
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
            writeNavBar(self)
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
            writeNavBar(self)
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
        cDBUtil.makeNextWednesday()
        cDBUtil.storeSeries()
        cDBUtil.updateAllSeries()
            
class SetUp(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            cdb = cDB()
            u = UserInfo(key_name = user.user_id())
            u.userLists=["Follow"+user.user_id()]
            u.put()
            c = cList(key_name="Follow"+user.user_id())
            c.name="Follow"
            c.series=["dummy series"]
            c.releases=["dummy series #1"]
            c.put()
            w= Wednesday()
            w.date= datetime.date(year=2012, month=12, day=5)
            w.put()
            t = cDBUtil.makeNextWednesday()
            while not t:
                t=cDBUtil.makeNextWednesday()
            r = Release()
            r.seriesName="dummy series"
            r.releaseName = "dummy series #1"
            r.put()
            #self.redirect("/update/UpdateSeries")
        else:
            self.redirect(users.create_login_url(self.request.uri))

class Test(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("hello")
        
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/PickSeries', pickSeries),
                               ('/UserSeries', userSeries),
                               ('/UserReleases', userReleases),
                               ('/update/UpdateSeries',UpdateSeries),
                               ('/update/Setup', SetUp)],
                              debug=True)