from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('accesses.views',
    # Profiles
    url(r'^accesses/$', 'index'),
)
