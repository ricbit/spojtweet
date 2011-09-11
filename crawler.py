from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

import model
import parser
import logging

def crawl_country(country_list):
  if not country_list:
    return
  code, name = country_list[0]
  url = 'http://www.spoj.pl/ranks/users/%s' % code
  logging.info('parsing %s', name)
  text = urlfetch.fetch(url).content
  user_list = parser.ParseCountryPage(text)
  users = []
  for position, username in user_list:
    users.append(model.UserPosition(username, position))
  model.CountryInfo(key_name=name, users=users).put()
  deferred.defer(crawl_country, country_list[1:])


class CrawlCountryPage(webapp.RequestHandler):
  def get(self):
    country_url = 'http://www.spoj.pl/ranks/countries/'
    country_page = urlfetch.fetch(country_url).content
    country_list = parser.ParseCountryList(country_page)
    deferred.defer(crawl_country, country_list)
    self.response.out.write('launched')
