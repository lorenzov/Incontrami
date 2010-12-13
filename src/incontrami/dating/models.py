from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from random import choice

# Create your models here.


class FacebookUser(models.Model):
	facebook_id = models.CharField(max_length=100, unique=True)
	contrib_user = models.OneToOneField(User)
	contrib_password = models.CharField(max_length=100)


class UserProfile(models.Model):
	user = models.ForeignKey(User, unique = True, db_index = True)
	sex = models.CharField(max_length = 1, default = 'F', db_index = True)
	points = models.IntegerField(default = 0)
	
	
class Like(models.Model):
	liker = models.ForeignKey(User, related_name = 'liker')
	liked = models.ForeignKey(User, related_name = 'likeds')
	date = models.DateTimeField(auto_now_add = True)
	
	
class FacebookSessionError(Exception):   
		def __init__(self, error_type, message):
			self.message = message
			self.type = error_type
		def get_message(self): 
			return self.message
		def get_type(self):
			return self.type
		def __unicode__(self):
			return u'%s: "%s"' % (self.type, self.message)

class FacebookSession(models.Model):

		access_token = models.CharField(max_length=103, unique=True)
		expires = models.IntegerField(null=True)

		user = models.ForeignKey(User, null=True)
		uid = models.BigIntegerField(unique=True, null=True)

		class Meta:
			unique_together = (('user', 'uid'), ('access_token', 'expires'))

		def query(self, object_id, connection_type=None, metadata=False):
			import urllib
			import simplejson

			url = 'https://graph.facebook.com/%s' % (object_id)
			if connection_type:
				url += '/%s' % (connection_type)

			params = {'access_token': self.access_token}
			if metadata:
				params['metadata'] = 1

			url += '?' + urllib.urlencode(params)
			response = simplejson.load(urllib.urlopen(url))
			if 'error' in response:
				error = response['error']
				raise FacebookSessionError(error['type'], error['message'])
			return response


