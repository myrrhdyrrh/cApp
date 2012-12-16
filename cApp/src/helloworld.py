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


def getTemplatePath(name):
    """
    get the path for a specified template file
    """
    return os.path.dirname(__file__)+"/templates/"+name+".html"

path = getTemplatePath("navigation")

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
            writeNavBar(self)
            series = cdb.getSeriesUserDoesNotFollow(user)
            tv = { 'series': series
                  }
            self.response.out.write(template.render(getTemplatePath("PickSeries"), tv))

            
        else:
            self.redirect(users.create_login_url(self.request.uri))
                          
    def post(self):
        results = self.request.get_all("seriesName")
        cdb=cDB()
        user =users.get_current_user()
        results = [r for r in results if cdb.addSeriesToListForUser(r, "Follow", user)]
        r2 = self.request.get("batchAdd")
        r2=[r.strip() for r in r2 if (cdb.addSeriesToListForUser(r.strip(), "Follow", user))]
        results.extend(r2)
        tv={"results":results}
        writeNavBar(self)
        self.response.out.write(template.render(getTemplatePath("results"), tv))
        
            

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
            tv= {"results":sorted(series)}
            self.response.out.write(template.render(getTemplatePath("UserResults"), tv))
    
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
                tv = {"results": l.releases}
                self.response.out.write(template.render(getTemplatePath("UserResults"), tv))
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
        
class ManageUserLists(webapp2.RequestHandler):
    
    def setup(self, user):
        cdb=cDB()
        writeNavBar(self)
        results = cdb.getAllListsForUser(user)
            
        
        tv = {"results": results,
                  "id":user.user_id()}
        self.response.out.write(template.render(getTemplatePath("ManageLists"), tv))
        
    def get(self):
        user = users.get_current_user()
        if user:
            self.setup(user)
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        user = users.get_current_user()
        if user:
            name = self.request.get("listName")
            cdb= cDB()
            cdb.createListForUser(name, user)
            self.setup(user)
        else:
            self.redirect(users.create_login_url(self.request.uri))


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/PickSeries', pickSeries),
                               ('/UserSeries', userSeries),
                               ('/UserReleases', userReleases),
                               ('/ManageLists', ManageUserLists),
                               ('/update/UpdateSeries',UpdateSeries),
                               ('/update/Setup', SetUp)],
                              debug=True)
template.register_template_library(
 'common.templatefilters')