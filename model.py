import pickle
from google.appengine.ext import db

import badge

VERSION = 2

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
  name = db.StringProperty()
  country = db.StringProperty()
  last_update = db.DateTimeProperty(indexed=False)
  badges = GenericListProperty(badge.Badge)
  version = db.IntegerProperty()

  def __str__(self):
    return ",".join([self.name, self.country, 
                     str(self.last_update),
		     ";".join(str(i) for i in self.badges)])


class SpojUserMetadata(db.Model):
  problems = GenericListProperty(UserProblem)
  country_position = db.IntegerProperty()
  first_place = db.IntegerProperty()

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
  name = db.StringProperty()
  users_accepted = db.IntegerProperty()
  submissions = db.IntegerProperty()
  accepted = db.IntegerProperty()
  wrong_answer = db.IntegerProperty()
  compile_error = db.IntegerProperty()
  runtime_error = db.IntegerProperty()
  time_limit_exceeded = db.IntegerProperty()
  first_place = db.StringProperty()
  first_place_time = db.IntegerProperty()
