from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('accessess.views',
    # Profiles
    url(r'^accesses/$', 'index'),
)
