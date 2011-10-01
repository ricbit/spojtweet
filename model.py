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

"""Models used to store data on datastore."""

__author__ = 'ricbit@google.com (Ricardo Bittencourt)'

import pickle

from google.appengine.ext import db

import badge

VERSION = 7

class UserProblem(object):
  def __init__(self, code,
               solved=False,
               languages=None,
               tries_before_ac=None,
               first_attempt_date=None,
               first_ac_date=None,
               best_time=None):
    self.code = code
    self.solved = solved
    self.languages = languages
    self.tries_before_ac = tries_before_ac
    self.first_attempt_date = first_attempt_date
    self.first_ac_date = first_ac_date
    self.best_time = best_time

  def __str__(self):
    return ",".join(str(i) for i in
        [self.code, self.solved, self.languages, self.tries_before_ac,
         self.first_attempt_date, self.first_ac_date, self.best_time])


class GenericListProperty(db.Property):
  data_type = list

  def __init__(self, instance_type):
    self.instance_type = instance_type
    super(GenericListProperty, self).__init__(indexed=False)

  def get_value_for_datastore(self, model_instance):
    problem = super(GenericListProperty,
                    self).get_value_for_datastore(model_instance)
    return db.Blob(pickle.dumps(problem, 2))

  def make_value_from_datastore(self, value):
    if value is None:
      return None
    return pickle.loads(value)

  def validate(self, value):
    if value is None:
      return None
    if not isinstance(value, list):
      raise ValueError()
    for item in value:
      if not isinstance(item, self.instance_type):
        raise ValueError()
    return value

class SpojUser(db.Model):
  name = db.StringProperty(indexed=False)
  country = db.StringProperty(indexed=False)
  last_update = db.DateTimeProperty(indexed=False)
  badges = GenericListProperty(badge.Badge)
  version = db.IntegerProperty(indexed=False)

  def __str__(self):
    return ",".join([self.name, self.country,
                     str(self.last_update),
                     ";".join(str(i) for i in self.badges)])


class SpojUserMetadata(db.Model):
  problems = GenericListProperty(UserProblem)
  granted_badges = GenericListProperty(badge.Badge)
  skipped_badges = GenericListProperty(badge.Badge)
  country_position = db.IntegerProperty(indexed=False)
  first_place = db.IntegerProperty(indexed=False)

  def __str__(self):
    return str(self.problems)

class UserPosition(object):
  def __init__(self, name, position):
    self.name = name
    self.position = position

  def __str__(self):
    return "(%s, %s)" % (self.name, self.position)

class CountryInfo(db.Model):
  users = GenericListProperty(UserPosition)

  def __str__(self):
    return ";".join(str(i) for i in self.users)

class ProblemList(db.Model):
  problems = GenericListProperty(str)

  def __str__(self):
    return ';'.join(i for i in self.problems)

class ProblemDetails(db.Model):
  name = db.StringProperty(indexed=False)
  users_accepted = db.IntegerProperty(indexed=False)
  submissions = db.IntegerProperty(indexed=False)
  accepted = db.IntegerProperty(indexed=False)
  wrong_answer = db.IntegerProperty(indexed=False)
  compile_error = db.IntegerProperty(indexed=False)
  runtime_error = db.IntegerProperty(indexed=False)
  time_limit_exceeded = db.IntegerProperty(indexed=False)
  first_place = db.StringProperty()
  first_place_permanent = db.StringProperty()

class OAuthData(db.Model):
  oauth_key = db.StringProperty(indexed=False)
  oauth_secret = db.StringProperty(indexed=False)

class UserPreferences(db.Model):
  twitter_screen_name = db.StringProperty(indexed=False)
  session_id = db.StringProperty(indexed=False)
  session_start = db.DateTimeProperty(indexed=False)
  spoj_user = db.StringProperty()
  send_solution = db.BooleanProperty(indexed=False)
  send_badge = db.BooleanProperty(indexed=False)
