# -*- encoding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, RequestContext, loader
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.mail import send_mail
from django.utils import timezone

from accounts.forms import *

from models import Request

from ldap_server.backend.base import *
from ldap_server.base.models import *
from ldap_server.models import *
from ldap_server import helpers
from ldap_server import settings

# Context processor
def session_info(request):
    return { 
        'logged_in': request.session.get('ldap_connected', False),
        'logged_uid': request.session.get('ldap_uid', None) 
    }

# View decorator
def connect_ldap(view, login_url='/login', redirect_field_name=REDIRECT_FIELD_NAME):
    def _view(request, *args, **kwargs):
        if not request.session.get('ldap_connected', False):
            path = request.get_full_path()

            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(path, login_url, redirect_field_name)
        
        try:
            bind_dict = {
                'NAME': 'ldap://ldap.rez-gif.supelec.fr/',
                'USER': 'uid=%s,ou=People,dc=rezomen,dc=fr' % request.session['ldap_uid'],
                'PASSWORD': request.session['ldap_passwd'],
                'CACERT': None,
                'STARTTLS': False
            }

            db = LdapDatabase(settings_dict = bind_dict)
        
        except InvalidCredentials:
            return logout(request, redirect_field_name)
        
        return view(request, db=db, *args, **kwargs)
    
    return _view

@connect_ldap
def index(request, db):
    application_accesses = LdapApplicationAccessGroup.find_all(database=db)
    server_accesses = LdapServerAccessGroup.find_all(database=db)
    web_accesses = LdapWebAccessGroup.find_all(database=db)

    return render_to_response('accesses/index.html', {
                                'application_accesses': application_accesses,
                                'server_accesses': server_accesses,
                                'web_accesses': web_accesses
                                }, context_instance=RequestContext(request))