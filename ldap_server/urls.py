from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('ldap_server.views',
    # Examples:
    # url(r'^$', 'ldap_server.views.home', name='home'),
    # url(r'^ldap_server/', include('ldap_server.foo.urls')),

    # Login, Logout, password recovery
    url(r'^$', 'home'),
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),
    url(r'^passwd/$', 'passwd'),
    url(r'^process/(?P<token>[a-z0-9]{32})/$', 'process'),

    # Help
    url(r'^help/$', 'help'),

    # Accounts urls
    url(r'', include('accounts.urls')),


    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
