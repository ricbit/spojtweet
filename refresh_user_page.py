# Copyright (C) 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Refresh data from a spoj user."""

__author__ = 'ricbit@google.com (Ricardo Bittencourt)'

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
      fastest_query = model.ProblemDetails.all(keys_only=True)
      self.first_place = fastest_query.filter("first_place", self.user).count()
      forever_query = model.ProblemDetails.all(keys_only=True)
      self.forever = forever_query.filter(
          "first_place_permanent", self.user).count()
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

  def _EvalSingleProblem(self, code, properties, date_map):
    solved = False
    languages = set()
    tries_before_ac = 0
    first_attempt_date = properties[0][0]
    first_ac_date = None
    best_time = None
    for date, status, language, time in properties:
      date_map[date.date()] = 1 + date_map.get(date.date(), 0)
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
    return problem
  
  def CreateUserProblems(self):
    self.metadata = badge.UserMetadata()
    self.metadata.problems = []
    date_map = {}
    for code, properties in self.problems.iteritems():
      # Skip problems not in classical set.
      if code not in self.classical:
	continue
      properties.sort()
      problem = self._EvalSingleProblem(code, properties, date_map)
      self.metadata.problems.append(problem)
    self.metadata.max_attempts_day = (
        max(date_map.values()) if date_map else None)

  def GrantBadges(self):
    self.metadata.country = self.country
    self.metadata.country_position = self.country_position
    self.metadata.first_place = self.first_place
    self.metadata.first_place_permanent = self.forever
    self.badges = badge.GrantBadges(self.metadata)

  def WriteDatastore(self):
    user = model.SpojUser(
        key_name=self.user, name=self.name, country=self.country,
	badges=self.badges, last_update=datetime.datetime.now(),
	version=model.VERSION)
    user_rpc = db.put_async(user)
    metadata = model.SpojUserMetadata(
        key_name=self.user, problems=self.metadata.problems,
	county_position=self.country_position, first_place=self.first_place)
    metadata_rpc = db.put_async(metadata)
    user_rpc.check_success()
    metadata_rpc.check_success()

  def Page404(self):
    self.error(404)
