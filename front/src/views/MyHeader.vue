<template>
    <div class="header-main">
        <el-button type="primary" @click="jumpToControl('futures')" size="mini" class="primary-button">期货</el-button>
        <h1>顺势而为 抓大放小 以小博大 提高胜率盈亏比（双盘|二买|完备|三买）</h1>
        <el-button type="danger" @click="jumpToControl('stock')" size="mini" class="primary-button">股票</el-button>
        <el-radio-group  style="float:right" v-model="themeOptions.theme" @change="applySetting" size="mini">
            <el-radio-button label="light-theme">Light</el-radio-button>
            <el-radio-button label="dark-theme">Dark</el-radio-button>
        </el-radio-group>
    </div>
</template>

<script>
    // @ is an alias to /src
    export default {
        name: 'my-header',
        props: {
            themeOptions: null,
        },
        data() {
            return {}
        },

        methods: {
            applySetting() {
                this.$parent.applySetting();
            },
            jumpToControl(type) {
                if (type === "futures") {
                    this.$router.replace("/futures-control")
                } else {
                    this.$router.replace("/stock-control")
                }
            }
        }
    }
</script>
<style lang="stylus">
    @import "../style/my-header.styl";
</style>