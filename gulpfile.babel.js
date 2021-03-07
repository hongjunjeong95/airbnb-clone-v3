import gulp from "gulp";
import sass from "gulp-sass";
import autoprefixer from "autoprefixer";
import csso from "gulp-csso";
import postCSS from "gulp-postcss";
import tailwindcss from "tailwindcss";
import del from "del";
import babelify from "babelify";
import bro from "gulp-bro";

const path = {
  scss: {
    src: "assets/scss/styles.scss",
    dest: "static/css",
    watch: "assets/scss/**/*.scss",
  },
  js: {
    src: "assets/js/main.js",
    dest: "static/js",
    watch: "assets/js/**/*.js",
  },
};

const scss = () => {
  sass.compiler = require("node-sass");
  return gulp
    .src(path.scss.src)
    .pipe(sass().on("error", sass.logError))
    .pipe(postCSS([tailwindcss, autoprefixer]))
    .pipe(csso())
    .pipe(gulp.dest(path.scss.dest));
};

const js = () =>
  gulp
    .src(path.js.src)
    .pipe(
      bro({
        transform: [babelify.configure({ presets: ["@babel/preset-env"] })],
      })
    )
    .pipe(gulp.dest(path.js.dest));

const watch = () => {
  gulp.watch(path.scss.watch, scss);
  gulp.watch(path.js.watch, js);
};

const clean = () => del(["static/css/"]);
const assets = gulp.series([scss, js]);

export const build = gulp.series([clean, assets]);
export const dev = gulp.series([build, watch]);
