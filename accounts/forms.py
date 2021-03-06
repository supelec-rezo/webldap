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

def first_name_field():
    return forms.CharField(max_length=200,
                           label='Prénom',
                           widget=forms.TextInput(attrs={'placeholder': 'Prénom'}))

def last_name_field():
    return forms.CharField(max_length=200,
                           label='Nom',
                           widget=forms.TextInput(attrs={ 'placeholder': 'Nom' }))

# ***********************************
# Description
# ***********************************

def description_field():
    return forms.CharField(max_length=256,
                           label='Description',
                           widget=forms.TextInput(attrs={ 'placeholder': 'Entrez ici votre description', 'class': 'input-xxlarge' })
                           )

# ***********************************
# Contact
# ***********************************
def email_field():
    return forms.EmailField(label="Email de contact", 
                            widget=forms.TextInput(attrs={'placeholder': 'contact.email@domain.com'}))

def street_field():
    return forms.CharField(max_length=200,
                           label='Adresse',
                           widget=forms.TextInput(attrs={ 'placeholder': 'N° Rue', 'class': 'input-xlarge' }))

def postal_code_field():
    return forms.CharField(max_length=200,
                           label='Code postal',
                           widget=forms.TextInput(attrs={ 'placeholder': 'Code Postal' }))

def city_field():
    return forms.CharField(max_length=200,
                           label='Ville',
                           widget=forms.TextInput(attrs={ 'placeholder': 'Ville' }))

def postal_address_field():
    return forms.CharField(max_length=20,
                           label='Casier/BàL',
                           widget=forms.TextInput(attrs={ 'placeholder': 'Numéro de Casier/BàL' }))

def mobile_field():
    return forms.CharField(max_length=20,
                           label='N° de tél.',
                           widget=forms.TextInput(attrs={ 'placeholder': '(+33) 06 01 02 03 04' }))

def redirection_status_field():
    return forms.BooleanField(label='Activer la redirection de votre adresse @rezomen.fr', required=False)

def redirects_to_field():
    return forms.EmailField(label="Email de redirection", 
                            widget=forms.TextInput(attrs={'placeholder': 'rezomen.fr.redirection@domain.com'}))


class LoginForm(forms.Form):
    uid = uid_field()
    passwd = passwd_field()


class AccountContactForm(forms.Form):
    # Basic contact information
    street = street_field()
    postal_code = postal_code_field()
    city = city_field()
    postal_address = postal_address_field()
    mobile = mobile_field()

    # Rezomen email management
    redirection_status = redirection_status_field()
    redirects_to = redirects_to_field() 


class AccountDescriptionForm(forms.Form):
    description = description_field()


class AccountIdentityForm(forms.Form):
    first_name = first_name_field()
    last_name = last_name_field()


class RequestPasswdForm(forms.ModelForm):
    uid = uid_field()
    email = email_field()

    class Meta:
        model = Request
        fields = ('uid', 'email')


class ProcessPasswdForm(forms.Form):
    passwd = passwd_field()
