from google.appengine.ext import db

class SpojUser(db.Model):
  name = db.StringProperty(required=True)
  country = db.StringProperty(required=True)
  last_update = db.DateTimeProperty(required=True)
  # problems

class UserProblem(db.Model):
  user = db.ReferenceProperty(SpojUser, collection_name='problems')
  code = db.StringProperty(required=True)
  status = db.StringProperty(required=True)
  date = db.DateTimeProperty(required=True)
  language = db.StringProperty(required=True)
