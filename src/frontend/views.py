import cgi, copy, time
from django.utils import simplejson as json
import controller
import geo.geotypes
from model import ParkingLot, ParkingSpace, LotGeoPoint
import os.path
from datetime import datetime, time

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db

base_path = os.path.dirname(__file__)
MI_TO_M = 1609

class MainPage(webapp.RequestHandler) :
    def get(self) :
        self.redirect('/lot/')

class LotPage(webapp.RequestHandler) :
    def get(self) :
        lots = ParkingLot.all()
        lots.order('-timestamp')

        values = {
            'title': 'Available Parking Lots',
            'body_actions': 'onload="initialize();"',
            'lots': lots,
        }
        path = os.path.join(base_path, 'templates/main.html')
        self.response.out.write(template.render(path, values))

    def post(self) :
        # Get data from request
        lot_id = self.request.get('lot_id')
        space_count = int(self.request.get('space_count'))
        if self.request.get('geo_pt') :
            (lat, lon) = self.request.get('geo_pt').split(',')
        else :
            (lat, lon) = (None, None)

        # create the lot
        controller.makeLot(lot_id, space_count, lat, lon)

        # return status 201
        self.response.set_status(201)
        self.redirect('/lot/')

class LotHandler(webapp.RequestHandler) :
    def show_json(self, spaces, lot) :
        if lot.geo_point :
            geo_pt = lot.geo_point.location
            geo_point = str(geo_pt.lat)+','+str(geo_pt.lon)
        else :
            geo_point = None

        spaces_out = []
        for s in spaces :
            space_out = {}
            space_out['space_id'] = s.key().name()
            space_out['is_empty'] = s.is_empty
            space_out['extra_info'] = s.extra_info
            space_out['timestamp'] = time.mktime(s.timestamp.timetuple())
            spaces_out.append(space_out)
        json_out = {'lot_id':lot.key().name(),
                    'geo_pt':geo_point,
                    'timestamp':time.mktime(lot.timestamp.timetuple()),
                    'spaces':spaces_out}
        self.response.out.write(json.dumps(json_out))

    def get(self, lot_id, type) :
        (spaces, lot) = controller.getSpaces(lot_id)
        if lot == None :
            self.error(404)
            values = {'title':'Error: Not Found',
                      'code': 404,
                      'message':'Could not find a lot by that id.'}
            path = os.path.join(base_path, 'templates/error.html')
            self.response.out.write(template.render(path, values))
            return

        full_spaces = copy.deepcopy(spaces)
        full_spaces.filter('is_empty =', False)

        if type == None or type == '/' :
            view = 'html'
        else :
            view = type.strip('/.')

        if view == 'json' :
            self.show_json(spaces, lot)
            return
        
        if lot.geo_point :
            geo_pt = lot.geo_point.location
            geo_point = str(geo_pt.lat)+','+str(geo_pt.lon)
            distance = 10 * MI_TO_M
            proxy = LotGeoPoint.proximity_fetch(LotGeoPoint.all(), geo_pt,
                                                max_results=10,
                                                max_distance=distance)
            near_lots = []
            for p in proxy :
                near_lots.append(ParkingLot.get_by_key_name(p.lot_id))
        else :
            geo_point = None
            near_lots = None

        values = {
            'title': 'Parking Lot '+lot_id,
            'lot': lot,
            'full_ratio': 100 * lot.full_count / lot.space_count,
            'unknown_ratio': 100 * lot.unknown_count / lot.space_count,
            'spaces': full_spaces,
            'geo_point': geo_point,
            'near_lots': near_lots,
            'body_actions': 'onload="initialize();"',
        }

        if self.request.get('nomap') == 'true' :
            values['nomap'] = True

        if view == 'html' :
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
        success = controller.putSpaces(lot_id, my_json)

        # return status 303 with location set to get
        if success :
            self.response.set_status(303)
        else :
            self.response.set_status(400)

class ChartPage(webapp.RequestHandler) :
    def get(self) :
        lots = ParkingLot.all()
        lots.order('-timestamp')

        values = {
            'title': 'Parking Lots',
            'lots': lots,
        }
        path = os.path.join(base_path, 'templates/chart_main.html')
        self.response.out.write(template.render(path, values))

class ChartHandler(webapp.RequestHandler) :
	def get(self, lot_id, type) :
		path = os.path.join(base_path, 'templates/chart.html')
		values = {}
		self.response.out.write(template.render(path, values))

	def post(self, lot_id, type) :
		min_date = self.request.get('mindate')
		max_date = self.request.get('maxdate')
		min_hour = self.request.get('minhour')
		min_minute = self.request.get('minminute')
		max_hour = self.request.get('maxhour')
		max_minute = self.request.get('maxminute')

		if min_date != '' :
			min_datetime = datetime.strptime(min_date, '%m/%d/%Y')
		else :
			min_datetime = datetime.min
		if max_date != '' :
			max_datetime = datetime.strptime(max_date, '%m/%d/%Y')
		else :
			max_datetime = datetime.max

		min_time = time(int(min_hour), int(min_minute))
		max_time = time(int(max_hour), int(max_minute))
		if int(max_hour) == 0 and int(max_minute) == 0 :
			# special case, we want end-of-day
			max_time = time.max
		min_datetime = datetime.combine(min_datetime.date(), min_time)
		max_datetime = datetime.combine(max_datetime.date(), max_time)

		# controller query
		buckets = controller.viewRange(lot_id, min_datetime, max_datetime)
		max_count = max(e['average'] for e in buckets)

		values = {'min_date':min_date, 'max_date':max_date,
				'buckets':buckets, 'max_count':max_count, 'lot_id':lot_id}
		path = os.path.join(base_path, 'templates/chart.html')
		self.response.out.write(template.render(path, values))
