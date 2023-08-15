module.exports = {
  transpileDependencies: true,
  pluginOptions: {
    vuetify: {
      // https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
    }
  },
  configureWebpack: {
    resolve: {
      fallback: {
        "path": require.resolve("path-browserify"),
        "fs": require.resolve("browserify-fs"),
        "crypto": require.resolve("crypto-browserify"),
        "stream": require.resolve("stream-browserify"),
        "util": require.resolve("util/"),
        "module": false,
        "./": false,
        "assert": false
      }
    }
  }
};
