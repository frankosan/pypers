var gulp = require('gulp');

// Fonts
gulp.task('fonts', function() {
    gulp.src(['./src/bower_components/fontawesome/fonts/fontawesome-webfont.*'])
        .pipe(gulp.dest('./dist/fonts/'));

    return;
});
