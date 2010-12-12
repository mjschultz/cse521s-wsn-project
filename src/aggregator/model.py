from google.appengine.ext import db
import geo.geomodel

class LotGeoPoint(geo.geomodel.GeoModel) :
    lot_id = db.StringProperty(required=True)

class ParkingLot(db.Model) :
    lot_id = db.StringProperty()
    timestamp = db.DateTimeProperty(auto_now=True)
    space_count = db.IntegerProperty()
    full_count = db.IntegerProperty()
    empty_count = db.IntegerProperty()
    unknown_count = db.IntegerProperty()
    geo_point = db.ReferenceProperty(LotGeoPoint)

class ParkingSpace(db.Model) :
    lot = db.ReferenceProperty(ParkingLot)
    space_id = db.StringProperty()
    is_empty = db.BooleanProperty()
    timestamp = db.DateTimeProperty(auto_now=True)
    extra_info = db.TextProperty()

class SpaceLog(db.Model) :
    space = db.ReferenceProperty(ParkingSpace, required=True)
    timestamp = db.DateTimeProperty(auto_now=True)
    is_empty = db.BooleanProperty()
    extra_info = db.TextProperty()

class LotLog(db.Model) :
    lot = db.ReferenceProperty(ParkingLot, required=True)
    timestamp = db.DateTimeProperty(auto_now=True)
    space_count = db.IntegerProperty()
    full_count = db.IntegerProperty()
    empty_count = db.IntegerProperty()
    unknown_count = db.IntegerProperty()
