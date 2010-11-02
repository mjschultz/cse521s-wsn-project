import cgi
from model import ParkingLot, ParkingSpace

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

class Query :
    def getLot(self, lot_id) :
        return db.GqlQuery('SELECT * FROM ParkingLot WHERE lot_id = :1',
                           lot_id)

    def getSpaces(self, lot_id) :
        lot = ParkingLot.get_by_key_name(lot_id)
        spaces = ParkingSpace.all()
        spaces.filter('lot =', lot).order('-timestamp')
        return (spaces, lot)

    def putSpaces(self, lot_id, data) :
        # if lot exists, update the data
        lot = ParkingLot.get_by_key_name(lot_id)

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
            
