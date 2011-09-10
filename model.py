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


class GenericList(object):
  def __init__(self, instance_type):
    self.problems = []
    self.instance_type = instance_type

  def __iter__(self):
    return self.problems.__iter__()

  def __len__(self):
    return len(self.problems)

  def __str__(self):
    return ";".join(str(i) for i in self.problems)

  def append(self, value):
    if not isinstance(value, self.instance_type):
      raise ValueError()
    self.problems.append(value)


class GenericListProperty(db.Property):
  data_type = GenericList

  def __init__(self, instance_type):
    self.instance_type = instance_type
    super(GenericListProperty, self).__init__()

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
      raise ValueError()
    return value


class Badge(object):
  def __init__(self, name, description):
    self.name = name
    self.description = description


class SpojUser(db.Model):
  name = db.StringProperty(required=True)
  country = db.StringProperty(required=True)
  last_update = db.DateTimeProperty(required=True)
  badges = GenericListProperty(Badge)

  def __str__(self):
    return ",".join([self.name, self.country, 
                     str(self.last_update), str(self.badges)])


class SpojUserMetadata(db.Model):
  problems = GenericListProperty(UserProblem)

  def __str__(self):
    return str(self.problems)

