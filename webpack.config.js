const path = require('path');

module.exports = {
    entry: './js/dyk_pingifier.js',
    output: {
        filename: 'dyk_pingifier.pack.js',
        path: path.resolve(__dirname, 'dist'),
    },
    mode: 'development',
    // devtool: 'eval-cheap-module-source-map',
    devtool: false,
    devServer: {
        static: '../dist',
        hot: true,
    },
};
