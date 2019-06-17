/*
  该文件主要用于国际化配置
 */
import Vue from 'vue'
// 引入vue国际化插件
import VueI18n from 'vue-i18n'

// 引入自定义的语言包
import zhCN from './zh'
import zhHK from './hk'
import enUS from './en'

Vue.use(VueI18n)

// 定义所有语言
let messages = {
  'zh-CN': {
    ...zhCN
  },
  'zh-TW': {
    ...zhHK
  },
  'en-US': {
    ...enUS
  }
}

const i18n = new VueI18n({
  locale: 'zh-CN', // 语言标识
  messages
})

export default i18n
