const { defineConfig } = require("@vue/cli-service");
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      "^/api": {
        target: "http://127.0.0.1:4000",
        changeOrigin: true,
        logLevel: "debug",
        ws: true,
        secure: false,
        pathRewrite: { "^/api": "/api" },
      },
    },
  },
  pages: {
    index: {
      entry: "src/main.js",
      title: "Finager",
    },
  },
});
