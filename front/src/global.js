import Vue from 'vue'
//期货账户
let futureAccount = 50;
//股票账户
let stockAccount = 3;
//数字货币账户
let digitCoinAccount = 0.01;
export default {
    install () {
        Vue.prototype.$futureAccount = futureAccount;
        Vue.prototype.$stockAccount = stockAccount;
        Vue.prototype.$digitCoinAccount = digitCoinAccount;
    }
}