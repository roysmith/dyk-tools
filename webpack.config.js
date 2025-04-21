const path = require('path');

module.exports = {
    entry: {
        pingifier: './js/dyk_pingifier.js',
        review: './js/dyk_reviewTool.js',
    },
    output: {
        filename: '[name].js',
    },
    mode: 'development',
    devtool: false,
    devServer: {
        static: '../dist',
        hot: true,
    },
};
