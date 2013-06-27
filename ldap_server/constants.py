SUBTREES_REGEXPS = {
  'People': r'^uid=(?P<uid>[a-z._-]+),ou=People,(?P<base>(dc=[a-z0-9]+,)+(dc=[a-z0-9]+))$',
  
  # Groups
  'Groups': r'^cn=(?P<group>[a-z._-]+),ou=Association,ou=Groups,(?P<base>(dc=[a-z0-9]+,)+(dc=[a-z0-9]+))$',
  'Promotions': r'^cn=(?P<promotion>[0-9]{4}),ou=Promos,ou=Groups,(?P<base>(dc=[a-z0-9]+,)+(dc=[a-z0-9]+))$',

  # Access Groups
  'ServerAccess': r'^cn=(?P<server>[a-z0-9._-]+),ou=ServerAccess,ou=AccessGroups,(?P<base>(dc=[a-z0-9]+,)+(dc=[a-z0-9]+))$',
  'ApplicationAccess': r'^cn=(?P<application>[a-z0-9._-]+),ou=ApplicationAccess,ou=AccessGroups,(?P<base>(dc=[a-z0-9]+,)+(dc=[a-z0-9]+))$',
  'SudoAccess': r'^cn=sudo,ou=(?P<server>[a-z0-9._-]+),ou=SudoAccess,ou=AccessGroups,(?P<base>(dc=[a-z0-9]+,)+(dc=[a-z0-9]+))$',
  'WebAccess': r'^cn=(?P<group>[a-zA-Z0-9._-]+),ou=WebAccess,ou=AccessGroups,(?P<base>(dc=[a-z0-9]+,)+(dc=[a-z0-9]+))$',

  # Aliases
  'Alias': r'^uid=(?P<uid>[a-z0-9._-]+),ou=Aliases,(?P<base>(dc=[a-z0-9]+,)+(dc=[a-z0-9]+))$'
}