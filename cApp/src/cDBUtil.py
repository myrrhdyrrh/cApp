'''
Created on Dec 4, 2012

@author: Frank
Contains utility methods for auto-populating the data store and retreiving updates for the series in the data store
'''


from google.appengine.ext import db
from google.appengine.api import users
import scrapeComicList, datetime, urllib,urllib2
import xml.dom.minidom as minidom
from cEntities import *


def seriesExists(name):
    """
    Check if a series exists in storage
    """
    check = db.GqlQuery("SELECT * FROM Series WHERE name = :1",name )
    return getCountOfQuery(check)>0
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

def getReleaseForSeries(seriesName):
    """
    Get a release for a series for the upcoming wednesday, if it exists
    """
    day = getNextWednesday()
    query = db.GqlQuery("SELECT * FROM Release WHERE ANCESTOR IS :1 AND seriesName= :2", day, seriesName)
    if getCountOfQuery(query)>0:
        return query.fetch(1)[0]
    return None

def makeNextWednesday():
    """
    Make an entry for the wednesday after the latest in storage
    """
    day = db.GqlQuery("SELECT * FROM Wednesday ORDER BY date DESC")
    results = day.fetch(limit=3)
    oldest = results[0]
    if datetime.date.today() >= oldest.date:
        new = Wednesday()
        new.date=oldest.date+datetime.timedelta(days=7)
        new.put()
        return True
    return False

def getNextWednesday():
    """
    Get the entity for the upcoming wednesday
    """
    dayQuery = db.GqlQuery("SELECT * FROM Wednesday WHERE date >=:1", datetime.date.today())
    day = dayQuery.fetch(1)[0] #only 1 wednesday in advance is possible
    return day

def getLastWednesday():
    """
    Get the entity for the Wednesday before the upcoming one
    """
    dayQuery = db.GqlQuery("SELECT * FROM Wednesday ORDER BY date DESC")
    results=dayQuery.fetch(limit=3)
    return results[1]
def makeReleaseForSeries(releaseName, seriesName):
    """
    creates a Release entity for a release
    """
    day = getNextWednesday()
    query = db.GqlQuery("SELECT * FROM Release WHERE ANCESTOR IS :1 AND seriesName= :2", day, seriesName)
    query2 = db.GqlQuery("SELECT * FROM Release WHERE releaseName= :1", releaseName)#hope this doesn't break
    if getCountOfQuery(query2)>0:
        return
    results = query.run()
    count =0
    for r in results:
        count+=1
    if count==0:
        release = Release(parent=day)
        release.seriesName=seriesName.strip()
        release.releaseName=releaseName.strip()
        release.put()
    
def getCountOfQuery(query):
    """
    get number of results of a query
    """
    count = 0
    for q in query:
        count+=1
    return count


def storeSeries():
    address = "http://www.midtowncomics.com/rssfeed/rssallnewrelease.xml"
    file_request = urllib2.Request(address) 
    file_opener = urllib2.build_opener() 
    file_object = file_opener.open(file_request) 
    file_feed = file_object.read() 
    file_xml = minidom.parseString(file_feed) 
    item_node = file_xml.getElementsByTagName("title")
    for item in item_node:
        name = item.firstChild.nodeValue
        name = scrapeComicList.formatTitle(name)
        name = scrapeComicList.formatLine(name)[1]
        name=name.strip()
        if name!="" and not seriesExists(name):
            e = Series(key_name=name)
            e.name = name
            e.date= getNextWednesday()
            e.put()

def test():
    db.delete(Wednesday.all())
    testDay = Wednesday()
    testDay.date=datetime.date(year=2012,month=11,day=28)
    testDay.put()
    makeNextWednesday()

