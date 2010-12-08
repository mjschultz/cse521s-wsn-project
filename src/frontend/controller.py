import cgi, copy
from model import ParkingLot, ParkingSpace, LotGeoPoint, SpaceLog, LotLog

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

def makeLot(lot_id, space_count, lat, lon) :
    lot = ParkingLot(key_name=lot_id)
    lot.lot_id = lot_id
    lot.space_count = space_count
    if lat != None and lon != None :
        point = LotGeoPoint(location=db.GeoPt(lat,lon), lot_id=lot_id)
        point.update_location()
        point.put()
        lot.geo_point = point

    lot.full_count = 0
    lot.empty_count = 0
    lot.unknown_count = space_count
    lot.put()

def viewRange(lot_id, min_datetime=None, max_datetime=None) :
	lot = ParkingLot.get_by_key_name(lot_id)
	log = LotLog.all()
	log.filter('lot =', lot)
	if min_datetime :
		log.filter('timestamp >=', min_datetime)
	if max_datetime :
		log.filter('timestamp <=', max_datetime)

	my_log = []
	min_time = min_datetime.time()
	max_time = max_datetime.time()
	for e in log :
		e_time = e.timestamp.time()
		print min_time, e_time, max_time
		if min_time <= e_time <= max_time :
			my_log.append(e)
	return my_log

def getSpaces(lot_id) :
    lot = ParkingLot.get_by_key_name(lot_id)
    spaces = ParkingSpace.all()
    spaces.filter('lot =', lot).order('-timestamp')
    return (spaces, lot)

def putSpaces(lot_id, data) :
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

        log = SpaceLog(space=space)
        log.is_empty = is_empty
        log.extra_info = extra_info
        log.put()

    # fix up the lot data
    spaces = ParkingSpace.all()
    spaces.filter('lot =', lot)
    full_spaces = copy.deepcopy(spaces)
    # update the number of spaces in the lot (if needed)
    # (we know about the number of spaces we've seen)
    if spaces.count() > lot.space_count :
        lot.space_count = spaces.count()
    full_count = full_spaces.filter('is_empty =', False).count()
    unknown_count = lot.space_count - spaces.count()
    empty_count = lot.space_count - unknown_count - full_count
    lot.full_count = full_count
    lot.empty_count = empty_count
    lot.unknown_count = unknown_count
    lot.put()

    log = LotLog(lot=lot)
    log.space_count = lot.space_count
    log.full_count = lot.full_count
    log.empty_count = lot.empty_count
    log.unknown_count = lot.unknown_count
    log.put()

    return True
