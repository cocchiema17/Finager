const { defineConfig } = require("@vue/cli-service");

const apiTarget = process.env.VUE_APP_API_TARGET || "http://127.0.0.1:4000";

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    host: "0.0.0.0",
    port: 8080,
    allowedHosts: "all",
    compress: false, // Mantiene fluido lo streaming dei chunk per Server-Sent Events
    proxy: {
      "^/api": {
        target: apiTarget,
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