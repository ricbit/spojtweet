from google.appengine.ext import db

class SpojUser(db.Model):
  name = db.StringProperty(required=True)
  country = db.StringProperty(required=True)
  last_update = db.DateTimeProperty(required=True)
  badges = db.StringListProperty(required=True)
  # problems

class UserProblem(db.Model):
  user = db.ReferenceProperty(SpojUser, collection_name='problems')
  code = db.StringProperty(required=True)
  languages = db.StringListProperty()
  solved = db.BooleanProperty()
  tries_before_ac = db.IntegerProperty()
  first_attempt_date = db.DateTimeProperty()
  first_ac_date = db.DateTimeProperty()
  best_time = db.IntegerProperty()

