'use strict';

var express = require('express'),
    path = require('path'),
    fs = require('fs'),
    mongoose = require('mongoose');


/**
 * Main application file
 */
var app = express();

// Default node environment to development
process.env.NODE_ENV = process.env.NODE_ENV || app.get('env') || 'development';

// For sneaky errors that were not caught
process.on('uncaughtException', function (err) {
    console.error('An uncaughtException was found, the program will end.', err);
    // TODO proper logging !
    process.exit(1);
});

// Application Config
var config = require('./lib/config/config');

// HTTPS SETUP
var http  = require('http');
var https = require('https');
var privateKey  = fs.readFileSync(process.env.HOME + '/.ssh/' + config.host + '.key', 'utf8');
var certificate = fs.readFileSync(process.env.HOME + '/.ssh/' + config.host + '.cer', 'utf8');

var credentials = {key: privateKey, cert: certificate};


// Connect to database
var db = mongoose.connect(config.mongo.uri, config.mongo.options);

// Bootstrap models
var modelsPath = path.join(__dirname, 'lib/models');
fs.readdirSync(modelsPath).forEach(function (file) {
  if (/(.*)\.(js$)/.test(file)) {
    require(modelsPath + '/' + file);
  }
});


// clear users table
// if (process.env.NODE_ENV) {
//   require('./lib/config/clearusers.js');
// }

// Populate empty DB with sample data
// require('./lib/config/dummydata');

// Passport Configuration
var passport = require('./lib/config/passport');

// Express settings
require('./lib/config/express')(app);

// Routing
require('./lib/routes')(app);

// Start server
// http.createServer(app).listen(config.port);
https.createServer(credentials, app).listen(config.port);

console.log('Express server listening on HTTPS PORT %d in %s mode', config.port, app.get('env'));

// Expose app
exports = module.exports = app;

