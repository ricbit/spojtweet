import datetime
import os
import urllib2

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import crawler
import model
import parser
import refresh_user_page

class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write('Under construction')

class UserPage(webapp.RequestHandler):
  def get(self, user):
    spojuser = model.SpojUser.get_by_key_name(user)
    path = os.path.join(os.path.dirname(__file__), 'user.html')
    values = {
      'name': spojuser.name,
      'country': spojuser.country.title(),
      'badges': spojuser.badges
    }
    self.response.out.write(template.render(path, values))

app = webapp.WSGIApplication(
          [('/', MainPage),
	   ('/user/([^/]+)', UserPage),
	   ('/refresh/([^/]+)', refresh_user_page.RefreshUserPage),
	   ('/crawl', crawler.CrawlCountryPage)],
	  debug=True)

def main():
  run_wsgi_app(app)

if __name__ == '__main__':
  main()
