<template>
  <div :class="{'disabled': disable}"
       @click.stop="verifyBtnClick">{{btnText}}
  </div>
</template>

<script>
  import { futureApi } from '@/api/futureApi'
  import geetestMixin from '@/tool/geetest'

  export default {
    name: 'VerifyBtn',
    mixins: [geetestMixin],
    props: {
      // 按钮文字
      text: {
        type: String,
        default: '发送验证码'
      },
      // 倒计时正在进行时的按钮文字
      onProgressText: {
        type: String,
        default: '{time}s'
      },
      // 倒计时结束后的按钮文字
      onStopedText: {
        type: String,
        default: '发送验证码'
      },
      // 是否需要极验
      geetest: {
        type: Boolean,
        default: true
      },
      // 倒计时时间，以秒为单位
      time: {
        type: Number,
        default: 60
      },
      // 按钮是否禁用
      disabled: {
        type: Boolean,
        default: false
      },
      // 按钮禁用的样式
      disableClass: {
        type: String,
        default: 'disabled'
      },
      // 短信/邮箱模板
      templateCode: {
        type: String,
        default: 'DYNAMIC_VERIFY_CODE'
      },
      // 手机或邮箱号
      value: {
        default: ''
      },
      // 发送验证码的类型，值有email、phone
      type: {
        type: String,
        default: ''
      },
      // 国际区号，只有当type = phone时有效
      countryCode: {
        type: String,
        default: ''
      },
      // 执行条件，函数返回true才会发送验证码，否则不会发送
      condition: {
        type: Function,
        default () {
          return function () {
            return true
          }
        }
      }
    },
    data () {
      return {
        // 是否是第一次执行
        isFirstStart: true,
        // 倒计时是否开始了
        started: false,
        // 倒计时是否结束了
        stoped: false,
        disable: this.disabled,
        // 倒计时时间
        countTime: parseInt(this.time),
        timer: null
      }
    },
    methods: {
      async verifyBtnClick () {
        let that = this
          let condition = await this.condition()
          let mailReg = /^([a-zA-Z0-9]+[_|\-|\\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\-|\\.]?)*[a-zA-Z0-9]+(\.[a-zA-Z]{2,3})+$/
          // mobileReg = /^((13|14|15|17|18)[0-9]{1}\d{8})$/;
          // 手机号只要不包含空格就ok，因为还有国外手机号
          let mobileReg = /\s/
        if (!this.type || (this.type !== 'phone' && this.type !== 'email')) {
          console.error('没有传递type，或type的值不是email或phone')
          return
        }
        if (this.type === 'phone' && !this.countryCode) {
          console.error('没有传递countryCode')
          return
        }
        if (this.disable || this.started) {
          return
        }

        if (condition === false) {
          return
        }
        if (!that.value) {
          console.error(that.value + '不是合法的邮箱或手机号！')
          that.$emit('emailError')
          return
        }
        if (!mailReg.test(that.value) && (mobileReg.test(that.value))) {
          console.error(that.value + '不是合法的邮箱或手机号！')
          return
        }

        if (this.geetest) {
          this.captchaObj.verify()
        } else {
          that.isFirstStart = false
          that.started = true
          that.stoped = false
          that.disable = true

          that._sendMsg()

          that.$emit('onstart', that.countTime)
          this.timer = setInterval(() => {
            if (that.countTime - 1 < 0) {
              clearInterval(that.timer)
              that.started = false
              that.stoped = true
              that.disable = false
              that.countTime = parseInt(that.time)
              that.$emit('onstop', that.countTime)
              return
            }
            that.countTime--
            that.$emit('onprogress', that.countTime)
          }, 1000)
        }
      },
      // 强制中断计时
      abort () {
        clearInterval(this.timer)
        this.countTime = parseInt(this.time)
        this.started = false
        this.stoped = true
        this.disable = false
      },
      // 真正的发送短信/邮箱
      _sendMsg () {
        // let countryCode = this.countryCode,
        //   isPhone = this.type == 'phone'
        // if (isPhone) {
        //   if (countryCode.charAt(0) !== '+') {
        //     countryCode = '+' + countryCode
        //   }
        // }
        this._sendMsgNeedGeetest()
      },
      // 发送短信/邮箱，需要极验
      _sendMsgNeedGeetest () {
        // let isPhone = this.type == 'phone'
        // let countryCode = this.countryCode
        // if (isPhone) {
        //   if (countryCode.charAt(0) !== '+') {
        //     countryCode = '+' + countryCode
        //   }
        // }
        let data = {
          // phone: this.value,
          templateCode: this.templateCode,
          // validateType: isPhone ? 2 : 1,
          // countryCode
          email: this.value
        }
        let geetest = {
          ...this.captchaSuccess,
          sign: this.sign
        }
        futureApi.sendSms(data, geetest)
          .then(() => {
            // alert('验证码发送成功!')
          })
      }
    },
    computed: {
      btnText () {
        if (this.isFirstStart) {
          return this.text
        }
        if (this.started) {
          return this.onProgressText.replace(/{(\w+)}/, this.countTime)
        }
        if (this.stoped) {
          return this.onStopedText
        }
        return ''
      }
    },
    mounted () {
      let that = this
      if (this.geetest) {
        this.initGeetest('a', 'bind', (data) => {
          console.log('极验数据', data)
          that.isFirstStart = false
          that.started = true
          that.stoped = false
          that.disable = true

          that._sendMsgNeedGeetest()

          that.$emit('onstart', that.countTime)
          this.timer = setInterval(() => {
            if (that.countTime - 1 < 0) {
              clearInterval(that.timer)
              that.started = false
              that.stoped = true
              that.disable = false
              that.countTime = parseInt(that.time)
              that.$emit('onstop', that.countTime)
              return
            }
            that.countTime--
            that.$emit('onprogress', that.countTime)
          }, 1000)
        })
      }
    }
  }
</script>

<style scoped>

</style>
