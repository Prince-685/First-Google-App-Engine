from google.cloud import ndb

class User(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    mobile = ndb.StringProperty()