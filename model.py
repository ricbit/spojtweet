import pickle
from google.appengine.ext import db

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


class UserProblemList(object):
  def __init__(self):
    self.problems = []

  def __iter__(self):
    return self.problems.__iter__()

  def __str__(self):
    return ",".join(str(i) for i in self.problems)

  def append(self, value):
    self.problems.append(value)


class UserProblemProperty(db.Property):
  data_type = UserProblemList

  def get_value_for_datastore(self, model_instance):
    problem = super(UserProblemProperty,
                    self).get_value_for_datastore(model_instance)
    return db.Blob(pickle.dumps(problem, 2))

  def make_value_from_datastore(self, value):
    if value is None:
      return None
    return pickle.loads(value)


class SpojUser(db.Model):
  name = db.StringProperty(required=True)
  country = db.StringProperty(required=True)
  last_update = db.DateTimeProperty(required=True)
  badges = db.StringListProperty(required=True)
  # metadata

  def __str__(self):
    return ",".join([self.name, self.country, 
                     str(self.last_update), str(self.badges)])


class SpojUserMetadata(db.Model):
  user = db.ReferenceProperty(SpojUser, collection_name='metadata')
  problems = UserProblemProperty()

