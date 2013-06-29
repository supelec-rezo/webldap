# -*- encoding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, RequestContext, loader
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.mail import send_mail
from django.utils import timezone

from accounts.forms import (LoginForm, RequestPasswdForm, ProcessPasswdForm)

from accounts.models import Request

from backend.base import *
from base.models import *
from models import *
import helpers
import settings

def home(request):
    return render_to_response('home.html', context_instance=RequestContext(request))

def login(request, redirect_field_name = REDIRECT_FIELD_NAME):
    redirect_to = request.REQUEST.get(redirect_field_name, '/account/')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            try:
                uid = form.cleaned_data['uid']
                passwd = form.cleaned_data['passwd']

                bind_dict = {
                    'NAME': 'ldap://ldap.rez-gif.supelec.fr/',
                    'USER': 'uid=%s,ou=People,dc=rezomen,dc=fr' % uid,
                    'PASSWORD': passwd,
                    'CACERT': None,
                    'STARTTLS': False
                }

                # Connects with a default databaseobject (see helpers)
                db = LdapDatabase(bind_dict)
        
            except InvalidCredentials:
                request.flash['error'] = "Vos identifiants sont incorrects."
        
            except ServerDown:
                request.flash['error'] = "Le serveur LDAP est injoignable."

            except ConnectionError:
                request.flash['error'] = "Une erreur indéterminée s'est produite lors de la connexion."
        
            else:
                request.session['ldap_connected'] = True
                request.session['ldap_uid'] = uid
                request.session['ldap_passwd'] = passwd

                request.flash['success'] = "Authentification réussie."
                return HttpResponseRedirect(redirect_to)
    
    else:
        form = LoginForm(label_suffix='')

    vars = { 'form': form, redirect_field_name: redirect_to }
    vars.update(csrf(request))

    return render_to_response('login.html', vars, context_instance=RequestContext(request))


def logout(request, redirect_field_name=REDIRECT_FIELD_NAME, next=None):
    redirect_to = next or request.REQUEST.get(redirect_field_name, '/')
    request.session.flush()
    request.flash['success'] = "Déconnexion réussie."
    return HttpResponseRedirect(reverse('ldap_server.views.login'))

def passwd(request):
    if request.method == 'POST':
        form = RequestPasswdForm(request.POST)

        if form.is_valid():
            req = form.save(commit=False)
            db = helpers.default_database()
            
            user = LdapUser(database = db, primary_value = req.uid, custom_filter = '(mail=%s)' % req.email)
            
            if not user.dn:
                request.flash['error'] = "Aucune entrée correspondant au couple identifiant, adresse email de contact n'a pu être trouvé."

            else:
                req.type = Request.PASSWD
                req.save()

                t = loader.get_template('accounts/mailer/passwd_request')
                c = Context({
                        'name': user.display_name,
                        'url': request.build_absolute_uri(reverse(process, kwargs={ 'token': req.token })),
                        'expire_in': settings.REQ_EXPIRE_STR,
                    })

                send_mail(u'Changement de mot de passe Supélec Rézo', 
                        t.render(c),
                        settings.EMAIL_FROM, 
                        [req.email], 
                        fail_silently=False)

                request.flash['success'] = "Un email a été envoyé à <a href=\"mailto:%(email)s\">%(email)s</a> pour que vous puissiez changer votre mot de passe." % {'email': req.email.encode("utf-8")}
                return HttpResponseRedirect(reverse('ldap_server.views.login'))
    else:
        form = RequestPasswdForm(label_suffix='')

    vars = { 'form': form }
    vars.update(csrf(request))

    return render_to_response('passwd.html', vars, context_instance=RequestContext(request))


def process(request, token):
    valid_reqs = Request.objects.filter(expires_at__gt=timezone.now())
    req = get_object_or_404(valid_reqs, token=token)

    if req.type == Request.PASSWD:
        return process_passwd(request, req)
    else:
        return error(request, 'Entrée incorrecte, contactez un admin')


def process_passwd(request, req):
    if request.method == 'POST':
        form = ProcessPasswdForm(request.POST)
        
        if form.is_valid():
            try:
                db = helpers.default_database()
                user = LdapUser(database = db, primary_value = req.uid)
                user.hashedPassword = form.cleaned_data['passwd'].encode('utf-8')
                user.save()

            except ConstraintViolation:
                request.flash['error'] = "Le mot de passe fourni ne respecte pas les règles de sécurité de l'annuaire LDAP"

            else:
                req.delete()

                request.flash['success'] = "Votre mot de passe a été réinitialisé avec succès."
                return HttpResponseRedirect(reverse('ldap_server.views.login'))
    
    else:
        form = ProcessPasswdForm(label_suffix='')

    vars = { 'form': form }
    vars.update(csrf(request))

    return render_to_response('process_passwd.html', vars, context_instance=RequestContext(request))

def help(request):
    return render_to_response('help.html', context_instance=RequestContext(request))
