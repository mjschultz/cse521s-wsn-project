import cgi, copy, time
from django.utils import simplejson as json
from controller import Controller
from model import ParkingLot, ParkingSpace
import os.path

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db

base_path = os.path.dirname(__file__)

class MainPage(webapp.RequestHandler) :
    def get(self) :
        self.redirect('/lot/')

class LotPage(webapp.RequestHandler) :
    def get(self) :
        c = Controller()
        in_lots = ParkingLot.all()
        in_lots.order('-timestamp')

        lots = []
        for lot in in_lots :
            (spaces, temp) = c.getSpaces(lot.key().name())
            space_count = lot.space_count
            full_spaces = copy.deepcopy(spaces)
            full_count = full_spaces.filter('is_empty =', False).count()
            unknown_count = space_count - spaces.count()
            empty_count = space_count - unknown_count - full_count
            lots.append((lot, full_count, unknown_count, empty_count))

        values = {
            'title': 'Available Parking Lots',
            'body_actions': 'onload="geo_locate();"',
            'lots': lots,
        }
        path = os.path.join(base_path, 'templates/main.html')
        self.response.out.write(template.render(path, values))

    def post(self) :
        # Get data from request
        lot_id = self.request.get('lot_id')
        space_count = int(self.request.get('space_count'))
        (lat, lon) = self.request.get('geo_pt').split(',')

        # create the lot
        c.makeLot(lot_id, space_count, lat, lon)

        # return status 201
        self.response.set_status(201)
        self.redirect('/lot/')

class LotHandler(webapp.RequestHandler) :

    def get(self, lot_id, type) :
        c = Controller()
        (spaces, lot) = c.getSpaces(lot_id)

        if type == None or type == '/' :
            view = 'html'
        else :
            view = type.strip('/.')
        
        if lot.geo_point :
            geo_point = str(lot.geo_point.lat)+','+str(lot.geo_point.lon)
        else :
            geo_point = None

        space_count = lot.space_count
        full_spaces = copy.deepcopy(spaces)
        full_count = full_spaces.filter('is_empty =', False).count()
        unknown_count = space_count - spaces.count()
        empty_count = space_count - unknown_count - full_count

        values = {
            'title': 'Parking Lot '+lot_id,
            'lot': lot,
            'full_count': full_count,
            'space_count': space_count,
            'unknown_count': unknown_count,
            'empty_count': empty_count,
            'full_ratio': 100 * full_count / space_count,
            'unknown_ratio': 100 * unknown_count / space_count,
            'spaces': full_spaces,
            'geo_point': geo_point,
            'body_actions': 'onload="initialize();"',
        }

        if view == 'json' :
            spaces_out = []
            for s in spaces :
                space_out = {}
                space_out['space_id'] = s.key().name()
                space_out['is_empty'] = s.is_empty
                space_out['extra_info'] = s.extra_info
                space_out['timestamp'] = time.mktime(s.timestamp.timetuple())
                spaces_out.append(space_out)
            json_out = {'lot_id':lot_id,
                        'geo_pt':geo_point,
                        'timestamp':time.mktime(lot.timestamp.timetuple()),
                        'spaces':spaces_out}
            self.response.out.write(json.dumps(json_out))
        elif view == 'html' :
            path = os.path.join(base_path, 'templates/lot.html')
            self.response.out.write(template.render(path, values))
        else :
            self.error(404)
            values = {'title':'Error: Not Found',
                      'code': 404,
                      'message':'Not Found'}
            path = os.path.join(base_path, 'templates/error.html')
            self.response.out.write(template.render(path, values))

    def put(self, lot_id, type) :
        my_json = json.loads(self.request.body)

        # process the data
        c = Controller()
        c.putSpaces(lot_id, my_json)

        # return status 303 with location set to get
        self.response.set_status(303)

