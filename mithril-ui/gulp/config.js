module.exports = {
  browserify: {
    // Enable source maps
    debug: true,
    bundleConfigs: [{
      entries: './src/scripts/app.js',
      dest: './.tmp',
      outputName: 'app.js'
    }]
  },
  images: {
    src:  './src/images/**',
    dest: './dist/images'
  }
};
