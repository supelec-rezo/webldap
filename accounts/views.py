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
def account(request, db):
    uid = request.session.get('ldap_uid', None)
    user = LdapUser(database = db, primary_value = uid)

    return render_to_response('accounts/account.html', {'user': user}, context_instance=RequestContext(request))


@connect_ldap
def jpeg_photo(request, db):
    from django.http import HttpResponse

    uid = request.session.get('ldap_uid', None)
    user = LdapUser(database = db, primary_value = uid)
    image = user.displayable_photo()

    # Serialize to HTTP response
    response = HttpResponse(mimetype="image/jpeg")
    image.save(response, "jpeg")
    return response

@connect_ldap
def edit_contact(request, db):
    uid = request.session.get('ldap_uid', None)
    user = LdapUser(database = db, primary_value = uid)

    if request.method == 'POST':
        form = AccountContactForm(request.POST)
        
        if form.is_valid():
            new_attributes = {
                'street': form.cleaned_data['street'],
                'city': form.cleaned_data['city'],
                'postal_code': form.cleaned_data['postal_code'],
                'postal_address': form.cleaned_data['postal_address'],
                'mobile': form.cleaned_data['mobile'],
                'rezomen_email_redirects_to': form.cleaned_data['redirects_to'],
                'rezomen_email_redirection_status': ('TRUE' if form.cleaned_data['redirection_status'] == True else 'FALSE')
            }

            try:
                user.update_attributes(new_attributes)
                user.save()
            except ConstraintViolation:
                request.flash['error'] = "La mise à jour des données transgresse une contrainte du LDAP."
            except InsufficientAccess:
                request.flash['error'] = "La mise à jour des données requiert des droits que vous ne possédez pas."
            except Exception:
                request.flash['error'] = "Une erreur s'est produite lors de la mise à jour."
            else:
                request.flash['success'] = "Vos coordonnées ont été mises à jour avec succès."
                return HttpResponseRedirect(reverse(account))

    else:
        form = AccountContactForm(label_suffix='', 
                                initial={ 
                                    'street': user.street,
                                    'city': user.city,
                                    'postal_code': user.postal_code,
                                    'postal_address': user.postal_address,
                                    'mobile': user.mobile,
                                    'redirects_to': user.rezomen_email_redirects_to,
                                    'redirection_status': (True if user.rezomen_email_redirection_status == 'TRUE' else False)
                                })

    c = { 'form': form }
    c.update(csrf(request))

    return render_to_response('accounts/edit_contact.html', c, context_instance=RequestContext(request))


@connect_ldap
def edit_description(request, db):
    uid = request.session.get('ldap_uid', None)
    user = LdapUser(database = db, primary_value = uid)

    if request.method == 'POST':
        form = AccountDescriptionForm(request.POST)
        
        if form.is_valid():
            new_attributes = {
                'description': form.cleaned_data['description'],
            }

            try:
                user.update_attributes(new_attributes)
                user.save()
            except ConstraintViolation:
                request.flash['error'] = "La mise à jour des données transgresse une contrainte du LDAP."
            except InsufficientAccess:
                request.flash['error'] = "La mise à jour des données requiert des droits que vous ne possédez pas."
            except Exception:
                request.flash['error'] = "Une erreur s'est produite lors de la mise à jour."
            else:
                request.flash['success'] = "Votre description a été mise à jour avec succès."
                return HttpResponseRedirect(reverse(account))

    else:
        form = AccountDescriptionForm(label_suffix='', 
                                initial={ 'description': user.description })

    c = { 'form': form }
    c.update(csrf(request))

    return render_to_response('accounts/edit_description.html', c, context_instance=RequestContext(request))
