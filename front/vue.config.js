const UglifyJSPlugin = require('uglifyjs-webpack-plugin')
const FileManagerPlugin = require('filemanager-webpack-plugin')
const path = require('path')

var FStream = require('fs')
let dev = 'http://127.0.0.1:5000'
let sit = 'http://47.75.57.245'
const os = require('os')
// const UglifyJsParallelPlugin = require('webpack-uglify-parallel')
// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
function resolve(dir) {
  return path.join(__dirname, dir)
}
module.exports = {
  // 基本路径
  outputDir: 'web',
  baseUrl: './',
  productionSourceMap: false,
  // filenameHashing:true,

  configureWebpack: config => {
    // TIP 发布到线上后 process.env.VUE_APP_VERSION 又被还原了 没有效果，
    // TIP 换成 config.plugins[1].definitions['process.env'].VUE_APP_VERSION 实测可行
    // process.env.VUE_APP_VERSION = new Date().getTime()
    config.plugins[1].definitions['process.env'].VUE_APP_VERSION = new Date().getTime()
    console.log('当前版本', config.plugins[1].definitions['process.env'].VUE_APP_VERSION)
    if (process.env.NODE_ENV === 'production' || process.env.NODE_ENV === 'sit' || process.env.NODE_ENV === 'sit_green') {
      // 去除console.log
      // let removeConsole = new UglifyJSPlugin({
      //   uglifyOptions: {
      //     compress: {
      //       drop_console: true,
      //       pure_funcs: ['console.log']
      //     }
      //   },
      //   parallel: os.cpus().length * 2
      // })
      FStream.writeFile('public/version.js', config.plugins[1].definitions['process.env'].VUE_APP_VERSION, function (err) {
        if (err) throw err
        console.log('版本信息写入成功!')
      })
      let fileManager = new FileManagerPlugin({
        onEnd: {
          copy: [
            { source: 'public/version.js', destination: 'web' }
          ],
          archive: [
            {
              source: 'web',
              destination: 'web.zip',
              format: 'zip'
            }
          ]
        }
      })
      // config.plugins.push(UglifyJsParallelPlugin);
      // config.plugins.push(removeConsole)
      config.plugins.push(fileManager)
    } else {
      // mutate for development...
    }
  },
  chainWebpack:(config)=>{
      config.resolve.alias.set('@',resolve('/src'))
  },
  // 配置多页面入口
  pages: {
    index: {
      // page 的入口
      entry: 'src/main.js',
      // 模板来源
      template: 'public/index.html',
      // 在 dist/index.html 的输出
      filename: 'index.html',
      // 当使用 title 选项时，
      // template 中的 title 标签需要是 <title><%= htmlWebpackPlugin.options.title %></title>
      title: 'Index Page',
      // 在这个页面中包含的块，默认情况下会包含
      // 提取出来的通用 chunk 和 vendor chunk。
      chunks: ['chunk-vendors', 'chunk-common', 'index']
    }
  },
  // webpack-dev-server 相关配置
  devServer: {
    // 自动打开浏览器
    open: true,
    port: 8089,
    https: false,
    // TIP 修复热更新失效问题
    hot: true,
    inline: true,
    hotOnly: false,
    // 设置代理
    proxy: {
      // 接口地址为"/v2/xxx/yyy"的所有请求都会走这个代理
      '/api/*': {
        target: dev,
        // target: process.env.VUE_APP_BASE_API,

        // secure: false,  // 如果是https接口，需要配置这个参数
        // 如果接口跨域，需要进行这个参数配置
        changeOrigin: true
      }
    },
    before: app => {}
  }
}
