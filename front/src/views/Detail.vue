<template>
  <div class="detail">
  </div>
</template>

<script>
  // @ is an alias to /src
  import { mapGetters, mapMutations } from 'vuex'
  // let moment = require('moment')
  export default {
    name: 'down',
    components: { qrCodeCom },
    computed: {
      ...mapGetters(['lang'])
    },
    data () {
      return {}
    },
    mounted () {

    },
    methods: {

    }
  }
</script>
<style lang="stylus">
  @import "../style/detail.styl";
</style>
