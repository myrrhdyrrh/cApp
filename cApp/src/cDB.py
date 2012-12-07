'''
Created on Dec 4, 2012

@author: Frank
implements IcDB "interface"
'''
from google.appengine.ext import db
from google.appengine.api import users
import cDBUtil
from cEntities import *
class cDB():
    
    def userExists(self,user):
        """
        check if a user exists in storage
        """
        test = db.Key.from_path("UserInfo", user.user_id())
        check = db.get(test)
        return check==None
    
    def getUserInfo(self, user):
        """
        get userInfo entity for a given user
        """
        if self.userExists(user):
            test = db.Key.from_path("UserInfo", user.user_id())
            check = db.get(test)
            return check
        else:
            userE = UserInfo(key_name = user.user_id())
            userE.put()
            listName = "Follow"+user.user_id()
            if listName not in userE.userLists:
                series = cList(key_name=listName)
                series.name="Follow"
                series.user=user.user_id()
                series.put()
                userE.userLists.append(listName)
                userE.put()
            return userE
    
    def getAllSeries(self):
        """
        get all series in storage
        """
        series= db.GqlQuery("SELECT * FROM Series ORDER BY name")
        return series
    
    def createInfoForUser(self, user):
        """
        create new entity for a given user
        """
        if not self.userExists(user):
            userE = UserInfo(key_name=user.user_id())
            userE.userID= user.user_id()
            userE.userLists=[]
            userE.put()
            series = cList(key_name = "Follow"+user.user_id())
            series.name="Follow"
            series.user=user.user_id()
            series.put()
            userE.userLists.append("Follow"+user.user_id())
            userE.put()
            return userE
     
    def createListForUser(self, listName, user):
        """
        create a new cList for a given user
        """
        listName=listName+user.user_id()
        if self.userExists(user):
            userI = self.getUserInfo(user)
            if listName not in userI.userLists:
                series = cList(parent= userI)
                series.name=listName
                series.user=user.user_id()
                #series.put()
                userI.userLists.append(listName)
                #userI.put()

    def deleteListForUser(self, listName, user):
        """
        remove a cList for a given user
        """
        l = self.getListForUser(listName, user)
        l.delete()
        
    def getAllListsForUser(self, user):
        test = self.getUserInfo(user)
        query = db.GqlQuery("SELECT * FROM cList WHERE ANCESTOR IS :1", test)
        output =set()
        for s in test.userLists:
            key = db.Key.from_path("cList", s)
            output.add(db.get(key))
        check = set()
        for q in output:
            if q.name not in check:
                check.add(q.name)
                output.add(q)
        return output
    
    def getListForUser(self, listName, user):
        
        key = db.Key.from_path("cList", listName+user.user_id())

        return db.get(key)
    
    def getAllSeriesForUser(self, user):
        """
        Get a list of all series a user has in lists
        """
        #something is happening causing a new clist to be created where user=userid of logged in user
        key = self.getUserInfo(user)
        query = self.getAllListsForUser(user)#db.GqlQuery("SELECT * FROM cList WHERE ANCESTOR IS :1", key)
        output=set()
        check= set()
        for q in query:
            series = q.series
            for s in series:
                if s not in check:
                    check.add(s)
                    query = db.GqlQuery("SELECT * FROM Series WHERE name= :1", s)
                    if cDBUtil.getCountOfQuery(query) >0:
                        output.add(query.fetch(1)[0])
        output = list(output)
        return output

    def getSeriesUserDoesNotFollow(self,user):
        """
        get all series a user is not currently following
        """
        follow = set()#set([s.name for s in self.getAllSeriesForUser(user)])
        all = set([s.name for s in self.getAllSeries()])
        notfollow =set.difference(all,follow)
        output = list(notfollow)
        output.sort() 
        return output   
    
    def addSeriesToListForUser(self, seriesName, listName, user):
        """
        add a new series to list for a given user
        """
        listName = listName if listName!=None or listName!="" else "Follow"
        listName= listName+user.user_id()
        test = self.getUserInfo(user)
        query = db.GqlQuery("SELECT * from cList WHERE ANCESTOR IS :1 AND name=:2", test,listName)
        results = query.fetch(1)
        key = db.Key.from_path("cList", listName)
        results = db.get(key)
        count = 1#cDBUtil.getCountOfQuery(query)
        if count!=0:
            userI = results#[0]
            series = userI.series
            if seriesName not in series and cDBUtil.seriesExists(seriesName):
                userI.series.append(seriesName)
                userI.put()
                return True
        return False
    
    def deletSeriesFromListForUser(self, seriesName, listName, user):  
        """
        remove a series from a given list for a user
        """
        l = self.getListForUser(listName, user)
        l.series.remove(seriesName)      
    
    def updateAllListsForUser(self, user):
        """
        updates all list for a user
        """
        for l in self.getUserInfo(user).userLists:
            self.updateListforUser(l, user)
    
    def updateListforUser(self,listName,user):
        """
        updates a list for a user
        """
        key = db.Key.from_path("cList", listName+user.user_id())#self.getUserInfo(user)
        #query = db.GqlQuery("SELECT * FROM cList WHERE ANCESTOR IS :1 and name= :2", key, listName)
        l = db.get(key)#query.fetch(1)[0]
        for series in l.series:
            check = cDBUtil.getReleaseForSeries(series)
            if check!=None and check.releaseName not in l.releases:
                
                l.releases.append(check.releaseName)
        l.put()
    
            