# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseServerError, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.vary import vary_on_headers
from django.contrib.auth.models import *
#from django.core.paginator import Paginator, InvalidPage, EmptyPage
#from django.core import serializers
from django.shortcuts import get_object_or_404
#from django.core.cache import cache
from geniusloci.loc.models import *
import foursquare
from decimal import *
import cgi
import logging
import urllib
import math
from django.db import connection
import geopy


def near_me(request):
	if request.POST:
		address = request.POST['address']

def login(request):
	error = None
	logging.debug
	if request.user.is_authenticated():
		return HttpResponseRedirect('/')

	if request.GET:
		if 'code' in request.GET:
			args = {
				'client_id': '129708490411788',
				'redirect_uri': 'http://www.euproweb.eu/login/',
				'client_secret': '359e32a34b5cbe94d452d7465803a20f',
				'code': request.GET['code'],
			}
			url = 'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(args)
			response = cgi.parse_qs(urllib.urlopen(url).read())
			access_token = ''
			try: 
				access_token = response['access_token'][0]
			except:
				return HttpResponse(url)
                

			facebook_session = FacebookSession.objects.get_or_create(
				access_token=access_token,
			)[0]
			expires = response['expires'][0]
			facebook_session.expires = expires
			facebook_session.save()
			logging.debug('session')
			user = auth.authenticate(token=access_token, request = request)
			if user:
				if user.is_active:
					auth.login(request, user)
					if 'backTo' in request.GET:
						logging.debug('backto ' + request.GET['backTo'])
						return HttpResponseRedirect(request.GET['backTo'])
					return HttpResponseRedirect('/')
				else:
					error = 'AUTH_DISABLED'
			else:
				error = 'AUTH_FAILED'
		elif 'error_reason' in request.GET:
			error = 'AUTH_DENIED'
	return HttpResponseRedirect('/')




def index(request):
	tips = Tip.objects.all().order_by('-date')[:10]
	likes = Like.objects.all().order_by('-date')[:10]	
	
	places = Place.objects.filter(foursquare_category__isnull = False).order_by('-id')[:30]
	c = RequestContext(request, {'places': places, 'tips': tips, 'likes': likes})
	t = loader.get_template('index.html')
	return HttpResponse(t.render(c))
	return HttpResponse('d')#render_to_response('index.html', template_context, context_instance = RequestContext(request))

def locate(request):
	query = request.GET['l']
	g = geopy.geocoders.Google()
	lat = 0
	lon = 0
	try:
		b = g.geocode_first(query)
		b = g.geocode(query)
		lat = b[1][0]
		lon = b[1][1]
	except Exception, ex:
		return HttpResponse('error ' + query + ' '+ ex.message)
		
	return HttpResponseRedirect('/mobile/home/?lat=' + str(lat) + '&lon=' + str(lon))

def search(request):
	query = request.GET['s']
	places = Place.objects.filter(name__icontains = query)[:50]
	c = RequestContext(request, {'places': places})
	t = loader.get_template('index.html')
	return HttpResponse(t.render(c))
	
	
def mobile_list(request):
	lat = 0
	lon = 0
	lat = request.GET.get('lat')
	lon = request.GET.get('lon')
	category = -1
	places = []
	if 'cat' in request.GET:
		category = int(request.GET['cat'])
	if 's' in request.GET:
	
			#filtering search by name
		places = find_near(lat, lon, 0.30, mult_limit = 20)
		places = filter_places_by_name(places, request.GET['s'])
	else:
		places = find_near(lat, lon, 0.30, 0.30, False, 20, category)#distance_orig = 0, null_foursquare_categ = False, mult_limit = 20
		
	if lat == None or len(lat) == 0:
		return HttpResponseRedirect('/geolocate/?')
	context_dict = {'venues': places, 'lat': lat, 'lon': lon}
	if 's'	in request.GET:
		context_dict['search'] = True
	c = RequestContext(request, context_dict)
	t = loader.get_template('mobile_list.html')
	return HttpResponse(t.render(c))	
	
