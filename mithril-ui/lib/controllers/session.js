'use strict';

var mongoose = require('mongoose'),
    passport = require('passport'),
     config  = require('../config/config'),
           _ = require('lodash');

/**
 * Logout
 */
exports.logout = function (req, res) {
  req.logout();
  res.json({message: 'OK'}, 200);
};

/**
 * Login
 */
exports.login = function (req, res, next) {
  // set LDAP base that corresponds to the user chosen group
  config.ldap.base = config.groups[req.body.groupname];

  passport.authenticate('ldap', function(err, user, info) {
    if(err)  {
      // 128 : connection refused to the ldap server
      if(err.code === 128) {
        return res.send(500, {message:  'Could not connect to LDAP server.'});
      }
      return res.send(500, err);
    }
    // ex: invalid username/password LDAP message
    if(info) return res.json(401, info.message || info);

    // user = LDAP user
    // will call passport.serializeUser -> req.user = sAMAccountName
    req.login(user, function(err) {
      if(err) return res.send(500, err.message);

      var userInfo = _.pick(req.user, [
        'description',
        'department',
        'displayName',
        'sAMAccountName',
        'givenName',
        'sn',
        'mail'
      ]);

      res.cookie('wbuser', JSON.stringify(userInfo));
      res.json(userInfo);
      res.status(200);
    });
  })(req, res, next);
};
