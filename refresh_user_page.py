import datetime

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
    try:
      self.user = user
      self.Measure(self.LoadSpojUserPages, 'Loading Time')
      self.Measure(self.ParseSpojUserPages, 'Parsing Time')
      self.Measure(self.CreateUserProblems, 'Create UserProblems Time')
      self.Measure(self.GrantBadges, 'Grant Badges Time')
      self.Measure(self.WriteDatastore, 'Write Datastore Time')
      user_link = ('Finished updating <a href="/user/%s">user %s</a>' %
                   (user, user))
      self.response.out.write(user_link)
    except RefreshException:
      self.Page404()

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
      classical_key = db.Key.from_path('ProblemList', 'classical')      
      classical_rpc = db.get_async(classical_key)
      gql = 'SELECT __key__ FROM ProblemDetails WHERE first_place=\'%s\''
      self.first_place = db.GqlQuery(gql % self.user).count()
      self.classical = set(classical_rpc.get_result().problems)
      self.status_page = status_rpc.get_result().content
      self.details_page = details_rpc.get_result().content
    except urlfetch.DownloadError:
      raise RefreshException()

  def ParseSpojUserPages(self):
    try:
      self.name, self.country = parser.ParseStatusPage(self.status_page)
      self.problems = parser.ParseDetailsPage(self.details_page)
      country_info = model.CountryInfo.get_by_key_name(self.country)
      self.country_position = None
      for user in country_info.users:
        if user.name == self.user:
	  self.country_position = user.position
    except parser.ParseError:
      raise RefreshException()
 
  def CreateUserProblems(self):
    self.user_problems = []
    for code, properties in self.problems.iteritems():
      # Skip problems not in classical set.
      if code not in self.classical:
	continue
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
      self.user_problems.append(problem)

  def GrantBadges(self):
    metadata = badge.UserMetadata()
    metadata.problems = self.user_problems
    metadata.country = self.country
    metadata.country_position = self.country_position
    metadata.first_place = self.first_place
    self.badges = badge.GrantBadges(metadata)

  def WriteDatastore(self):
    user = model.SpojUser(
        key_name=self.user, name=self.name, country=self.country,
	badges=self.badges, last_update=datetime.datetime.now())
    user_rpc = db.put_async(user)
    metadata = model.SpojUserMetadata(
        key_name=self.user, problems=self.user_problems,
	county_position=self.country_position, first_place=self.first_place)
    metadata_rpc = db.put_async(metadata)
    user_rpc.check_success()
    metadata_rpc.check_success()

  def Page404(self):
    self.error(404)

