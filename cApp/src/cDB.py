'''
Created on Dec 4, 2012

@author: Frank
implements IcDB "interface"
'''
from google.appengine.ext import db
from google.appengine.api import users
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
            check = self.createInfoForUser(user)
            return check
    
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
            series = cList(parent= userE)
            series.name="Follow"
            series.user=user.user_id()
            series.put()
            userE.userLists.append("Follow")
            userE.put()
            return userE
     
    def createListForUser(self, listName, user):
        """
        create a new cList for a given user
        """

        if self.userExists(user):
            userI = self.getUserInfo(user)
            series = cList(parent= userI)
            series.name=listName
            series.user=user.user_id()
            series.put()
            userI.userLists.append(listName)
            userI.put()

    def deleteListForUser(self, listName, user):
        """
        remove a cList for a given user
        """
        l = self.getListForUser(listName, user)
        l.delete()
        
    def getAllListsForUser(self, user):
        test = self.getUserInfo(user)
        query = db.GqlQuery("SELECT * FROM cList WHERE ANCESTOR IS :1", test)
        return query.run()
    
    def getListForUser(self, listName, user):
        test = self.getUserInfo(user)
        query = db.GqlQuery("SELECT * FROM cList WHERE ANCESTOR IS :1 AND name =:2", test, listName)

        return query.fetch(1)[0]
    
    def getAllSeriesForUser(self, user):
        """
        Get a list of all series a user has in lists
        """
        key = self.getUserInfo(user)
        query = db.GqlQuery("SELECT * FROM cList WHERE ANCESTOR IS :1", key)
        output=set()
        for q in query:
            series = q.series
            for s in series:
                if s not in output:
                    output.add(s)
        output = list(output)
        output.sort()
        return output
    
    def addSeriesToListForUser(self, seriesName, listName, user):
        """
        add a new series to list for a given user
        """
        listName = listName if listName!=None or listName!="" else "Follow"
        test = self.getUserInfo(user)
        query = db.GqlQuery("SELECT * from cList WHERE ANCESTOR IS :1 AND name=:2", test,listName)
        results = query.fetch(1)
        count = 0
        for r in results:
            count+=1
        if count!=0:
            userI = results[0]
            series = userI.series
            if seriesName not in series:
                userI.series.append(seriesName)
                userI.put()
    
    def deletSeriesFromListForUser(self, seriesName, listName, user):  
        """
        remove a series from a given list for a user
        """
        l = self.getListForUser(listName, user)
        l.series.remove(seriesName)      
        
    def updateSeriesForListforUser(self,seriesName, listName,user):
        raise NotImplementedError("abstract")
    