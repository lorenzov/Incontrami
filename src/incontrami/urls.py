from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from loc.views import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^geniusloci/', include('geniusloci.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # Uncomment the next line to enable the admin:
    #(r'^admin/', include(admin.site.urls)),
	
	(r'^$', 'incontrami.dating.views.index'),
	
	(r'^logout/$', 'incontrami.dating.views.logout_view'),
	
	(r'^login/$', 'incontrami.dating.views.login'),
	#mobile site
	
	(r'^static/(?P<path>.*)$', 'django.views.static.serve',
	        {'document_root': '/home/ubuntu/geniusloci/src/iui/'}),
			(r'^xd_receiver\.html$', direct_to_template, {'template': 'xd_receiver.htm'}),
	
)
