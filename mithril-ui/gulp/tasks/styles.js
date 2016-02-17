// var gulp = require('gulp');
// var less = require('gulp-less');
// var rename = require('gulp-rename');
// var plumber = require('gulp-plumber');

// gulp.task('styles', function () {
//   return gulp.src('src/styles/app.less')
//         .pipe(plumber())
//         .pipe(less({
//             paths: ['src/styles/']
//         }))
//         .pipe(rename('app.css'))
//         .pipe(gulp.dest('./.tmp'));
// });


'use strict';

var gulp = require('gulp');
var sass = require('gulp-sass');
var rename = require("gulp-rename");

gulp.task('styles', function () {
  gulp.src('./src/styles/*.scss')
    .pipe(sass({includePaths: ['./src/bower_components']}).on('error', sass.logError))
    .pipe(rename("app.css"))
    .pipe(gulp.dest('./.tmp'));
});