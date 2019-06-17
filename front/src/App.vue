<template>
  <div id="app">
    <router-view/>
  </div>
</template>
<script>
  import { mapGetters } from 'vuex'

  export default {
    name: 'app',
    computed: {
      ...mapGetters(['lang'])
    },
    created () {
      this.$i18n.locale = this.lang
    }
  }

</script>

<style lang="stylus">
  @import "./style/base.css"
</style>
