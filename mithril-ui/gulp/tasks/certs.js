var gulp = require('gulp'),
    os   = require('os');

var host = os.hostname();
var path = '~/.ssh/';

var cmd = 'openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout ' + path + host + '.key -out ' + path + host + '.cer';

gulp.task('certs', function (cb) {
    console.log(cmd);
});
