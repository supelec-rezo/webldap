import os, sys

sys.path.append('/var/www/webldap')

os.environ['DJANGO_SETTINGS_MODULE'] = 'ldap_server.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
