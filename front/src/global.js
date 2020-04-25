import Vue from 'vue'
// 期货账户
let futureAccount = 50
// 股票账户
let stockAccount = 3
// 数字货币账户
let digitCoinAccount = 60.3 / 10000
// 外盘账户
let globalFutureAccount = 6.4
// 数字货币 杠杆倍数
let digitCoinLevel = 20

export default {
    install () {
        Vue.prototype.$futureAccount = futureAccount
        Vue.prototype.$globalFutureAccount = globalFutureAccount
        Vue.prototype.$stockAccount = stockAccount
        Vue.prototype.$digitCoinAccount = digitCoinAccount
        Vue.prototype.$digitCoinLevel = digitCoinLevel
    }
}