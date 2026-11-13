const { defineConfig } = require("@vue/cli-service");
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    compress: false, // Disabilita compressione gzip che bufferizza gli stream SSE
    proxy: {
      "^/api": {
        target: "http://127.0.0.1:4000",
        changeOrigin: true,
        logLevel: "debug",
        ws: true,
        secure: false,
        pathRewrite: { "^/api": "/api" },
        onProxyRes(proxyRes) {
          // Forza il flush immediato dei chunk per Server-Sent Events
          if (proxyRes.headers["content-type"]?.includes("text/event-stream")) {
            proxyRes.headers["cache-control"] = "no-cache";
            proxyRes.headers["x-accel-buffering"] = "no";
          }
        },
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