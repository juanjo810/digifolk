module.exports = function (api) {
  api.cache(true);

  const presets = [ '@vue/cli-plugin-babel/preset' ];

  return {
    presets,
  };
}
