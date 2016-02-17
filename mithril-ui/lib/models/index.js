'use strict';

var mongoose = require('mongoose');

/**
 * User Schema
 * minimal columns imported from LDAP
 */
var UserSchema = new mongoose.Schema({
  description: String,
  department: String,
  displayName: String,
  sAMAccountName: String,
  mail: String,
  sn: String,
  givenName: String
});

module.exports = {
  User:  mongoose.model('User', UserSchema)
};