def mobile_home(request):
	lat = 0
	lon = 0
	lat = request.GET.get('lat')
	lon = request.GET.get('lon')
	if lat == None or len(lat) == 0:
		return HttpResponseRedirect('/geolocate/?')
	api = foursquare.Api()
	
	try:
		groups =  api.get_venues(geolat = lat, geolong = lon, l = 50)['groups']
	
	
		
		venues = []
		if len(groups)> 0:
			for venue in groups[0]['venues']:
			
				name = venue['name']
				distance = venue['distance']
				address = venue['address']
				city = venue['city']
				category = None
				try:
					category = venue['primarycategory']
					category = category['fullpathname']
				except:
					pass
				f_id = venue['id']
				geolat = venue['geolat']
				geolong = venue['geolong']
				myvenue = {}
			
				place, created = Place.objects.get_or_create(foursquare_id__exact = f_id)
				if created == True:
					place.city = city.lower()
					place.name = name
					place.address = address
					place.foursquare_id = f_id
					if category == 'None':
						category = ''
					place.foursquare_category = category
					place.geolat = Decimal(str(geolat))
					place.geolong = Decimal(str(geolong))
					try:
						place.save()
						place_cat(place.id)
					except:
						logging.debug('error saving venue from 4sq')	
				else:
					logging.debug('venue already existing')
				try:	
					tips = venue['tips']
					analyze_tips(place, tips)
				except:
					logging.debug('can\'t find tips section')
				venues.append(place)
			pass#for
		pass#if
	
	except:
		pass
		
	places = []
	if 's' in request.GET:
		#filtering search by name
		places = find_near(lat, lon, 0.30, mult_limit = 100)
		places = filter_places_by_name(places, request.GET['s'])
	else:
		places = find_near(lat, lon, 0.30)
	c = RequestContext(request, {'venues': places.filter(points__gt = 0).order_by('-points')[:4], 'lat': lat, 'lon': lon})
	t = loader.get_template('mobile_home.html')
	return HttpResponse(t.render(c))
			
			
	
def mobile_home_list(request):
	lat = 0
	lon = 0
	lat = request.GET.get('lat')
	lon = request.GET.get('lon')
	cat = -1
	if 'cat' in request.GET:
		cat = int(request.GET['cat'])
	places = []
	if 's' in request.GET:
		#filtering search by name
		places = find_near(lat, lon, 0.30, mult_limit = 80)
		places = filter_places_by_name(places, request.GET['s'])
	else:
		places = find_near(lat, lon, 0.30)
		places = find_near(lat, lon, 0.30, 0, False, 20, cat)
	c = RequestContext(request, {'venues': places, 'lat': lat, 'lon': lon})
	t = loader.get_template('mobile_list.html')
	return HttpResponse(t.render(c))
	

def mobile_map(request):
	lat = 0
	lon = 0
	lat = request.GET.get('lat')
	lon = request.GET.get('lon')
	if lat == None or len(lat) == 0:
		return HttpResponseRedirect('/geolocate/?')
	api = foursquare.Api()
	
	try:
		groups =  api.get_venues(geolat = lat, geolong = lon, l = 50)['groups']
	
	
		
		venues = []
		if len(groups)> 0:
			for venue in groups[0]['venues']:
			
				name = venue['name']
				distance = venue['distance']
				address = venue['address']
				city = venue['city']
				category = None
				try:
					category = venue['primarycategory']
					category = category['fullpathname']
				except:
					pass
				f_id = venue['id']
				geolat = venue['geolat']
				geolong = venue['geolong']
				myvenue = {}
			
				place, created = Place.objects.get_or_create(foursquare_id__exact = f_id)
				if created == True:
					place.city = city.lower()
					place.name = name
					place.address = address
					place.foursquare_id = f_id
					if category == 'None':
						category = ''
					place.foursquare_category = category
					place.geolat = Decimal(str(geolat))
					place.geolong = Decimal(str(geolong))
					try:
						place.save()
					except:
						logging.debug('error saving venue from 4sq')	
				else:
					logging.debug('venue already existing')
				try:	
					tips = venue['tips']
					analyze_tips(place, tips)
				except:
					logging.debug('can\'t find tips section')
				venues.append(place)
			pass#for
		pass#if
	
	except:
		pass
		
	places = []
	if 's' in request.GET:
		#filtering search by name
		places = find_near(lat, lon, 0.20, mult_limit = 40)
		places = filter_places_by_name(places, request.GET['s'])
	else:
		places = find_near(lat, lon, 0.30)
	
	for place in places:
		if place.category == 0:
			pass
		else:
			place.marker = ''
	c = RequestContext(request, {'places': places, 'lat': lat, 'lon': lon})
	t = loader.get_template('mobile_map.html')
	return HttpResponse(t.render(c))	


def place(request, slug, id):
	place = None
	try:
		place = Place.objects.get(pk = id)
	except:
		return HttpResponseServerError(id)
		
	likes = Like.objects.filter(place__exact = place)
	tips = Tip.objects.filter(place__exact = place)
	nearplaces = find_near(place.geolat, place.geolong, 0.10, 0.10, False, 3)[:3]
	
	c = RequestContext(request, {'place': place, 'likes': likes,'tips': tips, 'nearplaces': nearplaces, })
	t = loader.get_template('place.html')
	return HttpResponse(t.render(c))	
		


def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')

def services_mobile_tip(request, id):
	place = Place.objects.get(pk = id)
	if not 't' in request.GET or not request.user.is_authenticated():
		return HttpResponseRedirect("/p/" + str(place.slug()) + "/" + str(place.id) + "/")
	t = request.GET['t']
	tip = Tip(place = place)
	tip.user = request.user
	tip.source = 0
	tip.text = t
	tip.save()
	return HttpResponseRedirect("/mobile/p/" + str(place.slug()) + "/" + str(place.id) + "/")


