'''
Created on Dec 3, 2012

@author: Frank
'''
import webapp2,os
from google.appengine.api import users
from google.appengine.ext.webapp import template
import cEntities as cE
import cDBUtil, json
from collections import Iterable
from cUser import *
from cDB import *


def getTemplatePath(name):
    """
    get the path for a specified template file
    """
    return os.path.dirname(__file__)+"/templates/"+name+".html"
def getDictForObj(obj):
    """
    get dictionary of attributes for an object
    """
    temp = {}
    atts =[attr for attr in dir(obj) if not callable(attr) and not attr.startswith("_")]
    for a in atts:
        t= getattr(obj, a, "")
        if isinstance(t, basestring):
            temp[a]=t
    return temp

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
            series = [n.name for n in cdb.getAllSeries()]
            tv = { 'series': series,
                  'names':[n.name for n in cdb.getAllListsForUser(user)]
                  }
            self.response.out.write(template.render(getTemplatePath("PickSeries"), tv))

            
        else:
            self.redirect(users.create_login_url(self.request.uri))
                          
    def post(self):
        series = self.request.get_all("seriesName")
        cdb=cDB()
        user =users.get_current_user()
        lists = self.request.get_all("listName")
        series.extend([r.strip() for r in self.request.get("batchAdd").split("\n")])
        results=[]
        for s in series:
            for l in lists:
                if cdb.addSeriesToListForUser(s, l, user):
                    if s not in results:
                        results.append(s)
        tv={"results":results,
            "lists":lists}
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
            series = cdb.getAllSeriesForUser(user)
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

class GetUserList(webapp2.RequestHandler):
    def post(self):
        user=users.get_current_user()
        cdb= cDB()
        listName = self.request.get("listName");
        uList=  cdb.getListForUser(listName, user).series
        self.response.out.write(uList)
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

class UserAPI(webapp2.RequestHandler):
    def get(self):
         method = self.request.uri.split("/")[-1]
         
    def post(self):
        self.response.headers['Content-Type'] = 'application/json'   
        
        params = self.request.arguments()
        urlsplit = self.request.uri.split("/")
        apiIndex = urlsplit.index("api")
        userId = urlsplit[apiIndex+1]
        methodName = urlsplit[apiIndex+2].split("?")[0]
        paramVals = [str(self.request.get(t)).replace("\"","") for t in params]
        paramVals.append(cE.cUser(userId))
        cdb = cDB()
        method = getattr(cdb, methodName)
        if method!=None:
            output=method(*paramVals) 
            if output!=None:
                if output!=True and output !=False:
                    #we know it has to be some kind of entity or list of entities
                    if isinstance(output,Iterable):
                        temp =[]
                        for o in output:
                            temp.append(getDictForObj(o))
                        output=temp
                    else:
                        output= getDictForObj(output)
                    
                self.response.out.write(json.dumps(output))
        
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/GetUserList', GetUserList),
                               ('/PickSeries', pickSeries),
                               ('/UserSeries', userSeries),
                               ('/UserReleases', userReleases),
                               ('/ManageLists', ManageUserLists),
                               (r'/api/.*/.*', UserAPI),
                               ('/update/UpdateSeries',UpdateSeries),
                               ('/update/Setup', SetUp)],
                              debug=True)
template.register_template_library(
 'common.templatefilters')