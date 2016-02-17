'use strict';

var path = require('path'),
    os = require('os');

var rootPath = path.normalize(__dirname + '/../../..');

module.exports = {
  root: rootPath,
  host: os.hostname(),
  port: process.env.PORT || 3000,
  mongo: {
    options: {
      db: {
        safe: true
      }
    }
  },
  groups: {
    yourldapgourp: 'nihs'
  },
  ldap: {
    server: {
        url: 'ldaps://ldap.nestle.com:636',
        tlsOptions: {
            'rejectUnauthorized': false
        }
    },
    base: '',
    search: {
        filter: '(&(objectClass=user)(objectClass=person)(sAMAccountName={{username}}))',
        attributes: [
            'description',    // full name
            'department',     // department
            'givenName',      // first name
            'sn',             // last name
            'mail',           // email address
            'sAMAccountName', // user name
            'displayName'     // full name, location, depatment
        ],
        scope: 'sub'
    },
    uidTag: 'CN',
    usernameField: 'username',
    passwordField: 'password'
  }
};
