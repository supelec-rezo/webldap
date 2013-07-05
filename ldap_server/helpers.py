from backend.base import LdapDatabase
from base.models import LdapField, LdapModel
import ldap

import settings
from constants import SUBTREES_REGEXPS

from models import *

def group_filter(regexp):
    return lambda groups: sorted([g for g in groups if re.match(regexp, g)])

def default_database():
    return LdapDatabase(settings.DEFAULT_BIND_DICT)

def find_aliases_by_dn(database, dn):
    database = database if not database is None else default_database()

    base_dn = 'ou=Aliases,dc=rezomen,dc=fr'
    filter = '(&(objectClass=uidObject)(objectClass=alias)(objectClass=OpenLDAPdisplayableObject)(aliasedObjectName=%s))' % dn

    aliases = []

    results = database.search_s(base = base_dn, scope = ldap.SCOPE_SUBTREE, filterstr = filter, attrlist = None)

    for result in results:
        result_dn, result_attrs = result
        alias_name = re.match(SUBTREES_REGEXPS['Alias'], result_dn).group('uid')
        aliases.append(alias_name)

    return aliases
