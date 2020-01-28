const path = require('path')
const glob = require('glob');

const pageEntry = glob.sync('./src/pages/*').reduce((prev, curr) => {
    prev[curr.slice(12)] = curr;
    return prev;
}, {});

module.exports = (options = {}) => ({
    entry: Object.assign({}, pageEntry),
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: options.dev ? '[name].js' : '[name].js?[chunkhash]',
        chunkFilename: '[id].js?[chunkhash]'
    },
    module: {},
    plugins: [],
    resolve: {
        alias: {
            '~': path.resolve(__dirname, 'src')
        }
    },
    devServer: {},
    devtool: options.dev ? '#eval-source-map' : '#source-map'
});
