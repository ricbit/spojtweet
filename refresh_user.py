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
import string
import urllib

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.ext import webapp

import badge
import events
import language_codes
import model
import parser
import shortener
import twitter
import utils

EMPTY_GIF = ("data:image/gif;base64,R0lGODlhAQABAPABAP///"
             "wAAACH5BAEKAAAALAAAAAABAAEAAAICRAEAOw%3D%3D")

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
  logging.info('Posting event for spoj user: %s', spoj_user)
  event = model.Event(user=spoj_user, event_list=events)
  key = event.put()
  short_url = shortener.Shorten(
      'http://spojtweet.appspot.com/user/%s/%d' % (spoj_user, key.id()))
  query = model.UserPreferences.all()
  query.filter('spoj_user', spoj_user)
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
      self.log += (
          'Finished updating <a href="/user/%s?nocache=1">user %s</a>' %
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
      self.classical = set(i[0] for i in self.classical_list.problems)
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
    language_count = {}
    timeline = []
    for code, properties in self.problems.iteritems():
      # Skip problems not in classical set.
      if code not in self.classical:
        continue
      properties.sort()
      problem = self._EvalSingleProblem(code, properties, date_map)
      self.metadata.problems.append(problem)
      if problem.solved:
        for language in problem.languages:
          langcode = language_codes.LANGUAGE_CONVERT.get(language, language)
          language_count[langcode] = 1 + language_count.get(langcode, 0)
        timeline.append(problem.first_ac_date)
    self.metadata.max_attempts_day = (
        max(date_map.values()) if date_map else None)
    self.language_chart = self._BuildLanguageChart(language_count)
    self.timeline = self._BuildTimeline(timeline)
    self.punchcard = self._BuildPunchcard(timeline)

  def _BuildLanguageChart(self, language_count):
    languages = language_count.items()
    languages.sort(key=lambda x: x[1], reverse=True)
    counts = ','.join(str(i[1]) for i in languages)
    names = '|'.join(language_codes.LANGUAGE_CODES.get(i[0], i[0])
                     for i in languages)
    url = {'chs': '%dx%d' % (model.CHART_WIDTH, model.CHART_HEIGHT),
           'chd': 't:%s' % counts,
           'chl': '%s' % names,
           'cht': 'p3',
           'chco': 'FFFF10,505050,E6B43C'}
    return 'http://chart.apis.google.com/chart?' + urllib.urlencode(url)

  def _Encode(self, series, minval=None, maxval=None):
    code = ''.join([string.uppercase, string.lowercase, string.digits, '-.'])
    output = []
    if minval is None:
      minval = min(series)
    if maxval is None:
      maxval = max(series)
    interval = maxval - minval
    if not interval:
      interval = 1
    for data in series:
      scaled = int((data - minval) * 4095 / interval)
      output.append(code[scaled / 64])
      output.append(code[scaled % 64])
    return ''.join(output)

  def _BuildTimeline(self, timeline):
    if not timeline:
      return EMPTY_GIF
    timeline.sort()
    start_date, end_date = timeline[0], timeline[-1]
    start_year, end_year = start_date.year, end_date.year
    dates, problems = [], []
    for count, date in enumerate(timeline):
      dates.append((date - start_date).days)
      problems.append(count + 1)
    trim_dates = dates[::len(dates)/300 + 1] + [dates[-1]]
    trim_problems = problems[::len(problems)/300 + 1] + [problems[-1]]
    line = ','.join(self._Encode(i) for i in [trim_dates, trim_problems])
    axis_ticks = [] 
    years = range(start_year + 1, end_year + 1) 
    for year in years:
      date = datetime.datetime(year, 1, 1)
      scaled = (date - start_date).days * 100 / (end_date - start_date).days
      axis_ticks.append(scaled)
    url = {'chs': '%dx%d' % (model.CHART_WIDTH, model.CHART_HEIGHT),
           'chd': 'e:%s' % line,
           'chxt': 'x,y',
           'chxr': '1,%d,%d' % (0, count),
           'chxp': '0,%s' % ','.join(str(i) for i in axis_ticks),
           'chxl': '0:|%s' % '|'.join(str(i) for i in years),
           'chxtc': '0,-%d' % (model.CHART_HEIGHT - 20),
           'chxs': '0,505050,13,0,lt,D0D0D0,505050|'
                   '1,505050,13,0,lt,505050,505050',
           'cht': 'lxy'}
    return 'http://chart.apis.google.com/chart?' + urllib.urlencode(url)
    
  def _BuildPunchcard(self, timeline):
    if not timeline:
      return EMPTY_GIF
    punchcard = [[0] * 24 for weekday in xrange(7)]
    for ac_date in timeline:
      punchcard[ac_date.weekday()][ac_date.hour] += 1
    x, y, size = [], [], []
    for weekday in xrange(7):
      for hour in xrange(24):
        if not punchcard[weekday][hour]:
          continue
        # Spoj runs in poland time (GMT+1), converting to GMT.
        x.append((hour + 23) % 24 * 92 / 23 + 4)
        y.append(weekday * 90 / 6 + 5)
        size.append(punchcard[weekday][hour])
    points = [self._Encode(x, 0, 99),
              self._Encode(y, 0, 99),
              self._Encode(size, 0, max(size))]
    weekdays = ','.join(str(i * 90 / 6 + 5) for i in xrange(7))
    hours = ','.join(str(i * 92 / 23 + 4) for i in xrange(0, 24, 6))
    axis = '|'.join(['1,' + weekdays,
                     '2,' + weekdays,
                     '0,' + hours])
    weekday_names = 'Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday'
    hours_names = '|'.join('%dh' % i for i in xrange(0, 24, 6))
    axis_names = '|'.join(['1:|%s' % weekday_names,
                           '2:|%s' % weekday_names,
                           '0:|%s' % hours_names])
    url = {'chs': '%dx%d' % (model.CHART_WIDTH * 2, model.CHART_HEIGHT),
           'chd': 'e:%s' % ','.join(points),
           'cht': 's',
           'chco': 'D6A43C',
           'chxt': 'x,y,r',
           'chxp': axis,
           'chxl': axis_names}
    return 'http://chart.apis.google.com/chart?' + urllib.urlencode(url) 

  def GrantBadges(self):
    self.metadata.country = self.country
    self.metadata.country_position = self.country_position
    self.metadata.first_place = self.first_place
    self.metadata.first_place_permanent = self.forever
    self.metadata.granted_badges, self.metadata.skipped_badges = (
        badge.GrantBadges(self.metadata))

  def GenerateEvents(self):
    self.events = events.GenerateEvents(self.old_metadata, self.metadata)
    if self.events:
      deferred.defer(PostEvents, self.user, self.events)

  def WriteDatastore(self):
    self.spojuser = model.SpojUser(
        key_name=self.user, name=self.name, country=self.country,
        badges=self.metadata.granted_badges,
        last_update=datetime.datetime.now(),
        version=model.VERSION,
        language_chart=self.language_chart,
        timeline=self.timeline,
        punchcard=self.punchcard)
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
