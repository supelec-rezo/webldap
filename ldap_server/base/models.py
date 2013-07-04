# encoding = utf-8

from ldap_server.backend.base import *
import ldap

class LdapField(object):
    def __init__(self, db_column, multivalued=False, default=None):
        self.db_column = db_column
        self.multivalued = multivalued
        self.default = default

class DoesNotExist(Exception):
    pass

class NoDatabaseProvided(Exception):
    pass

class ConstraintViolation(Exception):
    pass

class UnknownAttribute(Exception):
    pass

class InsufficientAccess(Exception):
    pass

class LdapModel(object):
    
    base_dn = "dc=rezomen,dc=fr"
    object_classes = ['top']
    primary_key = None

    def __init__(self, database, primary_value, custom_filter = None):
        self.database = database
        self.primary_value = primary_value
        self.dn = None
        self.custom_filter = custom_filter

        if self.database:
            filter = self.build_filter()
            attrlist = [attr.db_column for attr in self.attrs_map.values()]
            
            # Array of results (tuples)
            entries = self.database.search_s(base = self.base_dn, 
                                        scope = ldap.SCOPE_SUBTREE, 
                                        filterstr = filter, 
                                        attrlist = attrlist)

            if not len(entries) > 0:
                self.new_entry = True

                for attr,field in self.attrs_map.iteritems():
                    if not field.db_column:
                        continue

                    if field.db_column == self.primary_key:
                        setattr(self, attr, self.primary_value)
                    elif field.default:
                        setattr(self, attr, field.default)
                    else:
                        if field.multivalued:
                            setattr(self, attr, [])
                        else:
                            setattr(self, attr, None)

            else:
                # Entry is a tuple (entry_dn, entry_attributes)
                entry = entries[0]

                if entry:
                    self.dn, self.raw_attributes = entry

                    for attr, field in self.attrs_map.iteritems():
                        if not field.db_column:
                            continue

                        if field.db_column in self.raw_attributes:
                            value = self.raw_attributes[field.db_column]
                        
                            if not field.multivalued:
                                value = value[0]
                            
                            setattr(self, attr, value)

                        else:
                            if not field.multivalued:
                                setattr(self, attr, None)
                            else:
                                setattr(self, attr, [])

        else:
            raise NoDatabaseProvided(self.database)


    def build_filter(self):
        classes_filter = ''.join(['(objectClass=%s)' % cls for cls in self.object_classes])
        primary_filter = '(%s=%s)'%(self.primary_key, self.primary_value)
        
        if not self.custom_filter is None:
            return '(&%s%s%s)'%(classes_filter, primary_filter, self.custom_filter)

        return '(&%s%s)'%(classes_filter, primary_filter)


    def build_rdn(self):
        bits = []
        for attr,field in self.attrs_map.iteritems():
            if field.db_column and field.db_column == self.primary_key:
                bits.append("%s=%s" % (field.db_column, getattr(self, attr)))
        
        if not len(bits):
            raise Exception("Could not build Distinguished Name")
        return '+'.join(bits)

    def build_dn(self):
        return "%s,%s" % (self.build_rdn(), self.base_dn)
        raise Exception("Could not build Distinguished Name")

    def delete(self):
        self.database.delete_s(self.dn)

    def encode(self, value):
        if isinstance(value, list):
            return [encode(val) for val in value]
        elif isinstance(value, (str,unicode)):
            return value.encode('utf-8')

        return value

    def update_attributes(self, attrs):
        for attr,value in attrs.iteritems():
            if not attr in self.attrs_map:
                raise UnknownAttribute(attr)

            else:
                setattr(self, attr, self.encode(value))

    def before_save(self):
        pass

    def save(self):
        self.before_save()

        if not self.dn:
            # Create a new entry 
            entry = [('objectClass', self.object_classes)]
            new_dn = self.build_dn()

            for attr,field in self.attrs_map.iteritems():
                if not field.db_column:
                    continue

                value = getattr(self, attr)

                if value:
                    entry.append((field.db_column, value))

            try:
                self.database.add_s(new_dn, entry)
            except ldap.CONSTRAINT_VIOLATION:
                raise ConstraintViolation
            except ldap.INSUFFICIENT_ACCESS:
                raise InsufficientAccess

            # update object
            self.dn = new_dn

        else:
            # update an existing entry
            modlist = []

            for attr,field in self.attrs_map.iteritems():
                if not field.db_column or not field.db_column in self.raw_attributes:
                    continue

                old_value = self.raw_attributes[field.db_column] if field.multivalued else self.raw_attributes[field.db_column][0]
                new_value = getattr(self, attr, None)

                if old_value != new_value:
                    if new_value:
                        modlist.append((ldap.MOD_REPLACE, field.db_column, new_value))
                    elif old_value:
                        modlist.append((ldap.MOD_DELETE, field.db_column, None))

            if len(modlist):
                # handle renaming
                new_dn = self.build_dn()

                try:
                    if new_dn != self.dn:
                        self.database.rename_s(self.dn, self.build_rdn())
                        self.dn = new_dn
                
                    self.database.modify_s(self.dn, modlist)

                except ldap.CONSTRAINT_VIOLATION:
                    raise ConstraintViolation
                except ldap.INSUFFICIENT_ACCESS:
                    raise InsufficientAccess

            else:
                pass

    @classmethod
    def find_all(cls, database):
        primary_value = '*'
        results = []

        if database:
            classes_filter = ''.join(['(objectClass=%s)' % clss for clss in cls.object_classes])
            primary_filter = '(%s=%s)'%(cls.primary_key, primary_value)

            filter = '(&%s%s)' % (classes_filter, primary_filter)
         
            # Array of results (tuples)
            entries = database.search_s(base = cls.base_dn, 
                                        scope = ldap.SCOPE_SUBTREE, 
                                        filterstr = filter, 
                                        attrlist = [cls.primary_key])

            for entry in entries:
                attributes = entry[1]
                value = attributes[cls.primary_key][0]

                if not value:
                    continue

                results.append(cls(database = database, primary_value = value, custom_filter = None))

        else:
            raise NoDatabaseProvided(database)

        return results
