// vue.config.js
module.exports = {
  publicPath: process.env.NODE_ENV === "production" ? "/oj/" : "/",

  assetsDir: "",

  // Used to forward API requests to Django
  devServer: {
    proxy: {
      "/oj/api": {
        target: "http://localhost:8000/oj/api",
        changeOrigin: true,
        pathRewrite: {
          "^/oj/api": "/",
        },
      },
    },
  },
};
