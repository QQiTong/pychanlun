import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store/store'
import axios from './http'
import * as filters from './filters'
import i18n from './lang/i18n'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import echarts from 'echarts'
Vue.config.productionTip = false
Vue.prototype.axios = Vue.prototype.$axios = axios
Vue.prototype.$echarts = echarts
Vue.use(ElementUI)
Object.keys(filters).forEach(key => {
  Vue.filter(key, filters[key])
})
new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app')
