'use strict';

var express = require('express'),
    path = require('path'),
    config = require('./config'),
    proxy = require('./proxy'),
    middleware = require('../middleware'),
    passport = require('passport'),
    mongoStore = require('connect-mongo')(express);

/**
 * Express configuration
 */
module.exports = function(app) {
  app.configure('development', function(){
    app.use(require('connect-livereload')());

    // Disable caching of scripts for easier testing
    app.use(function noCache(req, res, next) {
      if (req.url.indexOf('/scripts/') === 0) {
        res.header('Cache-Control', 'no-cache, no-store, must-revalidate');
        res.header('Pragma', 'no-cache');
        res.header('Expires', 0);
      }
      next();
    });

    app.use(express.static(path.join(config.root, '.tmp')));
    app.use(express.static(path.join(config.root, 'src')));
    app.set('views', config.root + '/src');
  });

  // Same as production
  app.configure('beta', function(){
    app.use(express.favicon(path.join(config.root, 'favicon.ico')));
    app.use(express.static(path.join(config.root)));
    app.set('views', config.root);
  });

  app.configure('production', function(){
    app.use(express.favicon(path.join(config.root, 'favicon.ico')));
    app.use(express.static(path.join(config.root)));
    app.set('views', config.root);
  });

  // app.configure('test', function(){
  //   app.use(express.static(path.join(config.root, '.tmp')));
  //   app.use(express.static(path.join(config.root, 'app')));
  //   app.set('views', config.root + '/app/views');
  // });

  app.configure(function(){
    app.engine('html', require('ejs').renderFile);
    app.set('view engine', 'html');
    app.use(express.logger('dev'));
    app.use(express.json());
    app.use(express.urlencoded());
    // app.use(express.multipart());
    app.use(express.methodOverride());
    app.use(express.cookieParser());

    // Persist sessions with mongoStore
    app.use(express.session({
      key: 'hola',
      secret: 'shhhh-workbench-secret',
      store: new mongoStore(
        {
          url: config.mongo.uri,
          collection: 'sessions'
        },
        function () {
          console.log("db connection open");
        }
      ),
      cookie: {
        maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
      }
    }));

    //use passport session
    app.use(passport.initialize());
    app.use(passport.session());

    // secured resources
    app.use('/static'      , middleware.auth);
    app.use('/api/users'   , middleware.auth);
    app.use('/file'        , middleware.auth);
    app.use(config.apiPath , middleware.auth);

    // proxy calls to external api
    app.use(config.apiPath , proxy.proxyRequest);

    // Router needs to be last
    app.use(app.router);
  });

  // Error handler
  app.configure('development', function(){
    app.use(express.errorHandler());
  });
};

