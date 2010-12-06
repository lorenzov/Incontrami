import foursquare
from geniusloci.loc.models import *
import facebook_oauth

import time

categories = ['Arts & Entertainment', 'Arcade', 'Art Galley']


api = foursquare.Api()
places = Place.objects.all()


for place in places:
	placex = api.get_venue_detail(place.foursquare_id)
	venue = placex['venue']
	name = venue['name']
	address = venue['address']
	city = venue['city']
	category = None
	try:
		category = venue['primarycategory']
		category = category['fullpathname']
	except:
		pass
	print name
	print city
	print category
	place.name = name
	place.address = address
	place.city = city
	place.category = category
	place.save()
	time.sleep(10)
	