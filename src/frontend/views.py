import cgi
from django.utils import simplejson as json
from controller import Query
from model import ParkingLot, ParkingSpace
import os.path

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db

class MainPage(webapp.RequestHandler) :
    def get(self) :
        self.redirect('/lot/')

class LotPage(webapp.RequestHandler) :
    def get(self) :
        lots = ParkingLot.all()
        lots.order('-timestamp')

        values = {
            'title': 'Available Parking Lots',
            'body_actions': 'onload="geo_locate();"',
            'lots': lots,
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
        self.response.out.write(template.render(path, values))

    def post(self) :
        # create a new lot
        lot_id = self.request.get('lot_id')
        space_count = int(self.request.get('space_count'))
        geo_pt = self.request.get('geo_pt')

        lot = ParkingLot(key_name=lot_id)
        lot.lot_id = lot_id
        lot.space_count = space_count
        lot.geo_point = db.GeoPt(*geo_pt.split(','))
        lot.put()

        # return status 201
        self.response.set_status(201)
        self.redirect('/lot/')

class LotHandler(webapp.RequestHandler) :
    def get(self, lot_id) :
        q = Query()
        (spaces, lot) = q.getSpaces(lot_id)
        
        if lot.geo_point :
            geo_point = str(lot.geo_point.lat)+','+str(lot.geo_point.lon)
        else :
            geo_point = None

        space_count = lot.space_count
        empty = 0
        for space in spaces :
            if space.is_empty :
                empty += 1

        values = {
            'title': 'Parking Lot '+lot_id,
            'empty': empty,
            'space_count': space_count,
            'fullness': 100.0 * empty / space_count,
            'spaces': spaces,
            'geo_point': geo_point,
            'body_actions': 'onload="initialize();"',
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/lot.html')
        self.response.out.write(template.render(path, values))

    def put(self, lot_id) :
        my_json = json.loads(self.request.body)

        # process the data
        q = Query()
        q.putSpaces(lot_id, my_json)

        # return status 303 with location set to get
        self.response.set_status(303)

