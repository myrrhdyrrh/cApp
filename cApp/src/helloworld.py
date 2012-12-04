'''
Created on Dec 3, 2012

@author: Frank
'''
import webapp2
import scrapeComicList
from google.appengine.api import users
import cEntities as cE
class MainPage(webapp2.RequestHandler):
    def get(self):
        series = scrapeComicList.getSeriesFromEntityList(cE.Series.all())
        for ser in series:
            self.response.out.write(ser+"<br>")

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)