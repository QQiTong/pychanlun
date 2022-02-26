import Vue from 'vue'
// 期货账户
let futureAccount = 58
// 股票账户
let stockAccount = 3
// 数字货币账户
let digitCoinAccount = 60.3 / 10000
// 外盘账户
let globalFutureAccount = 6
// 数字货币 杠杆倍数
let digitCoinLevel = 20
// 'NID', 'CP', 'CT', MZC 美玉米
let globalFutureSymbol = ['CL', 'GC', 'SI', 'HG', 'AHD','NID', 'ZSD','SND', 'ZS', 'MZC', 'ZL', 'FCPO', 'CT',"ZM"]

// 最大资金使用率
let maxAccountUseRate = 0.10

// 止损系数
let stopRate = 0.02

export default {
    install() {
        Vue.prototype.$futureAccount = futureAccount
        Vue.prototype.$globalFutureAccount = globalFutureAccount
        Vue.prototype.$stockAccount = stockAccount
        Vue.prototype.$digitCoinAccount = digitCoinAccount
        Vue.prototype.$globalFutureSymbol = globalFutureSymbol
        Vue.prototype.$maxAccountUseRate = maxAccountUseRate
        Vue.prototype.$stopRate = stopRate
    }
}