import Vue from 'vue'
import Vuex from 'vuex'
import * as getters from './getters'
import mutations from './mutations'

Vue.use(Vuex)
export default new Vuex.Store({
  state: {
    lang: ''
  },
  mutations,
  actions: {},
  getters
})
