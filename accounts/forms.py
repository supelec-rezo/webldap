# -*- encoding: utf-8 -*-
from django import forms
from accounts.models import Request

def uid_field():
    return forms.CharField(max_length=200,
                           label='Identifiant',
                           widget=forms.TextInput(attrs={ 'placeholder': 'prenom.nom' }))

def passwd_field():
    return forms.CharField(label='Mot de passe', 
                            widget=forms.PasswordInput(attrs={ 'placeholder': 'Mot de passe' }))

def firstname_field():
    return forms.CharField(max_length=200,
                           label='Prénom',
                           widget=forms.TextInput(attrs={'placeholder': 'Prénom'}))

def lastname_field():
    return forms.CharField(max_length=200,
                           label='Nom',
                           widget=forms.TextInput(attrs={ 'placeholder': 'Nom' }))

def nick_field():
    return forms.CharField(max_length=100, 
                            label='Pseudo')

def email_field():
    return forms.EmailField(label="Email de contact", 
                            widget=forms.TextInput(attrs={'placeholder': 'contact.email@domain.com'}))


class LoginForm(forms.Form):
    uid = uid_field()
    passwd = passwd_field()

class ProfileForm(forms.Form):
    firstname = firstname_field()
    lastname = lastname_field()
    
    nick = nick_field()
    
    email = email_field()
    
    passwd = forms.CharField(
             widget=forms.PasswordInput(attrs={'placeholder': 'Uniquement si nouveau' }),
             required=False,
             label='Mot de passe')

class RequestAccountForm(forms.ModelForm):
    uid = uid_field()
    firstname = firstname_field()
    lastname = lastname_field()

    class Meta:
        model = Request
        fields = ('uid', 'email', 'firstname', 'lastname')

class RequestPasswdForm(forms.ModelForm):
    uid = uid_field()
    email = email_field()

    class Meta:
        model = Request
        fields = ('uid', 'email')

class ProcessAccountForm(forms.Form):
    nick = nick_field()
    passwd = passwd_field()


class ProcessPasswdForm(forms.Form):
    passwd = passwd_field()
