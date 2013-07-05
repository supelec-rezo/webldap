from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('accesses.views',
    # Profiles
    url(r'^accesses/$', 'index'),
    url(r'^accesses/(?P<type>(web|server|app))/(?P<name>[a-z0-9]+)/$', 'show')
)
