import cgi, copy
from model import ParkingLot, ParkingSpace, LotGeoPoint, SpaceLog, LotLog

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from datetime import datetime, timedelta

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

def viewRange(lot_id, min_datetime=None, max_datetime=None, nbuckets=15) :
	lot = ParkingLot.get_by_key_name(lot_id)
	log = LotLog.all()
	log.filter('lot =', lot)
	if min_datetime :
		log.filter('timestamp >=', min_datetime)
	if max_datetime :
		log.filter('timestamp <=', max_datetime)

	buckets = [{'count':0,'n':0,'min':None,'max':None} for i in range(nbuckets)]
	min_time = min_datetime.time()
	max_time = max_datetime.time()
	min_dt = datetime.combine(datetime.now(), min_time)
	max_dt = datetime.combine(datetime.now(), max_time)
	td = max_dt - min_dt
	delta = td / nbuckets
	delta = delta.seconds
	for e in log :
		e_time = e.timestamp.time()
		e_dt = datetime.combine(datetime.now(), e_time)
		if min_time <= e_time <= max_time :
			d = e_dt - min_dt
			t = d.seconds / delta
			bucket = buckets[t]
			bucket['count'] += e.full_count
			bucket['n'] += 1
			if bucket['min'] == None or bucket['min'] > e.full_count :
				bucket['min'] = e.full_count
			if bucket['max'] == None or bucket['max'] < e.full_count :
				bucket['max'] = e.full_count

	for (i, b) in enumerate(buckets) :
		if b['n'] != 0 :
			b['average'] = b['count']/b['n']
		else :
			b['average'] = 0
		b['label'] = min_dt + timedelta(seconds=delta*i)
	return buckets

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
