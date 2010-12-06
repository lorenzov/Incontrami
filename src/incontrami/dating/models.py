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

