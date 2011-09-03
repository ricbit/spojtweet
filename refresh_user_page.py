import datetime
import urllib2

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

import badge
import parser
import model

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
    self.InsertNewUser(user, name, country, problems)
    after = datetime.datetime.now()
    self.response.out.write(
        'updated user %s in %s' % (user, str(after - before)))

  def InsertNewUser(self, user, name, country, problems):
    user_problems = []
    for code, properties in problems.iteritems():
      properties.sort()
      solved = False
      languages = set()
      tries_before_ac = 0
      first_attempt_date = properties[0][0]
      first_ac_date = None
      best_time = None
      for date, status, language, time in properties:
        if solved:
	  if status == 'AC':
	    languages.add(language)
	    if time < best_time:
	      best_time = time
	else:
	  if status == 'AC':
	    solved = True
	    languages.add(language)
	    first_ac_date = date
	    best_time = time
	  else:
	    tries_before_ac += 1
      problem = model.UserProblem(key_name=(user + code), code=code)
      problem.languages = list(languages)
      problem.tries_before_ac = tries_before_ac
      problem.solved = solved
      problem.first_attempt_date = first_attempt_date
      if solved:
        problem.best_time = best_time
        problem.first_ac_date = first_ac_date
      user_problems.append(problem)
      badges = badge.GrantBadges(user_problems)
    entity = model.SpojUser(
        key_name=user, name=name, country=country, language=language,
	badges=badges, last_update=datetime.datetime.now())
    entity.put()
    for problem in user_problems:
      problem.user = entity
    db.put(user_problems)

  def Page404(self, error):
    self.error(404)
    self.response.out.write('404, %s' % error)

