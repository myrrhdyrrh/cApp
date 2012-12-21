# import the webapp module
from google.appengine.ext import webapp
import json
# get registry, we need it to register our filter later.
register = webapp.template.create_template_register()

def replace(value, id):
    """
    custom django filter, wraps around str.replace
    removes id from a string
    """
    return value.replace(id,"")

def jsonify(object):
    return json.dumps(object)

register.filter(jsonify)
register.filter(replace)
