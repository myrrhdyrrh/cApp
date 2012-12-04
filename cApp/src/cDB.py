'''
Created on Dec 4, 2012

@author: Frank
implements IcDB "interface"
'''
from google.appengine.ext import db
from google.appengine.api import users
from cEntities import *
class cDB():
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
        test = db.Key.from_path("UserInfo", user.user_id())
        check = db.get(test)
        if check==None:
            userE = UserInfo(key_name=user.user_id())
            userE.userID= user.user_id()
            userE.userLists=[]
            self.createListForUser("Follow", user)
            userE.put()
     
    def createListForUser(self, listName, user):
        """
        create a new cList for a given user
        """
        test = db.Key.from_path("UserInfo", user.user_id())
        check = db.get(test)
        if check !=None:
            userI = check
            series = cList(parent= test)
            series.name=listName
            series.user=user.user_id()
            series.put()
            userI.userLists.append(listName)
            userI.put()

    def getAllListsForUser(self, user):
        test = db.Key.from_path("UserInfo", user.user_id())
        query = db.GqlQuery("SELECT * FROM cList WHERE ANCESTOR IS :1", test)
        return query.run()
    
    def getListForUser(self, listName, user):
        test = db.Key.from_path("UserInfo", user.user_id())
        query = db.GqlQuery("SELECT * FROM cList WHERE ANCESTOR IS :1 AND name =:2", test, listName)

        return query.fetch(1)[0]
    
    def addSeriesToListForUser(self, seriesName, listName, user):
        """
        add a new series to list for a given user
        """
        listName = listName if listName!=None or listName!="" else "Follow"
        test = db.Key.from_path("UserInfo", user.user_id())
        query = db.GqlQuery("SELECT * from cList WHERE ANCESTOR IS :1 AND name=:2", test,listName)
        check=query.fetch(1)[0]
        if check!=None:
            userI = check
            series = userI.series
            if seriesName not in series:
                userI.series.append(seriesName)
                userI.put()
            
    def updateSeriesForListforUser(self,seriesName, listName,user):
        raise NotImplementedError("abstract")
    