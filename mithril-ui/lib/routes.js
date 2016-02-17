'use strict';


var api = require('./controllers/api'),
    index = require('./controllers'),
    users = require('./controllers/users'),
    config = require('./config/config'),
    session = require('./controllers/session');

var middleware = require('./middleware');

/**
 * Application routes
 */
module.exports = function(app) {

  app.post('/api/session', session.login);
  app.del('/api/session' , session.logout);

  app.get('/api/users', users.query);
  app.get('/api/users/me', users.me);
  app.get('/api/users/unixme', users.unixme);
  app.get('/api/users/:username' , users.show);
  app.get('/api/users/:username/preferences' , users.preferences);

  app.get('/api/fs/dir.html'  , api.dirRender);
  app.get('/api/fs/dir'   , api.dirRead);
  app.get('/api/fs/txt'   , api.fileRead);
  app.get('/api/fs/fofn'  , api.fofnRead);
  app.get('/api/fs/pdf'   , api.pdfRead);
  app.get('/api/fs/css'   , api.cssRead);
  app.get('/api/fs/html'  , api.htmlRead);
  app.get('/api/fs/png'   , api.pngRead);
  app.post('/api/fs/dir'  , api.dirCreate);
  app.post('/api/fs/file' , api.fileCreate);
  app.del('/api/fs/dir'   , api.dirDelete);
  app.get('/api/fs/file/download', api.fileDownload);

  // All undefined api routes should return a 404
  app.get('/api/*', function(req, res) {
    res.send(404);
  });

  app.get('/*', middleware.setUserCookie , index.index);
};
