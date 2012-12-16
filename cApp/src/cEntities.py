'''
Created on Dec 3, 2012

@author: Frank

this module contains all storage entities used by the app
'''
import cgi
import datetime
import urllib
#import webapp2

from google.appengine.ext import db
from google.appengine.api import users


class Wednesday(db.Model):
    """Models a Wednesday"""
    date = db.DateProperty()

class Release(db.Model):
    """Modes a list of updates"""
    seriesName= db.StringProperty()
    releaseName = db.StringProperty()
    
class Series(db.Model):
    """Models a series title. Basic storage entity"""
    name = db.StringProperty()
    dateUpdated = db.DateProperty()
    
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
    #user = db.StringProperty()
    series = db.StringListProperty()
    releases = db.StringListProperty()