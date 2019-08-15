/*
  注册、登录专用mixin
 */
import { getGtCaptcha } from '../api/geetest'
import { mapGetters } from 'vuex'

export default {
  data () {
    return {
      // 极验验证对象
      captchaObj: null,
      // 极验验证成功后的数据
      captchaSuccess: {},
      // 错误消息
      errorMsg: '',
      // 所有的错误信息
      errorMsgs: [],
      geetestLang: {
        'zh_CN': 'zh-cn',
        'zh_TW': 'zh-tw',
        'en_US': 'en',
        'ja_JP': 'ja',
        'ko_KR': 'ko'
      },
      // 是否使用极验
      showGeetest: false,
      // 极验降级 用的签名
      sign: ''
    }
  },
  methods: {
    // 初始化极验验证
    initGeetest (geetestBox, product, cb) {
      let that = this
      if (!geetestBox && !product && !cb) {
        geetestBox = '#geetest_box'
        product = 'popup'
        cb = function () {
        }
      } else if (geetestBox && !product) {
        product = 'popup'
        cb = function () {
        }
      } else if (geetestBox && product && typeof product === 'function') {
        cb = product
        product = 'popup'
      }

      getGtCaptcha()
        .then(function (data) {
          that._initGeetset_internal_(data.data, geetestBox, product, cb)
        })
        .catch((err) => {
          console.log('极验初始化错误', err)
        })
    },
    // 极验初始化，内部使用
    _initGeetset_internal_ (data, geetestBox, product, cb) {
      let that = this
      console.log('that-----', that.lang)
      let lang = that.lang.replace('-', '_')
      // TIP 后台需要控制是否开启极验，因此需要判断 enable===true && success===1 才显示极限
      that.sign = data.sign
      if (typeof data.enable === 'undefined') {
        that.showGeetest = true
      }
      if (data.enable === true && data.success === 1) {
        that.showGeetest = true
      } else {
        that.showGeetest = false
        return
      }
      window.initGeetest({
        // 以下 4 个配置参数为必须，不能缺少
        gt: data.gt,
        challenge: data.challenge,
        offline: !data.success, // 表示用户后台检测极验服务器是否宕机
        new_captcha: true, // 用于宕机时表示是新验证码的宕机
        product: product, // 产品形式，包括：float，popup，bind
        width: '100%',
        lang: that.geetestLang[lang]
      }, function (captchaObj) {
        // 如果之前已经初始化过了，则线将之前生成的dom移除掉
        if (that.captchaObj) {
          try {
            that.captchaObj.destroy()
            that.captchaObj = null
          } catch (e) {
            console.log(e)
            console.log('销毁极验失败！')
          }
        }
        that.captchaObj = captchaObj
        that.captchaSuccess = {}
        if (product === 'popup') {
          captchaObj.appendTo(geetestBox || '#geetest_box')
        }
        // 当用户操作后并且通过验证后的回调
        captchaObj.onSuccess(function () {
          that.captchaSuccess = captchaObj.getValidate()
          console.log('极验成功:', that.captchaSuccess)
          if (typeof cb === 'function') {
            cb(that.captchaSuccess)
          }
        })
        captchaObj.onError(function () {
          console.log('极验出错了')
        })
      })
    }
  },
  computed: {
    ...mapGetters(['lang'])
  }
}
