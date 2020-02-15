/* eslint-disable no-unused-vars */
function prepareResize () {
  // 重调尺寸
  this.onResize()
  window.onresize = this.onResize.bind(this)
}

/**
 * 计算屏幕尺寸相关。并调整尺寸。
 * TIP 该方法，采用了YanNan的方式，目前运转正常。
 */
function onResize () {
  // 自动计算html字体
  let htmlFSize
  let adjustRatio = 2 // 为方便计算的整数比例。

  // 重新计算字体尺寸
  function reCalcSize () {
    const clientWidth = docEl.clientWidth > dSize ? dSize : docEl.clientWidth
    if (!clientWidth) {
      return
    }
    // 这里的  750  根据设计稿来定
    htmlFSize = 100 * (clientWidth / dSize) * adjustRatio
    // TIP 这里，我拓展了一下，
    docEl.style.fontSize = htmlFSize + 'px'

    // TIP 绑定方法
    regSizeMethods(htmlFSize)
  }

  // 一些转换方法
  function regSizeMethods (__rootSize) {
    // TIP 新增加的，修复方法。
    // const window_width = screen.width > 768 ? 768 : screen.width;
    // const rem          = window_width * dpr / 10;
    const dpr = window.devicePixelRatio || 1
    const rem = __rootSize
    // console.log('dpr', dpr, 'rem', rem)
    // 给js调用的，某一dpr下rem和px之间的转换函数
    window.rem2px = function (v) {
      const _v = parseFloat(v)
      return _v * rem
    }
    window.px2rem = function (v) {
      const _v = parseFloat(v)
      return _v / rem
    }
    window.dpr = dpr
    window.rem = rem
  }

  // TIP——————————————————————————————正式开始——————————————————————————————————

  // rem布局自适应
  const dSize = 750 // 设计宽度
  const docEl = document.documentElement
  // 获取浏览器支持的改变方向的函数，如果'orientationchange'存在，就使用这个
  const resizeEvt = 'orientationchange' in window ? 'orientationchange' : 'resize'

  // 绑定事件
  if (document.addEventListener) {
    window.addEventListener(resizeEvt, reCalcSize, false)
    document.addEventListener('DOMContentLoaded', reCalcSize, false)
  }
}
this.prepareResize()
