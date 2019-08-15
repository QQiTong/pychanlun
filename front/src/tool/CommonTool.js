// let moment = require('moment')

const CommonTool = {
  convertDate () {
    // moment().startOf('day').fromNow()
  },
  versions () {
    const u = navigator.userAgent
    const app = navigator.appVersion
    return {
      trident: u.indexOf('Trident') > -1, // IE内核
      presto: u.indexOf('Presto') > -1, // opera内核
      webKit: u.indexOf('AppleWebKit') > -1, // 苹果、谷歌内核
      gecko: u.indexOf('Gecko') > -1 && u.indexOf('KHTML') === -1, // 火狐内核
      mobile: !!u.match(/AppleWebKit.*Mobile.*/), // 是否为移动终端
      ios: !!u.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/), // 是否ios终端
      android: u.indexOf('Android') > -1 || u.indexOf('Adr') > -1, // 是否android终端
      iPhone: u.indexOf('iPhone') > -1, // 是否为iPhone或者QQHD浏览器
      iPad: u.indexOf('iPad') > -1, // 是否iPad
      safari: u.indexOf('Safari') === -1, // 是否web应该程序，没有头部与底部
      weixin: u.indexOf('MicroMessenger') > -1, // 是否微信
      qq: String(u.match(/\sqq/i)) === ' qq', // 是否QQ（QQ内置浏览器，空格加qq）
    }
  },
  copyToClipBoard (str) {
    const input = str
    const el = document.createElement('textarea')
    el.value = input
    el.setAttribute('readonly', '')
    // el.style.contain = 'strict';
    el.style.position = 'absolute'
    el.style.left = '-9999px'
    el.style.fontSize = '12pt' // Prevent zooming on iOS

    const selection = getSelection()
    let originalRange = null
    if (selection.rangeCount > 0) {
      originalRange = selection.getRangeAt(0)
    }
    document.body.appendChild(el)
    el.select()
    el.selectionStart = 0
    el.selectionEnd = input.length

    let success = false
    try {
      success = document.execCommand('copy')
    } catch (err) {
      //
    }

    document.body.removeChild(el)

    if (originalRange) {
      selection.removeAllRanges()
      selection.addRange(originalRange)
    }

    return success
  }
}
export default CommonTool
