from django.conf.urls import patterns, include, url
from os import path

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

site_media = path.join( path.dirname(__file__), 'media')

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hsolitaire.views.home', name='home'),
    # url(r'^hsolitaire/', include('hsolitaire.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', 'games.views.main_page', name='home'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
    url (r'^rules/$', 'games.views.rules_page', name='rules'),
    url (r'^interface/$', 'games.views.interface_page', name='interface'),
    url (r'^about/$', 'games.views.about_page', name='about'),
    url (r'^logout/$', 'games.views.logout_page', name='logout'),
    url (r'^newgame/$', 'games.views.new_random_game', name='newgame'),
	url (r'^newwinnable/$', 'games.views.new_winnable_game', name='newwinnable'),
	url (r'^quick/$', 'games.views.new_quick_game', name='newquick'),
    url (r'^continue/$', 'games.views.continue_game', name='continue'),
    url (r'^load/$', 'games.views.load_game', name='load'),
    url (r'^win/$', 'games.views.win', name='win'),
    url (r'^register/$', 'games.views.register_page', name='register'),
    url(r'^game/(?P<game_id>\d+)/$', 'games.views.game_page', name='game'),
    #url(r'^obvious/(?P<game_id>\d+)/$', 'games.views.apply_obvious', name='obvious'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media}, name='media'),
    url(r'^game/(?P<game_id>\d+)/move/$', 'games.views.move', name='move'),
    url(r'^game/(?P<game_id>\d+)/delete/$', 'games.views.delete', name='delete'),
    url(r'^game/(?P<game_id>\d+)/giveup/$', 'games.views.give_up', name='giveup'),
    url(r'^game/(?P<game_id>\d+)/savename/$', 'games.views.save_name', name='savename'),
)
