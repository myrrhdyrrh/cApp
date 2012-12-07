'''
Created on Dec 4, 2012

@author: Frank
contains all the functions needed for a user to interact with the data store
'''

from google.appengine.ext import db
from google.appengine.api import users
class cUser:
    """
    class that contains the functions needed for a user to interact with the datastore
    """
    user = None
    def __init__(self, user):
        self.user=user
    def getUser(self):
        return self.user
    