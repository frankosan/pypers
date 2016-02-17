'use strict';

 var config = require('./config'),
     request = require('request');

/**
 * Express configuration
 */
exports.proxyRequest = function(req, res) {
  var url = config.apiURL + req.url;

  // forward the GET or PUT HTTP methods
  var proxyRequest = null;

  if(req.method === 'PUT' || req.method === 'POST') {
    proxyRequest = request[req.method.toLowerCase()]({
      url: url,
      json: true,
      body: req.body
    });
  }
  else {
    proxyRequest = request.get({
      url: url,
      json: true
    });
  }

  // 2 secs timeout before aborting
  var proxyTimer = setTimeout(function () {
    proxyRequest.emit("timeout-proxy");
  }, 10000);

  proxyRequest.on("timeout-proxy", function() {
    res.send(408, 'TIMEOUT');
  });

  proxyRequest.on('error', function (e) {
    clearTimeout(proxyTimer);
    console.log('[PROXY-ERROR] %s %o', url, e);

    res.send(500, e);
  });

  proxyRequest.on('response', function (response) {
    clearTimeout(proxyTimer);
    proxyRequest.pipe(res);
  });
};

