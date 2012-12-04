'''
Created on Dec 3, 2012

@author: Frank

this module contains all storage entities used by the app
'''
import cgi
import datetime
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.api import users

class Series(db.Model):
    """Models a series title. Basic storage entity"""
    name = db.StringProperty()
    
class UserInfo(db.Model):
    """
    Entity for user
    contains user id as key, and list of lists the user has set up
    """
    userID = db.StringProperty()
    userLists = db.StringListProperty()

class cList(db.Model):
    """
    Entity for a list of series
    contains a field for the name of the list,
    a field for the id of the user that owns the list,
    a field for a list of series in the list,
    and a field for a list of upcoming releases for the series in the list
    """
    name = db.StringProperty()
    user = db.StringProperty()
    series = db.StringListProperty()
    releases = db.StringListProperty()

def clearAllSeries():
    """
    remove all series from storage
    """
    db.delete(Series.all())

def storeAllSeries():
    """
    test storage of all series in currentreads.txt
    """
    f = open("currentreads.txt")
    sers = [a.strip() for a in f]
    for ser in sers:
        series = Series()
        series.name=ser
        series.put()
        
def loadAllSeries():
    """
    test retrieval of all series in storage
    """
    series= db.GqlQuery("SELECT * FROM Series ORDER BY name")
    return series
        