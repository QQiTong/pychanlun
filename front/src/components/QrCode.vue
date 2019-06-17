<template>
  <div class="qrcode-com" :id="id"></div>
</template>

<script>
  import QRCode from 'qrcodejs2'

  export default {
    name: 'QrCode',
    props: {
      text: {
        type: String,
        default: ''
      },
      width: {
        type: Number,
        default: 145
      },
      height: {
        type: Number,
        default: 145
      },
      // 是否自动更新、当text更改时自定刷新
      autoUpdate: {
        type: Boolean,
        default: true
      }
    },
    data () {
      return {
        id: 'qrcodeCom_' + new Date().getTime() + '_' + Math.random().toString(32).substr(2),
        qrObj: null
      }
    },
    methods: {
      create () {
        if (!this.qrObj) {
          this.qrObj = new QRCode(this.id, {
            text: this.text,
            width: this.width,
            height: this.height
          })
        }
      },
      update (text) {
        if (this.qrObj) {
          this.qrObj.makeCode(text || this.text)
        }
      }
    },
    watch: {
      text (text) {
        if (this.autoUpdate) {
          this.update(text)
        }
      }
    },
    mounted () {
      this.$nextTick(() => {
        this.create()
      })
    }
  }
</script>
