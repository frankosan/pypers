var m  = require('mithril');

var error       = require('./pages/error'),
    login       = require('./pages/login'),
    assembly    = require('./pages/assembly'),
    annotation  = require('./pages/annotation'),
    runlist     = require('./pages/run-list'),
    landingpage = require('./pages/landingpage'),
    rundetails  = require('./pages/run-details'),
    runcreate   = require('./pages/run-create');
    steplist    = require('./pages/step-list'),
    services    = require('./pages/services');



m.route.mode = 'pathname';
m.route(document.body, '/landingpage', {
    '/error'                : error,
    '/login'                : login,
    '/landingpage'          : landingpage,

    '/runs/:type'           : runlist,
    '/runs/:type/:name'     : runlist,
    '/run/:id'              : rundetails,

    '/run/new/assembly'     : assembly,
    '/run/new/annotation'   : annotation,

    '/run/new/:type'        : runcreate,

    '/steps'                : steplist,

    '/services'             : services

});
