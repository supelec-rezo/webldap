# encoding = utf-8

import ldap
import logging

# Get an instance of a logger
logger = logging.getLogger('ldap_server.backend.base')
logger.setLevel(logging.INFO)

class InvalidCredentials(Exception):
    pass

class ServerDown(Exception):
    pass

class DatabaseCursor(object):
    def __init__(self, ldap_connection):
        self.connection = ldap_connection

class LdapDatabase(object):
    def __init__(self, settings_dict):
        self.settings_dict = settings_dict
        self.charset = "utf-8"
        self.connection = None
        self._cursor()

    def _cursor(self):
        if self.connection is None:
            try:
                logger.debug('Connecting to LDAP at %s with account %s' %(self.settings_dict['NAME'], self.settings_dict['USER']))
                
                if self.settings_dict['CACERT']:
                    logger.debug('Using CACERT: %s' % self.settings_dict['CACERT'])
                    ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, self.settings_dict['CACERT'])

                self.connection = ldap.initialize(self.settings_dict['NAME'])

                if self.settings_dict['STARTTLS']:
                    logger.debug('Using STARTTLS')
                    self.connection.start_tls_s()

                self.connection.simple_bind_s(
                    self.settings_dict['USER'],
                    self.settings_dict['PASSWORD'])

            except ldap.SERVER_DOWN:
                logger.error('LDAP server is down')
                raise ServerDown

            except ldap.INVALID_CREDENTIALS:
                logger.error('Invalid credentials')
                raise InvalidCredentials
        
        return DatabaseCursor(self.connection)

    def add_s(self, dn, modlist):
        logger.info('Adding entry \'%s\'' % dn)
        cursor = self._cursor()
        return cursor.connection.add_s(dn.encode(self.charset), modlist)

    def delete_s(self, dn):
        logger.info('Deleting entry \'%s\'' % dn)
        cursor = self._cursor()
        return cursor.connection.delete_s(dn.encode(self.charset))

    def modify_s(self, dn, modlist):
        logger.info('Modifying entry \'%s\'' % dn)
        if modlist:
          logger.debug('Modifying attributes: %s' % ', '.join([mod[1] for mod in modlist]))

        cursor = self._cursor()
        return cursor.connection.modify_s(dn.encode(self.charset), modlist)

    def rename_s(self, dn, newrdn):
        logger.info('Renaming entry \'%s\' to \'%s\'' % (dn, newrdn))
        cursor = self._cursor()
        return cursor.connection.rename_s(dn.encode(self.charset), newrdn.encode(self.charset))

    def search_s(self, base, scope, filterstr='(objectClass=*)', attrlist=None):
        logger.debug('Searching entries...')
        logger.debug('Base: %s' % base)
        logger.debug('Filter: %s' % filterstr)
        
        if attrlist:
            logger.debug('Attributes: %s' % ', '.join(attrlist))

        cursor = self._cursor()
        results = cursor.connection.search_s(base, scope, filterstr.encode(self.charset), attrlist)
        output = []
        for dn, attrs in results:
            output.append((dn.decode(self.charset), attrs))
        return output

    def whoami(self):
        return self.settings_dict['USER']
