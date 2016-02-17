var gulp = require('gulp');
var gulpif = require('gulp-if');
var useref = require('gulp-useref');
var uglify = require('gulp-uglify');
var csso = require('gulp-csso');
var plumber = require('gulp-plumber');

gulp.task('build', ['browserify', 'styles', 'images', 'fonts'], function() {
    var assets = useref.assets({ searchPath: ['./.tmp', './src'] });

    gulp.src(['./src/index.html', './src/favicon.ico'])
        .pipe(plumber())
        .pipe(assets)
        .pipe(gulpif('*.js', uglify()))
        .pipe(gulpif('*.css', csso()))
        .pipe(assets.restore())
        .pipe(useref())
        .pipe(gulp.dest('./dist'));

    // move the node server resources
    gulp.src('./server.js')
        .pipe(gulp.dest('./dist'));

    gulp.src('./lib/**/*.js')
        .pipe(gulp.dest('./dist/lib'));

    return;
});
