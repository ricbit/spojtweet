import datetime
import urllib2

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

import badge
import parser
import model

class RefreshException(Exception):
  pass

class RefreshUserPage(webapp.RequestHandler):
  def get(self, user):
    self.user = user
    self.Measure(self.LoadSpojUserPages, 'Loading Time')
    self.Measure(self.ParseSpojUserPages, 'Parsing Time')
    before = datetime.datetime.now()
    self.InsertNewUser(self.user, self.name, self.country, self.problems)
    after = datetime.datetime.now()
    self.response.out.write(
        'updated user %s in datestore %s' % (user, str(after - before)))

  def Measure(self, method, message):
    before = datetime.datetime.now()
    method()
    after = datetime.datetime.now()
    self.response.out.write("%s: %s<br>" % (message, str(after - before)))

  def LoadSpojUserPages(self):
    try:
      status_url = 'http://www.spoj.pl/users/%s' % self.user
      status_rpc = urlfetch.create_rpc()
      urlfetch.make_fetch_call(status_rpc, status_url)
      details_url = 'http://www.spoj.pl/status/%s/signedlist/' % self.user
      details_rpc = urlfetch.create_rpc()
      urlfetch.make_fetch_call(details_rpc, details_url)
      self.status_page = status_rpc.get_result().content
      self.details_page = details_rpc.get_result().content
    except urlfetch.DownloadError:
      raise RefreshException()

  def ParseSpojUserPages(self):
    try:
      self.name, self.country = parser.ParseStatusPage(self.status_page)
      self.problems = parser.ParseDetailsPage(self.details_page)
    except parser.ParseError:
      raise RefreshException()
 
  def InsertNewUser(self, user, name, country, problems):
    user_problems = model.UserProblemList()
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
      problem = model.UserProblem(code=code)
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
    model.SpojUserMetadata(
        key_name=user, user=entity, problems=user_problems).put()

  def Page404(self, error):
    self.error(404)
    self.response.out.write('404, %s' % error)

