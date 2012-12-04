'''
Created on Dec 4, 2012

@author: Frank
Contains utility methods for auto-populating the data store and retreiving updates for the series in the data store
'''


from google.appengine.ext import db
from google.appengine.api import users
import scrapeComicList, datetime
from cEntities import *

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

def updateAllSeries():
    series = loadAllSeries()
    scrapeComicList.getSeriesFromEntityList(series, makeReleaseForSeries)

def getAllWeekReleases():
    """
    Get all releases for the upcoming wednesday
    """
    day = getNextWednesday()
    query = db.GqlQuery("SELECT * FROM Release WHERE ANCESTOR IS :1", day)
    return query.run()

def makeNextWednesday():
    """
    Make an entry for the wednesday after the latest in storage
    """
    day = db.GqlQuery("SELECT * FROM Wednesday ORDER BY date DESC")
    results = day.fetch(limit=10)
    oldest = results[0]
    if datetime.date.today() > oldest.date:
        new = Wednesday()
        new.date=oldest.date+datetime.timedelta(days=7)
        new.put()
def getNextWednesday():
    """
    Get the entity for the upcoming wednesday
    """
    dayQuery = db.GqlQuery("SELECT * FROM Wednesday WHERE date >:1", datetime.date.today())
    day = dayQuery.fetch(1)[0] #only 1 wednesday in advance is possible
    return day

def makeReleaseForSeries(releaseName, seriesName):
    """
    creates a Release entity for a release
    """
    day = getNextWednesday()
    release = Release(parent=day)
    release.seriesName=seriesName.strip()
    release.releaseName=releaseName.strip()
    release.put()
    
def test():
    testDay = Wednesday()
    testDay.date=datetime.date(year=2012,month=11,day=28)
    testDay.put()
    makeNextWednesday()
    updateAllSeries()
    return getAllWeekReleases()