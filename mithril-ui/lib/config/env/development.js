'use strict';

module.exports = {
  env: 'development',
  // apiURL: 'http://pypers.nihs.ch.nestle.com:5001/api',
  apiURL: 'http://localhost:5001/api',
  apiPath: '/api/pypers',
  mongo: {
    uri: 'mongodb://localhost/flock-dev'
  }
};

