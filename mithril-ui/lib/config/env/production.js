'use strict';

module.exports = {
  env: 'production',
  apiURL: 'http://localhost:5001/api',
  apiPath: '/api/pypers',
  mongo: {
    uri: process.env.MONGOLAB_URI ||
         process.env.MONGOHQ_URL ||
         'mongodb://localhost/flock'
  }
};
