import datetime
import urllib2

from google.appengine.ext import webapp
from google.appengine.api import urlfetch

import parser
import spojuser

class RefreshUserPage(webapp.RequestHandler):
  def get(self, user):
    before = datetime.datetime.now()
    try:
      url = 'http://www.spoj.pl/users/%s' % user
      status_page = urlfetch.fetch(url).content
      url = 'http://www.spoj.pl/status/%s/signedlist/' % user
      details_page = urlfetch.fetch(url).content
    except urlfetch.DownloadError:
      self.Page404('page')
      return
    try:
      name, country = parser.ParseStatusPage(status_page)
      problems = parser.ParseDetailsPage(details_page)
    except parser.ParseError:
      self.Page404('parse')
      return
    user = spojuser.SpojUser(key_name=user,
                             name=name,
			     country=country,
			     last_update=datetime.datetime.now())
    user.put()
    for problem in problems:
      problem.user = user
      problem.put()
    after = datetime.datetime.now()
    self.response.out.write(
        'updated user %s in %s' % (user, str(after - before)))

  def Page404(self, error):
    self.error(404)
    self.response.out.write('404, %s' % error)