def services_tip(request, id):
	place = Place.objects.get(pk = id)
	if not 't' in request.GET or not request.user.is_authenticated():
		return HttpResponseRedirect("/p/" + str(place.slug()) + "/" + str(place.id) + "/")
	t = request.GET['t']
	tip = Tip(place = place)
	tip.user = request.user
	tip.source = 0
	tip.text = t
	tip.save()
	return HttpResponseRedirect("/p/" + str(place.slug()) + "/" + str(place.id) + "/")


def services_like(request, id):
	place = Place.objects.get(pk = id)
	if request.user.is_authenticated():
	 	count = Like.objects.filter(place__id__exact = id, user__exact = request.user).count()
		if count == 0:
			like = Like(place = place)
			like.user = request.user
			like.save()
			place.points = place.points + 1
			place.save()
		pass
	return HttpResponseRedirect("/p/" + str(place.slug()) + "/" + str(place.id) + "/")
	

def services_mobile_like(request, id):
	place = Place.objects.get(pk = id)
	if request.user.is_authenticated():
	 	count = Like.objects.filter(place__id__exact = id, user__exact = request.user).count()
		if count == 0:
			like = Like(place = place)
			like.user = request.user
			like.save()
			place.points = place.points + 1
			place.save()
		pass
	return HttpResponseRedirect("/mobile/p/" + str(place.slug()) + "/" + str(place.id) + "/")

	
	
def mobile_place(request, slug, id):
	lat = ''
	lon = ''
	try:
		lat = request.GET['lat']
		lon = request.GET['lon']
	except:
		pass
	place = None
	try:
		place = Place.objects.get(pk = id)
	except:
		return HttpResponseServerError(id)
	likes = Like.objects.filter(place__exact = place)
	tips = Tip.objects.filter(place__exact = place)
	likecount = likes.count()
	likes = likes.order_by('-date')[:5]
	tipscount = tips.count()
	tips = tips[:3]
	context_data = {'place': place, 'likes': likes, 'tips': tips, 'likecount': likecount, 'tipscount': tipscount,   'lat': lat, 'lon': lon}
	if 'from' in request.GET:
		context_data['from'] = request.GET['from'].replace('%26', '&')
	c = RequestContext(request, context_data)
	t = loader.get_template('mobile_place.html')
	return HttpResponse(t.render(c))	
	
	
	
	
#500m = 0.33 miles ca
#places = find_near(lat, lon, 0.30, 0.30, False, 20, category)
def find_near(mylat, mylong, distance, distance_orig = 0, null_foursquare_categ = False, mult_limit = 20, category = -1):
	mylong = float(str(mylong))
	mylat = float(str(mylat))
	lon1 = mylong - distance/math.fabs(math.cos(math.radians(mylat))*69)

	lon2 = mylong + distance/math.fabs(math.cos(math.radians(mylat))*69)


	lat1= mylat - (distance/69)
	lat2 = mylat+(distance/69)
	
	places = Place.objects.filter(geolong__gte = str(lon1), geolong__lte = str(lon2), geolat__gte = str(lat1), geolat__lte = str(lat2), foursquare_category__isnull = False)
	print 'category ' + str(category)
	if category >= 0:
		print 'filtering by categ ' + str(category)
		places = places.filter(category__exact = category)
	else:
		places = places.filter(category__gte = 1)
	if places.count() > 10 and mult_limit <= 20:
		return places
	if distance_orig == 0:
		distance_orig = distance
	elif distance > distance_orig * mult_limit: #mult_limit times the original distance
		return places
	logging.debug('new find near query ' + str(distance))
	return find_near(mylat, mylong, distance * 2, distance_orig, null_foursquare_categ, mult_limit, category)

def filter_places_by_name(places, name):
	return places.filter(name__icontains = name)

def analyze_tips(place, tips):
	e_tips = Tip.objects.filter(place__exact = place)
	for tip in tips:
		text = tip['text']
		loggin.debug('tip: ' + text)
		
		found = False
		for e_tip in tips:
			if e_tip.text.lower() == text.lower():
				logging.debug('tip existing ' + text)
				found = True
				break
			pass
		pass
		
		if not found:
			#create new tip
			newtip = Tip()
			newtip.text = text
			newtip.place = place
			newtip.save()
		pass
		
def place_cat(place_id):
	place = Place.objects.get(pk = place_id)
	cat = place.foursquare_category
	if cat is None:
		return
	print cat
	if cat.find('Arts & Entertainment:') == 0:
		place.category = 1 #visit
	if cat.find('Food:') == 0:
		place.category = 2 #eat
	if cat.find('Parks & Outdoors:') == 0:
		place.category = 1 #visit		
	#Shops:
	if cat.find('Shops:') == 0:
		place.category = 3 #shop
	#Travel:
	if cat.find('Travel:') == 0:
		place.category = 1 #visit
	#Home / Work / Other:
	if cat.find('Home / Work / Other:') == 0:
		place.category = 0 #excluded
	#Nightlife:
	if cat.find('Nightlife:') == 0:
		place.category = 4 #have fun
	place.save()
		
		