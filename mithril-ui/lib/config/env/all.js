'use strict';

var path = require('path'),
    os = require('os'),
    fs = require('fs');

var rootPath = path.normalize(__dirname + '/../../..');

module.exports = {
  root: rootPath,
  host: os.hostname(),
  port: process.env.PORT || 3000,

  services: {
    pypers: {
        path: '/api/pypers',

        ssh: true,
        host: 'localhost',
        port: 5001,

        auth: {
            user: process.env.USER,
            secret: fs.readFileSync(process.env.HOME + '/.ssh/pypers-token').toString()
        },

        rewrite: '/api'
    }
  },

  mongo: {
    options: {
      db: {
        safe: true
      }
    }
  },
  groups: {
    your_company: 'OU=string-Site,OU=Users and Groups,OU=something,OU=EUR,OU=Organizations,DC=somethinc,DC=com',
  },
  ldap: {
    server: {
        url: 'ldaps://ldap.company.com:636',
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
