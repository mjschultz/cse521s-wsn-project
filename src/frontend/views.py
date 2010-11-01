import cgi
from django.utils import simplejson as json
from controller import Query
from model import ParkingLot, ParkingSpace

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db

class MainPage(webapp.RequestHandler) :
    def get(self) :
        self.redirect('/lot/')

class LotPage(webapp.RequestHandler) :
    def get(self) :
        lots = ParkingLot.all()
        lots.order('-timestamp')

        display = """<!doctype html>
<html><head><title>Parking Lots</title>
<script type="text/javascript">
function geo_locate() {
    if (navigator.geolocation) {
        geo_pt = document.getElementById('geo_pt');
        navigator.geolocation.getCurrentPosition(function(position) {
        loc = position.coords.latitude+","+position.coords.longitude;
        geo_pt.value = loc;
        });
    }
}
</script>
<style>
.field { display: block; margin:4px 0; }
.field > label { display: block; }
.required { font-weight:bold; }
</style>
</head><body onload="geo_locate();">
<h1>Available Parking Lots</h1>
"""
        display += '<ul>'
        for lot in lots :
            display += '<li><a href="/lot/'+lot.lot_id+'">'+lot.lot_id+'</a></li>'
        display += '</ul>'

        display += """
<form method="post">
    <fieldset>
        <legend>Create Parking Lot</legend>
        <div class="field required">
            <label for="lot_id">Lot Id:</label>
            <input type="text" name="lot_id" id="lot_id" />
        </div>
        <div class="field required">
            <label for="space_count">Number of Spaces:</label>
            <input type="number" name="space_count" id="space_count" />
        </div>
        <div class="field">
            <label for="geo_pt">Geo Location:</label>
            <input type="text" name="geo_pt" id="geo_pt" />
        </div>

        <input type="submit" name="submit" value="Create" />
    </fieldset>
</form>
"""
        self.response.out.write(display)

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
        
        title = 'Parking Lot '+lot_id
        html = '<!doctype html><html><head><title>'+title+'</title>'
        if lot.geo_point :
            lat = lot.geo_point.lat
            lon = lot.geo_point.lon
            point = str(lat)+','+str(lon)
            html += """
<style>
html { height: 100% }
body { height: 90%; margin: 0px; padding: 0px }
#map_canvas { height: 90% }
</style>
<script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>
<script type="text/javascript">
  function initialize() {
    var latlng = new google.maps.LatLng("""+point+""");
    var myOptions = {
      zoom: 14,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
    var marker = new google.maps.Marker({position: latlng, map: map, title:"Parking Lot: """+lot_id+""""});
  }
</script>
</head>
<body onload="initialize();">
"""
        else :
            html += '</head><body>'
        # return to normal processing
        html += '<h1>Parking Lot: '+str(lot_id)+'</h1>'
        html += '<ul>'
        empty = 0
        for space in spaces :
            if space.is_empty :
                status = 'empty'
                empty += 1
            else :
                status = 'full'
            html += '<li>Space '+space.key().name()+' is '+status+'</li>'
        html += '</ul>'

        fullness = 100.0*empty / lot.space_count
        html += '<p><em>'+str(empty)+'/'+str(lot.space_count)
        html += ' ('+str(fullness)+'%) fullness</em></p>'

        if lot.geo_point :
            html += '<div id="map_canvas" style="width:90%;height:90%;"></div>'
        self.response.out.write(html)

    def put(self, lot_id) :
        my_json = json.loads(self.request.body)

        # process the data
        q = Query()
        q.putSpaces(lot_id, my_json)

        # return status 303 with location set to get
        self.response.set_status(303)

