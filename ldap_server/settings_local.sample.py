# Local settings
import os

SETTINGS_PATH = os.path.dirname(os.path.realpath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',             # Or path to database file if using sqlite3.
        'USER': '',             # Not used with sqlite3.
        'PASSWORD': '',         # Not used with sqlite3.
        'HOST': '',             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',             # Set to empty string for default. Not used with sqlite3.
    }
}

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SETTINGS_PATH, '../templates/')
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'SET ME'

# Settings specific to 'accounts'

# SMTP relay (host and port) to use for confirmation mails
EMAIL_HOST = 'incoming-relays.illinois.edu'
EMAIL_PORT = 25

# Address to appear in From field
EMAIL_FROM = 'userhelp@example.org'

# Number of hours a token sent by email remains valid after having been
# created. Numeric and string versions should have the same meaning.
REQ_EXPIRE_HRS = 48
REQ_EXPIRE_STR = '48 heures'

# Special user credentials to bind to the LDAP server
DEFAULT_BIND_DICT = {
    'NAME': 'ldap://domain.com/',                    # LDAP server URL
    'USER': 'cn=admin,dc=domain,dc=com',     # Bind user dn
    'PASSWORD': '',                               # Bind user password
    'CACERT': None,
    'STARTTLS': False
}

# Default LDAP groups for created users
LDAP_DEFAULT_GROUPS = []
