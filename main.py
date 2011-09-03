import datetime
import urllib2

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import model
import parser
import refresh_user_page

class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write('Under construction')

class UserPage(webapp.RequestHandler):
  def get(self, user):
    model = model.SpojUser.get_by_key_name(user)
    if model is not None:
      self.response.out.write('Hello user %s' % model.name)
      for problem in model.problems:
        self.response.out.write('<br>%s' % problem.code)
    else:
      self.response.out.write('not present')

app = webapp.WSGIApplication(
          [('/', MainPage),
	   ('/user/([^/]+)', UserPage),
	   ('/refresh/([^/]+)', refresh_user_page.RefreshUserPage)],
	  debug=True)

def main():
  run_wsgi_app(app)

if __name__ == '__main__':
  main()
