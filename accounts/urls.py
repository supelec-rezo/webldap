from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('accounts.views',
    # Profiles
    url(r'^account/$', 'account'),
    url(r'^account/jpeg_photo/$', 'jpeg_photo'),
)
