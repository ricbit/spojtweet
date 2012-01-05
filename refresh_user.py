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
import logging

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.ext import webapp

import badge
import events
import model
import parser
import shortener
import twitter
import utils

class RefreshException(Exception):
  pass

def PostTweet(user, events, short_url):
  # Skip if the user doesn't want to tweet every solution.
  if not user.send_solution:
    return

  if len(events) == 1:
    message = "I solved problem %s on SPOJ! %s #spojtweet" % (
        events[0].code, short_url)
  else:
    message = "I solved problems %s on SPOJ! %s #spojtweet" % (
        ",".join(event.code for event in events), short_url)
  twitter.SendTweet(user.key().name(), message)

def PostEvents(spoj_user, events):
  event = model.Event(user=spoj_user, event_list=events)
  key = event.put()
  logging.info('Event key: %d', key.id())
  logging.info('Event user: %s', spoj_user)
  short_url = shortener.Shorten(
      'http://spojtweet.appspot.com/user/%s/%d' % (spoj_user, key.id()))
  query = model.UserPreferences.all()
  query.filter('spoj_user', spoj_user)
  logging.info(short_url)
  for user in query.run():
    deferred.defer(PostTweet, user, events, short_url)

class RefreshUser():
  def __init__(self):
    self.update_events = False

  def refresh(self, user):
    try:
      self.user = user
      self.log = ''
      self.Measure(self.LoadSpojUserPages, 'Loading Time')
      self.Measure(self.ParseSpojUserPages, 'Parsing Time')
      self.Measure(self.CreateUserProblems, 'Create UserProblems Time')
      self.Measure(self.GrantBadges, 'Grant Badges Time')
      if self.update_events:
        self.Measure(self.GenerateEvents, 'Generate Events')
      self.Measure(self.WriteDatastore, 'Write Datastore Time')
      self.log += ('Finished updating <a href="/user/%s">user %s</a>' %
                   (user, user))
      return self.spojuser, self.log
    except RefreshException:
      pass

  def Measure(self, method, message):
    before = datetime.datetime.now()
    method()
    after = datetime.datetime.now()
    self.log += "%s: %s<br>" % (message, str(after - before))

  def LoadSpojUserPages(self):
    try:
      status_url = 'http://www.spoj.pl/users/%s' % self.user
      details_url = 'http://www.spoj.pl/status/%s/signedlist/' % self.user
      fetcher = utils.ParallelFetch(
          first_place=utils.QueryCount(
              model.ProblemDetails, 'first_place', self.user),
          forever=utils.QueryCount(
              model.ProblemDetails, 'first_place_permanent', self.user),
          status_page=utils.FetchUrl(status_url),
          details_page=utils.FetchUrl(details_url),
          classical_list=utils.GetModel('ProblemList', 'classical'),
          old_metadata=utils.GetModel('SpojUserMetadata', self.user),
          crawling=utils.GetModel('CrawlingInfo', 'info'))
      self.__dict__.update(fetcher.run())
      self.classical = set(self.classical_list.problems)
      if self.crawling is None or not self.crawling.crawling:
        self.update_events = True
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
    self.metadata.granted_badges, self.metadata.skipped_badges = (
        badge.GrantBadges(self.metadata))

  def GenerateEvents(self):
    self.events = events.GenerateEvents(self.old_metadata, self.metadata)
    logging.info(self.events)
    if self.events:
      deferred.defer(PostEvents, self.user, self.events)

  def WriteDatastore(self):
    self.spojuser = model.SpojUser(
        key_name=self.user, name=self.name, country=self.country,
        badges=self.metadata.granted_badges,
        last_update=datetime.datetime.now(),
        version=model.VERSION)
    user_rpc = db.put_async(self.spojuser)
    if self.update_events:
      metadata = model.SpojUserMetadata(
          key_name=self.user, problems=self.metadata.problems,
          country_position=self.country_position, first_place=self.first_place,
          granted_badges=self.metadata.granted_badges,
          skipped_badges=self.metadata.skipped_badges)
      metadata_rpc = db.put_async(metadata)
    user_rpc.check_success()
    if self.update_events:
      metadata_rpc.check_success()

class RefreshUserPage(webapp.RequestHandler):
  def get(self, user):
    spojuser, log = RefreshUser().refresh(user)
    self.response.out.write(log)
