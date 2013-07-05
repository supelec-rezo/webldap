# -*- encoding: utf-8 -*-

from backend.base import LdapDatabase
from base.models import LdapField, LdapModel
import ldap

from PIL import Image
from io import BytesIO
import base64, getpass, hashlib

import re
from constants import SUBTREES_REGEXPS
import helpers


class LdapUser(LdapModel):

    base_dn = "ou=People,dc=rezomen,dc=fr"
    object_classes = ['inetOrgPerson', 'mailAccountUser', 'posixAccount', 'shadowAccount']
    primary_key = 'uid'

    attrs_map = {
        # Identity
        'username':         LdapField(db_column = 'uid'),
        'nick':             LdapField(db_column = 'cn'),
        'first_name':       LdapField(db_column = 'givenName'),
        'last_name':        LdapField(db_column = 'sn'),
        'display_name':     LdapField(db_column = 'displayName'),

        # Photo
        'photo':            LdapField(db_column = 'jpegPhoto'),

        # Description
        'description':      LdapField(db_column = 'description'),

        # Contacts
        'contact_email':    LdapField(db_column = 'mail'),
        'street':           LdapField(db_column = 'street', default = 'Résidence CÉSAL, 1 rue Joliot-Curie'),
        'city':             LdapField(db_column = 'l', default = 'Gif-sur-Yvette'),
        'postal_code':      LdapField(db_column = 'postalCode', default = '91190'),
        'postal_address':   LdapField(db_column = 'postalAddress', default = 'Inconnu'),
        'mobile':           LdapField(db_column = 'mobile', default = 'Inconnu'),

        # rezomen.fr address
        'rezomen_email':                    LdapField(db_column = 'mailAlternateAddress'),
        'rezomen_email_redirects_to':       LdapField(db_column = 'mailForwardingAddress'),
        'rezomen_email_redirection_status': LdapField(db_column = 'mailAccountStatus', default = 'TRUE'),

        # Server account information
        'uid':      LdapField(db_column = 'uidNumber'),
        'gid':      LdapField(db_column = 'gidNumber'),
        'shell':    LdapField(db_column = 'loginShell', default = '/bin/bash'),
        'home':     LdapField(db_column = 'homeDirectory'),

        # Shadow information and password
        'shadow_min':       LdapField(db_column = 'shadowMin', default = '0'),
        'shadow_max':       LdapField(db_column = 'shadowMax', default = '99999'),
        'shadow_warning':   LdapField(db_column = 'shadowWarning', default = '7'),
        'hashedPassword':   LdapField(db_column = 'userPassword'),

        # Groups
        'groups':           LdapField(db_column = 'memberOf', multivalued = True)
    }

    def __init__(self, *args, **kwargs):
        super(LdapUser, self).__init__(*args, **kwargs)

        self.access_groups = {
            'web_access': [],
            'server_access': [],
            'application_access': [],
            'sudo_access': [],
        }

        self.association_groups = []
        self.promotion_groups = []

        self._init_groups()

    def _init_groups(self):
        if hasattr(self, 'groups'):
            self.access_groups = {
                'web_access':           helpers.group_filter(SUBTREES_REGEXPS['WebAccess'])(self.groups),
                'server_access':        helpers.group_filter(SUBTREES_REGEXPS['ServerAccess'])(self.groups),
                'application_access':   helpers.group_filter(SUBTREES_REGEXPS['ApplicationAccess'])(self.groups),
                'sudo_access':          helpers.group_filter(SUBTREES_REGEXPS['SudoAccess'])(self.groups)
            }

            self.association_groups = helpers.group_filter(SUBTREES_REGEXPS['Groups'])(self.groups)
            self.promotion_groups = helpers.group_filter(SUBTREES_REGEXPS['Promotions'])(self.groups)


    def before_save(self):
        # Formats firstname and lastname
        self.last_name = self.last_name.upper()
        self.first_name = self.first_name.capitalize()
        self.display_name = '%s %s' %(self.first_name, self.last_name)


    def displayable_photo(self):
        if self.photo:
            return Image.open(BytesIO(base64.b64decode(self.photo.encode('base64'))))

        return None

    def promo(self):
        if len(self.promotion_groups) > 0:
            group = self.promotion_groups[0]
            promotion = re.match(SUBTREES_REGEXPS['Promotions'], group).group('promotion')

            return promotion

        return None

    def address(self):
        return "%s, %s %s" % (self.street, self.postal_code, self.city)

    def aliases(self):
        aliases_names = helpers.find_aliases_by_dn(self.database, self.dn)
        return [ LdapAlias(self.database, name) for name in aliases_names ]

    def server_accesses(self):
        servers = []

        for server_dn in self.access_groups['server_access']:
            server_name = re.match(SUBTREES_REGEXPS['ServerAccess'], server_dn).group('server')
            servers.append(LdapServerAccessGroup(self.database, server_name))

        return servers

    def application_accesses(self):
        apps = []

        for group_dn in self.access_groups['application_access']:
            group_name = re.match(SUBTREES_REGEXPS['ApplicationAccess'], group_dn).group('application')
            apps.append(LdapApplicationAccessGroup(self.database, group_name))

        return apps

    def web_accesses(self):
        accesses = []

        for group_dn in self.access_groups['web_access']:
            group_name = re.match(SUBTREES_REGEXPS['WebAccess'], group_dn).group('group')
            accesses.append(LdapWebAccessGroup(self.database, group_name))

        return accesses

    def change_password(self, clear_password):
        self.hashedPassword = clear_password.encode('utf8')
        self.save()

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.display_name

    def __lt__(self, other):
        return self.display_name < other.display_name


