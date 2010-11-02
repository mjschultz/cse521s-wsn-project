from google.appengine.ext import db

class ParkingLot(db.Model) :
    lot_id = db.StringProperty()
    timestamp = db.DateTimeProperty(auto_now=True)
    space_count = db.IntegerProperty()
    geo_point = db.GeoPtProperty()

class ParkingSpace(db.Model) :
    lot = db.ReferenceProperty(ParkingLot)
    space_id = db.StringProperty()
    is_empty = db.BooleanProperty()
    timestamp = db.DateTimeProperty(auto_now=True)
    extra_info = db.TextProperty()
