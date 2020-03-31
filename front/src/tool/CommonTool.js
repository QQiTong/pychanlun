// let moment = require('moment')

const CommonTool = {
    convertDate() {
        // moment().startOf('day').fromNow()
    },
    versions() {
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
    copyToClipBoard(str) {
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
    },
    dateFormat(fmt) {
        var o = {
            "M+": new Date().getMonth() + 1, //月份
            "d+": new Date().getDate(), //日
            "h+": new Date().getHours(), //小时
            "m+": new Date().getMinutes(), //分
            "s+": new Date().getSeconds(), //秒
            "q+": Math.floor((new Date().getMonth() + 3) / 3), //季度
            "S": new Date().getMilliseconds() //毫秒
        };
        if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (new Date().getFullYear() + "").substr(4 - RegExp.$1.length));
        for (var k in o)
            if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
        return fmt;
    },

    /**
     * Parse the time to string
     * @param {(Object|string|number)} time
     * @param {string} cFormat
     * @returns {string | null}
     */
    parseTime(time, cFormat) {
        if (arguments.length === 0) {
            return null
        }
        const format = cFormat || '{y}-{m}-{d} {h}:{i}:{s}'
        let date
        if (typeof time === 'object') {
            date = time
        } else {
            if ((typeof time === 'string') && (/^[0-9]+$/.test(time))) {
                time = parseInt(time)
            }
            if ((typeof time === 'number') && (time.toString().length === 10)) {
                time = time * 1000
            }
            date = new Date(time)
        }
        const formatObj = {
            y: date.getFullYear(),
            m: date.getMonth() + 1,
            d: date.getDate(),
            h: date.getHours(),
            i: date.getMinutes(),
            s: date.getSeconds(),
            a: date.getDay()
        }
        const time_str = format.replace(/{([ymdhisa])+}/g, (result, key) => {
            const value = formatObj[key]
            // Note: getDay() returns 0 on Sunday
            if (key === 'a') {
                return ['日', '一', '二', '三', '四', '五', '六'][value]
            }
            return value.toString().padStart(2, '0')
        })
        return time_str
    },

    debounce(func, wait, immediate) {
        let timeout, args, context, timestamp, result

        const later = function () {
            // 据上一次触发时间间隔
            const last = +new Date() - timestamp

            // 上次被包装函数被调用时间间隔 last 小于设定时间间隔 wait
            if (last < wait && last > 0) {
                timeout = setTimeout(later, wait - last)
            } else {
                timeout = null
                // 如果设定为immediate===true，因为开始边界已经调用过了此处无需调用
                if (!immediate) {
                    result = func.apply(context, args)
                    if (!timeout) context = args = null
                }
            }
        }
    }
}
export default CommonTool