class LdapAlias(LdapModel):
    base_dn = "ou=Aliases,dc=rezomen,dc=fr"
    object_classes = ['alias', 'OpenLDAPdisplayableObject']
    primary_key = 'uid'

    attrs_map = {
        'name':                 LdapField(db_column = 'uid'),
        'display_name':         LdapField(db_column = 'displayName'),
        'ref':                  LdapField(db_column = 'aliasedObjectName')
    }

    def __init__(self, *args, **kwargs):
        super(LdapAlias, self).__init__(*args, **kwargs)

    def get_user(self):
        uid = re.match(SUBTREES_REGEXPS['People'], self.ref).group('uid')
        return LdapUser(database = self.database, primary_value = uid)

    def get_user_dn(self):
        return self.ref

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.display_name
    
    def __lt__(self, other):
        return self.display_name < other.display_name


class LdapAccessGroup(LdapModel):
    suffix_dn = "ou=AccessGroups,dc=rezomen,dc=fr"
    object_classes = ['groupOfUniqueNames', 'OpenLDAPdisplayableObject']
    primary_key = 'cn'

    attrs_map = {
        # Information
        'name':             LdapField(db_column = 'cn'),
        'display_name':     LdapField(db_column = 'displayName'),
        'owners':           LdapField(db_column = 'owner', multivalued = True),

        # Members
        'members':          LdapField(db_column = 'uniqueMember', multivalued = True)
    }

    def __init__(self, server, *args, **kwargs):
        super(LdapAccessGroup, self).__init__(*args, **kwargs)

    def get_members(self):
        result = []

        for member_dn in self.members:
            name = re.match(SUBTREES_REGEXPS['People'], member_dn).group('uid')

            if not name:
                continue
                
            user = LdapUser(self.database, name)
            retult.append(user)

        return sorted(result)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.display_name

    def __lt__(self, other):
        return self.display_name < other.display_name


class LdapServerAccessGroup(LdapAccessGroup):
    base_dn = "ou=ServerAccess,ou=AccessGroups,dc=rezomen,dc=fr"
    object_classes = ['groupOfUniqueNames', 'OpenLDAPdisplayableObject']
    primary_key = 'cn'

    attrs_map = {
        # Information
        'name':             LdapField(db_column = 'cn'),
        'display_name':     LdapField(db_column = 'displayName'),
        'owners':           LdapField(db_column = 'owner', multivalued = True),

        # Members
        'members':          LdapField(db_column = 'uniqueMember', multivalued = True)
    }

    def __init__(self, *args, **kwargs):
        super(LdapServerAccessGroup, self).__init__(*args, **kwargs)

    def get_sudoers_group(self):
        return LdapSudoAccessGroup(server = self.name, database = self.database, primary_value = 'sudo')

    def get_sudoers_dn(self):
        return self.get_sudoers_group().members


class LdapSudoAccessGroup(LdapAccessGroup):

    suffix_dn = "ou=SudoAccess,ou=AccessGroups,dc=rezomen,dc=fr"
    object_classes = ['groupOfUniqueNames', 'OpenLDAPdisplayableObject', 'posixAccount']
    primary_key = 'cn'

    attrs_map = {
        # Information
        'name':             LdapField(db_column = 'cn'),
        'display_name':     LdapField(db_column = 'displayName'),
        'owners':           LdapField(db_column = 'owner', multivalued = True),

        # Uid, gid
        'uid':              LdapField(db_column = 'uidNumber', default = '27000'),
        'gid':              LdapField(db_column = 'gidNumber', default = '27000'),
        'homeDirectory':    LdapField(db_column = 'homeDirectory', default = '/dev/null'),

        # Members
        'members':          LdapField(db_column = 'uniqueMember', multivalued = True)
    }

    def __init__(self, server, *args, **kwargs):
        self.server = server
        self.base_dn = "ou=%s,%s" %(server, self.suffix_dn)

        super(LdapSudoAccessGroup, self).__init__(*args, **kwargs)


class LdapApplicationAccessGroup(LdapAccessGroup):
    base_dn = "ou=ApplicationAccess,ou=AccessGroups,dc=rezomen,dc=fr"
    object_classes = ['groupOfUniqueNames', 'OpenLDAPdisplayableObject', 'labeledURIObject']
    primary_key = 'cn'

    attrs_map = {
        # Information
        'name':             LdapField(db_column = 'cn'),
        'display_name':     LdapField(db_column = 'displayName'),
        'url':              LdapField(db_column = 'labeledURI'),

        # Owners
        'owners':           LdapField(db_column = 'owner', multivalued = True),

        # Members
        'members':          LdapField(db_column = 'uniqueMember', multivalued = True)
    }

    def __init__(self, *args, **kwargs):
        super(LdapApplicationAccessGroup, self).__init__(*args, **kwargs)


class LdapWebAccessGroup(LdapAccessGroup):
    base_dn = "ou=WebAccess,ou=AccessGroups,dc=rezomen,dc=fr"
    object_classes = ['groupOfUniqueNames', 'OpenLDAPdisplayableObject', 'labeledURIObject']
    primary_key = 'cn'

    attrs_map = {
        # Information
        'name':             LdapField(db_column = 'cn'),
        'display_name':     LdapField(db_column = 'displayName'),
        'url':              LdapField(db_column = 'labeledURI'),

        # Owners
        'owners':           LdapField(db_column = 'owner', multivalued = True),

        # Members
        'members':          LdapField(db_column = 'uniqueMember', multivalued = True)
    }

    def __init__(self, *args, **kwargs):
        super(LdapWebAccessGroup, self).__init__(*args, **kwargs)