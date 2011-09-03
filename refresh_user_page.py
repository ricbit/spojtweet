import datetime
import urllib2

from google.appengine.ext import webapp
from google.appengine.api import urlfetch

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
      self.response.out.write('<p>%s' % code)
      properties.sort()
      solved = False
      languages = set()
      tries_before_ac = 0
      first_attempt_date = properties[0][0]
      first_ac_date = None
      best_time = None
      for date, status, language in properties:
        if solved:
	  if status == 'AC':
	    languages.add(language)
	else:
	  if status == 'AC':
	    solved = True
	    languages.add(language)
	    first_ac_date = date
	  else:
	    tries_before_ac += 1
      problem = model.UserProblem(code=code)
      problem.languages = list(languages)
      problem.tries_before_ac = tries_before_ac
      problem.solved = solved
      problem.first_attempt_date = first_attempt_date
      if first_ac_date is not None:
        problem.first_ac_date = first_ac_date
      user_problems.append(problem)
    entity = model.SpojUser(
        key_name=user, name=name, country=country, language=language,
	last_update=datetime.datetime.now())
    entity.put()
    for problem in user_problems:
      problem.user = entity
      problem.put()


  def Page404(self, error):
    self.error(404)
    self.response.out.write('404, %s' % error)

