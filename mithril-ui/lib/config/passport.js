'use strict';

var LdapStrategy = require('passport-ldapjs').Strategy,
        passport = require('passport'),
        mongoose = require('mongoose'),
            User = mongoose.model('User'),
          config = require('./config');

/**
 * Passport configuration
 */
passport.use(new LdapStrategy(config.ldap,
  function(user, done) {
    var condition = {'sAMAccountName': user.sAMAccountName.toLowerCase()};
    // standardize login to all lowercase
    user.sAMAccountName = user.sAMAccountName.toLowerCase();
    User.update(condition, user, {'upsert': true}, function(err, user) {});

    // wait till the upsert is done
    process.nextTick(function() {
      return done(null, user);
    });
  }
));

// serialize user to his identifier to store with the session
passport.serializeUser(function(user, done) {
  done(null, user.sAMAccountName);
});
// deserialize user to store to be set in the req.user
passport.deserializeUser(function(username, done) {

  User.findOne({
    'sAMAccountName': username
  },
  function(err, user) {
    done(err, user);
  });

});

module.exports = passport;

