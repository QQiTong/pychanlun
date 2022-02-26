import Vue from 'vue'
// 全局变量
let xxx = 0

export default {
    install() {
        Vue.prototype.$xxx = xxx
    }
}