var gulp = require('gulp');
var wiredep = require('wiredep').stream;


// This wires dependencies using wiredep. In our case, we are putting bower components
// in the index.html sections marked by <!-- bower -->

// inject bower components into index.html
gulp.task('wiredep', function () {
    gulp.src('src/index.html')
        .pipe(wiredep({
            exclude: ['nihs-birdcage'],
            directory: 'src/bower_components',
            fileTypes: {
                html: {
                    block: /(([\s\t]*)<!--\s*bower:*(\S*)\s*-->)(\n|\r|.)*?(<!--\s*endbower\s*-->)/gi,
                    detect: {
                        js: /<script.*src=['"](.+)['"]>/gi,
                        css: /<link.*href=['"](.+)['"]/gi
                    },
                    replace: {
                        js: '<script src="/{{filePath}}"></script>',
                        css: '<link rel="stylesheet" href="/{{filePath}}" />'
                    }
                }
            }
        }))
        .pipe(gulp.dest('src'));
});
