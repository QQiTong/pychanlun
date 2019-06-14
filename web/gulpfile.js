var gulp = require('gulp');
var server = require('gulp-devserver');

gulp.task('devserver', function () {
  gulp.src('./')
    .pipe(server({
      livereload: {
      	clientConsole: true
      },
      proxy: {
      	enable: true,
      	host: 'http://127.0.0.1:5000',
      	urls: /^\/api\//
      }
     }));
});