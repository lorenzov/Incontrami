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

