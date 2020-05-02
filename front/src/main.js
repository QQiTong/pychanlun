import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store/store'
import axios from './http'
import * as filters from './filters'
import i18n from './lang/i18n'
import ElementUI from 'element-ui'
// import 'element-ui/lib/theme-chalk/index.css'
import './style/theme/index.css'
import echarts from 'echarts'
import global from "./global";
import NodeCache from 'node-cache';

Vue.config.productionTip = false
Vue.prototype.axios = Vue.prototype.$axios = axios
Vue.prototype.$echarts = echarts
Vue.use(ElementUI)
Vue.use(global);

Object.keys(filters).forEach(key => {
    Vue.filter(key, filters[key])
})

if (!Vue.prototype.$cache) {
    Vue.prototype.$cache = new NodeCache({
        stdTTL: 3600
    })
}

new Vue({
    router,
    store,
    i18n,
    render: h => h(App)
}).$mount('#app')
