from google.appengine.ext import db

class SpojUser(db.Model):
  name = db.StringProperty(required=True)
  country = db.StringProperty(required=True)
  # problems

class SpojProblem(db.Model):
  user = db.ReferenceProperty(SpojUser, collection_name='problems')
  code = db.StringProperty(required=True)
  date = db.DateTimeProperty(required=True)
  language = db.StringProperty(required=True)
