import gulp from "gulp";
import sass from "gulp-sass";
import autoprefixer from "autoprefixer";
import csso from "gulp-csso";
import postCSS from "gulp-postcss";
import tailwindcss from "tailwindcss";
import del from "del";

const path = {
  scss: {
    src: "assets/scss/styles.scss",
    dest: "static/css",
    watch: "assets/scss/**/*.scss",
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

const watch = () => {
  gulp.watch(path.scss.watch, scss);
};

const clean = () => del(["static/css/"]);
const assets = gulp.series([scss]);

export const build = gulp.series([clean, assets]);
export const dev = gulp.series([build, watch]);
