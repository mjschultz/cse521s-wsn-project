import cgi, copy
from model import ParkingLot, ParkingSpace

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

class Controller :
    def makeLot(self, lot_id, space_count, lat, lon) :
        lot = ParkingLot(key_name=lot_id)
        lot.lot_id = lot_id
        lot.space_count = space_count
        if lat != None and lon != None :
            lot.geo_point = db.GeoPt(lat, lon)

        lot.full_count = 0
        lot.empty_count = 0
        lot.unknown_count = space_count

        lot.put()

    def getSpaces(self, lot_id) :
        lot = ParkingLot.get_by_key_name(lot_id)
        spaces = ParkingSpace.all()
        spaces.filter('lot =', lot).order('-timestamp')
        return (spaces, lot)

    def putSpaces(self, lot_id, data) :
        # if lot exists, update the data
        lot = ParkingLot.get_by_key_name(lot_id)

        if lot == None :
            return False

        # update any spaces (insert if they didn't exist before)
        for d in data :
            space_id = str(d['space_id'])
            is_empty = d['is_empty']
            del d['space_id']
            del d['is_empty']
            extra_info = ''
            for k in d.keys() :
                extra_info += k+':'+str(d[k])+';'

            space = ParkingSpace.get_or_insert(space_id)
            space.lot = lot.key()
            space.space_id = space_id
            space.is_empty = is_empty
            space.extra_info = extra_info
            space.put()

        # fix up the lot data
        spaces = ParkingSpace.all()
        spaces.filter('lot =', lot)
        full_spaces = copy.deepcopy(spaces)
        full_count = full_spaces.filter('is_empty =', False).count()
        unknown_count = lot.space_count - spaces.count()
        empty_count = lot.space_count - unknown_count - full_count
        lot.full_count = full_count
        lot.empty_count = empty_count
        lot.unknown_count = unknown_count
        lot.put()

        return True
