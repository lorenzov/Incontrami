from django.db import models

# Create your models here.


class FacebookUser(models.Model):
	facebook_id = models.CharField(max_length=100, unique=True)
	contrib_user = models.OneToOneField(User)
	contrib_password = models.CharField(max_length=100)


class Like(models.Model):
	place = models.ForeignKey(Place, db_index = True)
	user = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add = True)
	valid = models.BooleanField(default = True)
	
class UserProfile(models.Model):
	user = models.ForeignKey(User, unique = True, db_index = True)

