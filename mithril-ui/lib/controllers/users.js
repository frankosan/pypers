'use strict';

var mongoose = require('mongoose'),
    models = require('../models'),
    passport = require('passport'),
    url = require('url');

/**
 * List users
 */
exports.query = function(req, res, next) {
  var queryObject = url.parse(req.url, true).query || {};

  models.User.find(queryObject, function(err, users) {
    if(err) return next(err);

    res.json(users);
  });
};

/**
 * Create user
 */
// exports.create = function (req, res, next) {
//   var newUser = new models.User(req.body);
//   newUser.provider = 'local';
//   newUser.save(function(err) {
//     if (err) return res.json(400, err);

//     req.logIn(newUser, function(err) {
//       if (err) return next(err);

//       return res.json(req.user.userInfo);
//     });
//   });
// };

/**
 *  Get profile of specified user
 */
exports.show = function (req, res, next) {
  var username = req.params.username;

  models.User.findOne({'username': username}, function (err, user) {
    if (err) return next(err);
    if (!user) return res.send(404);

    res.json(user);
  });
};

exports.preferences = function(req, res, next) {
  var username = req.params.username;

  res.send(200, username);
};

/**
 * Change password
 */
// exports.changePassword = function(req, res, next) {
//   var userId = req.user._id;
//   var oldPass = String(req.body.oldPassword);
//   var newPass = String(req.body.newPassword);

//   models.User.findById(userId, function (err, user) {
//     if(user.authenticate(oldPass)) {
//       user.password = newPass;
//       user.save(function(err) {
//         if (err) return res.send(400);

//         res.send(200);
//       });
//     } else {
//       res.send(403);
//     }
//   });
// };

/**
 * Get current user
 */
exports.me = function(req, res) {
  res.json(req.user || null);
};


/**
 * get current user unix inof
 */
exports.unixme = function(req, res) {
  var getent = require('getent');

  var users = getent.passwd(req.user.sAMAccountName);
  if(users.length > 0) {
    res.send(200, users[0]);
  }
  else {
    res.send(404, {
      message: 'user ' +
               req.user.sAMAccountName +
               ' does not have a unix account'
    });
  }
};

