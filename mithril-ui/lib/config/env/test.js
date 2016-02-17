'use strict';

module.exports = {
  env: 'test',
  apiURL: 'http://localhost:5001',
  //apiURL: 'http://flock-alpha4.nihs.ch.nestle.com:5000',
  apiPath: '/api/cgi',
  mongo: {
    uri: 'http://localhost/flock-test'
  }
  // mongo: {
  //   uri: 'mongodb://flock-beta.nihs.ch.nestle.com/flock-test'
  // }
};
